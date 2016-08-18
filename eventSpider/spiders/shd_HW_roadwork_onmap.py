# -*- coding: utf-8 -*-
from scrapy.http import FormRequest
from eventSpider.items import EventspiderItem
import scrapy
import time
import bs4 as bs # use BS to parse XML
class shdHWApp(scrapy.spiders.Spider):
    name = "shdHWApp"
    allowed_domains = ["www.sdjtcx.com"]
    start_urls = [
        # 'http://www.sdjtcx.com/map/getEvent',
        # 'http://www.sdjtcx.com/index2.jsp'
        'http://www.sdjtcx.com/showIndex.do?method=index'
    ]

    def calculate_dist(self,item):
        fst_stake = item['spider_fststake']
        lst_stake = item['spider_lststake']

        # parsestake

        fst_stakenum = float(str(fst_stake).upper().replace(u'K', u'').replace(u'+', u'.'))
        lst_stakenum = float(str(lst_stake).upper().replace(u'K', u'').replace(u'+', u'.'))
        return (max(fst_stakenum, lst_stakenum) - min(fst_stakenum, lst_stakenum)) * 1000


    def parse(self, response):
        yield FormRequest(
            url='http://www.sdjtcx.com/map/getEvent',
            method='POST',
            formdata={'type':'007002'}, dont_filter=True, #事故
            callback=self.event_data_parse

        )
        yield FormRequest(
            url='http://www.sdjtcx.com/map/getEvent',
            method='POST',
            formdata={'type': '007001'}, dont_filter=True,  # 施工
            callback=self.roadwork_data_parse
        )

    def event_data_parse(self, response):
        xmlevents = response.text
        if xmlevents:
            soup = bs.BeautifulSoup(xmlevents, 'xml')

            for eventtag in soup.eventlist.contents:
                item = EventspiderItem()
                item['event_source'] = u'山东交通出行网'
                item['reason'] = 1

                item['START_TIME'] = eventtag.starttime.text if eventtag.starttime else None
                item['END_TIME'] = eventtag.endtime.text if eventtag.endtime else None
                X = eventtag.x.text
                Y = eventtag.y.text

                item[ 'description'] = eventtag.title.text if eventtag.title.text == eventtag.eventms.text else eventtag.title.text + eventtag.eventms.text
                item['loc_name'] = eventtag.glmc.text if eventtag.glmc else None
                item['ref_point_type'] = 4
                item['ref_point'] = str(X) + u' ,' + str(Y)
                item['spider_ref'] = self.start_urls[0]

                # item['spider_postdate'] = self.start_urls[0]
                item['spider_oid'] = eventtag.id.text if eventtag.id else None

                startdir = eventtag.startnode.text if eventtag.startnode else None
                enddir = eventtag.endnode.text if eventtag.endnode else None
                text_direction = startdir + u'-' + enddir if startdir and enddir else eventtag.roadfx.text
                item['spider_direction'] = text_direction

                item['spider_lststake'] = eventtag.endzh.text.encode('utf-8') if eventtag.endzh else -1
                item['spider_fststake'] = eventtag.startzh.text.encode('utf-8') if eventtag.startzh else -1
                item['spider_dist'] = self.calculate_dist(item)

                # todo: parse time to timestamp
                item['start_time'] = time.strptime(eventtag.starttime.text, '%Y-%m-%d %H:%M:%S')
                item['end_time'] = time.strptime(eventtag.endtime.text,
                                                 '%Y-%m-%d %H:%M:%S') if eventtag.endtime.text else None

                yield item


    def roadwork_data_parse(self, response):
        xmlroadworks = response.text
        if xmlroadworks:
            soup =bs.BeautifulSoup(xmlroadworks,'xml')

            for eventtag in soup.eventlist.contents:

                item = EventspiderItem()
                item['event_source'] = u'山东交通出行网'
                item['reason'] = 2

                item['START_TIME'] = eventtag.starttime.text if eventtag.starttime else None
                item['END_TIME'] = eventtag.endtime.text  if eventtag.endtime else None
                X = eventtag.x.text
                Y = eventtag.y.text

                item['description'] = eventtag.title.text if eventtag.title.text == eventtag.eventms.text else eventtag.title.text + eventtag.eventms.text
                item['loc_name'] = eventtag.glmc.text if eventtag.glmc else None
                item['ref_point_type'] = 4
                item['ref_point'] = str(X) + u' ,' + str(Y)
                item['spider_ref'] = self.start_urls[0]

                # item['spider_postdate'] = self.start_urls[0]
                item['spider_oid'] = eventtag.id.text if eventtag.id else None

                startdir = eventtag.startnode.text if eventtag.startnode else None
                enddir = eventtag.endnode.text if eventtag.endnode else None
                text_direction = startdir + u'-' + enddir if startdir and enddir else eventtag.roadfx.text
                item['spider_direction'] = text_direction

                item['spider_lststake'] = eventtag.endzh.text.encode('utf-8') if eventtag.endzh else -1
                item['spider_fststake'] = eventtag.startzh.text.encode('utf-8') if eventtag.startzh else -1
                item['spider_dist'] = self.calculate_dist(item)

                # todo: parse time to timestamp
                item['start_time'] = time.strptime(eventtag.starttime.text, '%Y-%m-%d %H:%M:%S')
                item['end_time'] = time.strptime(eventtag.endtime.text, '%Y-%m-%d %H:%M:%S') if eventtag.endtime.text else None


                yield item