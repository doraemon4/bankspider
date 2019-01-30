# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  广发银行爬取
# ----------------------------------------------------------------------
import scrapy
import re

from bankproduct.items import BankproductItem
from bankproduct.service import BankHttpService


class CgbSpider(scrapy.Spider):
    name = 'cgb'
    allowed_domains = ['www.cgbchina.com.cn']
    start_url = 'http://www.cgbchina.com.cn/Channel/16684283'
    base_url = 'http://www.cgbchina.com.cn'

    form_data = {
        'prodFlag': '2',
        'rowsPerpage': '12',
        'turnPageShowNum': '12',
        'turnPageBeginPos': '1',
        'productcycle': '1',
        'currencytypeFlag': '0',
        'currencytype': 'NOT',
        'leastamount': 'NOT',
        'leastamountFlag': '0',
        'yearyield': 'NOT',
        'yearyieldFlag': '0',
        'riskLevel': '00',
        'riskLevelFlag': '0',
        'financingType': '2',
        'producttype': '3',
        'producttypeFlag': '0',
        'status': '0',
        'structureFlag': '0',
        'sort': '4',
        'sortType': '2',
        'inputyearyield': '',
        'currPage': '1',
        'nav': '2',
        'turnPageShowNum': ''
    }

    # 重写start_requests方法
    def start_requests(self):
        yield scrapy.FormRequest(self.start_url, method="POST", formdata=self.form_data)
        pass

    def parse(self, response):
        # 解析各个产品
        for product_item in response.xpath("//*[@id='product_tab']//tr[@class='bg2']"):
            item = BankproductItem()
            item['bankCode'] = 'cgb'
            item['channel'] = 'web'

            item['proName'] = self.__get_xpath_value(product_item, "td[@class='name']/a/text()").strip()
            item_url = self.__get_xpath_value(product_item, "td[@class='name']/a/@href").strip()
            item['proCode'] = self.__get_re_value(item_url, 'productno=(.*)', 1)
            item['currency'] = self.__get_xpath_value(product_item, "td[2]/text()").strip()
            item['cycleTime'] = self.__get_xpath_value(product_item, "td[3]/text()").strip().replace('&nbsp','')
            item['firstAmount'] = self.__get_xpath_value(product_item, "td[4]/text()").strip()
            item['incomeRateName'] = self.__get_xpath_value(response, "//*[@id='product_tab']/tr[1]/th[5]/text()").strip()
            item['incomeRate'] = self.__get_xpath_value(product_item, "td[5]/b/text()").strip()
            item['riskLevel'] = self.__get_xpath_value(product_item, "td[6]/text()").strip()

            recruitment_period = self.__get_xpath_value(product_item, "td[7]/text()").strip()
            if recruitment_period != '长&nbsp&nbsp&nbsp期':
                item['startDate'] = self.__get_re_value(recruitment_period, "(.*?)至", 1)
                item['endDate'] = self.__get_re_value(recruitment_period, "至(.*?)", 1)
                pass

            product_item_url = "{}{}".format(self.base_url, item_url)
            yield scrapy.Request(product_item_url, meta={'item': item}, callback=self.parse_product_detail, dont_filter=True)

        # 是否存在下一页数据
        exist_data = response.xpath("//*[@id='product_tab']//tr[@class='bg2']/td[@class='name']/a/@href")
        if exist_data:
            # 当前页
            currPage = int(re.search('currPage=(\d+)', str(response.request.body, encoding='utf-8')).group(1))
            currPage = currPage + 1
            # 每页数量
            pageSize = int(re.search('rowsPerpage=(\d+)', str(response.request.body, encoding='utf-8')).group(1))
            # 每页开始
            turnPageBeginPos = int(re.search('turnPageBeginPos=(\d+)', str(response.request.body, encoding='utf-8')).group(1))
            turnPageBeginPos = turnPageBeginPos + pageSize
            self.form_data['currPage'] = str(currPage)
            self.form_data['turnPageBeginPos'] = str(turnPageBeginPos)
            yield scrapy.FormRequest(self.start_url, method="POST", formdata=self.form_data, dont_filter=True)
    pass

    def parse_product_detail(self, response):
        item = response.meta['item']
        item['minSubUnit'] = self.__get_xpath_value(response, "//dt[text()='购买单位(元)：']/following-sibling::dd/text()").strip()
        instructionUrl = self.__get_xpath_value(response, "//*[@id='pdf_product']/a[@class='media']/@href").strip()
        if instructionUrl:
            item['instructionUrl'] = '{}{}'.format(self.base_url, instructionUrl)
        riskDisclosureUrl = self.__get_xpath_value(response, "//*[@id='pdf_risk']/a[@class='media']/@href").strip()
        if riskDisclosureUrl:
            item['riskDisclosureUrl'] = '{}{}'.format(self.base_url, riskDisclosureUrl)
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
        bank_http_service.uploadResult({'bankCode': 'cgb'})
        pass