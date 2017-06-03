#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author Julien
@date 2017-05-31
'''
import requests
import re
from multiprocessing import Pool, Manager
import json
import gc
import os

#{{需要修改}} 抓取目标名称 如 xxx.tumblr.com中的 'xxx'
NAME = ''

#{{无需修改}
URL = 'https://'+ NAME +'.tumblr.com/'

#{{需要修改}} 这儿使用代理翻墙  代理无法使用的话则完全无法使用
proxies = {
    'http': 'http://127.0.0.1:1080',
    'https': 'http://127.0.0.1:1080'
}
#{{按需修改}} 设置抓取帖子点赞数限制  低于点赞数的不会抓取
setLimit = 1000

def getPageNum():
    '''
    获取抓取目标总页数
    :return: int(pages)
    '''
    r = requests.get(URL, proxies=proxies)
    setRe = re.compile(r'data-total-pages="(\d*?)">')
    result = setRe.search(r.text)
    if result == None :
        return None
    else:
        return int(result.group(1))

def getData(page, data):
    '''
    多线程抓取每个page的内容, 并使用Manger进行数据共享
    :param page: 页数
    :param data: 用于进行进程间通信
    :return: 返回抓取成功或失败
    '''
    targetUrl = URL + 'page/'+ str(page)
    print('正在抓取'+ targetUrl )
    r = requests.get(targetUrl, proxies=proxies)
    setRe = re.compile(r'<article class="(.*?)not-page post-(\d*?) ".*?post-notes">(.*?) ', re.S)
    result = setRe.findall(r.text)
    if result:
        data.extend(list(result))
        print(targetUrl + ' 抓取成功')
        return True
    else:
        print(targetUrl + ' 抓取失败')
        return False

def getPhoto(data):
    path = NAME + '/photos'
    if not os.path.exists(path):
        os.mkdir(path)
    r = requests.get(data['url'], proxies=proxies)
    setRe = re.compile(r'''type="application/ld\+json">(.*?)</script>''', re.S)
    result = setRe.search(r.text)
    if result:
        image =  json.loads(result.group(1).strip())['image']
        imageArr = image.split('/')
        if not os.path.exists(path + '/' + imageArr[-1]):
            ir = requests.get(image, proxies=proxies)
            if ir.status_code == 200:
                open(path + '/' + imageArr[-1], 'wb').write(ir.content)
        return  image
    else:
        return None

def getPhotoSet(data):
    path = NAME + '/photos'
    if not os.path.exists(path):
        os.mkdir(path)
    r = requests.get(data['url'], proxies=proxies)
    setRe = re.compile(r'''type="application/ld\+json">(.*?)</script>''', re.S)
    result = setRe.search(r.text)
    if result:
        images = json.loads(result.group(1).strip())['image']['@list']
        for image in images:
            imageArr = image.split('/')
            if not os.path.exists(path + '/' + imageArr[-1]):
                ir = requests.get(image, proxies=proxies)
                if ir.status_code == 200:
                    open(path + '/' + imageArr[-1], 'wb').write(ir.content)
        return images
    else:
        return None

def getVideo(data):
    path = NAME + '/videos'
    if not os.path.exists(path):
        os.mkdir(path)
    r = requests.get(data['url'], proxies=proxies)
    setRe = re.compile(r'''<meta property="og:image".*?/tumblr_(.*?)_''', re.S)
    result = setRe.search(r.text)
    if result:
        video = 'https://vtt.tumblr.com/tumblr_' + result.group(1) + '.mp4'
        videoArr = video.split('/')
        if not os.path.exists(path + '/' + videoArr[-1]):
            print('开始下载' + video)
            ir = requests.get(video, proxies=proxies)
            if ir.status_code == 200:
                open(path + '/' + videoArr[-1], 'wb').write(ir.content)
        return video
    else:
        return None

def getContent(data):
    if data['type'] == 'photo':
        data['source'] = getPhoto(data)
        print(data)
    elif data['type'] == 'photoset':
        data['source'] = getPhotoSet(data)
        print(data)
    elif data['type'] == 'video':
        data['source'] = getVideo(data)
        print(data)
    else:
        return None

def useMap(li):
    liData = list(li)
    return {
        'type': liData[0].replace('reblogged', '').strip(),
        'url': URL + 'post/' + liData[1],
        'post': liData[1],
        'notes': int(liData[2].replace(',', ''))
    }

def useFilter(li):
    return li['notes'] > setLimit

def useSorted(li):
    return li['notes']

def main():
    pages = getPageNum()
    print('已获取总页数: ' + str(pages))
    p = Pool()
    data = Manager().list()
    for page in range(1, pages+1):
        p.apply_async(getData, args=(page, data))
    p.close()
    p.join()
    targetData = sorted(filter(useFilter, map(useMap, data)), key = useSorted, reverse = True)
    print('已获得总数据, 现在开始下载')
    del data
    gc.collect()
    print(list(targetData))
    p = Pool()
    for data in targetData:
        p.apply_async(getContent, args=(data,))
    p.close()
    p.join()

if __name__ == '__main__':
    if not os.path.exists(NAME):
        os.mkdir(NAME)
    main()

