# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  招商银行爬取
# ----------------------------------------------------------------------
import scrapy
import re

from bankproduct.items import BankproductItem
from bankproduct.service import BankHttpService


class CmbSpider(scrapy.Spider):
    name = 'cmb'
    allowed_domains = ['www.cmbchina.com']
    start_urls = ['http://www.cmbchina.com/cfweb/svrajax/product.ashx?op=search&type=m&series=01&pagesize=20&pageindex=1']
    base_url = 'http://www.cmbchina.com/cfweb/personal/productdetail.aspx?code='

    def parse(self, response):

        # 解析具体的产品
        for product_item in re.findall('PrdCode:"(\S+?)"', response.text):
            url = "{}{}{}".format(self.base_url, product_item, "&type=prodinfo")
            yield scrapy.Request(url, callback=self.parse_product_detail, dont_filter=True)

        # 是否存在下一页数据
        exist_data = re.search('PrdCode:"(\S+?)"', response.text)
        if exist_data:
            # 拼接url
            pageindex = int(re.search('pageindex=(\d+)', response._url).group(1)) + 1
            next_page_url = '{}{}'.format('http://www.cmbchina.com/cfweb/svrajax/product.ashx?op=search&type=m&salestatus=&baoben=&currency=&term=&keyword=&series=01&risk=&city=&date=&pagesize=20&orderby=ord1&t=0.8941125939142096&citycode=&pageindex=', pageindex)
            yield scrapy.Request(next_page_url, dont_filter=True)
        pass

    def parse_product_detail(self, response):
        item = BankproductItem()

        item['bankCode'] = 'cmb'
        item['channel'] = 'web'
        proCode = self.__get_xpath_value(response, "//li[contains(text(),'产品代码')]/span/text()").strip()
        item['proCode'] = proCode

        item['proName'] = self.__get_xpath_value(response, "//td[contains(text(), '产品简称')]/following-sibling::td[1]/text()").strip()
        item['proAttr'] = self.__get_xpath_value(response, "//li[contains(text(),'产品类别')]/span/text()").strip()
        item['proType'] = self.__get_xpath_value(response, "//li[contains(text(),'投资类型')]/span/text()").strip()
        # item['sellObject'] = self.__get_xpath_value(response)
        # item['status'] = self.__get_xpath_value(response)
        item['currency'] = self.__get_xpath_value(response, "//td[contains(text(), '币种')]/following-sibling::td[1]/text()").strip()
        # item['crFlag'] = self.__get_xpath_value(response)
        # item['cycleTime'] = self.__get_xpath_value(response)
        # item['incomeRateName'] = self.__get_xpath_value(response)
        # item['incomeRate'] = self.__get_xpath_value(response)
        # item['nextIncomeRate'] = self.__get_xpath_value(response)
        # item['interestType'] = self.__get_xpath_value(response)
        item['riskLevel'] = self.__get_xpath_value(response, "//li[contains(text(),'风险评级')]/span/text()").strip()
        # item['redRule'] = self.__get_xpath_value(response)
        # item['buyRule'] = self.__get_xpath_value(response)
        item['startDate'] = self.__get_xpath_value(response, "//li[contains(text(),'发售起始日期')]/span/text()").strip()
        item['endDate'] = self.__get_xpath_value(response, "//li[contains(text(),'发售截止日期')]/span/text()").strip()
        # item['openDate'] = self.__get_xpath_value(response)
        # nextOpenDate = self.__get_xpath_value(response)
        # nextEndDate = self.__get_xpath_value(response)
        item['realEndDate'] = self.__get_xpath_value(response, "//li[contains(text(),'产品到期日')]/span/text()").strip()
        # openTime = self.__get_xpath_value(response)
        # closeTime = self.__get_xpath_value(response)
        # proManager = self.__get_xpath_value(response)
        # sellArea = self.__get_xpath_value(response)
        item['sellChannel'] = self.__get_xpath_value(response, "//li[contains(text(),'销售渠道')]/span/text()").strip()
        # currentPurchases = self.__get_xpath_value(response)
        item['firstAmount'] = self.__get_xpath_value(response, "//td[contains(text(), '认购价格')]/following-sibling::td[1]/text()").strip()
        item['firstSubMinAmount'] = self.__get_xpath_value(response, "//td[contains(text(), '首次认购下限')]/following-sibling::td[1]/text()").strip()
        item['minPurBalance'] = self.__get_xpath_value(response, "//td[contains(text(), '最低申购余额')]/following-sibling::td[1]/text()").strip()
        item['minRedBalance'] = self.__get_xpath_value(response, "//td[contains(text(), '最低赎回余额')]/following-sibling::td[1]/text()").strip()
        item['minSubUnit'] = self.__get_xpath_value(response, "//td[contains(text(), '认购基数')]/following-sibling::td[1]/text()").strip()
        item['minPurUnit'] = self.__get_xpath_value(response, "//td[contains(text(), '申购基数')]/following-sibling::td[1]/text()").strip()
        item['minRedUnit'] = self.__get_xpath_value(response, "//td[contains(text(), '赎回基数')]/following-sibling::td[1]/text()").strip()
        item['maxSingleSub'] = self.__get_xpath_value(response, "//td[contains(text(), '认购单笔上限')]/following-sibling::td[1]/text()").strip()
        item['maxSinglePur'] = self.__get_xpath_value(response, "//td[contains(text(), '申购单笔上限')]/following-sibling::td[1]/text()").strip()
        item['maxSingleRed'] = self.__get_xpath_value(response, "//td[contains(text(), '赎回单笔上限')]/following-sibling::td[1]/text()").strip()
        item['minSingleSub'] = self.__get_xpath_value(response, "//td[contains(text(), '认购单笔下限')]/following-sibling::td[1]/text()").strip()
        item['minSinglePur'] = self.__get_xpath_value(response, "//td[contains(text(), '申购单笔上限')]/following-sibling::td[1]/text()").strip()
        item['minSingleRed'] = self.__get_xpath_value(response, "//td[contains(text(), '赎回单笔上限')]/following-sibling::td[1]/text()").strip()
        # maxOneDaySub = self.__get_xpath_value(response)
        # plainHold = self.__get_xpath_value(response)
        # proNetValue = self.__get_xpath_value(response)
        # allowedResRed = self.__get_xpath_value(response)
        # allowedRelRed = self.__get_xpath_value(response)
        item['overviewUrl'] = '{}{}{}'.format("http://www.cmbchina.com/cfweb/Personal/productdetail.aspx?code=", proCode, "&type=prodintro")
        # item['overviewDownloadUrl'] = ''
        item['infoUrl'] = '{}{}{}'.format("http://www.cmbchina.com/cfweb/Personal/productdetail.aspx?code=", proCode, "&type=prodinfo")
        # item['infoDownloadUrl'] = ''
        item['noticeUrl'] = '{}{}{}'.format("http://www.cmbchina.com/cfweb/Personal/productdetail.aspx?code=", proCode, "&type=prodnotice")
        # item['noticeDownloadUrl'] = ''
        item['netWorthUrl'] = '{}{}{}'.format("http://www.cmbchina.com/cfweb/Personal/productdetail.aspx?code=", proCode, "&type=prodvalue")
        # item['netWorthDownloadUrl'] = ''
        item['reportUrl'] = '{}{}{}'.format("http://www.cmbchina.com/cfweb/Personal/productdetail.aspx?code=", proCode, "&type=prodir")
        # item['reportDownloadUrl'] = ''
        item['commentUrl'] = '{}{}{}'.format("http://www.cmbchina.com/cfweb/Personal/productdetail.aspx?code=", proCode, "&type=prodcomment")
        # item['commentDownloadUrl'] = ''
        item['instructionUrl'] = '{}{}{}'.format("http://www.cmbchina.com/cfweb/Personal/productdetail.aspx?code=", proCode, "&type=prodexplain")
        # item['instructionDownloadUrl'] = ''
        item['riskDisclosureUrl'] = '{}{}{}'.format("http://www.cmbchina.com/cfweb/Personal/productdetail.aspx?code=", proCode, "&type=prodrisk")
        # item['riskDisclosureDownloadUrl'] = ''

        yield scrapy.Request(item['instructionUrl'], meta={'item': item}, callback=self.parse_product_detail_2, dont_filter=True)
        # yield item

    # 取出产品说明书下载地址
    def parse_product_detail_2(self, response):
        # 接收上级已爬取的数据
        item = response.meta['item']
        item['instructionDownloadUrl'] = self.__get_xpath_value(response, "//a[contains(text(), '理财计划产品说明书')]/@href").strip()

        yield scrapy.Request(item['riskDisclosureUrl'], meta={'item': item}, callback=self.parse_product_detail_3, dont_filter=True)

    # 取出风险揭示书下载地址
    def parse_product_detail_3(self, response):
        # 接收上级已爬取的数据
        item = response.meta['item']
        item['riskDisclosureDownloadUrl'] = self.__get_xpath_value(response, "//a[contains(text(), '理财计划风险揭示书')]/@href").strip()

        yield scrapy.Request(item['netWorthUrl'], meta={'item': item}, callback=self.parse_product_detail_4, dont_filter=True)

    # 取出最新的产品净值
    def parse_product_detail_4(self, response):
        # 接收上级已爬取的数据
        item = response.meta['item']
        item['proNetValue'] = self.__get_xpath_value(response,"//table[@class='ProductTable']//tr[2]/td[3]/text()").strip()

        yield scrapy.Request(item['overviewUrl'], meta={'item': item}, callback=self.parse_product_detail_5, dont_filter=True)

    # 取出费用
    def parse_product_detail_5(self, response):
        # 接收上级已爬取的数据
        item = response.meta['item']
        selectors = response.xpath("//span[contains(text(), '费用')]/../../following-sibling::td/p")
        if selectors:
            content = ''
            for selector in selectors:
                content = content + "".join(selector.xpath("span/text()").extract())
            item['feeRate'] = content
        yield item

        # 获取返回内容
    def __get_response_content(self, response) -> str:
        return response.body.decode(response.encoding, errors='ignore')

    # 通用的xpath解析值
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
        bank_http_service.uploadResult({'bankCode': 'cmb'})
        pass
