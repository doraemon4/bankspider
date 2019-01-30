# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  华夏银行爬取(这个是前端分页)
# ----------------------------------------------------------------------
import scrapy
import re
from scrapy import Selector

from bankproduct.items import BankproductItem
from bankproduct.service import BankHttpService


class HxbSpider(scrapy.Spider):
    name = 'hxb'
    allowed_domains = ['www.hxb.com.cn']
    start_urls = ['http://www.hxb.com.cn/grjr/lylc/zzfsdlccpxx/index.shtml']

    def parse(self, response):
        selector = Selector(response)
        for product_item in selector.xpath("//*[@id='content']//li[@name='pageli']"):
            item = BankproductItem()
            item['bankCode'] = 'hxb'
            item['channel'] = 'web'

            item['proName'] = self.__get_xpath_value(product_item, "div[@class='pro_box']/p[@class='box_title']/a/text()").strip()
            item['cycleTime'] = self.__get_xpath_value(product_item, "div[@class='pro_box']/ul//span[@class='highlight']/text()").strip()
            title = self.__get_xpath_value(product_item, "div[@class='pro_box']/div[@class='box_lf']/p[2]/text()").strip()

            if title == '预期最高年化收益率':
                item['incomeRateName'] = title
                item['incomeRate'] = self.__get_xpath_value(product_item, "div[@class='pro_box']//p[@class='box_num']/text()").strip()
            else:
                item['proNetValue'] = self.__get_xpath_value(product_item, "div[@class='pro_box']//p[@class='box_num']/text()").strip()

            item['startDate'] = re.search('(.*?)至', self.__get_xpath_value(product_item,
                    "div[@class='pro_box']//span[text()='发售日期']/../span[2]/text()")).group(1)
            item['endDate'] = re.search('至(.*)', self.__get_xpath_value(product_item,
                    "div[@class='pro_box']//span[text()='发售日期']/../span[2]/text()")).group(1)
            item['firstSubMinAmount'] = self.__get_xpath_value(product_item,
                    "div[@class='pro_box']//span[@class='amt']/text()").strip() + self.__get_xpath_value(product_item,
                    "div[@class='pro_box']//span[@class='amt']/following-sibling::text()").strip()
            sellChannel = self.__get_xpath_value(product_item, "div[@class='pro_box']//span[text()='购买渠道']/../span[2]/text()").strip()
            # 替换不可见字符
            item['sellChannel'] = re.sub('[\r\n\t\s]', '', sellChannel)
            yield item
        pass

    # 获取返回内容
    def __get_response_content(self, response) -> str:
        return response.body.decode(response.encoding, errors='ignore')

    # 通用的xpath解析值)
    def __get_xpath_value(self, response, xpath) -> str:
        xpath_value = response.xpath(xpath)
        return xpath_value.extract()[0] if len(xpath_value) else ""

    # 爬取完成之后，推送数据
    def close(self, reason):
        bank_http_service = BankHttpService()
        bank_http_service.uploadResult({'bankCode': 'hxb'})
        pass