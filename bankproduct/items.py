# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BankproductItem(scrapy.Item):
    bankCode = scrapy.Field()  # 银行缩写
    channel = scrapy.Field()  # 通道
    proCode = scrapy.Field()  # 产品代码
    proName = scrapy.Field()  # 产品名称
    proAttr = scrapy.Field()  # 产品类别
    proType = scrapy.Field()  # 产品类型
    sellObject = scrapy.Field()  # 销售对象
    status = scrapy.Field()  # 产品状态
    currency = scrapy.Field()  # 产品币种
    crFlag = scrapy.Field()  # 钞汇标志
    cycleTime = scrapy.Field()  # 投资周期
    incomeRateName = scrapy.Field()  # 产品收益率名称
    incomeRate = scrapy.Field()  # 本期预期收益率
    nextIncomeRate = scrapy.Field()  # 下期预期收益率
    interestType = scrapy.Field()  # 计息基准类型
    riskLevel = scrapy.Field()  # 风险等级
    redRule = scrapy.Field()  # 赎回规则
    buyRule = scrapy.Field()  # 买入规则
    startDate = scrapy.Field()  # 募集开始日
    endDate = scrapy.Field()  # 募集截止日
    openDate = scrapy.Field()  # 产品成立日，即起息日
    nextOpenDate = scrapy.Field()  # 下一开放日
    nextEndDate = scrapy.Field()  # 下下开放日
    realEndDate = scrapy.Field()  # 产品到期日
    openTime = scrapy.Field()  # 开市时间
    closeTime = scrapy.Field()  # 闭市时间
    proManager = scrapy.Field()  # 代理机构
    sellArea = scrapy.Field()  # 销售区域
    sellChannel = scrapy.Field()  # 销售渠道
    currentPurchases = scrapy.Field()  # 当前购买人数
    firstAmount = scrapy.Field()  # 起购金额
    firstSubMinAmount = scrapy.Field()  # 首次认购下限
    minPurBalance = scrapy.Field()  # 最低申购余额
    minRedBalance = scrapy.Field()  # 最低赎回余额
    minSubUnit = scrapy.Field()  # 认购基数
    minPurUnit = scrapy.Field()  # 申购基数
    minRedUnit = scrapy.Field()  # 赎回基数
    maxSingleSub = scrapy.Field()  # 单笔认购上限
    maxSinglePur = scrapy.Field()  # 单笔申购上限
    maxSingleRed = scrapy.Field()  # 单笔赎回上限
    minSingleSub = scrapy.Field()  # 单笔认购下限
    minSinglePur = scrapy.Field()  # 单笔申购下限
    minSingleRed = scrapy.Field()  # 单笔赎回下限
    maxOneDaySub = scrapy.Field()  # 当日购买上限
    plainHold = scrapy.Field()  # 最低持仓份额
    proNetValue = scrapy.Field()  # 产品净值
    allowedResRed = scrapy.Field()  # 是否允许预约赎回
    allowedRelRed = scrapy.Field()  # 是否允许实时赎回
    feeRate = scrapy.Field()  # 费率
    overviewUrl = scrapy.Field()   # 产品概览
    overviewDownloadUrl = scrapy.Field()   # 产品概览下载地址
    infoUrl = scrapy.Field()   # 产品信息
    infoDownloadUrl = scrapy.Field()   # 产品信息下载地址
    noticeUrl = scrapy.Field()   # 产品公告
    noticeDownloadUrl = scrapy.Field()   # 产品公告下载地址
    netWorthUrl = scrapy.Field()   # 产品净值
    netWorthDownloadUrl = scrapy.Field()   # 产品净值下载地址
    reportUrl = scrapy.Field()   # 产品报告
    reportDownloadUrl = scrapy.Field()   # 产品报告下载地址
    commentUrl = scrapy.Field()   # 产品评论
    commentDownloadUrl = scrapy.Field()   # 产品评论下载地址
    instructionUrl = scrapy.Field()   # 产品说明书
    instructionDownloadUrl = scrapy.Field()   # 产品说明书下载地址
    riskDisclosureUrl = scrapy.Field()   # 风险揭示书
    riskDisclosureDownloadUrl = scrapy.Field()   # 风险揭示书下载地址
    createTime = scrapy.Field()   # 爬取时间
