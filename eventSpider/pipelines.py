# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime, time
from scrapy import signals
from scrapy.exporters import CsvItemExporter


class CSVPipeline(object):
    def __init__(self):
        self.files = {}

    # TODO add logic,if start_time is null, fill them with postdate
    # Rules - switchers
    def from_spider_to_fields(self, spider):
        public_fields = [
            #self-generated field for filtering items;
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
         ]


        switcher = {
            'bjevent': public_fields,
            'bjevent2': public_fields,
            'zjHWApp': public_fields,
            'jsHWApp': public_fields,
            'fjHWApp': public_fields,
            'chqevent1':public_fields,
            'lnHWlz':public_fields,
            'chq_roadwork':public_fields,
            'shdHWApp':public_fields,
            'shHWApp':public_fields

        }

        return switcher.get(spider.name, 'NONE')

    def convert_timestamp(self,strdatetime):
        if not strdatetime:
            return None
        return int(time.mktime(strdatetime)) * 1000

    def check_status(self, item):
        from datetime import datetime
        td = datetime.today()
        sdate = min(item['start_time'], item['spider_postdate'])
        enddate = item['end_time']
        dt2 = datetime.strptime(sdate, '%Y-%m-%d %H:%M')
        dt3 = datetime.strptime(enddate, '%Y-%m-%d %H:%M')

        if (dt2 < td and dt3 > td):
            return 'ACTIVE'
        return 'OVERDUE'

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        # for all spiders
        dt = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        file = open('%s.csv' % (spider.name + '_' + dt), 'w+b')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file)

        self.exporter.fields_to_export = self.from_spider_to_fields(spider)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()
        #attension{ working directory - output
        import ExportOptions as eo

        _next = raw_input("Delta input ? Y/N")
        _purgefile = eo.delta_input(file.name, _next, _spider = spider.name)
        _filename = _purgefile.name if _purgefile else file.name

        from scrapy import log
        log.logger.info("Processing: Remove fields for link info calculating")
        eo.export_linkinfo_in_file(_filename)
        _next = raw_input("Next: exporting manual input rcrds? Y/N")
        eo.export_manualinput_rows(file.name,_next)


    def process_item(self, item, spider):

        item['ref_point'] = u"-1,-1" if item['ref_point'].upper().find(u'NULL') > -1 else item['ref_point']
        if spider.name in [ 'bjevent','fjHWApp','lnHWlz','jsHWApp','shHWApp','zjHWApp',
                        'shdHWApp']:
            item['start_time'] = self.convert_timestamp(item['start_time']) if item['START_TIME'] else None
            item['end_time'] = self.convert_timestamp(item['end_time']) if item['END_TIME'] else u'0'

        item['is_sure'] = u'0' if not item['END_TIME'] else u'1'
        self.exporter.export_item(item)
        return item