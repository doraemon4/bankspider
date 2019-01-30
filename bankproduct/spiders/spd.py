# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  浦发银行爬取(post请求form表单)
#  网站增加了限制必须有cookie才可以爬取
# ----------------------------------------------------------------------
import json
import logging
import re
import urllib.parse

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from scrapy.conf import settings
from bankproduct.items import BankproductItem
from bankproduct.service import BankHttpService
from pyvirtualdisplay import Display


class SpdSpider(scrapy.Spider):
    logger = logging.getLogger(__name__)

    name = 'spd'
    allowed_domains = ['per.spdb.com.cn', 'ebank.spdb.com.cn']
    cookies_url = 'https://per.spdb.com.cn/bank_financing/financial_product/'
    start_url = 'https://per.spdb.com.cn/was5/web/search'
    detail_url = 'https://ebank.spdb.com.cn/nbper/PreBankFinanceBuy.do?selectedMenu=menu3_1_1&FinanceNo='
    detail2_url = 'https://ebank.spdb.com.cn/nbper/financeBuyInput.do?selectedMenu=menu3_1_1&FinanceNo='

    headers = {
        'Host': 'per.spdb.com.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }

    # 固定期限
    product_type_3_form_data = {
        'metadata': 'finance_state|finance_no|finance_allname|finance_anticipate_rate|finance_limittime|'
                    'finance_lmttime_info|finance_type|docpuburl|finance_ipo_enddate|finance_indi_ipominamnt|'
                    'finance_indi_applminamnt|finance_risklevel|product_attr|finance_ipoapp_flag|finance_next_openday',
        'channelid': '266906',
        'page': '1',
        'searchword': "(product_type=3)*finance_limittime = %*%*(finance_state='可购买')"
    }

    # 现金管理类
    product_type_4_form_data = {
        'metadata': 'finance_state|finance_no|finance_allname|finance_anticipate_rate|finance_limittime|'
                    'finance_lmttime_info|finance_type|docpuburl|finance_ipo_enddate|finance_indi_ipominamnt|'
                    'finance_indi_applminamnt|finance_risklevel|product_attr|finance_ipoapp_flag|finance_next_openday',
        'channelid': '266906',
        'page': '1',
        'searchword': "(product_type=4)*finance_limittime = %*%*(finance_state='可购买')"
    }

    # 净值类
    product_type_2_form_data = {
        'metadata': 'finance_state|finance_no|finance_allname|finance_anticipate_rate|finance_limittime|'
                    'finance_lmttime_info|finance_type|docpuburl|finance_ipo_enddate|finance_indi_ipominamnt|'
                    'finance_indi_applminamnt|finance_risklevel|product_attr|finance_ipoapp_flag|finance_next_openday',
        'channelid': '266906',
        'page': '1',
        'searchword': "(product_type=2)*finance_limittime = %*%*(finance_state='可购买')"
    }

    # 汇理财
    product_type_form_data = {
        'metadata': 'finance_allname|finance_anticipate_rate|finance_limittime|finance_indi_ipominamnt|finance_type|'
                    'finance_no|finance_state|docpuburl|finance_risklevel|product_attr',
        'channelid': '263468',
        'page': '1',
        'searchword': "finance_limittime = %*%*(finance_state='可购买')"
    }

    # 私行专属
    product_type_0_form_data = {
        'metadata': 'finance_state|finance_no|finance_allname|finance_anticipate_rate|finance_limittime|'
                    'finance_lmttime_info|finance_type|docpuburl|finance_ipo_enddate|finance_indi_ipominamnt|'
                    'finance_indi_applminamnt|finance_risklevel|product_attr|finance_ipoapp_flag|finance_next_openday',
        'channelid': '266906',
        'page': '1',
        'searchword': "(product_type=0)*finance_limittime = %*%*(finance_state='可购买')"
    }

    form_data_list = [product_type_3_form_data, product_type_4_form_data, product_type_2_form_data,
                      product_type_form_data, product_type_0_form_data]

    def __init__(self, *args, **kwargs):
        super(SpdSpider, self).__init__(*args, **kwargs)
        display = Display(visible=0, size=(800, 800))
        display.start()
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_experimental_option('useAutomationExtension', False)
        driver_path = settings.get("WEBDRIVER_CHROME_PATH")
        self.browser = webdriver.Chrome(executable_path=driver_path,
                                        chrome_options=chrome_options)
        self.browser.set_page_load_timeout(30)

    # 重写start_requests方法
    def start_requests(self):
        cookies = self.convert_cookies(self.get_cookies())
        if cookies:
            for form_data in self.form_data_list:
                yield scrapy.FormRequest(self.start_url, method="POST", cookies=cookies, formdata=form_data,
                                         dont_filter=True)
            pass

    def parse(self, response):
        # 解析具体的产品
        content = self.__get_response_content(response)
        product_list = json.loads(content)['rows']
        # 返回的是对象集合
        for product_item in product_list:
            item = BankproductItem()
            item['bankCode'] = 'spd'
            item['channel'] = 'web'
            item['proCode'] = product_item['finance_no']
            item['proName'] = product_item['finance_allname']

            # 产品类型
            params = urllib.parse.unquote(str(response.request.body, encoding='utf-8'))
            proAttr = self.__get_re_value(params, 'product_type=(\d+)', 1)
            item['proAttr'] = proAttr.replace('0', '私行专属').replace('2', "净值类").replace('3', "固定期限") \
                .replace('4', "现金管理类") if proAttr else "汇理财"

            item['incomeRate'] = product_item['finance_anticipate_rate']
            item['riskLevel'] = product_item['finance_risklevel'].replace('A', "低风险等级").replace('B', "较低风险等级") \
                .replace('C', "中风险等级").replace('D', "较高风险等级").replace('E', "高风险等级")
            item['firstAmount'] = product_item['finance_indi_ipominamnt']
            item['nextOpenDate'] = product_item['finance_next_openday'] if 'finance_next_openday' in product_item.keys() else ""
            item['instructionUrl'] = product_item['product_attr'] if 'product_attr' in product_item.keys() else ""
            item['status'] = product_item['finance_state']

            channelid = re.search('channelid=(\d+)', str(response.request.body, encoding='utf-8')).group(1)
            if channelid == '266906':
                product_item_detail_url = '{}{}'.format(self.detail_url, item['proCode'])
            elif channelid == '263468':
                product_item_detail_url = '{}{}'.format(self.detail2_url, item['proCode'])
            yield scrapy.Request(product_item_detail_url, meta={'item': item}, callback=self.parse_product_detail,
                                 dont_filter=True)
        # 是否存在下一页数据
        exist_data = re.search('"rows":\[([\S\s]+)\]', response.text)
        if exist_data:
            current_page = int(re.search('page=(\d+)', str(response.request.body, encoding='utf-8')).group(1))
            current_page = current_page + 1
            current_form_data = self.fromData2Dict(str(response.request.body, encoding='utf-8'))
            current_form_data['page'] = str(current_page)
            yield scrapy.FormRequest(self.start_url, method="POST", formdata=current_form_data, dont_filter=True)
        pass

    def parse_product_detail(self, response):
        # 接收上一个页面抓取的数据
        item = response.meta['item']
        cycleTime = self.__get_xpath_value(response, "//div[contains(text(),'产品周期')]/text()").strip()
        item['cycleTime'] = self.__get_re_value(cycleTime, "(\d+)", 1)
        proType = self.__get_xpath_value(response, "//div[contains(text(),'产品类型')]/text()").strip()
        item['proType'] = self.__get_re_value(proType, "产品类型:([\s]+)([\S]+)", 2)
        item['minPurUnit'] = self.__get_xpath_value(response, "//input[@name='FinanceIndiSaddIpoAmnt']/@value").strip()
        item['sellChannel'] = self.__get_xpath_value(response, "//input[@name='FinanceAvailChannel']/@value").strip()
        currentPurchases = self.__get_xpath_value(response, "//p[@class='peopleTotal']").strip()
        item['currentPurchases'] = self.__get_re_value(currentPurchases, "已抢人数:(.*)人", 1)
        item['openDate'] = self.__get_xpath_value(response, "//input[@name='FinanceIncomeStartDate']/@value").strip()
        item['realEndDate'] = self.__get_xpath_value(response, "//input[@name='FinanceProductEndDate']/@value").strip()
        item['startDate'] = self.__get_xpath_value(response, "//input[@name='FinanceIpoStartDate']/@value").strip()
        item['endDate'] = self.__get_xpath_value(response, "//input[@name='FinanceIpoEndDate']/@value").strip()
        currency = self.__get_xpath_value(response, "//input[@name='FinanceCurrency']/@value").strip()
        item['currency'] = currency.replace('01', '人民币')
        yield item
        pass

    # 通用的xpath解析值)
    def __get_xpath_value(self, response, xpath) -> str:
        xpath_value = response.xpath(xpath)
        return xpath_value.extract()[0] if len(xpath_value) else ""

    # 获取返回内容
    def __get_response_content(self, response) -> str:
        return response.body.decode(response.encoding, errors='ignore')

    # 通用的正则解析值
    def __get_re_value(self, content: str, pattern, index: int) -> str:
        value = ''
        try:
            value = re.search(pattern, content, re.M | re.I).group(index)
        except Exception as e:
            pass
        return value

    # 表单数据转化为dict
    def fromData2Dict(self, formData):
        # urlencode会把空格转化为+，此处做个转换
        params = urllib.parse.unquote(formData).replace('+', ' ').split("&")
        nums = len(params)
        form_data = {}
        for i in range(0, nums):
            param = params[i].split("=", 1)
            key = param[0]
            value = param[1]
            form_data[key] = value
        return form_data

    # 通过webdriver获取cookies
    def get_cookies(self):
        self.browser.get(self.cookies_url)
        cookies = []
        try:
            WebDriverWait(self.browser, 100).until(
                expected_conditions.visibility_of_element_located((By.XPATH, "//*[@id='headSearchInput']")))
                # expected_conditions.element_to_be_clickable((By.XPATH, "//a[@class='searchbutton']")))
            cookies = self.browser.get_cookies()
        except Exception as e:
            self.logger.info("获取cookies出错")

        finally:
            # 关闭浏览器
            self.browser.quit()
        return cookies

    def convert_cookies(self, cookies):
        newcookies = {}
        for cookie in cookies:
            newcookies[cookie['name']] = cookie['value']
        return newcookies

    # 爬取完成之后，推送数据
    def close(self, reason):
        bank_http_service = BankHttpService()
        bank_http_service.uploadResult({'bankCode': 'spd'})
        pass