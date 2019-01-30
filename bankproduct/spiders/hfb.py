# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  恒丰银行爬取
# ----------------------------------------------------------------------
import scrapy
import re

from scrapy import Selector

from bankproduct.items import BankproductItem
from bankproduct.service import BankHttpService


class HfbSpider(scrapy.Spider):
    name = 'hfb'
    allowed_domains = ['www.hfbank.com.cn']
    start_url = 'http://www.hfbank.com.cn/ucms/hfyh/jsp/gryw/lc_lb.jsp'
    detail_url = 'http://www.hfbank.com.cn/ucms/hfyh/jsp/gryw/lc_xq.jsp'

    form_data = {
        'ptType': 'lcpt',
        'order': 'false',
        'nameValue': 'RsgStrtDt',
        'search': '',
        'TypeNo': '0,1,2',
        'Status': '',
        'Limit': '',
        'RiskLevel': '',
        'CurrType': '',
        'pageStartCount': '0',
        'pagecount': '8'
    }

    # 重写start_requests方法
    def start_requests(self):
        yield scrapy.FormRequest(self.start_url, method="POST", formdata=self.form_data)
        pass

    def parse(self, response):
        # 解析各个产品
        for product_item in re.findall('PrdCode=(.*?)&', response.text):
            product_item_url = "{}{}{}{}".format(self.detail_url, '?PrdCode=', str(product_item),
                                                 '&staticPrefix=q')
            yield scrapy.Request(product_item_url, callback=self.parse_product_detail, dont_filter=True)
        # 是否存在下一页数据
        exist_data = re.search('PrdCode=(.*?)', response.text)
        if exist_data:
            pageStartCount = int(re.search('pageStartCount=(\d+)', str(response.request.body, encoding='utf-8')).group(1))
            # 每页数据条数
            pagecount = int(re.search('pagecount=(\d+)', str(response.request.body, encoding='utf-8')).group(1))
            pageStartCount = pageStartCount + pagecount
            self.form_data['pageStartCount'] = str(pageStartCount)
            yield scrapy.FormRequest(self.start_url, method="POST", formdata=self.form_data, dont_filter=True)
        pass

    def parse_product_detail(self, response):
        selector = Selector(response)
        item = BankproductItem()

        item['bankCode'] = 'hfb'
        item['channel'] = 'web'
        item['proCode'] = self.__get_xpath_value(response, "//table[@class='con2']/tbody/tr[1]/td[2]/text()").strip()
        item['proName'] = self.__get_xpath_value(response, "//table[@class='con2']/tbody/tr[1]/td[4]/text()").strip()
        item['openDate'] = self.__get_xpath_value(response, "//table[@class='con2']/tbody/tr[2]/td[2]/text()").strip()
        item['realEndDate'] = self.__get_xpath_value(response, "//table[@class='con2']/tbody/tr[2]/td[4]/text()").strip()
        item['currency'] = self.__get_xpath_value(response, "//table[@class='con2']/tbody/tr[3]/td[2]/text()").strip()
        item['riskLevel'] = self.__get_xpath_value(response, "//table[@class='con2']/tbody/tr[3]/td[4]/text()").strip()
        item['cycleTime'] = self.__get_xpath_value(response, "//table[@class='con2']/tbody/tr[5]/td[2]/text()").strip()
        item['endDate'] = self.__get_xpath_value(response, "//table[@class='con2']/tbody/tr[5]/td[4]/text()").strip()
        sellChannel = self.__get_xpath_value(response, "//table[@class='con2']/tbody/tr[6]/td[2]/text()").strip()
        item['sellChannel'] = re.sub('[\r\n\t\s]', '', sellChannel)
        item['incomeRateName'] = self.__get_xpath_value(response, "//div[@class='con1 of']/table/tbody/tr[1]/td[1]/text()").strip()
        item['incomeRate'] = self.__get_xpath_value(response, "//div[@class='con1 of']/table/tbody/tr[1]/td[2]/p/text()").strip()
        item['firstAmount'] = self.__get_xpath_value(response, "//table[@class='con2']/tbody/tr[4]/td[2]/text()").strip()
        minSubUnit = self.__get_xpath_value(response, "//table[@class='con2']/tbody/tr[4]/td[4]/text()").strip()
        item['minSubUnit'] = re.search('((\d)+.(\d)+)', minSubUnit).group(0)

        # 产品说明书下载路径
        instructionUrl = self.__get_xpath_value(response, "//a[@class='download' and contains(@href,'说明书')]/@href")
        if instructionUrl:
            strs = self.start_url.split('/')
            num = len(strs)
            index = self.start_url.find(strs[num - 1], 0)
            item['instructionUrl'] = '{}{}'.format(self.start_url[0:index], instructionUrl)
        # 风险说明书下载路径
        riskDisclosureUrl = self.__get_xpath_value(response, "//a[@class='download' and contains(@href,'风险')]/@href")
        if riskDisclosureUrl:
            strs = self.start_url.split('/')
            num = len(strs)
            index = self.start_url.find(strs[num - 1], 0)
            item['riskDisclosureUrl'] = '{}{}'.format(self.start_url[0:index], riskDisclosureUrl)
        yield item
        pass

    # 通用的xpath解析值)
    def __get_xpath_value(self, response, xpath) -> str:
        xpath_value = response.xpath(xpath)
        return xpath_value.extract()[0] if len(xpath_value) else ""

    # 爬取完成之后，推送数据
    def close(self, reason):
        bank_http_service = BankHttpService()
        bank_http_service.uploadResult({'bankCode': 'hfb'})
        pass
