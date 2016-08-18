# -*- coding: utf-8 -*-
import datetime,time
import re
strftime = '2016/6/30  5:20:00'
realtime = time.strptime(strftime,'%Y/%m/%d %H:%M:%S')


text = u'G70线福银高速福州段三明、南平往福州方向K57处（过梅溪收费所9公里）发生交通事故，占用主车道，该路段目前单车道通行，请途经车辆谨慎驾驶，提前减速。'


t0 = re.split(u'线',text)[0]
t1 = re.split(u'线',text)[-1]
t1_1 = re.split(u'高速',t1)[0]

print t0 + u'|' + t1_1 + u'高速'


