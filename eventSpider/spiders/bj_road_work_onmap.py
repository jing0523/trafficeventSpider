# -*- coding: utf-8 -*-
from eventSpider.items import EventspiderItem
from scrapy.http import Request
import scrapy
import json, codecs, os, sys
import datetime, time


class bjRoadWorkOnMap(scrapy.spiders.Spider):
    name = 'bjevent'
    allowed_domains = ['glcx.bjlzj.gov.cn']
    start_urls = [
        'http://glcx.bjlzj.gov.cn/bjglwww/index.shtml'
    ]
    def parse(self, response):
        yield Request(
                url="http://glcx.bjlzj.gov.cn/bjglwww/ws/publish/publishEvent/publishEvents",
                method="POST",
            cookies={'JSESSIONID': 'AE0E5EE2F39355DE399BE9B9CB258E21',
                     '_gscu_813094265': '63640433yb4sh416'},
                callback=self.fill_in_items)

    def reason_switcher(self, reason):
        switcher = {
            'B5': u'施工'
        }

        return switcher.get(reason, 'NONE')
    def eventtype_switcher(self,eventtype):
        switcher = {
            u'半幅封闭':u'受阻',
            u'双向封闭':u'道路禁行'
        }

        return switcher.get(eventtype[0:4], 'NONE')

    def fill_in_items(self, response):
        # parse json and fill them into items

        item = EventspiderItem()
        data = json.loads(response.body)
        real_data = data[u'roadEvents'][u'roadEvents']
        strnow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for row in real_data:

            item['loc_name'] = row[u'roadName'].encode('utf-8')
            item['reason'] = self.reason_switcher(row[u'eventType'].encode('utf-8')) #switcher
            item['event_type'] = self.eventtype_switcher(row[u'dealCase']).encode('utf-8')
            # need to parse to unix regex
            item['start_time'] = time.strptime(row[u'occurTime'], '%Y-%m-%d')
            item['START_TIME'] = row[u'occurTime']
            endtime = row[u'endTime']
            if endtime:
                item['is_sure']  = 1
                item['end_time'] = time.strptime(row[u'endTime'], '%Y-%m-%d %H:%M')
                item['END_TIME'] = row[u'endTime']
            else:
                item['is_sure'] = 0

            item['description'] = row[u'description'].strip().replace('\n', ' ').replace('\r', '').encode('utf-8')+  ':' + row[u'dealCase'].encode('utf-8')
            '''
                "参考点坐标类型：
                    0:墨卡托坐标
                    1: 标准经纬度
                    2: google偏转经纬度
                    3: baidu偏转经纬度
                    4: 高德坐标

                '''
            item['ref_point_type'] = 4
            item['ref_point'] = row[u'lonlatData'][4:-2].encode('utf-8')
            item['ref_point'] = item['ref_point'].replace('y:','')
            item['event_source'] = u'北京市路政局公路出行信息服务站'
            item['city'] = u'北京'
            # default value
            # item['cycle'] = 0
            # item['begin_end'] = 0

            item['spider_oid'] = row[u'eventId']
            item['spider_ref'] = self.start_urls[0]

            yield item
