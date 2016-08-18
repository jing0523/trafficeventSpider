# -*- coding: utf-8 -*-
import sys
import re
reload(sys)

from eventSpider.items import EventspiderItem

import scrapy
import json, os, sys
import datetime, time


class jsHWApp(scrapy.spiders.Spider):
    name = "jsHWApp"
    allowed_domains = ['218.2.208.140:8091']
    start_urls = [
        'http://218.2.208.140:8091/JSWeb/servlet/custService?key=getLUWSJSSB&traffictype='
    ]
    def create_oid(self,item):

        toparse = []

        rname_ptrn = u'(\[)?[GSXYCZ]\d+(\])?'  # 国道、省道
        # stakename_ptrn = u'(K\d+\+\d+\-K\d+\+\d+)|(\w+\.+\w+K\u5904)|(\d+K\u81f3\d+K)' #桩号标志
        stakename_ptrn = u'(K\d+\+\d+\-K\d+\+\d+)|(\d+(\.+\d+)?K处)|(\d+(\.+\d+)?K至\d+(\.+\d+)?K)|K(\d+(\.+\d+)?至K\d+(\.+\d+)?)' #桩号标志
        p = re.compile(rname_ptrn)
        utest = item['description'].strip() + item['loc_name'].strip()
        for result in p.finditer(utest) :
            t=result.group()
            if t.find(u'[') > -1:
                t = t[1:-1]
            toparse.append(t)


        finalfirst = None
        finallast = None
        q = re.compile(stakename_ptrn)
        for result in q.finditer(utest):
            t= result.group()
            if t.find(u'处') > -1:
                toparse.append(t[0:t.find(u'处')])
                toparse.append(t[t.find(u'处')+1:])
                finalfirst = t[0:t.find(u'处')]
                finallast =t[t.find(u'处')+1:]

            elif t.find(u'-') > -1:
                toparse.append(t[0:t.find(u'-')]) # first stake
                toparse.append(t[t.find(u'-') + 1:])
                finalfirst= t[0:t.find(u'-')]
                finallast = t[t.find(u'-') + 1:]
            elif t.find(u'至') > -1:
                toparse.append(t[0:t.find(u'至')])# first stake
                toparse.append(t[t.find(u'至') + 1:])
                finalfirst = t[0:t.find(u'至')]
                finallast = t[t.find(u'至') + 1:]

        toparse = list(set(toparse))
        toparse.sort(reverse=True)
        new_oid = '-'.join([w for w in toparse]).replace('.','')
        new_oid = new_oid.replace('+','')
        # before return function value ,fill up 2 stake cell anyway
        item['spider_lststake'] = finallast
        item['spider_fststake'] = finalfirst

        if new_oid:
            return new_oid
        return 'Cannot create oid'

    def event_type_switcher(self, eventTypeID):
        if type(eventTypeID) is unicode:
            _event_type_id = int(eventTypeID)
            switcher = {
                151: u'2',#u'养护施工'
                115: u'4',#u'通告',
                131: u'天气受阻-雨',#u'0',
                134: u'天气受阻-雾',#u'0'
                121: u'1',#u'交通事故',
                173: u'1',#u'紧急事故',
                144: u'2',#u'断路',
                141: u'2',#u'断路',
            }

            return switcher.get(_event_type_id, '-99')

        return 'NONE'
    def fill_fakedistance(self,item):
        return False
    def fill_fakedirection(self,item):
        return True


    def calculate_dist(self,item):
        # null - checking
        if item['spider_oid'] ==  'Cannot create oid':
            return -1
        fst_stake = item['spider_fststake']
        lst_stake = item['spider_lststake']
        description = item['description']
        if not fst_stake or not lst_stake:
            return -1

        fst_stakenum = float(str(fst_stake).upper().replace(u'K',u''))
        lst_stakenum = float(str(lst_stake).upper().replace(u'K',u''))

        if fst_stake.find(u'K') == 0 or lst_stake.find(u'K') == 0: # start with K
            # when stake starts with character ' K', it should consider other way to parse from
            # [event description] 1. that contains stake info - regex to findset
            #                     2. that does not contain stake info,write -1 instead
            regex_stake = u'(K\d+(\+\d+)*\WK\d+(\+\d+)*)|(K\d+(\+\d+)*)' #[-~至—] replaced with \W
            p = re.compile(regex_stake)
            utest = description.strip()
            for result in p.finditer(utest):
                t = result.group()
                if not t:
                    return -1 # no distance provided
                else:
                    # add checking
                    t = t.replace(u'\uff5e',u'-') if t.find(u'\uff5e') > 0 else t

                    fst_finalmatch = re.split(u'[-~至—]+',t)[0]
                    lst_finalmatch = re.split(u'[-~至—]+',t)[-1]

                    if not fst_finalmatch or not lst_finalmatch:
                        return -1  # -description no distance provided


                    finalfst = fst_finalmatch.replace(u'K',u'').replace(u'+',u'.')
                    finallst = lst_finalmatch.replace(u'K',u'').replace(u'+',u'.')

                    finalfst = float(str(finalfst))
                    finallst = float(str(finallst))

                    item['spider_fststake'] = fst_finalmatch
                    item['spider_lststake'] = lst_finalmatch

                    return max(finalfst, finallst)- min(finalfst, finallst)
        else:
            return max(fst_stakenum,lst_stakenum) - min(fst_stakenum,lst_stakenum)

    def parse(self, response):
        data = json.loads(response.body.decode('gb18030').encode('utf8'))
        if data:
            for case in data[u'LUWSJSSB']:
                item = EventspiderItem()

                add_text = case[u'LUXBSM'] if case[u'LUXBSM'].find(u'LX') < 0 else u""
                item['loc_name'] = case[u'LUDMC'] + u'|' + add_text
                item['event_source'] = u'江苏省交通运输厅'

                item['reason'] = self.event_type_switcher(case[u'SHIJLX'])
                item['weather'] = u'-1' if int(str(item['reason'])) > 0 else u'待定'

                item['start_time'] = time.strptime(case[u'SHIFSJ'], '%Y-%m-%d %H:%M:%S')
                item['end_time'] =   time.strptime(case[u'YUJHFSJ'], '%Y-%m-%d %H:%M:%S')

                item['START_TIME'] = case[u'SHIFSJ']
                item['END_TIME'] =  case[u'YUJHFSJ']

                direction = case[u'FANGX']
                postdate = case[u'CHUANGJSJ']
                desc =  case[u'SHIJNR'].strip().replace('\n', ' ').replace('\r', '')
                item['description'] = desc[:-5] if desc.find(u'发布时间') > -1 else desc


                item['spider_ref'] = self.start_urls[0]
                item['ref_point_type'] = u'1'
                item['ref_point'] =  case[u'X'] + ',' + case[u'Y']
                item['spider_postdate'] =  postdate
                item['spider_oid'] = self.create_oid(item)
                item['spider_direction'] = direction.strip().replace('\n', ' ').replace('\r', '')
                item['spider_dist']  = self.calculate_dist(item)

                yield item
