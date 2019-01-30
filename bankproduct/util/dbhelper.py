# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# mongodb的操作工具
# ----------------------------------------------------------------------
from pymongo import MongoClient


class MongodbBaseDao(object):

    def __init__(self, uri, database):
        self.conn = MongoClient(uri)
        self.db = self.conn[database]

    def get_state(self):
        return self.conn is not None and self.db is not None

    def delete(self, col, condition):
        if self.get_state():
            return self.db[col].delete_many(filter=condition).deleted_count
        return 0

    def find(self, col, condition, column=None):
        if self.get_state():
            if column is None:
                return self.db[col].find(condition, {'_id': 0})
            else:
                return self.db[col].find(condition, column)
        else:
            return None

    def insert_one(self, collection, data):
        if self.get_state():
            ret = self.db[collection].insert_one(data)
            return ret.inserted_id
        else:
            return ""

    def insert_many(self, collection, data):
        if self.get_state():
            ret = self.db[collection].insert_many(data)
            return ret.inserted_id
        else:
            return ""

    def update(self, collection, data):
        # data format:
        # {key:[old_data,new_data]}
        data_filter = {}
        data_revised = {}
        for key in data.keys():
            data_filter[key] = data[key][0]
            data_revised[key] = data[key][1]
        if self.get_state():
            return self.db[collection].update_many(data_filter, {"$set": data_revised}).modified_count
        return 0
