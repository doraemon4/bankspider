# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  民生银行app爬取
# ----------------------------------------------------------------------
import json
import re

import scrapy

from bankproduct.items import BankproductItem
from bankproduct.service import BankHttpService


class CmbcAppSpider(scrapy.Spider):
    name = 'cmbc_app'
    allowed_domains = ['m1.cmbc.com.cn']
    start_url = 'https://m1.cmbc.com.cn/CMBC_MBServer/svt/transservlet.Ihtml'
    # 产品列表参数
    request_data = {"flag": "2", "startId": "1", "pageSize": "10", "prdName": "", "income": "0", "deadLine": "",
                    "transAmt": "", "prdType": "", "transCurrency": "", "livTimeMin": "", "livTimeMax": "",
                    "conditionQueryFlag": "", "sortType": "1", "orderType": "Down", "acctType": "0", "prdCategory": "",
                    "TransId": "cmbc.queryBankFinanceList"}
    # 详情页面请求参数
    request_data2 = {"prdCode": "FSLA18277A", "getVipFlag": "1", "GroupFlag": "1", "TransId": "cmbc.queryPrdInfoNew"}

    def start_requests(self):
        yield scrapy.Request(self.start_url, method="POST",
                             body=json.dumps(self.request_data),
                             headers={'Content-Type': 'application/json'})

    def parse(self, response):
        productItems = json.loads(response.text)['respData']['list']
        for productItem in productItems:
            item = BankproductItem()
            item['bankCode'] = 'cmbc'
            item['channel'] = 'app'
            item['proCode'] = productItem['PRD_CODE'].strip()
            item['proName'] = productItem['PRD_NAME'].strip()
            item['proAttr'] = productItem['PRD_ATTR'].strip()
            # PRD_TYPE(0:每日型,1:定期开放型,2:封闭型,3:收益型,4:净值类周期型,5:活期型),
            item['proType'] = productItem['PRD_TYPE_NAME'].strip()
            item['incomeRateName'] = productItem['INCOME_TYPE']
            item['incomeRate'] = productItem['INCOME_RATE']
            item['nextIncomeRate'] = productItem['NEXT_INCOME_RATE']
            item['proNetValue'] = productItem['NAV']
            item['openDate'] = productItem['START_DATE'].strip()
            item['realEndDate'] = productItem['REALEND_DATE'].strip()
            item['cycleTime'] = productItem['LIV_TIME_UNIT_NAME'].strip()
            item['firstAmount'] = productItem['FIRST_AMT']
            # currency(156:人民币,840:美元)
            item['currency'] = productItem['CURR_TYPE_NAME'].strip()

            self.request_data2['prdCode'] = item['proCode']
            yield scrapy.Request(self.start_url, method="POST",
                                 body=json.dumps(self.request_data2), meta={'item': item},
                                 headers={'Content-Type': 'application/json'}, callback=self.parse_product_detail,
                                 dont_filter=True)

        # 是否存在下一页数据
        exist_data = re.search('"PRD_CODE":"(.*?)"', response.text)
        if exist_data:
            current_startId = int(
                self.__get_re_value(str(response.request.body, encoding='utf-8'), '"startId": "(.*?)"', 1))
            pagesize = int(
                self.__get_re_value(str(response.request.body, encoding='utf-8'), '"pageSize": "(\d+)"', 1))
            next_startId = current_startId + pagesize
            self.request_data['startId'] = str(next_startId)
            yield scrapy.Request(self.start_url, method="POST",
                                 body=json.dumps(self.request_data),
                                 headers={'Content-Type': 'application/json'}, dont_filter=True)

        pass

    def parse_product_detail(self, response):
        productItem = json.loads(response.text)['respData']['list']
        item = response.meta['item']
        item['status'] = productItem['STATUS']
        item['plainHold'] = productItem['PMIN_HOLD']
        item['interestType'] = productItem['INTEREST_TYPE']
        item['sellChannel'] = productItem['CHANNELS_NAME'].strip()
        item['sellArea'] = productItem['PRD_TRUSTEE_NAME'].strip()
        item['riskLevel'] = productItem['RISK_LEVEL_NAME'].strip()
        item['startDate'] = productItem['IPO_START_DATE'].strip()
        item['endDate'] = productItem['IPO_END_DATE'].strip()
        item['minSubUnit'] = productItem['PSUB_UNIT']
        item['minRedUnit'] = productItem['PRED_UNIT']
        item['minRedBalance'] = productItem['PMIN_RED']
        item['minPurBalance'] = productItem['PAPP_AMT']
        item['nextOpenDate'] = productItem['PRD_NEXT_DATE'].strip()
        item['nextEndDate'] = productItem['NEXT_END_DATE'].strip()
        item['openTime'] = productItem['OPEN_TIME'].strip()
        item['closeTime'] = productItem['CLOSE_TIME'].strip()
        yield item

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
        bank_http_service.uploadResult({'bankCode': 'cmbc'})
        pass
