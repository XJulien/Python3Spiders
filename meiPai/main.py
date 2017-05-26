#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author Julien
@date 2017-05-26
'''

from urllib import request
from urllib.parse import urlencode
import json
import re

def getPageIndex(keyword, offset = 0 ):
    '''
    目标是抓取头条图集, 分析页面发现ajxa调用接口
    GET "http://www.toutiao.com/search_content/?offset=0&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20&cur_tab=3"
    其中keyword为urlencode之后的搜索关键字
    offset为分页 方法默认为0即首页
    curl_tab=3为搜索图集
    :param keyword: urlencode(搜索关键字)
    :param offset: 分页
    :return: 接口搜索内容
    '''
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 3
    }
    url = 'https://www.toutiao.com/search_content/?'+ urlencode(data)
    try:
        with request.urlopen(url) as r:
            data = r.read()
            if r.status == 200:
                return data
            else:
                return  None
    except Exception:
        return None

def getPageUrl(html):
    '''
    解析通过接口获取的json字符串
    通过生成器的方式返回解析到的url
    :param html: 接口获取内容
    :return: 返回解析到的图集url
    '''
    data = json.loads(html.decode('utf-8'))
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield 'http://www.toutiao.com/a'+item.get('group_id')
    else:
        return None

def getAllImages(url):
    '''
    正则匹配, 获取页面内所需要的内容
    :param url: 爬取的页面
    :return: 返回标题+图片集
    '''
    try:
        with request.urlopen(url) as r:
            data = r.read()
            setRe = re.compile('var gallery =(.*?);')
            result = setRe.search(data.decode('utf-8'))
            if result:
                data = json.loads(result.group(1))
                if data and 'sub_images' in data.keys():
                    images = [item.get('url') for item in data.get('sub_images')]
                    #return list({'abstracts':abstracts,'image':image} for abstracts,image in zip(data.get('sub_abstracts'),images))
                    return {
                        'title': data.get('sub_titles')[0],
                        'images': images
                    }
                else:
                    return None
            else:
                return None
    except Exception:
        return None


def main():
    html = getPageIndex('街拍')
    for url in getPageUrl(html):
        print(getAllImages(url))

if __name__ == '__main__':
    main()
