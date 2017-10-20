#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
from urllib import request
import csv
import types

provincedict={}
with open('province_name.txt', 'r') as f:
	for line in f.readlines():
		provincedict[line.split()[0]]=line.split()[1]

with open('boring.csv', 'r') as fread:
	boring = csv.reader(fread)
	with open('excited','w') as fwrite:
		for line in boring:
			if line[0]=='ID':
				fwrite.write('%s,Province\n'%(line[0]))
			else:
				with request.urlopen('http://api.map.baidu.com/geocoder?output=json&location=%s,%s&key=37492c0ee6f924cb5e934fa08c6b1676'%(line[1],line[2])) as f:
					data=json.loads(f.read())
					province=data['result']['addressComponent']['province']
					if province=='':
						province='其他'
					province_EN=provincedict[province]
					fwrite.write('%s,%s\n'%(line[0],province_EN))

