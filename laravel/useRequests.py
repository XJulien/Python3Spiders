#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author Julien
@date 2017-05-31
'''
import requests
import re

def getXsrf():
    '''
    获取xsrf_token
    :return: token
    '''
    r = session.get(LOGIN_URL, headers=headers)
    setRe = re.compile('<meta name="csrf-token" content="(.*?)">')
    return setRe.search(r.text).group(1)

def main():
    '''
    登陆
    :return:
    '''
    postData = {
        '_token': getXsrf(),
        'email': '*******',
        'password': '**********',
        'remember': 'on',
    }
    t = session.post(LOGIN_URL, data=postData, headers=headers)
    #print(t.text)
    print('登陆成功')


if __name__ == '__main__':
    session = requests.session()
    LOGIN_URL = 'https://your.host.name/login'
    AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'
    headers = {
        "Host": "your.host.name",
        'User-Agent': AGENT
    }
    main()