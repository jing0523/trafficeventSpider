# -*- coding: utf-8 -*-


import scrapy
from eventSpider.items import EventspiderItem
import json
import datetime, time
from scrapy.http import Request
import re
class Chqevent1Spider(scrapy.spiders.Spider):
    name = "chqevent1"
    allowed_domains = ["stat.cq.gov.cn"]
    start_urls = (
        'http://cx.cqjt.gov.cn/zjcx/queryAllroadCtrlNews.html',
    )
    DEFAULT_AFFECT_DIST = 1000
    def parse(self, response):
        yield Request(
            url=self.start_urls[0],
            method="GET",
            dont_filter=True,
            callback=self.get_road_mapping)

    def get_road_mapping(self,response):
        """
            'spider_oid', 'spider_fststake', 'spider_lststake', 'spider_direction', 'spider_dist',
            'spider_postdate', 'spider_ref', 'START_TIME', 'END_TIME', 'spider_status', 'fake_dist', 'fake_direction',
            'event_type', 'reason'
            , 'event_source'
            , 'start_time'
            , 'end_time'
            , 'loc_name'
            , 'cycle'
            , 'begin_end'
            , 'ref_point'
            , 'ref_point_type'
            , 'description'
            , 'is_sure'
            , 'speed'
            , 'available'
            , 'occupy'
            , 'weather'
            , 'city',
            'link_info'
    """
        data = json.loads(response.body_as_unicode())
        for r in data["data"]:
            item = EventspiderItem()

            rdname = r[u'roadLineName']
            rdid = int(r[u'code'])
            content = r[u'name'].encode('utf8')
            occurtime = [str(content).split('，')][0]
            xy = "{0},{1}".format(str(r[u'longitude']),str(r[u'latitude']))

            item['spider_oid'] = rdid
            item['spider_fststake'] = None
            item['spider_lststake'] = None
            item['spider_direction'] = r[u'gbDirection']
            item['spider_dist'] = self.DEFAULT_AFFECT_DIST
            item['spider_postdate'] = None
            item['spider_ref'] = self.start_urls[0]


            _parse_occurtime = "2016年" + occurtime[0]
            _parse_occurtime = _parse_occurtime.replace("年","-").replace("月","-").replace("日","-").replace("时","-").replace("分","")
            _occurtime = datetime.datetime.strptime(_parse_occurtime,"%Y-%m-%d-%H-%M") if _parse_occurtime.rfind("-") +1 < len(_parse_occurtime) else datetime.datetime.strptime(_parse_occurtime, "%Y-%m-%d-%H-")

            item['START_TIME'] = _occurtime

            _endtime  =occurtime[1]
            parse_end_pattern = u'(\u9884\u8ba1)[\d+\W]*(\u7ed3\u675f)'
            if re.search(parse_end_pattern,content):
                item['END_TIME'] = re.split(parse_end_pattern,_endtime)[1]
            else:
                item['END_TIME'] = -1
            # item['start_time'] = time.strptime(occurtime[0], '%Y-%m-%d %H:%M:%S')
            # item['end_time'] = time.strptime( item['END_TIME'], '%Y-%m-%d %H:%M:%S')

            item['spider_status'] = u'ACTIVE'
            item['event_type'] = 0
            item['reason'] = 2
            item['event_source'] = u'1：重庆交通出行网'
            item['loc_name'] = rdname
            item['ref_point'] = xy
            item['ref_point_type'] = 2 #google 偏转经纬度

            item['description'] = content
            item['city'] = u'重庆'



            yield item