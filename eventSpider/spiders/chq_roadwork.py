# -*- coding: utf-8 -*-
import scrapy, os
import urllib2, urllib
from eventSpider.items import EventspiderItem
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
import time, datetime, time
from bs4 import BeautifulSoup as BS
import re

class ChqRoadworkSpider(scrapy.Spider):
    name = "chq_roadwork"
    allowed_domains = ['183.64.107.220:9037',
              # map
              ]
    start_urls = [
        # 'http://183.64.107.220:9037/Traffic/List'
        "http://183.64.107.220:9037/Traffic/AllMap?selectedGov=&selectedRoad="
    ]

    def event_type_switcher(self, eventTypeID):
        """
        rewrite fields
        :param eventTypeID:
        :return:
        """
        if type(eventTypeID) is unicode:
            _event_type_id = int(eventTypeID)
            switcher = {
                u'全幅封闭': 0, #禁行
                u'半幅封闭': 1, #受阻
                u'便道通行': 0, #禁行
                u'间断放行': 0, #禁行
                u'限速': 1, #受阻
                u'半幅通行': 1, #受阻
                u'限载': 1, #受阻
            }

            return switcher.get(_event_type_id, 'NONE')

        return 'NONE'
    def parse_dot_onmap(self,response):

        content = response.body_as_unicode()
        soup = BS(content,'html.parser')
        script = soup.find("script")
        text = soup.get_text()
        #todo:  functionalize
        lines = [line.strip() for line in text.splitlines()]
        for i in range(1,):
            xy_tg_line = [l for l in lines if l.find("var point"+str(i+1) + " = ") > -1]
            opts_tg_line = [l for l in lines if l.find("var opts" + str(i + 1) + " = ") > -1]
            infowin_tg_line = [l for l in lines if l.find("var infoWindow" + str(i + 1) + " = ") > -1]
            xy_tg_line = ''.join(xy_tg_line)
            re_pattern_xy  = u'(?:\d*\.)+\d+'
            if re.search(re_pattern_xy,xy_tg_line):
                p = re.compile(re_pattern_xy)
                tempx = [result.group() for result in  p.finditer(xy_tg_line)][0]
                tempy = [result.group() for result in  p.finditer(xy_tg_line)][1]
                xy = "{0},{1}".format(tempx,tempy)
            else:
                xy = "-1,-1"

    def parse(self, response):

        yield FormRequest(
            url = "http://183.64.107.220:9037/Traffic/AllMap?selectedGov=&selectedRoad=",
            method="GET",
            dont_filter=True,
            callback=self.parse_dot_onmap
        )
        selector = HtmlXPathSelector(response)
        sels = selector.select('//div[@class="ui-wrap path"]/ul/li')

        itemdir = self.name
        if not os.path.exists(itemdir):
            os.makedirs(itemdir)
        for sel in sels:
            _title = ''.join(sel.xpath('a/p[@class="p1"]/text()').extract())
            _content = ''.join(sel.xpath('a/p[@class="p2"]/text()').extract())
            _type = ''.join(sel.xpath('a/p[@class="p1"]/strong/text()').extract())
            _loc = ''.join(sel.xpath('strong/text()').extract())
            _url = ''.join(sel.xpath('a/@href').extract())

            url = 'http://' + self.allowed_domains[0] + _url
            road_alias = _title.split('-')[0] #todo: set request on road alias
            item = EventspiderItem()
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

            """


            item['event_source'] = u'1：重庆公路网'
            item['event_type'] = self.event_type_switcher(_type.strip())
            item['description'] = _content.strip().replace('\n', ' ').replace('\r', '').encode('utf-8')

            item['spider_ref'] = url
            _content = urllib2.urlopen(url)
            import BeautifulSoup
            _ctnt = _content.read()
            if not _ctnt:
                continue
            rp = BeautifulSoup.BeautifulSoup(_ctnt)
            timelist = []
            for l in rp.findAll('li', {'style': True}):
                t = l.getText().strip()
                timelist.append(t)
            item['START_TIME'] = timelist[1][5:]
            item['END_TIME'] = timelist[2][5:]
            item['start_time'] = timelist[2][5:]
            item['END_TIME'] = timelist[2][5:]
            item['spider_postdate'] = datetime.datetime.today().strftime('%Y-%m-%d')
            _attachedtxt = ''.join([l.getText() for l in rp.findAll('label')])

            item['TITLE'] = (_title + _attachedtxt).strip().replace('\n', ' ').replace('\r', '').encode('utf-8')
            item['POSTDATE'] = timelist[1][5:]
            try:
                pics = rp.findAll('img', {'src': True})
                img_urls = [pic["src"] for pic in pics]
                if not img_urls:
                    continue
                for img_url in img_urls:
                    img_opener = urllib.URLopener()
                    import random
                    r = ''.join(str(random.random()).split('.'))
                    imgname = _title + r + img_url[-4:]
                    img_opener.retrieve(url=img_url,
                                        filename=itemdir + '\\' + imgname)
            except:
                # raise DropItem("No images support: %s" % item) //for pics cannot be downloaded
                yield item
            yield item