# -*- coding: utf-8 -*-
import scrapy, os
from eventSpider.items import EventspiderItem
from scrapy.selector import HtmlXPathSelector
import time, datetime, time
from scrapy.http import Request

class lnHWLzSpider(scrapy.spiders.Spider):
    name = 'lnHWlz'
    allowed_domains = ['218.25.53.5:7080']
    start_urls = [
        'http://218.25.53.5:7080/lk/web/highwaylk.do',
        # referer
    ]

    def parse(self, response):
        selector = HtmlXPathSelector(response)
        trcount = selector.xpath("count(//tr[@class='lxzn_content_td'])").extract()
        int_trcount = int(str(''.join(trcount)).split('.')[0])

        for i in range(2,int_trcount):
            sels = selector.xpath('//*[@class="lxzn_content"]/tr[' + str(i) + ']')
            for sel in sels:
                item = EventspiderItem()
                rdname = ''.join(sel.xpath('td[2]/text()').extract())
                direction = ''.join(sel.xpath('td[3]/text()').extract())
                content = ''.join(sel.xpath('td[4]/text()').extract())
                eventtype =  ''.join(sel.xpath('td[5]/text()').extract())
                reason = ''.join(sel.xpath('td[6]/text()').extract())
                start_time = ''.join(sel.xpath('td[7]/text()').extract())
                end_time = ''.join(sel.xpath('td[8]/text()').extract())
                url = ''.join(sel.xpath('td[9]/a/@href').extract())

                beginlat = [t for t in url.split('&') if t.startswith('beginLat=')][0]
                beginlng = [t for t in url.split('&') if t.startswith('beginLng=') ][0]

                endLat = [t for t in url.split('&') if t.startswith('endLat=')][0]
                endLng = [t for t in url.split('&') if t.startswith('endLng=') ][0]
                # uuid = [t for t in url.split('&') if t.startswith('uuid=') ][0]

                # content += beginlng.replace('beginLng=','') + ','+  beginlat.replace('beginLat=','')

                rdname = rdname.strip().replace('/n','').replace('/r','')
                direction = direction.strip().replace('/n','').replace('/r','')
                content = content.strip().replace('/n','').replace('/r','')
                reason = reason.strip().replace('/n','').replace('/r','')
                start_time = start_time.strip().replace('/n','').replace('/r','')
                end_time = end_time.strip().replace('/n','').replace('/r','')

                item['description'] = content.encode('utf-8') +  direction.encode('utf-8')
                # item['TITLE'] = rdname.encode('utf-8')
                item['loc_name'] = rdname.encode('utf-8')
                # item['COLLECTDATE'] = datetime.datetime.today().strftime('%Y-%m-%d')
                # item['DIRECTION'] = direction.encode('utf-8')
                item['START_TIME'] = start_time.encode('utf-8')
                item['END_TIME'] = end_time.encode('utf-8')

                # item['start_time'] =  time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                # item['end_time'] =  time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                item['reason'] = reason.encode('utf-8')
                item['event_type'] = eventtype.encode('utf-8')


                item['spider_ref'] = 'http://' + self.allowed_domains[0] + '/'+ url
                item['ref_point_type'] = u'百度'
                item['event_source'] = u'辽宁省交通厅'
                item['ref_point'] =  beginlng.replace('beginLng=','') + ','+  beginlat.replace('beginLat=','') + ';' + endLng.replace('endLng=','')  + ','+endLat.replace('endLat=','')
                # item['NE2'] =
                yield item

            next_pages_urls = ['http://218.25.53.5:7080/lk/web/roadlk.do']
            print "*******************next page**********************"
            for next_page_url in next_pages_urls:
                yield Request(next_page_url, callback=self.parse)