# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  光大银行爬取(post请求form表单)
# ----------------------------------------------------------------------
import scrapy
import re
from scrapy import Selector
from bankproduct.items import BankproductItem
from bankproduct.service import BankHttpService


class CebSpider(scrapy.Spider):
    name = 'ceb'
    allowed_domains = ['www.cebbank.com']
    start_url = 'http://www.cebbank.com/eportal/ui?' \
                'moduleId=12073&struts.portlet.action=/app/yglcAction!listProduct.action'
    base_url = 'http://www.cebbank.com'
    # 请求参数
    # form_data='codeOrName=&TZBZMC=RMB&QGJE=&QGJELEFT=&QGJERIGHT=&CATEGORY=&CPQXLEFT=&CPQXRIGHT=&CPFXDJ=&SFZS=Y&qxrUp=Y&qxrDown=&dqrUp=&dqrDown=&qdjeUp=&qdjeDown=&qxUp=&qxDown=&yqnhsylUp=&yqnhsylDown=&page=1&pageSize=12&channelIds[]=yxl94&channelIds[]=ygelc79&channelIds[]=hqb30&channelIds[]=dhb2&channelIds[]=cjh&channelIds[]=gylc70&channelIds[]=Ajh67&channelIds[]=Ajh84&channelIds[]=901776&channelIds[]=Bjh91&channelIds[]=Ejh99&channelIds[]=Tjh70&channelIds[]=tcjh96&channelIds[]=ts43&channelIds[]=ygjylhzhMOM25&channelIds[]=yxyg87&channelIds[]=zcpzjh64&channelIds[]=wjyh1&channelIds[]=smjjb9&channelIds[]=ty90&channelIds[]=tx16&channelIds[]=ghjx6&channelIds[]=wf36&channelIds[]=ygxgt59&channelIds[]=wbtcjh3&channelIds[]=wbBjh77&channelIds[]=wbTjh28&channelIds[]=sycfxl&channelIds[]=cfTjh&channelIds[]=jgdhb&channelIds[]=tydhb&channelIds[]=jgxck&channelIds[]=jgyxl&channelIds[]=tyyxl&channelIds[]=dgBTAcp&channelIds[]=27637097&channelIds[]=27637101&channelIds[]=27637105&channelIds[]=27637109&channelIds[]=27637113&channelIds[]=27637117&channelIds[]=27637121&channelIds[]=27637125&channelIds[]=27637129&channelIds[]=27637133&channelIds[]=gyxj32&channelIds[]=yghxl&channelIds[]=ygcxl&channelIds[]=ygjxl&channelIds[]=ygbxl&channelIds[]=ygqxl&channelIds[]=yglxl&channelIds[]=ygzxl'
    form_data = {
        'codeOrName': '',
        'TZBZMC': '',
        'SFZS': '',
        'qxrUp': 'Y',
        'qxrDown': '',
        'dqrUp': '',
        'dqrDown': '',
        'qdjeUp': '',
        'qdjeDown': '',
        'qxUp': '',
        'qxDown': '',
        'yqnhsylUp': '',
        'yqnhsylDown': '',
        'page': '1',
        'pageSize': '12',
        'channelIds[]': ['yxl94', 'ygelc79', 'hqb30', 'dhb2', 'cjh', 'gylc70', 'Ajh67', 'Ajh84', '901776', 'Bjh91',
                         'Ejh99', 'Tjh70', 'tcjh96', 'ts43', 'ygjylhzhMOM25', 'zcpzjh64', 'wjyh1', 'smjjb9', 'ty90',
                         'tx16', 'ghjx6', 'ygxgt59', 'wbtcjh3', 'wbBjh77', 'wbTjh28', 'sycfxl', 'cfTjh', 'jgdhb',
                         'tydhb', 'jgxck', 'jgyxl', 'tyyxl', 'dgBTAcp', '27637097', '27637101', '27637105', '27637109',
                         '27637113', '27637117', '27637121', '27637125', '27637129', '27637133', 'gyxj32', 'yghxl',
                         'ygcxl', 'ygjxl', 'ygbxl', 'ygqxl', 'yglxl', 'ygzxl']
    }

    # 重写start_requests方法
    def start_requests(self):
        yield scrapy.FormRequest(self.start_url, method="POST", formdata=self.form_data)
        pass

    def parse(self, response):
        # 解析各个产品
        # for product_item in re.findall('lccpsj/(.*?)/index', response.text):
        for product_item in response.xpath("//div[@class='lccp_main_content_tx']/ul/li"):
            item = BankproductItem()
            item['bankCode'] = 'ceb'
            item['channel'] = 'web'
            item['incomeRate'] = self.__get_xpath_value(product_item,
                                                        "p[@class='lccp_syl']/span[@class='lccp_ll fc_box']/text()").strip()
            product_item_url = "{}{}".format(self.base_url, self.__get_xpath_value(product_item, "a/@href").strip())
            yield scrapy.Request(product_item_url, callback=self.parse_product_detail, meta={'item': item}, dont_filter=True)

        # 是否存在下一页数据
        exist_data = re.search('cpmc-(.*?)', response.text)
        if exist_data:
            # response.request.body获取请求中的body
            page_index = int(re.search('page=(\d+)', str(response.request.body, encoding='utf-8')).group(1)) + 1
            self.form_data['page'] = str(page_index)
            yield scrapy.FormRequest(self.start_url, method='POST', formdata=self.form_data, dont_filter=True)

    def parse_product_detail(self, response):
        selector = Selector(response)
        item = response.meta['item']
        item['proCode'] = self.__get_xpath_value(response, "//input[@id='cpCode']/@value").strip()
        item['proName'] = self.__get_xpath_value(response, "//div[@class='xq_tit']/text()").strip()
        item['proType'] = self.__get_xpath_value(response, "//input[@id='sfzqxcpmc']/@value").strip()
        # 隐藏表单区域页面显示不出来
        item['firstAmount'] = self.__get_xpath_value(response, "//input[@id='qgje']/@value").strip()
        item['currency'] = self.__get_xpath_value(response, "//input[@id='tzbzmc']/@value").strip()
        start_date = self.__get_xpath_value(response, "//input[@id='startDate']/@value").strip()
        item['startDate'] = start_date if re.match(r'\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}',
                                                   start_date, re.M | re.I) else ""
        end_date = self.__get_xpath_value(response, "//input[@id='endDate']/@value").strip()
        item['endDate'] = end_date if re.match(r'\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}',
                                               end_date, re.M | re.I) else ""
        next_open_date = self.__get_xpath_value(response, "input[@id='jzxkfr1']/@value").strip()
        item['nextOpenDate'] = next_open_date if re.match(r'\d{4}年\d{1,2}月\d{1,2}日',
                                                          next_open_date, re.M | re.I) else ""
        item['incomeRateName'] = self.__get_xpath_value(response, "//div[@class='syl_wz']/text()").strip()
        # item['incomeRate'] = self.__get_xpath_value(response, "//div[@class='syl_sz']/text()").strip()
        item['cycleTime'] = self.__get_xpath_value(response, "//div[@class='lcqx_sz']/text()").strip()
        item['riskLevel'] = self.__get_xpath_value(response, "//div[text()='风险等级']/../div[2]/text()").strip()

        # 匹配动态区域,enumerate返回的是下标和item组成的元组
        name_list = selector.xpath("//ul[@class='fdsy_con_name1 fl']/li")
        for index, name_selector in enumerate(name_list):
            field_name = name_selector.xpath("text()").extract()[0]
            data = name_selector.xpath("../following-sibling::ul[@class='fdsy_con_nr1 fl']/li/text()").extract()
            if field_name == '起息日':
                item['openDate'] = data[index].strip()
            elif field_name == '到期日':
                item['realEndDate'] = data[index].strip()
            elif field_name == '销售起始日':
                # 不做处理等同于item['startDate']
                pass
            elif field_name == '销售终止日':
                # 不做处理等同于item['endDate']
                pass
            elif field_name == '下一申购日':
                item['nextOpenDate'] = data[index].strip()

        name_list = selector.xpath("//ul[@class='fdsy_con_name fl']/li")

        for index, name_selector in enumerate(name_list):
            field_name = name_selector.xpath("text()").extract()[0]
            data = name_selector.xpath("../following-sibling::ul[@class='fdsy_con_nr fl']/li/text()").extract()
            if field_name == '产品种类':
                item['proAttr'] = data[index].strip()
                pass
        instructionUrl = self.__get_xpath_value(response, "//a[@class='cpsms_file']/@href").strip()
        item['instructionUrl'] = "{}{}".format(self.base_url, instructionUrl) if instructionUrl else ''
        yield item
        pass

    # 通用的xpath解析值
    def __get_xpath_value(self, response, xpath) -> str:
        xpath_value = response.xpath(xpath)
        return xpath_value.extract()[0] if len(xpath_value) else ""

    # 爬取完成之后，推送数据
    def close(self, reason):
        bank_http_service = BankHttpService()
        bank_http_service.uploadResult({'bankCode': 'ceb'})
        pass