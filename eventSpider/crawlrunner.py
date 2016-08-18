# -*- coding: utf-8 -*-
'''Run Scrapy Spider in Cmdline todo: run scrapy in a script'''



from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
#from spiders.zj_HW_roadwork_onmap import zjfHWApp
from spiders.bj_roadwork_news import bjHWNews
from spiders.bj_road_work_onmap import bjRoadWorkOnMap
from spiders.js_HW_roadwork_onmap import jsHWApp
from spiders.fj_HW_roadwork_onmap import fjHWApp
from spiders.chqevent1 import Chqevent1Spider
import sys
from scrapy.utils.log import configure_logging
from twisted.internet import reactor, defer,task
# add 2 mode : retrieve history - 保留过期数据 ACTIVE 进行上线， OVERDUE 筛选施工完毕信息
# add 2 mode : update new - random capture 不保留过期数据
pip = get_project_settings()
process = CrawlerProcess(pip)
def other():

    process.crawl(Chqevent1Spider())
    process.start()
    print "**********************************************************"
    reactor.stop()


#set timer

    

l = task.LoopingCall(other)
l.start(120) # call every 2 minutes

# l.stop() will stop the looping calls
reactor.run()
