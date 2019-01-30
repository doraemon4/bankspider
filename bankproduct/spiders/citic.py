# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  中信银行爬取
# ----------------------------------------------------------------------
import re

import scrapy

from bankproduct.items import BankproductItem
from bankproduct.service import BankHttpService


class CiticSpider(scrapy.Spider):
    name = 'citic'
    allowed_domains = ['https://etrade.citicbank.com', 'http://www.citicbank.com']
    start_url = 'https://etrade.citicbank.com/portalweb/fd/getFinaList.htm'
    detail_url = 'http://www.citicbank.com/personal/investment/financing'

    form_data = {
        'currType': '',
        'dayDeadline': '',
        'riskLevel': '',
        'firstAmt': '',
        'branchId': '701100',
        'prodState': '',
        'openAttr': '',
        'breakEvenAttr': '',
        'endInterestDate': '',
        'finaQrycondi': '',
        'totuseAmt': '02',
        'orderField': 'ppo_incomerate',
        'orderType': 'desc',
        'currentPage': '1',
        'pageSize': '10',
        'tcstNo': '',
        'userId': '',
        'pwdControlFlag': '0',
        'responseFormat': 'JSON',
        'random': '8040'
    }

    # 重写start_requests方法
    def start_requests(self):
        yield scrapy.FormRequest(self.start_url, method="POST", formdata=self.form_data)
        pass

    def parse(self, response):
        # 解析各个产品
        for product_item in re.findall('"prdNo":"(.*?)"', response.text):
            product_item_url = "{}{}{}{}".format(self.detail_url, '/', str(product_item),
                                                 '.html')
            yield scrapy.Request(product_item_url, callback=self.parse_product_detail, dont_filter=True)

        # 是否存在下一页数据
        exist_data = re.search('"prdNo":"(.*?)"', response.text)
        if exist_data:
            currentPage = int(re.search('currentPage=(\d+)', str(response.request.body, encoding='utf-8')).group(1))
            currentPage = currentPage + 1
            self.form_data['currentPage'] = str(currentPage)
            yield scrapy.FormRequest(self.start_url, method="POST", formdata=self.form_data, dont_filter=True)
        pass

    def parse_product_detail(self, response):
        item = BankproductItem()

        item['bankCode'] = 'citic'
        item['channel'] = 'web'
        item['proCode'] = self.__get_xpath_value(response, "//td[text()='产品代码']/../td[2]/text()").strip()
        item['proName'] = self.__get_re_value(response.text, "<div class=\"title_l\">(.*?)<span>", 1).strip()
        cycleTime = self.__get_xpath_value(response, "//td[text()='产品期限']/../td[2]/script/text()").strip()
        item['cycleTime'] = self.__get_re_value(cycleTime, "'(.*?)'", 1) + '天'
        item['firstAmount'] = self.__get_xpath_value(response, "//td[text()='购买起点']/../td[2]/@startpoint").strip()

        # 币种
        currency_flag = self.__get_xpath_value(response, "//span[text()='币种']/../span[2]/@curr_type")
        if currency_flag == '001':
            item['currency'] = "人民币"
        elif currency_flag == '014':
            item['currency'] = "美元"
        pass

        # 风险等级
        riskLevel_flag = self.__get_xpath_value(response, "//span[text()='风险等级']/../span[2]/@risklevel")
        if riskLevel_flag == '0':
            item['riskLevel'] = '无风险'
        elif riskLevel_flag == '1':
            item['riskLevel'] = '低风险'
        elif riskLevel_flag == '2':
            item['riskLevel'] = '较低风险'
        elif riskLevel_flag == '3':
            item['riskLevel'] = '中等风险'
        elif riskLevel_flag == '4':
            item['riskLevel'] = '较高风险'
        elif riskLevel_flag == '5':
            item['riskLevel'] = '高风险'

        # 产品状态
        status_flag = self.__get_xpath_value(response, "//span[text()='产品状态']/../span[2]/@prod_state")
        if status_flag == '0':
            item['status'] = '开放期'
        elif status_flag == '1':
            item['status'] = '募集期'
        elif status_flag == '3':
            item['status'] = '发行失败'
        elif status_flag == '4':
            item['status'] = '停止交易'

        # 管理机构
        proManager_code = self.__get_xpath_value(response, "//span[text()='管理机构']/../span[2]/@prdmanager")
        if proManager_code == '008':
            item['proManager'] = '中信银行'

        item['openDate'] = self.__get_xpath_value(response, "//span[text()='起息日']/../span[2]/text()").strip()
        item['realEndDate'] = self.__get_xpath_value(response, "//span[text()='到期日']/../span[2]/text()").strip()
        item['nextOpenDate'] = self.__get_xpath_value(response, "//span[text()='下一开放日']/../span[2]/text()").strip()

        # 销售对象
        sellObject = self.__get_xpath_value(response, "//span[text()='产品面向客户群']/../span[2]/script/text()")
        sellObject = self.__get_re_value(sellObject, '"(.*?)"', 1)
        item['sellObject'] = sellObject.replace('0', "个人普通客户 ").replace('1', "个人金卡客户 ") \
            .replace('2', "个人白金客户 ").replace('4', "个人钻石客户")

        # 销售区域
        item['sellArea'] = self.__get_xpath_value(response, "//span[text()='销售区域']/../span[2]/text()").strip()
        item['incomeRate'] = self.__get_xpath_value(response, "//div[@class='col-lg-4 col-md-4 col-sm-4  lc_text_m']/div/span/@finagains")

        proNetValue = self.__get_xpath_value(response, "//span[text()='产品净值']/../span[2]/script/text()")
        item['proNetValue'] = self.__get_re_value(proNetValue, '"(.*?)"', 1)

        maxSingleRed = self.__get_xpath_value(response, "//span[text()='赎回单笔上限']/../span[2]/script/text()")
        item['maxSingleRed'] = '0.00' if self.__get_re_value(maxSingleRed, '"(.*?)"', 1) == '' \
            else self.__get_re_value(maxSingleRed, '"(.*?)"', 1)

        minSingleRed = self.__get_xpath_value(response, "//span[text()='赎回单笔下限']/../span[2]/script/text()")
        item['minSingleRed'] = '0.00' if self.__get_re_value(minSingleRed, '"(.*?)"', 1) == '' \
            else self.__get_re_value(minSingleRed, '"(.*?)"', 1)

        maxSingleSub = self.__get_xpath_value(response, "//span[text()='认购单笔上限']/../span[2]/script/text()")
        item['maxSingleSub'] = '0.00' if self.__get_re_value(maxSingleSub, '"(.*?)"', 1) == '' \
            else self.__get_re_value(maxSingleSub, '"(.*?)"', 1)

        minSingleSub = self.__get_xpath_value(response, "//span[text()='认购单笔下限']/../span[2]/script/text()")
        item['minSingleSub'] = '0.00' if self.__get_re_value(minSingleSub, '"(.*?)"', 1) == '' \
            else self.__get_re_value(minSingleSub, '"(.*?)"', 1)

        maxSinglePur = self.__get_xpath_value(response, "//span[text()='申购单笔上限']/../span[2]/script/text()")
        item['maxSinglePur'] = '0.00' if self.__get_re_value(maxSinglePur, '"(.*?)"', 1) == '' \
            else self.__get_re_value(maxSinglePur, '"(.*?)"', 1)

        minSinglePur = self.__get_xpath_value(response, "//span[text()='申购单笔下限']/../span[2]/script/text()")
        item['minSinglePur'] = '0.00' if self.__get_re_value(minSinglePur, '"(.*?)"', 1) == ''\
            else self.__get_re_value(minSinglePur, '"(.*?)"', 1)

        minRedUnit = self.__get_xpath_value(response, "//span[text()='赎回基数']/../span[2]/script/text()")
        item['minRedUnit'] = '0.00' if self.__get_re_value(minRedUnit, '"(.*?)"', 1) == '' \
            else self.__get_re_value(minRedUnit, '"(.*?)"', 1)

        minSubUnit = self.__get_xpath_value(response, "//span[text()='认购基数']/../span[2]/script/text()")
        item['minSubUnit'] = '0.00' if self.__get_re_value(minSubUnit, '"(.*?)"', 1) == '' \
            else self.__get_re_value(minSubUnit, '"(.*?)"', 1)

        minPurUnit = self.__get_xpath_value(response, "//span[text()='申购基数']/../span[2]/script/text()")
        item['minPurUnit'] = '0.00' if self.__get_re_value(minPurUnit, '"(.*?)"', 1) == '' \
            else self.__get_re_value(minPurUnit, '"(.*?)"', 1)

        allowedResRed = self.__get_xpath_value(response, "//span[text()='是否允许预约赎回']/../span[2]/@dataisbit")
        item['allowedResRed'] = allowedResRed.replace('0', "否").replace('1', "是")

        allowedRelRed = self.__get_xpath_value(response, "//span[text()='是否允许实时赎回']/../span[2]/@dataisbit")
        item['allowedRelRed'] = allowedRelRed.replace('0', "否").replace('1', "是")

        item['instructionUrl'] = self.__get_xpath_value(response, "//div[@class='title_r']/ul/li[1]/a/@href")

        yield item

    pass

    # 通用的xpath解析值)
    def __get_xpath_value(self, response, xpath) -> str:
        xpath_value = response.xpath(xpath)
        return xpath_value.extract()[0] if len(xpath_value) else ""

    # 通用的正则解析值
    def __get_re_value(self, content: str, pattern, index: int) -> str:
        value = ''
        try:
            value = re.search(pattern, content, re.M | re.I).group(index)
        except Exception as e:
            pass
        return value

    # 爬取完成之后，推送数据
    def close(self, reason):
        bank_http_service = BankHttpService()
        bank_http_service.uploadResult({'bankCode': 'citic'})
        pass
