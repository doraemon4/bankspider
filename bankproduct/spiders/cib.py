# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  兴业银行爬取
# ----------------------------------------------------------------------
import logging
import re
from datetime import datetime

import scrapy
from scrapy import Selector
from bankproduct.service import BankHttpService
from bankproduct.items import BankproductItem


class CibSpider(scrapy.Spider):
    name = 'cib'
    allowed_domains = ['wealth.cib.com.cn']
    start_urls = ['http://wealth.cib.com.cn/retail/onsale/index.html',
                  'http://wealth.cib.com.cn/retail/onsale/open.html',
                  'http://wealth.cib.com.cn/retail/onsale/zyb.html',
                  'http://wealth.cib.com.cn/retail/onsale/cash.html',
                  'http://wealth.cib.com.cn/private/wealth/onsale/index.html',
                  'http://wealth.cib.com.cn/organization/gold-ball/',
                  'http://wealth.cib.com.cn/organization/gold-cash/',
                  'http://wealth.cib.com.cn/organization/gold-yyue/'
                  'http://wealth.cib.com.cn/organization/duration/',
                  'http://wealth.cib.com.cn/organization/financing/',
                  'http://wealth.cib.com.cn/institution/hxcf-jl/',
                  'http://wealth.cib.com.cn/institution/hxcf-xy/',
                  'http://wealth.cib.com.cn/institution/hxcf/',
                  'http://wealth.cib.com.cn/institution/security/'
                  ]

    base_url = 'http://wealth.cib.com.cn'

    logger = logging.getLogger(__name__)

    def parse(self, response):
        # 零售理财
        if response.url.find("retail") > 0:
            # 近期发售理财产品
            if response.url.find('index') > 0:
                return self.parse_retail_index(response)
            # 净值型开放式产品简介
            elif response.url.find('open') > 0:
                return self.parse_retail_open(response)
            # 智盈宝
            elif response.url.find('zyb') > 0:
                return self.parse_retail_zyb(response)
            elif response.url.find('cash') > 0:
                return self.parse_retail_cash(response)
            pass
        # 私人银行理财
        elif response.url.find("private") > 0:
            return self.parse_private(response)
        # 机构业务
        elif response.url.find("organization") > 0:
            return self.parse_organization(response)
        # 同业客户业务
        elif response.url.find("institution") > 0:
            return self.parse_organization(response)

    def parse_retail_index(self, response):
        selector = Selector(response)
        for product_item in selector.xpath("//tbody/tr"):
            item = BankproductItem()
            item['bankCode'] = 'cib'
            item['channel'] = 'web'
            item['proCode'] = re.search('lccp(.*?).png', product_item.xpath('td[9]/img/@src').extract()[0]).group(1)
            item['proAttr'] = '零售理财'
            # 判断属否有超链接
            proName = re.search('<a[\S\s]*>(.*?)</a>', product_item.xpath('td[1]').extract()[0])
            item['proName'] = proName.group(1) if (proName != None) else product_item.xpath('td[1]/text()').extract()[0]

            item['incomeRate'] = product_item.xpath('td[7]/text()').extract()[0].strip()
            item['currency'] = product_item.xpath('td[4]/text()').extract()[0].strip()
            item['startDate'] = product_item.xpath('td[2]/text()').extract()[0].strip()
            item['endDate'] = product_item.xpath('td[3]/text()').extract()[0].strip()
            # 大额客户参考净收益率(客户要求放在next_income_rate）
            item['nextIncomeRate'] = product_item.xpath('td[8]/text()').extract()[0].strip()

            # 判断是否含有超链接
            href_num = len(product_item.xpath('td[1]/a/@href').extract())
            if href_num > 0:
                next_page_url = "{}{}".format(self.base_url, product_item.xpath('td[1]/a/@href').extract()[0])
                yield scrapy.Request(next_page_url, meta={'item': item}, callback=self.parse_product_detail,
                                     dont_filter=True)
            else:
                yield item
        pass

    def parse_retail_open(self, response):
        selector = Selector(response)
        # 遍历产品类型
        for product_type in selector.xpath("//*[@id='content']//div[@class='middle']/p"):
            # 找到兄弟节点
            table_selector = product_type.xpath("following-sibling::table[1]")
            title_num = len(table_selector.xpath("tbody/tr[1]").css("td"))
            proAttr = self.__get_xpath_value(product_type, "strong/text()").strip()
            # 遍历除了表头的元素
            for index, product_item in enumerate(table_selector.xpath("tbody/tr[not(contains(td,'产品名称'))]")):
                item = BankproductItem()
                item['bankCode'] = 'cib'
                item['channel'] = 'web'
                item['proAttr'] = proAttr[0:proAttr.find('产品')]
                if title_num == 10:
                    item['proName'] = self.__get_xpath_value(product_item, "td[1]/text()").strip()
                    item['startDate'] = self.__get_xpath_value(product_item, "td[2]/text()").strip()
                    item['endDate'] = self.__get_xpath_value(product_item, "td[3]/text()").strip()
                    item['sellArea'] = self.__get_xpath_value(product_item, "td[4]/text()").strip()
                    item['currency'] = self.__get_xpath_value(product_item, "td[5]/text()").strip()
                    item['cycleTime'] = self.__get_xpath_value(product_item, "td[6]/text()").strip()
                    item['proType'] = self.__get_xpath_value(product_item, "td[7]/text()").strip()
                    item['firstAmount'] = self.__get_xpath_value(product_item, "td[8]/text()").strip()
                    item['incomeRateName'] = '业绩比较基准'
                    # 多个xpath路径可以一起使用
                    item['incomeRate'] = self.__get_xpath_value(product_item, "td[9]/strong/text()|td[9]/text()").strip()
                    product_pic = product_item.xpath('td[10]/img/@src')
                    item['proCode'] = re.search('lccp(.*?).png', product_pic.extract()[0]).group(1) if product_pic else ''
                else:
                    item['proName'] = self.__get_xpath_value(product_item, "td[1]/text()").strip()
                    item['openTime'] = self.__get_xpath_value(product_item, "td[2]/text()").strip()
                    item['sellArea'] = self.__get_xpath_value(product_item, "td[3]/text()").strip()
                    item['currency'] = self.__get_xpath_value(product_item, "td[4]/text()").strip()
                    item['cycleTime'] = self.__get_xpath_value(product_item, "td[5]/text()").strip()
                    item['proType'] = self.__get_xpath_value(product_item, "td[6]/text()").strip()
                    item['firstAmount'] = self.__get_xpath_value(product_item, "td[7]/text()").strip()
                    item['incomeRateName'] = '业绩比较基准'
                    item['incomeRate'] = self.__get_xpath_value(product_item, "td[8]/strong/text()|td[8]/text()").strip()
                    product_pic = product_item.xpath('td[9]/img/@src')
                    item['proCode'] = re.search('lccp(.*?).png', product_pic.extract()[0]).group(1) if product_pic else ''
                pass
                yield item
        pass

    def parse_retail_zyb(self, response):
        table = response.xpath("//*[@id='content']//div[@class='middle']/table")
        proAttr = self.__get_xpath_value(response, "//*[@id='content']//div[@class='middle']/h1/text()").strip()
        for product_item in table.xpath("tbody/tr[not(contains(td,'产品名称'))]"):
            item = BankproductItem()
            item['bankCode'] = 'cib'
            item['channel'] = 'web'
            item['proAttr'] = proAttr
            item['proName'] = self.__get_xpath_value(product_item, "td[1]/text()").strip()
            item['sellArea'] = self.__get_xpath_value(product_item, "td[2]/text()").strip()
            item['proType'] = self.__get_xpath_value(product_item, "td[3]/text()").strip()
            item['firstAmount'] = self.__get_xpath_value(product_item, "td[4]/text()").strip()
            # 募集时间
            raise_date = self.__get_xpath_value(product_item, "td[5]/text()").strip()
            item['startDate'] = self.__get_re_value(raise_date, "(.*)-(.*)", 1).strip()
            year = datetime.strptime(item['startDate'], '%Y年%m月%d日').year
            item['endDate'] = str(year) + "年" +self.__get_re_value(raise_date, "(.*)-(.*)", 2).strip()
            item['incomeRateName'] = self.__get_xpath_value(table, "tbody/tr[1]/td[6]/text()").strip()
            item['incomeRate'] = self.__get_xpath_value(product_item, "td[6]/text()").strip()
            product_pic = product_item.xpath("td[9]/img/@src")
            item['proCode'] = re.search('lccp(.*?).png', product_pic.extract()[0]).group(1) if product_pic else ''
            yield item
        pass

    def parse_retail_cash(self, response):
        table = response.xpath("//*[@id='content']//div[@class='middle']/table")
        proAttr = self.__get_xpath_value(response, "//*[@id='content']//div[@class='middle']/h1/text()").strip()
        for product_item in table.xpath("tbody/tr[not(contains(td,'产品名称'))]"):
            item = BankproductItem()
            item['bankCode'] = 'cib'
            item['channel'] = 'web'
            item['proAttr'] = proAttr
            item['proName'] = self.__get_xpath_value(product_item, "td[1]/strong/a/text()|td[1]/a/text()").strip()
            item['sellArea'] = self.__get_xpath_value(product_item, "td[2]/text()|td[2]/strong/text()").strip()
            item['currency'] = self.__get_xpath_value(product_item, "td[3]/text()|td[3]/strong/text()").strip()
            item['cycleTime'] = self.__get_xpath_value(product_item, "td[4]/text()|td[4]/strong/text()").strip()
            item['proType'] = self.__get_xpath_value(product_item, "td[5]/text()|td[5]/strong/text()").strip()
            item['firstAmount'] = self.__get_xpath_value(product_item, "td[6]/text()|td[6]/strong/text()").strip()
            item['incomeRateName'] = self.__get_xpath_value(table, "tbody/tr[1]/td[7]/strong/text()|tbody/tr[1]/td[7]/text()").strip()
            item['incomeRate'] = self.__get_xpath_value(product_item, "td[7]/text()|td[7]/strong/text()").strip()
            product_pic = product_item.xpath("td[8]/img/@src")
            item['proCode'] = re.search('lccp(.*?).png', product_pic.extract()[0]).group(1) if product_pic else ''
            # 判断是否有超链接
            href_num = len(product_item.xpath('td[1]/strong/a/@href|td[1]/a/@href').extract())
            if href_num:
                next_page_url = self.__get_xpath_value(product_item, "td[1]/strong/a/@href|td[1]/a/@href")
                yield scrapy.Request(next_page_url, meta={'item': item}, callback=self.product_announcement,
                                     dont_filter=True)
                pass
            else:
                yield item
        pass

    def product_announcement(self, response):
        item = response.meta['item']
        setup_announcement = self.__get_xpath_value(response, "//div[@class='financial-tab']/a[contains(text(),'成立公告')]/@href")
        run_announcement = self.__get_xpath_value(response,"//div[@class='financial-tab']/a[contains(text(),'运作公告')]/@href")
        netvalue_rate = self.__get_xpath_value(response,"//div[@class='financial-tab']/a[contains(text(),'净值/收益率')]/@href")
        if run_announcement != '#':
            next_page_url = "{}{}".format(self.base_url, run_announcement)
            yield scrapy.Request(next_page_url, meta={'item': item}, callback=self.next_phase,
                                 dont_filter=True)
        elif setup_announcement != '#':
            next_page_url = "{}{}".format(self.base_url, setup_announcement)
            yield scrapy.Request(next_page_url, meta={'item': item}, callback=self.next_phase,
                                 dont_filter=True)
        elif netvalue_rate != '#':
            next_page_url = "{}{}".format(self.base_url, netvalue_rate)
            yield scrapy.Request(next_page_url, meta={'item': item}, callback=self.next_phase,
                                 dont_filter=True)
        else:
            yield item

    # 返回一个list页面或者直接显示内容
    def next_phase(self, response):
        item = response.meta['item']
        # 不需要再点击一次链接跳转
        if response.xpath("//div[@id='main-text']"):
            table = response.xpath("//*[@id='main-text']/table[1]")
            for product_item in table.xpath("tbody/tr[not(contains(td,'产品代码'))]"):
                item['proCode'] = self.__get_xpath_value(product_item, "td[1]/text()").strip()
                item['proName'] = self.__get_xpath_value(product_item, "td[2]/text()").strip()
                item['openDate'] = self.__get_xpath_value(product_item,"td[3]/text()").strip()
                item['realEndDate'] = self.__get_xpath_value(product_item, "td[4]/text()").strip()
                item['cycleTime'] = self.__get_xpath_value(product_item, "td[5]/text()").strip()
                item['proType'] = self.__get_xpath_value(product_item, "td[6]/text()").strip()
                yield item
        else:
            ul = response.xpath("//div[@id='content']//div[@class='middle']/ul")
            if ul and ul.xpath("li[contains(a,'定期报告')]|li[contains(a,'估值日公告')]"):
                next_page_url = "{}{}".format(self.base_url,self.__get_xpath_value(ul, "li[contains(a,'定期报告')]/a/@href|li[contains(a,'估值日公告')]/a/@href").strip())
                yield scrapy.Request(next_page_url, meta={'item': item}, callback=self.parse_product_detail2,
                                     dont_filter=True)
            else:
                yield item
        pass

    def parse_private(self, response):
        selector = Selector(response)
        # 遍历产品类型
        for product_type in selector.xpath("//*[@id='content']//div[@class='middle']/p[not(@align)]"):
            # 找到兄弟节点
            table_selector = product_type.xpath("following-sibling::table[1]")
            title_num = len(table_selector.xpath("tbody/tr[1]").css("td"))
            # 遍历除了表头的元素
            for index, product_item in enumerate(table_selector.xpath("tbody/tr[not(contains(td,'产品名称'))]")):
                child_num = len(product_item.xpath("td"))
                item = BankproductItem()
                item['bankCode'] = 'cib'
                item['channel'] = 'web'
                item['proType'] = self.__get_xpath_value(product_type, "strong/text()").strip()[2:]

                # 获取产品名称和代码(xpath <br/>会转化为两个节点)
                name_code = product_item.xpath("td[1]/text()").extract()
                if len(name_code) == 1:
                    length = len(re.findall(r"[\(（][^\(（]+[\)）]", name_code[0].strip()))
                    # 含有多个括号的情况，取最后一个
                    if length > 1:
                        product_code = re.findall(r"[\(（][^\(（]+[\)）]", name_code[0].strip())[length - 1]
                    else:
                        product_code = re.search(r"[\(（][^\(（]+[\)）]", name_code[0].strip()).group(0)
                        pass
                else:
                    product_code = name_code[1].strip()[1:-1]

                item['proCode'] = product_code
                item['proName'] = name_code[0][0:name_code[0].find(str(item['proCode']))-1] if len(name_code) == 1 else \
                    name_code[0].strip()

                # 是否含有合并行
                if child_num == title_num:
                    item['cycleTime'] = self.__get_xpath_value(product_item, "td[3]/text()").strip()
                    item['nextIncomeRate'] = self.__get_xpath_value(product_item, "td[4]/text()").strip()
                    pass
                else:
                    item['cycleTime'] = self.__get_xpath_value(product_item, "td[2]/text()").strip()
                    item['nextIncomeRate'] = self.__get_xpath_value(product_item, "td[3]/text()").strip()

                yield item
        pass

    def parse_organization(self, response):
        product_attr = response.xpath("//div[@id='content']//div[@class='top']").css("p>a:last-child::text").extract()[0]
        product_ul = response.xpath("//div[@id='content']//div[@class='middle']/ul")
        for product_item in product_ul.xpath("li"):
            item = BankproductItem()
            item['bankCode'] = 'cib'
            item['channel'] = 'web'
            item['proAttr'] = product_attr
            item['proName'] = self.__get_xpath_value(product_item, "a/text()")
            time_str = self.__get_xpath_value(product_item, "span[@class='time']/text()")
            year = datetime.strptime(time_str, '%Y-%m-%d').year
            # 判断是否是今年的数据
            if year == datetime.now().year:
                next_page_url = "{}{}".format(self.base_url, self.__get_xpath_value(product_item, "a/@href").strip())
                yield scrapy.Request(next_page_url, meta={'item': item}, callback=self.product_announcement,
                                     dont_filter=True)
            else:
                yield item
        pass

    def parse_product_detail(self, response):
        item = response.meta['item']
        selector = Selector(response)
        product_item = selector.xpath("//td[contains(text(),'" + item['proCode'] + "')]/..")
        # 计算总列数
        child_num = len(product_item.css("td"))
        title_num = len(selector.xpath("//table//tr[1]").css("td"))
        # 表头
        title_item = selector.xpath("//table//tr[1]")

        if title_num == 14:
            item['openDate'] = product_item.xpath("td[6]/text()").extract()[0].strip()
            item['realEndDate'] = product_item.xpath("td[7]/text()").extract()[0].strip()
            item['proType'] = product_item.xpath("td[9]/text()").extract()[0].strip()
            if title_num == child_num:
                item['sellChannel'] = product_item.xpath("td[13]/text()").extract()[0].strip()
            else:
                siblings = len(product_item.xpath("preceding-sibling::tr"))
                for i in range(1, siblings):
                    # 找到第一个兄弟元素
                    sibling = product_item.xpath("preceding-sibling::tr["+str(i)+"]")
                    if len(sibling.css("td")) == title_num:
                        item['sellChannel'] = sibling.xpath("td[13]/text()").extract()[0].strip()
                        break
            pass
        else:
            item['openDate'] = product_item.xpath("td[7]/text()").extract()[0].strip()
            item['realEndDate'] = product_item.xpath("td[8]/text()").extract()[0].strip()
            item['proType'] = product_item.xpath("td[11]/text()").extract()[0].strip()
            item['sellArea'] = product_item.xpath("td[6]/text()").extract()[0].strip()
            if title_num == child_num:
                item['sellChannel'] = product_item.xpath("td[15]/text()|td[15]/p/text()").extract()[0].strip()
            else:
                # 兄弟节点的个数
                siblings = len(product_item.xpath("preceding-sibling::tr"))
                for i in range(1, siblings):
                    # 找到第一个兄弟元素
                    sibling = product_item.xpath("preceding-sibling::tr["+str(i)+"]")
                    if len(sibling.css("td")) == title_num:
                        item['sellChannel'] = sibling.xpath("td[15]/text()|td[15]/p/text()").extract()[0].strip()
                        break
            pass
        yield item

    def parse_product_detail2(self, response):
        item = response.meta['item']
        table = response.xpath("//*[@id='main-text']/table[1]")
        for product_item in table.xpath("tbody/tr[not(contains(td,'产品代码'))]|tr[not(contains(td,'产品代码'))]"):
            item['proCode'] = self.__get_xpath_value(product_item, "td[1]/text()").strip()
            item['proName'] = self.__get_xpath_value(product_item, "td[2]/text()").strip()
            item['openDate'] = self.__get_xpath_value(product_item, "td[3]/text()").strip()
            item['realEndDate'] = self.__get_xpath_value(product_item, "td[4]/text()").strip()
            item['cycleTime'] = self.__get_xpath_value(product_item, "td[5]/text()").strip()
            item['proType'] = self.__get_xpath_value(product_item, "td[6]/text()").strip()
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
        bank_http_service.uploadResult({'bankCode': 'cib'})
        pass



