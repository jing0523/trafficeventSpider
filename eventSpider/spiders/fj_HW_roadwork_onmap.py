# -*- coding: utf-8 -*-
from scrapy.http import FormRequest
from eventSpider.items import EventspiderItem
import re
import scrapy
import json, codecs, os, sys
import datetime, time


class fjHWApp(scrapy.spiders.Spider):
    name = "fjHWApp"
    allowed_domains = ['appserver.fjgsgl.cn']
    start_urls = [
        'http://appserver.fjgsgl.cn/NewFJGSWechatAPIServer/index.php/userautoserver/showtrafficinfo?tab=1',  #
        # 路名-非必要
    ]

    response_id_map = {}
    page = -1
    def extract_loc(self,ustring):

        if len(ustring) < 1:
            return None

        t0 = re.split(u'\u7ebf', ustring)[0]
        t1 = re.split(u'\u7ebf', ustring)[-1]
        t1_1 = re.split(u'\u9ad8\u901f', t1)[0] if ustring.find(u'\u590d\u7ebf') < 0 else re.split(u'\u590d\u7ebf', ustring)[0]
        t_cons = t0 + u'|' + t1_1 + u'高速' if ustring.find(u'\u590d\u7ebf') < 0 else t0 + u'|' + t1_1 + u'复线'

        t_cons = t_cons if len(t_cons) < 20 else t0 + u'|'

        return t_cons

    def calculate_dist(self,item):

        fst_stake = item['spider_fststake']
        lst_stake = item['spider_lststake']
        description = item['description'].strip().encode('utf-8')
        regex_stake = u'(K\d+(\+\d+)*[-~至—](K)*\d+(\+\d+)*)|(K\d+(\+\d+)*)'
        # parsestake
        p = re.compile(regex_stake)
        utest = description.strip()
        match = p.findall(utest)

        if not fst_stake or not lst_stake or not match:
            return -1
        elif fst_stake and lst_stake and not match:
            fst_stakenum = float(str(fst_stake).upper().replace('K', ''))
            lst_stakenum = float(str(lst_stake).upper().replace('K', ''))
            return (max(fst_stakenum,lst_stakenum) - min(fst_stakenum,lst_stakenum))*1000
        else: # no stake provide but can be parsed from desc
            finalfst = None
            finallst = None


            if len(match)==2:
                assem_t = []
                for result in p.finditer(utest):
                    t = result.group()
                    assem_t.append(t)
                str_assem_t = ','.join(assem_t)
                fst_finalmatch = re.split(u'[\,-]+', str_assem_t)[0]
                lst_finalmatch = re.split(u'[\,-]+', str_assem_t)[-1]

                finalfst = fst_finalmatch.replace(u'K', u'').replace(u'+', u'.')
                finallst = lst_finalmatch.replace(u'K', u'').replace(u'+', u'.')

                finalfst = float(str(finalfst))
                finallst = float(str(finallst))
                item['spider_fststake'] = fst_finalmatch
                item['spider_lststake'] = lst_finalmatch

                return (max(finalfst, finallst) - min(finalfst, finallst)) * 100
            for result in p.finditer(utest):
                t = result.group()
                if not t:
                    return -1
                fst_finalmatch = re.split(u'[-~至－]+', t)[0]
                lst_finalmatch = re.split(u'[-~至－]+', t)[-1]
                finalfst = fst_finalmatch.replace(u'K', u'').replace(u'+', u'.')
                finallst = lst_finalmatch.replace(u'K', u'').replace(u'+', u'.')
                finalfst = float(str(finalfst))
                finallst = float(str(finallst))
                item['spider_fststake'] = fst_finalmatch
                item['spider_lststake'] = lst_finalmatch
            return (max(finalfst, finallst) - min(finalfst, finallst)) * 1000


    def parse(self, response):
        yield FormRequest(
            url='http://appserver.fjgsgl.cn/NewFJGSWechatAPIServer/index.php/userautoserver/c007',
            method='POST',
            formdata={'roadlineid': '0', 'eventtype': '1006001', 'pageid': '0'}, dont_filter=True,
            callback=self.event_data_parse

        )

        yield FormRequest(
            url='http://appserver.fjgsgl.cn/NewFJGSWechatAPIServer/index.php/userautoserver/c007',
            method='POST',
            formdata={'roadlineid': '0', 'eventtype': '1006002', 'pageid': '0'}, dont_filter=True,
            callback=self.roadwork_data_parse

        )

    def event_data_parse(self, response):

        jdata = json.loads(response.body)
        events = jdata[u'data']
        if events:
            for event in events:
                item = EventspiderItem()

                item['event_source'] = u'福建高速公路'
                item['reason'] = 1

                item['START_TIME'] = event[u'occtime']
                item['END_TIME'] = event[u'planovertime']
                X = event[u'coor_x']
                Y = event[u'coor_y']

                enc_event_text = event[u'remark'].strip().replace('\n', ' ').replace('\r', '')
                item['description'] = enc_event_text
                item['loc_name'] = self.extract_loc(enc_event_text)
                item['ref_point_type'] = 4  # u'高德'坐标类型-2火星-4wgs84-6百度
                item['ref_point'] =  str(X) + u' ,' + str(Y)


                item['spider_ref'] = self.start_urls[0]
                item['spider_postdate'] = (event[u'intime']).encode('utf-8')
                item['spider_oid'] = event[u'eventid']
                item['spider_direction'] = (event[u'startnodename'] + u'-' + event[u'endnodename']).encode( 'utf-8')


                item['spider_lststake'] = (event[u'endstake']).encode('utf-8')
                item['spider_fststake'] = (event[u'startstake']).encode('utf-8')
                item['spider_dist'] = self.calculate_dist(item)

                # todo: parse time to timestamp
                item['start_time'] = time.strptime(event[u'occtime'], '%Y-%m-%d %H:%M:%S')
                item['end_time'] = time.strptime(event[u'planovertime'], '%Y-%m-%d %H:%M:%S') if event[u'planovertime'] else None
                yield item

    def roadwork_data_parse(self, response):
        jdata = json.loads(response.body)
        events = jdata[u'data']
        if events:
            for event in events:
                item = EventspiderItem()


                item['event_source'] = u'福建高速公路'
                item['reason'] = 2

                item['START_TIME'] = event[u'occtime']
                item['END_TIME'] = event[u'planovertime']
                enc_event_text = event[u'remark'].strip().replace('\n', ' ').replace('\r', '')
                item['description'] = enc_event_text
                item['loc_name'] = self.extract_loc(enc_event_text)
                X = event[u'coor_x']
                Y = event[u'coor_y']
                item['ref_point'] = str(X) + u' ,' + str(Y)
                item['ref_point_type'] = 4  # u'高德'

                item['spider_ref'] = self.start_urls[0][-1:] + '4'
                item['spider_postdate'] = (event[u'intime']).encode('utf-8')
                item['spider_oid'] = event[u'eventid']
                item['spider_direction'] = (event[u'startnodename'] + u'-' + event[u'endnodename']).encode(
                    'utf-8')
                item['spider_lststake'] = (event[u'endstake']).encode('utf-8')
                item['spider_fststake'] = (event[u'startstake']).encode('utf-8')
                item['spider_dist'] = self.calculate_dist(item)

                item['start_time'] = time.strptime(event[u'occtime'], '%Y-%m-%d %H:%M:%S')
                item['end_time'] = time.strptime(event[u'planovertime'], '%Y-%m-%d %H:%M:%S') if event[u'planovertime'] else None

                yield item
