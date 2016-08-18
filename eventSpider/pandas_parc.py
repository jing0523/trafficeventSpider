# -*- coding: utf-8 -*-
import pandas as pandas


df0 = pandas.read_csv("output/fjHWApp_2016-08-17_13-51.csv",index_col='spider_oid')
df1= pandas.read_csv("input/input_history.csv",index_col='spider_oid')

result = df0.join(df1,how='left')

finalresult = result[pandas.isnull(result.eventid)]

manualinput = finalresult[finalresult.ref_point == u"-1 ,-1"] # need to manualinput
print manualinput['loc_name']
finalresult.to_csv('input/joinresult.csv',sep=",",line_terminator='\n')

transposed = finalresult.T
transposed.to_csv('input/joinresultT.csv',sep=",",line_terminator='\n')