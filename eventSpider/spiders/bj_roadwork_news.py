# -*- coding: utf-8 -*-
from eventSpider.items import EventspiderItem
from scrapy.selector import HtmlXPathSelector
import scrapy
import datetime,time
import re

class bjHWNews(scrapy.spiders.Spider):
    name = 'bjevent2'
    allowed_domains = ['www.bj96011.com']
    start_urls = [
        'http://www.bj96011.com/action.php?type=chuxingxinxi&page=1'  # referer
        'http://www.bj96011.com/action.php?type=chuxingxinxi&page=2'  # referer
    ]

    def parse_xy_coords(self,desc):
        import re
        regex_stake = u'x=\d+.\d+&y=\d+.\d+'
        p = re.compile(regex_stake)
        utest = desc.strip()
        match = p.findall(utest)
        if len(match) > 0:
            assem_t = []
            for result in p.finditer(utest):
                t = result.group()
                assem_t.append(t)
            str_assem_t = ','.join(assem_t)
            pattern = '&y='
            str_assem_t =str_assem_t.replace("x=",'')
            x = re.split(pattern=pattern,string =str_assem_t)[0]
            y = re.split(pattern=pattern,string =str_assem_t)[1]
            return '%s,%s' % (x,y)
        return '-1,-1'
    def parse(self, response):
        selector = HtmlXPathSelector(response)
        sels = selector.xpath('//*[@class="road_one"]')
        for sel in sels:
            item = EventspiderItem()

            roadname = ''.join(sel.xpath('div[@class="road_one_title"]/span[1]/text()').extract())
            event_type = ''.join(sel.xpath('div[@class="road_one_title"]/span[2]/text()').extract())
            occtime = ''.join(sel.xpath('div[@class="road_one_title"]/span[3]/text()').extract())
            info = ''.join(sel.xpath('div[@class="road_info"]/p[1]/text()').extract())
            partial_url = ''.join(sel.xpath('div[@class="road_info"]/p[2]/a/@href').extract())

            encode_ctnt = info.strip().replace('\n', '').replace('\r', '').encode('utf-8')
            roadname = roadname.encode('utf-8')
            event_type = event_type.encode('utf-8')

            item['event_type'] = event_type
            item['reason'] = u'2'
            item['description'] = encode_ctnt
            item['loc_name'] = roadname

            item['START_TIME'] = occtime
            item['END_TIME'] = "2019-01-01 00:00:00"

            # from eventSpider.ParserOptions import DataParser as dp
            # parser = dp()
            # parser.setRules(_spidername='bjevent2')
            # item['END_TIME'] = parser.check_fill_ed(item_desc=encode_ctnt)


            item['start_time'] = time.strptime(occtime, '%Y-%m-%d %H:%M:%S')
            item['end_time'] = time.strptime(item['END_TIME'], '%Y-%m-%d %H:%M:%S')
            item['is_sure'] = u'0' if not item['END_TIME'] else u'1'

            item['spider_ref'] = partial_url
            item['ref_point'] = self.parse_xy_coords(partial_url)
            item['ref_point_type'] = u'4'
            item['spider_postdate'] = occtime
            item['event_source'] = u'首发高速出行网'
            import random as rdm
            item["spider_oid"] =  ''.join(str(rdm.choice(range(0,9))) for i in range(0,8)) # 8 digit random number
            yield item