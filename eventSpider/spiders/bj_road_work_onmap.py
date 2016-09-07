# -*- coding: utf-8 -*-
from eventSpider.items import EventspiderItem
from scrapy.http import Request
import scrapy
import json, codecs, os, sys
import datetime, time
import re


class bjRoadWorkOnMap(scrapy.spiders.Spider):
    name = 'bjevent'
    allowed_domains = ['glcx.bjlzj.gov.cn']
    start_urls = [
        'http://glcx.bjlzj.gov.cn/bjglwww/index.shtml'
    ]

    def calculate_dist(self, item):
        description = item['description']
        regex_stake = u'(K\d+(\+\d+)*[~](K)*\d+(\+\d+)*)|(K\d+(\+\d+)*)'
        p = re.compile(regex_stake)
        utest = description.strip()
        match = p.findall(utest)

        if len(match) == 1:
            assem_t = []
            for result in p.finditer(utest):
                t = result.group()
                assem_t.append(t)
            str_assem_t = ','.join(assem_t)
            fst_finalmatch = re.split(u'~', str_assem_t)[0]
            lst_finalmatch = re.split(u'~', str_assem_t)[-1]

            finalfst = fst_finalmatch.replace(u'K', u'').replace(u'+', u'.')
            finallst = lst_finalmatch.replace(u'K', u'').replace(u'+', u'.')

            finalfst = float(str(finalfst))
            finallst = float(str(finallst))
            item['spider_fststake'] = fst_finalmatch
            item['spider_lststake'] = lst_finalmatch
            short_dist = (max(finalfst, finallst) - min(finalfst, finallst)) * 1000
            return short_dist
        return -1
    def parse(self, response):
        yield Request(
                url="http://glcx.bjlzj.gov.cn/bjglwww/ws/publish/publishEvent/publishEvents",
                method="POST",
            cookies={'JSESSIONID': 'AE0E5EE2F39355DE399BE9B9CB258E21',
                     '_gscu_813094265': '63640433yb4sh416'},
                callback=self.fill_in_items)

    def reason_switcher(self, reason):
        switcher = {
            'B5': 2
        }

        return switcher.get(reason, 'NONE')
    def eventtype_switcher(self,eventtype):
        switcher = {
            u'半幅封闭':1,
            u'双向封闭':0
        }

        return switcher.get(eventtype[0:4], -1)

    def fill_in_items(self, response):
        # parse json and fill them into items
        item = EventspiderItem()
        data = json.loads(response.body)
        real_data = data[u'roadEvents'][u'roadEvents']
        strnow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for row in real_data:

            item['loc_name'] = row[u'roadName'].encode('utf-8')
            item['reason'] = self.reason_switcher(row[u'eventType'].encode('utf-8')) #switcher
            raw_type = self.eventtype_switcher(row[u'dealCase'])
            item['event_type'] = str(raw_type).encode('utf-8') if type(raw_type) is int else -99
            # need to parse to unix regex
            item['start_time'] = datetime.datetimestrptime(row[u'occurTime'], '%Y-%m-%d')
            item['START_TIME'] = row[u'occurTime']
            endtime = row[u'endTime']
            if endtime:
                item['is_sure']  = 1
                item['end_time'] = datetime.datetime.strptime(row[u'endTime'], '%Y-%m-%d %H:%M')
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
            item['ref_point_type'] = 1
            raw_coords = row[u'lonlatData'][4:-2].encode('utf-8')
            item['ref_point'] =u'-1,-1' if raw_coords.find("0.0,0.0") > -1 else raw_coords
            item['ref_point'] = item['ref_point'].replace('y:','')

            item['event_source'] = u'北京市路政局公路出行信息服务站'
            item['city'] = u'北京'

            item['spider_oid'] = row[u'eventId']
            item['spider_ref'] = self.start_urls[0]
            item['spider_dist'] = self.calculate_dist(item)

            yield item
