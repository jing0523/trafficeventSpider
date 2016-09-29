# -*- coding: utf-8 -*-
from scrapy.http import FormRequest
from scrapy.http import Request
from eventSpider.items import EventspiderItem

import scrapy
import json, codecs, os, sys
import datetime, time


class zjHWApp(scrapy.spiders.Spider):
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
        """

         'spider_oid', 'spider_fststake', 'spider_lststake','spider_direction', 'spider_dist',
            'spider_postdate', 'spider_ref','START_TIME', 'END_TIME','spider_status','fake_dist','fake_direction',
            'event_type','reason'
            ,'event_source'
            ,'start_time'
            ,'end_time'
            , 'loc_name'
            , 'cycle'
            , 'begin_end'
            , 'ref_point'
            , 'ref_point_type'
            ,'description'
            , 'is_sure'
            ,'speed'
            ,'available'
            ,'occupy'
            ,'weather'
            ,'city',
            'link_info'
        :param response:
        :return:
        """
        item = EventspiderItem()
        d = self.response_id_map
        int_realRoadID = int(response.request.body[-2:].replace("=", ""))
        realRoadName = d[int_realRoadID][0]

        jdata = json.loads(response.body)
        events = jdata[u'data']
        if len(events) < 1:
            item['spider_oid'] = int_realRoadID
            item['loc_name'] = realRoadName
            item['event_source'] = u'1：浙江智慧高速'
            item['event_type'] = u'-1'
            yield None
            # return
        else:
            for e in events:
                item['spider_oid'] = int_realRoadID
                item['loc_name'] = realRoadName

                str_passby_stations = e[u'startnodename'] + ' - ' + e[u'endnodename']
                item['event_type'] = e[u'eventtype']
                item['reason'] = u'2'
                item['spider_direction'] = (e[u'directionname'] + str_passby_stations)
                item['START_TIME'] = e[u'occtime']
                item['END_TIME'] = "2019-01-01 00:00:00"
                item['start_time'] = time.strptime(e[u'occtime'], '%Y-%m-%d %H:%M:%S')
                item['end_time'] = time.strptime(item['END_TIME'], '%Y-%m-%d %H:%M:%S')
                item['is_sure'] = u'0' if not item['END_TIME'] else u'1'
                # strip content
                ecode_ctnt = (e[u'reportout'].strip().replace('\n', ' ').replace('\r', '')).encode('utf-8')
                utitle = ''.join(e[u'title'].split())
                ecode_title = utitle.encode('utf-8')



                item['ref_point'] = u"-1,-1"
                item['ref_point_type'] = 1


                item['description'] = ecode_ctnt
                item['spider_ref'] = 'http://app.zjzhgs.com/MQTTWechatAPIServer/businessserver/showhighdetail/' + str(
                    int_realRoadID)
                item['spider_postdate'] = e[u'occtime'].encode('utf-8')
                item['event_source'] = u'1:浙江智慧高速'

                yield item
