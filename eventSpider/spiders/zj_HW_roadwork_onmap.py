# -*- coding: utf-8 -*-
from scrapy.http import FormRequest
from scrapy.http import Request
from eventSpider.items import EventspiderItem

import scrapy
import json, codecs, os, sys
import datetime, time


class zjfHWApp(scrapy.spiders.Spider):
    name = "zjHWApp"
    allowed_domains = ['zjzhgs.com']
    start_urls = [
        'http://app.zjzhgs.com/MQTTWechatAPIServer/businessserver/getTrafficByRoad',
        'http://app.zjzhgs.com/MQTTWechatAPIServer/businessserver/loadAllroad'
    ]
    response_id_map = {}
    page = -1
    # '''
    #     Method：-
    #     parse                        -Request        show all road list and id
    #     get_road_mapping             -json/dict      road name and id mapping dict
    #     dataparse                    -Item/dict      return Items can be exported through out pipelinetool

    # '''
    def parse(self, response):
        yield Request(
            url='http://app.zjzhgs.com/MQTTWechatAPIServer/businessserver/loadAllroad',
            method="POST",
            dont_filter=True,
            callback=self.get_road_mapping)
    def get_road_mapping(self, response):
        data = json.loads(response.body)
        for r in data["data"]:
            rdname = r[u'shortname']
            rdid = int(r[u'roadoldid'])
            self.response_id_map.update({rdid: [rdname, response]})

        for i in [k for k, v in self.response_id_map.items()]:
            # add timer
            import time, random
            if (i % 5 == 0):
                time.sleep(random.random() * 30)
            self.page = i
            yield FormRequest(
                url="http://app.zjzhgs.com/MQTTWechatAPIServer/businessserver/getTrafficByRoad",
                method="POST",
                formdata={'roadoldid': str(i)}, dont_filter=True,
                callback=self.data_parse)

    def reason_switcher(self, eventtype):
        switcher = {
            u'半幅封闭': u'受阻',
            u'双向封闭': u'道路禁行'
        }
        i = eventtype.index(u'附近有')
        return switcher.get(eventtype[len(eventtype) - i:], eventtype)
    def data_parse(self, response):

        item = EventspiderItem()
        d = self.response_id_map
        int_realRoadID = int(response.request.body[-2:].replace("=", ""))
        realRoadName = d[int_realRoadID][0]

        jdata = json.loads(response.body)
        events = jdata[u'data']
        if len(events) < 1:
            item['OID'] = int_realRoadID
            item['ROADNAME'] = realRoadName
            item['POSTFROM'] = u'浙江智慧高速'
            item['CONTENT'] = u'目前无路况'
            item['TITLE'] = u'目前无路况'
            yield None
            # return
        else:
            for e in events:
                item['OID'] = int_realRoadID
                item['ROADNAME'] = realRoadName
                item['COLLECTDATE'] = datetime.datetime.today().strftime('%Y-%m-%d')

                str_passby_stations = e[u'startnodename'] + ' - ' + e[u'endnodename']
                item['REASON'] = e[u'eventtype']
                item['DIRECTION'] = (e[u'directionname'] + str_passby_stations)
                item['START_TIME'] = e[u'occtime']
                item['END_TIME'] = datetime.datetime.today().strftime('%Y-%m-%d')

                # strip content
                ecode_ctnt = (e[u'reportout'].strip().replace('\n', ' ').replace('\r', '')).encode('utf-8')
                utitle = ''.join(e[u'title'].split())
                ecode_title = utitle.encode('utf-8')
                item['CONTENT'] = ecode_ctnt
                item['TITLE'] = ecode_title
                item['REF'] = 'http://app.zjzhgs.com/MQTTWechatAPIServer/businessserver/showhighdetail/' + str(
                    int_realRoadID)
                item['POSTDATE'] = e[u'occtime'].encode('utf-8')
                item['POSTFROM'] = u'浙江智慧高速'

                yield item
