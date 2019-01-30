# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  浙商银行爬取(这个和别的不同，要获取sessionId和cookies)
#  ----------------------------------------------------------------------
import re

import scrapy

from bankproduct.items import BankproductItem
from bankproduct.service import BankHttpService


class CzbSpider(scrapy.Spider):
    name = 'czb'
    allowed_domains = ['perbank.czbank.com']
    # 获取sessionId值
    session_url = "https://perbank.czbank.com/PERBANK/WebBank"
    start_url = 'https://perbank.czbank.com/PERBANK/Trans'

    session_id = ''
    session_form_data = {
        'dse_operationName': 'financeQryBuySrvOp',
        'cmd': '5',
        'logonflag': '0'
    }

    headers = {
        'Host': 'perbank.czbank.com',
        'Origin': 'https://perbank.czbank.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    form_data = {
        'dse_sessionId': 'DIAFBLCQCPFIFVIADXHZFMBAGQDEBODEEHGXDNBS',
        'dse_operationName': 'financeQryBuySrvOp',
        'cmd': '0',
        'logonflag': '0',
        'OrderFlag': '',
        'CurrType': '',
        'minAmt': '',
        'maxAmt': '9999999999',
        'minTerm': '',
        'maxTerm': '',
        'nowPage': '1',
        'OffSet': '1'
    }

    def start_requests(self):
        # 首先要获取session_id
        yield scrapy.FormRequest(self.session_url, headers=self.headers, formdata=self.session_form_data)
        pass

    def parse(self, response):
        self.session_id = self.__get_xpath_value(response, "//form[@name='financeSignForm']/input[@name='dse_sessionId']/@value").strip()
        self.form_data['dse_sessionId'] = self.session_id
        yield scrapy.FormRequest(self.start_url, method="POST", headers=self.headers, formdata=self.form_data,
                                 callback=self.start_crawl, dont_filter=True)
        pass

    def start_crawl(self, response):
        # 遍历产品
        for product_item in response.xpath("//lotinfo/ul/li"):
            yield self.parse_product_detail(product_item)
        # 判断是否分页
        exist_data = response.xpath("//lotinfo/ul/li")
        if exist_data:
            page_index = int(re.search('nowPage=(\d+)', str(response.request.body, encoding='utf-8')).group(1)) + 1
            off_set = int(re.search('OffSet=(\d+)', str(response.request.body, encoding='utf-8')).group(1)) + 10
            self.form_data['nowPage'] = str(page_index)
            self.form_data['OffSet'] = str(off_set)
            self.form_data['dse_sessionId'] = self.session_id
            yield scrapy.FormRequest(self.start_url, method="POST", headers=self.headers, formdata=self.form_data,
                                     callback=self.start_crawl, dont_filter=True)

        pass

    def parse_product_detail(self, response):
        item = BankproductItem()
        item['bankCode'] = 'czb'
        item['channel'] = 'web'
        product_name = self.__get_xpath_value(response, "div[contains(@class,'nameLC')]/h3/text()").strip()
        item['proCode'] = re.search('型(.*)', product_name).group(1) if re.search('型(.*)',
                                                                                 product_name) else product_name
        item['proName'] = product_name
        firstAmount = self.__get_xpath_value(response, "div[contains(@class,'nameLC')]/p/text()").strip()
        item['firstAmount'] = re.search('(.*)起购', firstAmount).group(1)
        item['incomeRateName'] = self.__get_xpath_value(response, "div[contains(@class,'num_det')]/div[@class='fl_num']/p[@class='num_txt']/text()")
        item['incomeRate'] = self.__get_xpath_value(response, "div[contains(@class,'num_det')]/div[@class='fl_num']/p[1]/text()").strip()
        item['currency'] = self.__get_xpath_value(response, "div[contains(@class,'num_det')]/div[@class='mid_date' and contains(p[@class='num_txt'],'币种')]/p[1]/text()").strip()
        item['cycleTime'] = self.__get_xpath_value(response, "div[contains(@class,'num_det')]/div[@class='mid_date' and contains(p[@class='num_txt'],'理财期限')]/p[1]/text()").strip()
        item['endDate'] = self.__get_xpath_value(response, "div[contains(@class,'num_det')]/div[@class='fr_date' and contains(p[@class='num_txt'],'认购截止日')]/p[1]/text()").strip()
        item['openTime'] = self.__get_xpath_value(response, "div[contains(@class,'num_det')]/div[@class='fr_date' and contains(p[@class='num_txt'],'申购时间')]/p[1]/text()").strip()
        return item

    # 通用的xpath解析值)
    def __get_xpath_value(self, response, xpath) -> str:
        xpath_value = response.xpath(xpath)
        return xpath_value.extract()[0] if len(xpath_value) else ""

    # 爬取完成之后，推送数据
    def close(self, reason):
        bank_http_service = BankHttpService()
        bank_http_service.uploadResult({'bankCode': 'czb'})
        pass