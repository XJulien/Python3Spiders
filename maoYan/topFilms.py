#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author Julien
@date 2017-05-26
'''

from urllib import request
import re

def getPageIndex(offset=0):
    url = 'http://maoyan.com/board/4?offset='+ str(offset)
    with request.urlopen(url) as r:
        data = r.read()
        if r.status == 200:
            return data
        else:
            return None

def getContent(html):
    setRe = re.compile(r'<dd>.*?board-index-(\d{1,3})">.*?title="(.*?)".*?主演：(.*?)</p>.*?上映时间：(.*?)</p>.*?<i class="integer">(\d.)</i><i class="fraction">(\d)</i>.*?</dd>', re.S)
    items = setRe.findall(html.decode('utf-8'))
    for item in items:
        yield {
            'index':item[0],
            'name':item[1],
            'actors':item[2].strip().split(','),
            'time':item[3],
            'score':item[4]+str(item[5])
        }

def main():
    for i in list(i for i in range(100) if i%10==0):
        html = getPageIndex(i)
        for item in getContent(html):
            print(item)

if __name__ == '__main__':
    main()