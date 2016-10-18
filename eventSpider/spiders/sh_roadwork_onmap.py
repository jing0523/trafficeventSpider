# -*- coding: utf-8 -*-
from scrapy.http import FormRequest
from eventSpider.items import EventspiderItem
import scrapy
import json,time,datetime

class shHWApp(scrapy.spiders.Spider):
    name = "shHWApp"
    allowed_domains = ["map.shlzj.sh.cn"]
    start_urls = [
        # 'http://www.sdjtcx.com/map/getEvent',
        # 'http://www.sdjtcx.com/index2.jsp'
        'http://map.shlzj.sh.cn/LuZhengMap/mapwork/queryAllZD?_='
    ]

    def parse(self,response):
        token = 1473132450865
        yield FormRequest(
            url='http://map.shlzj.sh.cn/LuZhengMap/mapwork/queryAllZD?_=' + str(token),
            method='GET',
            dont_filter=True,  # 事故
            callback=self.road_work_data_parse

        )

    def convert_markingnum_coords(self,**kwargs):
        import math as Math
        x = float(kwargs.items()[1][-1])
        y = float(kwargs.items()[0][-1])

        x -= 660606.640282
        gPosX = x / 34280000 + 0.8374087555555556
        y = 477300.294757 - y
        gPosY = -y / 34190000 + 0.4085873712111339
        lon = gPosX * 360 - Math.floor(gPosX) * 360 - 180
        if (gPosX == 1):
            lon = 180
        lat = (0.5 - gPosY) * 2 * Math.pi
        lat = Math.atan(Math.exp(lat)) / Math.pi * 360 - 90
        return str(lon) + "," + str(lat)

    def calc_distance(self,**kwargs):

        fst_stake = kwargs.items()[0][1]
        lst_stake = kwargs.items()[1][1]

        finalfst = float(str(fst_stake.replace(u'k',u'')))
        finallst = float(str(lst_stake.replace(u'k',u'')))
        return (max(finalfst, finallst) - min(finalfst, finallst)) * 1000

    def check_status(self,**kwargs):
        from datetime import datetime
        td = datetime.today()
        postdate = kwargs.items()[0][1]
        plandate = kwargs.items()[-1][1]

        postdate = str(postdate) if type(postdate) is unicode else None
        plandate = str(plandate) if type(plandate) is unicode else None

        dt2 = datetime.strptime(postdate, '%Y-%m-%d %H:%M')
        dt3 = datetime.strptime(plandate, '%Y-%m-%d %H:%M')

        if (dt2 < td and dt3 > td):
            return 'active'
        return 'overdue'

    def parse_occpuies(self,**kwargs):
        description = kwargs.items()[0][1]
        import re as REGEX
        occupy_re = u'\u5360\u7528\u8f66\u9053\u6570\uff1a\d+'
        av_re = u'\u53ef\u7528\u8f66\u9053\u6570\uff1a\d+'
        fst_match = ''
        snd_match = ''

        utest = description.strip()
        p = REGEX.compile(occupy_re)
        match = p.findall(utest)

        p2 = REGEX.compile(av_re)
        match2 = p2.findall(utest)
        if match:
            assem_t = []
            for result in p.finditer(utest):
                t = result.group()
                assem_t.append(t)
            fst_match = REGEX.split(u'\u5360\u7528\u8f66\u9053\u6570\uff1a',  ','.join(assem_t))[-1]
        if match2:
            assem_t = []
            for result in p2.finditer(utest):
                t = result.group()
                assem_t.append(t)
            snd_match = REGEX.split(u'\u53ef\u7528\u8f66\u9053\u6570\uff1a',  ','.join(assem_t))[-1]

        result_dict = {"occupy": int(fst_match), "available": int(snd_match)}
        return result_dict

    def road_work_data_parse(self,response):
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

        print "============================parse call back function=========================="
        data = json.loads(response.body_as_unicode())
        pdata = data['rows']
        for i in range(0, len(pdata), 1):
            item = EventspiderItem()
            dl = pdata[i]
            item["spider_oid"] = dl[u'id']
            item["spider_fststake"] = dl[u"startNumDis"]
            item["spider_lststake"] = dl[u"endNumDis"]
            item["spider_direction"] = (dl[u'position'] + '_' + dl[u'directionTypeDis']).strip('\r\n\t')
            item["description"] = dl[u'describe'].strip().replace('\n', '').replace('\r', '')
            item["spider_dist"] =  self.calc_distance(fst_stake = item['spider_fststake'],
                                                      lst_stake = item['spider_lststake'],
                                                      desc = item["description"])
            item["spider_postdate"] =  dl[u'detectionTimeDis']


            item["START_TIME"] =  dl[u'detectionTimeDis']
            item["END_TIME"] =  dl[u'planTimeDis']

            item['start_time'] =time.strptime(dl[u'detectionTimeDis'], '%Y-%m-%d %H:%M')
            item['end_time'] = time.strptime( dl[u'planTimeDis'], '%Y-%m-%d %H:%M') if dl[u'planTimeDis'] else None
            item['spider_status'] = self.check_status(postdate = item["START_TIME"],
                                                      plandate =item["END_TIME"] )

            item["event_type"] = 0
            item["reason"] = 2
            item["event_source"] = u"1：上海市路政局"
            item["loc_name"] = dl[u'roadName']

            coord_array = dl[u'markingNumber']
            x0 = coord_array.split(",")[0]
            y0 = coord_array.split(",")[-1]
            item["ref_point"] = self.convert_markingnum_coords(x=x0,y=y0) if coord_array else u"NULL"
            item["ref_point_type"] = 1

            occupies = self.parse_occpuies(desc = item["description"]) # return dict / array
            if occupies:
                item["occupy"] = occupies['occupy']
                item["available"] = occupies['available']
            item["city"] = u"上海"

            """
            +++++++++++++++++++++++DropItem cannot apply to all spider, drop item here ++++++++++++++++++++++++++++++

            """
            if item['spider_status'] == "overdue":
                continue
            yield item