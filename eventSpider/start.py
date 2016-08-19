# -*- coding: utf-8 -*-
'''Run Scrapy Spider in Cmdline todo: run scrapy in a script'''

# done:runs multiple spiders simultaneously
from twisted.internet import task
from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.zj_HW_roadwork_onmap import zjfHWApp
from spiders.bj_roadwork_news import bjHWNews
from spiders.bj_road_work_onmap import bjRoadWorkOnMap
from spiders.js_HW_roadwork_onmap import jsHWApp
from spiders.fj_HW_roadwork_onmap import fjHWApp
from spiders.chq_roadwork import ChqRoadworkSpider
from spiders.liaoning_roadwork_news import lnHWLzSpider
from spiders.chqevent1 import Chqevent1Spider
from spiders.shd_HW_roadwork_onmap import shdHWApp
import sys

# add 2 mode : retrieve history - 保留过期数据 ACTIVE 进行上线， OVERDUE 筛选施工完毕信息
# add 2 mode : update new - random capture 不保留过期数据

pip = get_project_settings()
process = CrawlerProcess(pip)

# process.crawl(bjHWNews())
# process.crawl(bjRoadWorkOnMap())
# process.crawl(lnHWLzSpider())
# process.crawl(zjfHWApp())
# process.crawl(jsHWApp())
process.crawl(fjHWApp())
# process.crawl(shdHWApp())
# process.crawl(ChqRoadworkSpider())
# process.crawl(Chqevent1Spider())



#set timer
process.start()

# if __name__ == "__main__":
#     mode = raw_input('PLEASE ENTR MODE -1 : REMAIN HISTORY DATA;-0 UPDATE NEW DATA ONLY')
#     sys.exit(main(mode))
