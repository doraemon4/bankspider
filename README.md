### 银行理财公网爬虫（scrapy)


#### 1. 安装python环境

#### 2. 安装相关python包

```bash
    pip install scrapy
    pip install pymongo
    pip install requests
```

#### 3. 编辑items.py

定义的模型和字段

#### 4. 通过scrapy命令添加spider

如：
```bash
    scrapy genspider cmb http://www.cmbchina.com
```

#### 5. 编辑生成spider文件，爬取解析

可通过scrapy list 命令查看工程有哪些spider
```bash
~/PycharmProjects/bankproduct scrapy list
cmb
```

#### 6. 编辑pipeline.py

添加items的管道处理类，并配置到settings中去

```python
ITEM_PIPELINES = {
   'bankproduct.pipelines.MongoPipeline': 300,
}
```
数字代表优先级，越小优先级越高，一般1~1000之间


#### 7. 编辑middlewares.py

添加中间件配置，scrapy中有很多默认的中间件可以使用

```python
{
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': 100,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 300,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350
    # ...
}
```

#### 8. 编辑settings.py

* 设置全局变量（数据库、日志级别等）
* 自定义scrapy的一些components（core, extensions, pipelines and spiders ）
    如：
    * 设置爬取休眠，DOWNLOAD_DELAY，默认为0
* 使用self.settings.attributes.keys()拿到所有settings
* 其他设置请参看[官方文档](https://doc.scrapy.org/en/latest/topics/settings.html)

#### 7. 执行爬取命令

如：
```bash
    scrapy crawl cmb
```
或执行begin.py

#### 8. 脚本说明
脚本  |   脚本描述 | 爬取网址 |
------------- | ------------- | ------------- |
ceb.py |光大银行 |http://www.cebbank.com/site/gryw/yglc/lccp49/index.html?channelIds=yxl94&channelName=2 |
cgb.py |广发银行 |http://www.cgbchina.com.cn/Channel/16684283?nav=2?nav=2 |
cib.py |兴业银行 |http://wealth.cib.com.cn/retail/onsale/index.html |
citic.py |中信银行 |https://etrade.citicbank.com/portalweb/html/finList.html |
cmb.py |招商银行 |http://www.cmbchina.com/cfweb/personal/default.aspx |
cmbapp.py |招商银行app通道 | |
cmbc.py |民生银行 |http://www.cmbc.com.cn/channelApp/finance/financial.jsp |
cmbcapp.py |民生银行app通道 | |
hfb.py |恒丰银行 |http://www.hfbank.com.cn/gryw/cfgl/lc/rmlctj/index.shtml |
hxb.py |华夏银行 |http://www.hxb.com.cn/grjr/lylc/zzfsdlccpxx/index.shtml |
spd.py |浦发银行 |https://per.spdb.com.cn/bank_financing/financial_product/ |
czb.py |浙商银行 |https://perbank.czbank.com/PERBANK/pbIndex.jsp?menuFlag=7 |

## 参考文档

[Scrapy文档地址](https://doc.scrapy.org/en/latest)