# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  民生银行爬取(post请求json数据)
# ----------------------------------------------------------------------
import scrapy
import json
import re
from bankproduct.items import BankproductItem
from bankproduct.service import BankHttpService


class CmbcSpider(scrapy.Spider):
    name = 'cmbc'
    allowed_domains = ['www.cmbc.com.cn']
    # start_urls = ['http://http://www.cmbc.com.cn//']
    start_url = 'http://www.cmbc.com.cn/channelApp/ajax/Financialpage'
    base_url = "http://www.cmbc.com.cn/channelApp/ajax/FinancialDetail"

    # 重写start_requests方法
    def start_requests(self):

        data = {"request": {"body": {"page": 1, "row": 10}}}

        # FormRequest 是Scrapy发送POST请求的方法
        yield scrapy.Request(self.start_url, method="POST",
                             body=json.dumps(data),
                             headers={'Content-Type': 'application/json'})

    def parse(self, response):
        # 解析具体的产品
        for product_item in re.findall('"PRD_CODE":"(.*?)"', response.text):
            data = {"request": {"body": {"prd_code": str(product_item)}}}

            yield scrapy.Request(self.base_url, method="POST",
                                 body=json.dumps(data),
                                 headers={'Content-Type': 'application/json'},
                                 callback=self.parse_product_detail, dont_filter=True)
        # 是否存在下一页数据
        exist_data = re.search('"PRD_CODE":"(.*?)"', response.text)
        if exist_data:
            # 拼接url
            pageindex = int(re.findall('"page":(\d+)', response.text)[1]) + 1
            data = {"request": {"body": {"page": pageindex, "row": 10}}}
            yield scrapy.Request(self.start_url, method="POST",
                                 body=json.dumps(data),
                                 headers={'Content-Type': 'application/json'}, dont_filter=True)
        pass

    def parse_product_detail(self, response):
        url = response.url
        content = self.__get_response_content(response)
        item = BankproductItem()

        item['bankCode'] = 'cmbc'
        item['channel'] = 'web'

        product = json.loads(content)['returnData']
        item['proCode'] = product['PRD_CODE'].strip()
        item['proName'] = product['PRD_NAME'].strip()
        item['proAttr'] = product['PRD_ATTR_NAME'].strip()
        item['proType'] = product['PRD_TYPE_NAME'].strip()
        item['sellObject'] = product['SELLDIR'].strip()
        item['status'] = product['STATUS_NAME'].strip()
        item['currency'] = product['CURR_TYPE_NAME'].strip()
        item['crFlag'] = product['CRFLAGNAME'].strip()
        item['startDate'] = product['IPO_START_DATE'].strip()
        item['endDate'] = product['IPO_END_DATE'].strip()
        item['openDate'] = product['START_DATE'].strip()
        item['nextOpenDate'] = product['PRD_NEXT_DATE'].strip()
        item['nextEndDate'] = product['EDDATE'].strip()
        item['realEndDate'] = product['REALEND_DATE'].strip()
        item['cycleTime'] = product['LIV_TIME_UNIT_NAME'].strip()
        item['incomeRate'] = product['INCOME_RATE'].strip()
        item['nextIncomeRate'] = product['Next_Income_Rate'].strip()
        item['interestType'] = product['INTEREST_TYPE_NAME'].strip()
        item['riskLevel'] = product['RISK_LEVEL_NAME'].strip()
        item['openTime'] = product['OPEN_TIME'].strip()
        item['closeTime'] = product['CLOSE_TIME'].strip()
        item['firstSubMinAmount'] = product['PFIRST_AMT'].strip()
        item['minRedBalance'] = product['PRED_UNIT'].strip()
        item['minSubUnit'] = product['PSUB_UNIT'].strip()
        item['maxSingleSub'] = product['PMAX_AMT'].strip()
        item['maxSingleRed'] = product['PMAX_RED'].strip()
        item['maxOneDaySub'] = product['PDAY_MAX'].strip()
        item['plainHold'] = product['PMIN_HOLD'].strip()
        item['proNetValue'] = product['NAV'].strip()
        yield item

    # 获取返回内容
    def __get_response_content(self, response) -> str:
        return response.body.decode(response.encoding, errors='ignore')

    # 爬取完成之后，推送数据
    def close(self, reason):
        bank_http_service = BankHttpService()
        bank_http_service.uploadResult({'bankCode': 'cmbc'})
        pass