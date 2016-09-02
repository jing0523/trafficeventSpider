# -*- coding: utf-8 -*-
from pandas import *
import numpy as num
# TODO: joinresult 制备工具需要的列：id	名称编号用|分隔	坐标x	坐标y	坐标类型 长度-米	方向
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\input_join\join_fake.csv
#C:\Users\lijing211574\PycharmProjects\eventSpider\eventSpider\output\fjHWApp_2016-08-19_11-20.csv
df0 = read_csv("input_join/fake.csv") # output joinresult
df1= read_csv("input_join/fujian-final-fake.csv")
df1_a = df1.copy()

#福建版本
def formatchanger(x):
    if type(x) is str:
        if x.startswith("1"): #use regex to exchange
            return long(float(x))
        return -1
    return x


df0["_id"] = df0["spider_oid"].astype(int)
df1_a["_id"] = df1_a["id"].apply(formatchanger)
df1_a["_id"] = df1_a["_id"].astype(int)
print df1_a["_id"].head(5)
print df0["_id"].head(5)

temp = df0.merge(df1_a)
temp.to_csv("input_join/temp.csv")
