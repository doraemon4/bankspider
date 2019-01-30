# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import os
import re
import time

import pymongo
import logging

from bankproduct.service import BankHttpService


class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):

        # 优先proCode去重，若为空则找proName
        if 'proCode' in item.keys():
            query = {"bankCode": item['bankCode'], "proCode": item['proCode']}
        elif 'proName' in item.keys():
            query = {"bankCode": item['bankCode'], "proName": item['proName']}
        else:
            # 都为空则添加日志或告警不存储
            logging.error('{} has error data: {}'.format(item['bankCode'], item))
            return item
        # 增加爬取时间
        date = datetime.datetime.now()
        item['createTime'] = date.strftime("%Y-%m-%d %H:%M:%S")
        self.db[self.collection_name].delete_one(query)
        self.db[self.collection_name].insert_one(dict(item))
        return item


class FilePipeline(object):
    bank_http_service = BankHttpService()

    def process_item(self, item, spider):
        # 本地存放路径
        base_path = spider.settings.get("SAVE_PATH") + '/' + time.strftime('%Y%m%d', time.localtime(time.time()))

        if 'proCode' in item.keys():
            self.base_path = base_path + "/" + item['bankCode'] + "/" + item['channel'] + "/" + item['proCode'] + "/"
        # 判断是否有产品说明书
        '''
        if 'instructionUrl' in item.keys() and item['instructionUrl']:
            self.download(item['instructionUrl'], item['bankCode'])
        # 判断是否含有风险说明书
        if 'riskDisclosureUrl' in item.keys() and item['riskDisclosureUrl']:
            self.download(item['riskDisclosureUrl'], item['bankCode'])
        '''
        return item

    def download(self, downloadUrl, bucket_name):
        isExists = os.path.exists(self.base_path)
        # 判断是否存在目录，不存在创建
        if not isExists:
            os.makedirs(self.base_path)
        pass
        # 兼容多种下载路径
        strs = re.split('/|=', downloadUrl)
        num = len(strs)
        file_name = strs[num-1]
        # 要存放的路径
        file_path = self.base_path + file_name
        self.bank_http_service.downloadFile(downloadUrl, file_path)
        # 文件上传
        #self.bank_http_service.uploadFile(file_path, bucket_name)
