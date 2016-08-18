# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EventspiderItem(scrapy.Item):
    spider_oid = scrapy.Field()
    description = scrapy.Field()
    loc_name = scrapy.Field()

    spider_direction = scrapy.Field()
    spider_fststake = scrapy.Field()
    spider_lststake = scrapy.Field()
    spider_dist = scrapy.Field()

    ref_point = scrapy.Field()
    ref_point_type = scrapy.Field()


    event_type = scrapy.Field()
    reason = scrapy.Field()
    event_source = scrapy.Field()

    START_TIME = scrapy.Field()
    start_time = scrapy.Field()

    END_TIME = scrapy.Field()
    end_time = scrapy.Field()

    cycle = scrapy.Field()
    begin_end = scrapy.Field()


    is_sure = scrapy.Field()
    speed = scrapy.Field()
    available = scrapy.Field()
    occupy = scrapy.Field()
    weather = scrapy.Field()
    city = scrapy.Field()

    # spider required
    spider_status = scrapy.Field()
    fake_dist = scrapy.Field()
    fake_direction = scrapy.Field()


    # location pairs

    spider_ref = scrapy.Field()
    spider_postdate = scrapy.Field()


