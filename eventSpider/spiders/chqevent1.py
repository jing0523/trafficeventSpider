# -*- coding: utf-8 -*-
import scrapy
from eventSpider.items import EventspiderItem
import json
import datetime, time
from scrapy.http import Request

class Chqevent1Spider(scrapy.spiders.Spider):
    name = "chqevent1"
    allowed_domains = ["stat.cq.gov.cn"]
    start_urls = (
        'http://cx.cqjt.gov.cn/zjcx/queryAllroadCtrlNews.html',
    )

    def parse(self, response):
        yield Request(
            url=self.start_urls[0],
            method="GET",
            dont_filter=True,
            callback=self.get_road_mapping)

    def get_road_mapping(self,response):
        data = json.loads(response.body)
        for r in data["data"]:
            item = EventspiderItem()
            rdname = r[u'roadLineName']
            rdid = int(r[u'code'])
            content = r[u'name'].encode('utf8')
            occurtime = [str(content).split('，')][0]

            xy = 'x:\t' +  str(r[u'longitude']) +  ',y:'  + str(r[u'latitude'])
            item['OID'] = rdid
            item['ROADNAME'] = rdname
            item['POSTFROM'] = u'重庆交通出行网'
            item['START_TIME'] = occurtime[0]
            item['POSTDATE'] = occurtime[0]
            item['COLLECTDATE'] = datetime.datetime.today().strftime('%Y-%m-%d')
            item['CONTENT'] = content
            # item['TITLE'] = xy
            item['CITY'] = u'重庆'
            item['REF'] = self.start_urls[0]


            item['COORDSYS'] = u'高德'
            item['NE1'] = xy

            yield item