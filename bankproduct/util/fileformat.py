# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 文本转化为pdf工具(pip install pdfkit)
# ----------------------------------------------------------------------
import os

import pdfkit


class FileUtil(object):

    def from_url(self, url, file_path):
        self.createFolders(file_path)
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        pdfkit.from_url(url, file_path, options=options)

    def from_str(self, text, file_path):
        self.createFolders(file_path)
        pdfkit.from_string(text, file_path)
        pdfkit.from_file()

    # 判断路径是否存在，不存在新建
    def createFolders(self, file_path):
        strs = file_path.split('/')
        num = len(strs)
        file_name = strs[num - 1]
        index = file_path.find(file_name, 0)
        folders = file_path[0:index]
        isExist = os.path.exists(folders)
        if not isExist:
            os.makedirs(folders)


if __name__ == '__main__':
    fileUtil = FileUtil()
    fileUtil.from_url("http://www.cmbchina.com/", "/tmp/file/2018/test.pdf")
