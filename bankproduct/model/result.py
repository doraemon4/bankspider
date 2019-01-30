import json
import logging
from bankproduct.util.obj2json import jsonModel
from bankproduct.util.dateformat import formatDateStr
from bankproduct.util.dateformat import formatTimeStr
from bankproduct.util.dbhelper import MongodbBaseDao


@jsonModel()
class ProductBaseInfo(object):
    # 银行缩写
    bankCode = ''
    # 通道
    channel = ''
    # 产品代码
    proCode = ''
    # 产品名称
    proName = ''
    # 产品类别
    proAttr = ''
    # 产品类型
    proType = ''
    # 销售对象
    sellObject = ''
    # 产品状态
    status = ''
    # 产品币种
    currency = ''
    # 钞汇标志
    crFlag = ''
    # 投资周期
    cycleTime = ''
    # 产品收益率名称
    incomeRateName = ''
    # 本期预期收益率
    incomeRate = ''
    # 下期预期收益率
    nextIncomeRate = ''
    # 计息基准类型
    interestType = ''
    # 风险等级
    riskLevel = ''
    # 赎回规则
    redRule = ''
    # 买入规则
    buyRule = ''
    # 募集开始日
    startDate = ''
    # 募集截止日
    endDate = ''
    # 产品成立日，即起息日
    openDate = ''
    # 下一开放日
    nextOpenDate = ''
    # 下下开放日
    nextEndDate = ''
    # 产品到期日
    realEndDate = ''
    # 开市时间
    openTime = ''
    # 闭市时间
    closeTime = ''
    # 代理机构
    proManager = ''
    # 销售区域
    sellArea = ''
    # 销售渠道
    sellChannel = ''
    # 当前购买人数
    currentPurchases = ''
    # 起购金额
    firstAmount = ''
    # 首次认购下限
    firstSubMinAmount = ''
    # 最低申购余额
    minPurBalance = ''
    # 最低赎回余额
    minRedBalance = ''
    # 认购基数
    minSubUnit = ''
    # 申购基数
    minPurUnit = ''
    # 赎回基数
    minRedUnit = ''
    # 单笔认购上限
    maxSingleSub = ''
    # 单笔申购上限
    maxSinglePur = ''
    # 单笔赎回上限
    maxSingleRed = ''
    # 单笔认购下限
    minSingleSub = ''
    # 单笔申购下限
    minSinglePur = ''
    # 单笔赎回下限
    minSingleRed = ''
    # 当日购买上限
    maxOneDaySub = ''
    # 最低持仓份额
    plainHold = ''
    # 产品净值
    proNetValue = ''
    # 是否允许预约赎回
    allowedResRed = ''
    # 是否允许实时赎回
    allowedRelRed = ''
    # 费率
    feeRate = ''

    def __init__(self, data):
        properties = ['bankCode', 'channel', 'proCode', 'proName', 'proAttr', 'proType', 'sellObject', 'status',
                      'currency', 'crFlag', 'cycleTime', 'incomeRateName', 'incomeRate', 'nextIncomeRate',
                      'interestType', 'riskLevel', 'redRule', 'buyRule', 'startDate', 'endDate', 'openDate',
                      'nextOpenDate', 'nextEndDate', 'realEndDate', 'openTime', 'closeTime', 'proManager', 'sellArea',
                      'sellChannel', 'currentPurchases', 'firstAmount', 'firstSubMinAmount', 'minPurBalance',
                      'minRedBalance', 'minSubUnit', 'minPurUnit', 'minRedUnit', 'maxSingleSub', 'maxSinglePur',
                      'maxSingleRed', 'minSingleSub', 'minSinglePur', 'minSingleRed', 'maxOneDaySub', 'plainHold',
                      'proNetValue', 'allowedResRed', 'allowedRelRed', 'feeRate']
        # 初始化值
        for i, v in enumerate(properties):
            setattr(self, v, '')

        if data:
            items = data.items() if isinstance(data, dict) else data
            for key, value in items:
                if hasattr(self, key):
                    if isinstance(key, str) and key.endswith("Date"):
                        value = formatDateStr(value)
                        pass
                    if isinstance(key, str) and key.endswith("Time"):
                        value = formatTimeStr(value)
                    setattr(self, key, value)
                else:
                    pass
            # 对于proCode为空设置为proName
            '''if getattr(self, 'proCode') == '':
                setattr(self, 'proCode', getattr(self, 'proName'))
            '''

    '''
    def __repr__(self):
        return repr((self.bankCode, self.channel, self.proCode, self.proName, self.proAttr, self.proType,
                     self.sellObject, self.status, self.currency, self.crFlag, self.cycleTime, self.incomeRateName,
                     self.incomeRate, self.nextIncomeRate, self.interestType, self.riskLevel, self.redRule,
                     self.buyRule, self.startDate, self.endDate, self.openDate, self.nextOpenDate, self.nextEndDate,
                     self.realEndDate, self.openTime, self.closeTime, self.proManager, self.sellArea, self.sellChannel,
                     self.currentPurchases, self.firstAmount, self.firstSubMinAmount, self.minPurBalance,
                     self.minRedBalance, self.minSubUnit, self.minPurUnit, self.minRedUnit, self.maxSingleSub,
                     self.maxSinglePur, self.maxSingleRed, self.minSingleSub, self.minSinglePur, self.minSingleRed,
                     self.maxOneDaySub, self.plainHold, self.proNetValue, self.allowedResRed, self.allowedRelRed))

    '''

