import logging
import time
import datetime
import re

# ----------------------------------------------------------------------
#  格式化日期字符串
# ----------------------------------------------------------------------

FORMAT = "%(asctime)s %(thread)d %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="[%Y-%m-%d %H:%M:%S]")


def formatDateStr(date_string, target_pattern='%Y-%m-%d'):
    # 日期格式转换(yyyy-MM-dd HH:mm:ss,yyyy/MM/dd,yyyyMMdd
    patterns = {'%Y-%m-%d %H:%M:%S': '\d{4}-[01]\d-[0123]\d\s[012]\d:[0-5]\d:[0-5]\d',
                '%Y-%m-%d %H:%M': '\d{4}-[01]\d-[0123]\d\s[012]\d:[0-5]\d',
                '%Y-%m-%d': '\d{4}-[01]\d-[0123]\d',
                '%Y/%m/%d': '\d{4}/[01]\d/[0123]\d',
                '%Y%m%d': '\d{4}[01]\d[0123]\d',
                '%Y年%m月%d日': '\d{4}年[01]\d月[0123]\d日',
                '%Y.%m.%d': '\d{4}.[01]\d.[0123]\d'}
    for key, value in patterns.items():
        if re.match(value, date_string, re.M | re.I):
            # 字符转换为tuple
            try:
                time_tuple = time.strptime(date_string, key)
            except Exception as e:
                logging.getLogger().info("日期转换异常:"+date_string+", key:"+key)
                pass
            # tuple转化为字符串
            return time.strftime(target_pattern, time_tuple)
        else:
            pass
    return date_string


def formatTimeStr(time_str, target_pattern='%H:%M:%S'):
    patterns = {'%H:%M:%S': '[012]\d:[0-5]\d:[0-5]\d', '%H%M%S': '[012]\d[0-5]\d[0-5]\d'}
    for key, value in patterns.items():
        if re.match(value, time_str, re.M | re.I):
            # 字符转换为tuple
            time_tuple = time.strptime(time_str, key)
            # tuple转化为字符串
            return time.strftime(target_pattern, time_tuple)
        else:
            pass
    return time_str


def formatDateStr2(date_string, target_pattern='%Y-%m-%d'):
    # 日期格式转换(yyyy-MM-dd HH:mm:ss,yyyy/MM/dd,yyyyMMdd
    patterns = {'%Y-%m-%d %H:%M:%S': '\d{4}-[01]\d-[0123]\d\s{1,2}[012]\d:[0-5]\d:[0-5]\d',
                '%Y/%m/%d': '\d{4}/[01]\d/[0123]\d',
                '%Y%m%d': '\d{4}[01]\d[0123]\d',
                '%Y.%m.%d': '\d{4}.[01]\d.[0123]\d'}
    for key, value in patterns.items():
        if re.match(value, date_string, re.M | re.I):
            # 字符转换为time
            date = datetime.datetime.strptime(date_string, key)
            return date.strftime(target_pattern)
        else:
            pass
    return ''

def parseTimeStamp2Date(timestamp):
    # 时间戳转化为time
    return time.localtime(timestamp)

def parseDate2TimeStamp(time_tuple):
    # 转化为时间戳
    return time.mktime(time_tuple)


if __name__ == '__main__':
    str = '092459'
    print(formatTimeStr(str))
    str = "20181226"
    print(formatDateStr(str))
