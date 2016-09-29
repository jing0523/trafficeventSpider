# -*- coding: utf-8 -*-


from pandas import *
from scrapy.spiders import Spider
import re
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\output\jsHWApp_2016-08-22_16-04.csv
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\output\fjHWApp_2016-08-24_18-48.csv
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\output\fjHWApp_2016-08-25_10-06.csv
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\output\bjevent_2016-08-25_16-22.csv
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\output\bjevent_2016-09-21_14-30.csv
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\output\fjHWApp_2016-09-21_15-53.csv
"""
+++++++++++++++++++++++++++++++++++++++上传匹配link的脚本++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++没有坐标的,比如浙江，跳过这一步直接合并其他列++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++确定哪些路段需要人工绘制see console++++++++++++++++++++++++++++++++++++++++++++++++

"""
# TODO: export another csv only supports fields for link-calculation; pandas
# finalresult = result[isnull(result.eventid)]
# manualinput = finalresult[finalresult.ref_point == u"-1,-1"] # need to manualinput -1,-1
allrcrs_df = pandas.read_csv("output/fjHWApp_2016-09-22_14-42.csv", index_col='spider_oid')
link_calc_rcrs = pandas.DataFrame({
    'loc_name': allrcrs_df['loc_name'],
    'ref_point': allrcrs_df['ref_point'],
    'ref_point_type': allrcrs_df['ref_point_type'],
    'spider_dist': allrcrs_df['spider_dist'].map(lambda x: '%2.1f' % x),
    'zdirection': allrcrs_df['spider_direction'],
})
link_calc_rcrs.to_csv('input_join/%s.csv' % ("fjHWApp_2016-09-22_14-42" + "_linkcalc"), sep=",", line_terminator='\n')