@jsonModel()
class ProductDetailInfo(object):
    # 银行缩写
    bankCode = ''
    # 通道
    channel = ''
    # 产品代码
    proCode = ''
    # 产品名称
    proName = ''
    # 产品概览下载地址
    overviewUrl = ''
    # 产品信息
    infoUrl = ''
    # 产品公告
    noticeUrl = ''
    # 产品净值
    netWorthUrl = ''
    # 产品报告
    reportUrl = ''
    # 产品评论
    commentUrl = ''
    # 产品说明书
    instructionUrl = ''
    # 风险揭示书
    riskDisclosureUrl = ''

    def __init__(self, data):
        properties = ['bankCode', 'channel', 'proCode', 'proName', 'overviewDownloadUrl', 'infoUrl',
                      'noticeUrl', 'netWorthUrl', 'reportUrl', 'commentUrl', 'instructionUrl',
                      'riskDisclosureUrl']
        # 初始化值
        for i, v in enumerate(properties):
            setattr(self, v, '')

        if data:
            items = data.items() if isinstance(data, dict) else data
            for key, value in items:
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    pass
            # 对于proCode为空设置为proName
            if getattr(self, 'proCode') == '':
                setattr(self, 'proCode', getattr(self, 'proName'))
    pass
    '''
    def __repr__(self):
        return repr((self.bankCode, self.channel, self.proCode, self.proName, self.overviewDownloadUrl, self.infoUrl,
                    self.noticeUrl, self.netWorthUrl, self.reportUrl, self.commentUrl, self.instructionUrl,
                    self.riskDisclosureUrl))
    pass
    '''


@jsonModel({"base_info": ProductBaseInfo, "detail_info": ProductDetailInfo})
class ProductMsg(object):

    def __init__(self, productBaseInfo, productDetailInfo):
        self.base_info = productBaseInfo
        self.detail_info = productDetailInfo


@jsonModel(listClassMap={'product_list': ProductMsg})
class BPDataV1(object):
    def __init__(self, productMsgList):
        self.product_list = productMsgList


# 数据推送的实体
@jsonModel(objectMap={'data': BPDataV1})
class TaskResult(object):

    def __init__(self, code='0', message='请求数据成功', data=None):
        self.code = code
        self.message = message
        self.data = data


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    productMsglist = list()
    dao = MongodbBaseDao("127.0.0.1", 27017, "bank")
    for bankproductItem in list(dao.find("bankproduct", {'bankCode': 'cib'})):
        productBaseInfo = ProductBaseInfo(bankproductItem)
        productDetailInfo = ProductDetailInfo(bankproductItem)
        productMsg = ProductMsg(productBaseInfo, productDetailInfo)
        productMsglist.append(productMsg)
    print(json.dumps(ProductMsg.objectArrayToJsonArray(productMsglist), ensure_ascii=False))
    data = BPDataV1(productMsglist)
    taskResult = TaskResult(data=data)
    print(json.dumps(data.toKeyValue(), ensure_ascii=False))
    print(json.dumps(taskResult.toKeyValue(), ensure_ascii=False))
    print(json.dumps(taskResult, default=lambda o: o.__dict__, ensure_ascii=False))
    pass
