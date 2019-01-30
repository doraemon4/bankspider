# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  招商银行app爬取
# ----------------------------------------------------------------------
import re

import scrapy

from bankproduct.items import BankproductItem
from bankproduct.service import BankHttpService


class CmbAppSpider(scrapy.Spider):
    name = 'cmb_app'
    allowed_domains = ['mobile.cmbchina.com']
    start_url = 'https://mobile.cmbchina.com/IEntrustFinance/FinanceProduct/FP_AjaxQueryList.aspx'
    detail_url = 'https://mobile.cmbchina.com/IEntrustFinance/FinanceProduct/FP_FinanceDetail.aspx?' \
                 'DeviceType=E&Version=7.1.2&SystemVersion=6.0&behavior_entryid=lca503018'
    rule_url = 'https://mobile.cmbchina.com/IEntrustFinance/FinanceProduct/FP_TransRules.aspx'
    risk_url = 'https://mobile.cmbchina.com/IEntrustFinance/FinanceProduct/FP_PrdInfo.aspx'
    instruction_url = 'https://mobile.cmbchina.com/IEntrustFinance/FinanceProduct/FP_PrdInstruction.aspx'
    # 列表表单
    form_data = {
        '$RequestMode$': '1',
        'ListNo': '1',
        'PrdTerm': '0',
        'PrdPurch': '0',
        'BobFlg': 'A',
        'CcyNbr': '',
        'CltCtl': '0',
        'BbkTag': '',
        'OdrTyp': 'D',
        'OdrFld': 'B',
        'AgtCtm': 'N',
        'PrdTyp': 'All',
        'TimTmp': '1545207914477',
        'ClientNo': 'b73a7bb588df42a3be8ecfc101c890e8',
        'Command': 'CMD_DOQUERYLIST'
    }
    # 详情表单
    form_data2 = {
        'Command': '',
        'Code': '107107',
        'ClientNo': 'b73a7bb588df42a3be8ecfc101c890e8',
        'BbkTag': '',
        'behavior_prodcode': '107107',
        'fromPrdList': 'Y',
        'showtopbar': 'true'
    }
    # 查看规则表单
    form_data3 = {
        'Code': '107107',
        'CMBReturnJson': '.4.8ClientNo.8%3A.870513d7df24542b9ababf7231f228628.8.6.8Code.8%3A.8107107.8.6.8CMBReturnDeep.8%3A0.6.8CMBReturnFuncID.8%3A.86016005.8.6.8Command.8%3A.8.8.5',
        'Command': '',
        'ClientNo': '70513d7df24542b9ababf7231f228628',
        'behavior_entryid': 'lcb005001',
        'behavior_prodcode': '107107'
    }
    # 风险说明表单
    form_data4 = {
        'type': 'risk',
        'Code': '8197',
        'RiskLevel': 'R2',
        'CMBReturnJson': '',
        'Command': '',
        'ClientNo': '8e6ba9a67154433e96a73c10ad6b6a68'
    }
    # 产品说明书表单
    form_data5 = {
        'Command': '',
        'Code': '8188',
        'behavior_prodcode': '8188',
        'showtopbar': 'true'
    }

    # 重写start_requests方法
    def start_requests(self):
        yield scrapy.FormRequest(self.start_url, method="POST", formdata=self.form_data)

    def parse(self, response):
        # 解析各个产品
        for product_no in re.findall('"RipCod":"(\d+)"', response.text):
            self.form_data2['Code'] = str(product_no)
            self.form_data2['behavior_prodcode'] = str(product_no)
            yield scrapy.FormRequest(self.detail_url, method="POST", formdata=self.form_data2,
                                     callback=self.parse_product_detail, dont_filter=True)
        # 是否存在下一页数据
        exist_data = re.search('"RipCod":"(\d+)"', response.text)
        if exist_data:
            current_page = int(re.search('ListNo=(\d+)', str(response.request.body, encoding='utf-8')).group(1))
            next_page = current_page + 1
            self.form_data['ListNo'] = str(next_page)
            yield scrapy.FormRequest(self.start_url, method="POST", formdata=self.form_data, dont_filter=True)
        pass

    def parse_product_detail(self, response):
        item = BankproductItem()
        item['bankCode'] = 'cmb'
        item['channel'] = 'app'
        item['proCode'] = re.search('Code=(\d+)', str(response.request.body, encoding='utf-8')).group(1)
        item['proName'] = self.__get_re_value(response.text, 'prdname: "(.*?)"', 1)
        item['proType'] = self.__get_re_value(response.text, 'prdtype: "(.*?)"', 1)
        item['incomeRateName'] = self.__get_xpath_value(response, "//span[@id='ctl00_cphBody_RatBre']/text()").strip()
        item['incomeRate'] = self.__get_xpath_value(response, "//span[@id='ctl00_cphBody_PrdRat']/text()").strip()
        item['cycleTime'] = self.__get_xpath_value(response, "//span[@id='ctl00_cphBody_TerDay']/text()").strip()
        item['riskLevel'] = self.__get_xpath_value(response, "//span[@id='ctl00_cphBody_RiskLvl2']/text()").strip()
        item['currentPurchases'] = self.__get_xpath_value(response, "//span[@id='ctl00_cphBody_SalAmt']/text()").strip()
        item['firstSubMinAmount'] = self.__get_xpath_value(response, "//span[@id='ctl00_cphBody_SbsUqt']/text()").strip()

        self.form_data3['Code'] = item['proCode']
        self.form_data3['behavior_prodcode'] = item['proCode']
        yield scrapy.FormRequest(self.rule_url, method="POST", meta={'item': item}, formdata=self.form_data3,
                                 callback=self.parse_product_rules, dont_filter=True)
        pass

    def parse_product_rules(self, response):
        item = response.meta['item']
        buyRules = response.xpath("//ul[@id='ctl00_cphBody_BuyBlock']/li[contains(@class,'fp-list-item')]")
        item['buyRule'] = ''
        for buyRule in buyRules:
            item['buyRule'] = item['buyRule'] + '{}:{};'.format(
                self.__get_xpath_value(buyRule, "div[@class='hog-item-ib']/label/text()").strip(),
                self.__get_xpath_value(buyRule, "div[@class='hog-item-ib']/span/span/text()").strip())

        redRules = response.xpath("//ul[@id='ctl00_cphBody_RedeemBlock']/li[contains(@class,'fp-list-item')]")

        item['redRule'] = ''
        for redRule in redRules:
            item['redRule'] = item['redRule'] + '{}:{};'.format(
                self.__get_xpath_value(redRule, "div[@class='hog-item-ib']/label/text()").strip(),
                self.__get_xpath_value(redRule, "div[@class='hog-item-ib']/span/span/text()").strip())

        self.form_data4['Code'] = item['proCode']
        yield scrapy.FormRequest(self.risk_url, method="POST", meta={'item': item}, formdata=self.form_data4,
                                 callback=self.parse_product_risk, dont_filter=True)
        pass

    def parse_product_risk(self, response):
        item = response.meta['item']
        riskDisclosureUrl = self.__get_xpath_value(response, "//div[@id='ctl00_cphBody_risk_PDF']/@onclick").strip()
        item['riskDisclosureUrl'] = self.__get_re_value(riskDisclosureUrl, "window.location = '(.*?)'", 1)

        self.form_data5['Code'] = item['proCode']
        self.form_data5['behavior_prodcode'] = item['proCode']
        yield scrapy.FormRequest(self.instruction_url, method="POST", meta={'item': item}, formdata=self.form_data5,
                                 callback=self.parse_product_instruction, dont_filter=True)
        pass

    def parse_product_instruction(self, response):
        item = response.meta['item']
        instructionUrl = self.__get_xpath_value(response, "//div[@id='ctl00_cphBody_info_PDF']/@onclick").strip()
        item['instructionUrl'] = self.__get_re_value(instructionUrl, "window.location = '(.*?)'", 1)
        yield item

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
        bank_http_service.uploadResult({'bankCode': 'cmb'})
        pass

