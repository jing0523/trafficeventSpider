# -*- coding: utf-8 -*-
from pandas import *
import numpy as num
import numpy

"""
+++++++++++++++++++++++++++++++++++++++用于拼接link匹配结果和其他字段的脚本++++++++++++++++++++++++++++++++++++++++++++++++
"""
# C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\zjHWApp_2016-09-26_13-24.csv
# C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider/output/shdHWApp_2016-09-27_13-54.csv
df1 = read_csv("input_join/shdHWApp_2016-09-29_14-46_linkcalc.csv") # output joinresult
# df0 = read_csv("input_join/zjHWApp_2016-09-26_13-24.csv") # output joinresult
df0= read_csv("output/shdHWApp_2016-09-29_14-46.csv")
df1_a = df1.copy()


temp = pandas.merge(left=df0,right=df1_a,left_on=['spider_oid'],right_on=['id'],suffixes=['_L','_R'])
temp.to_csv("input_join/shdHWApp_2016-09-29_14-46_merge.csv")
export_result = temp.copy()
# export_result = df0.copy()
export_result = export_result.drop(export_result.columns[[0,1,2,3,4,5,6,7,8,9,
                                                          10,11,29,
                                                          30,
                                                          32
                                                          ]],axis=1)
# export_result["link_info"] = export_result.iloc[:33].map(lambda x: x.replace(';',","))


export_result.to_csv("input_join/shdHWApp_2016-09-29_14-46drop.csv") #15 rows 1 file to export

rows_cnt = len(export_result.index)
for i in range(0,rows_cnt +1,15):
    blockrows =  export_result.iloc[i:i+15, ]
    blockrows.to_csv("input_join/shdHWApp_2016-09-29_14-46_p" + str(i/15) +".csv")
 #make selection using iloc [axis=0,axis=1]
