# -*- coding: utf-8 -*-
from pandas import *
from scrapy.spiders import Spider
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\output\jsHWApp_2016-08-22_16-04.csv
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\output\fjHWApp_2016-08-24_18-48.csv
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\output\fjHWApp_2016-08-25_10-06.csv
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\output\bjevent_2016-08-25_16-22.csv
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\output\fjHWApp_2016-08-30_10-16.csv
df0 = read_csv("output/bjevent_2016-09-01_10-12.csv",index_col='spider_oid')
df1= read_csv("input_join/input_history_bj.csv",index_col='spider_oid')

result = df0.join(df1,how='left')
#todo: history left join with data source, search spider_oid is null
temp = df1.join(df0,how='left',lsuffix='_left',rsuffix='_right')
offdata = temp[isnull(temp.loc_name) & isnull(temp.deleted) & isnull(temp.ref_point)]
manualrevert = pandas.DataFrame({'EVENT_TO_REMOVE':offdata['eventid']})
manualrevert.to_csv('input_join/offdata_bj.csv',sep=",",line_terminator='\n')

finalresult = result[isnull(result.eventid)]
manualinput = finalresult[finalresult.ref_point == u"-1,-1"] # need to manualinput -1,-1


#remove duplicates and then export manual input records
print manualinput['loc_name']
finalresult.to_csv('input_join/joinresult_bj.csv',sep=",",line_terminator='\n')

transposed = finalresult.T
transposed.to_csv('input_join/joinresultT_bj.csv',sep=",",line_terminator='\n')

class AdvancedParser(object):
    '''
        Attributes：-
        based on which spider
        _history                     -file          recorded data @social-navi platform #properties relied on spidername
        _link_infos                  -file          result csv converted from tools,
        current_path                 -str           processing path

        Method: - Properties
        export_overdue_rows          -file          return csv file
        setParser                    -obj           return attributes, define the parser
        export_manualinput_rows      -file          return rows that coordinates  == [-1,-1] that need to manually
        combine_linkinfo_file        -file          combine linkinfo with current spider result
    '''
    def __init__(self):
        self._history = 1
        pass

    def setParser(self,spider):
        return self._history
    def export_overdue_rows(self,file):
        pass
    def export_manualinput_rows(self,file):
        pass

    def combine_linkinfo(self,file):
        pass

