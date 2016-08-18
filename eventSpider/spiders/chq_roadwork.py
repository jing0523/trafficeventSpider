# -*- coding: utf-8 -*-
import scrapy, os
import urllib2, urllib
from eventSpider.items import EventspiderItem
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
import time, datetime, time

class ChqRoadworkSpider(scrapy.Spider):
    name = "chq_roadwork"
    allowed_domains = ['183.64.107.220:9037',
              # map
              ]
    start_urls = (
        'http://183.64.107.220:9037/Traffic/List'
    )

    def event_type_switcher(self, eventTypeID):
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

    def parse(self, response):
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



            item['event_source'] = u'重庆公路网'
            item['event_type'] = self.event_type_switcher(_type.strip())
            item['CONTENT'] = _content.strip().replace('\n', ' ').replace('\r', '').encode('utf-8')

            item['REF'] = url
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
            item['COLLECTDATE'] = datetime.datetime.today().strftime('%Y-%m-%d')
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