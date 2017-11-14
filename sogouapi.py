# coding:utf-8
from __future__ import print_function
import requests
import bs4, os
import pandas as pd
import time
import wechatsogou
import pymongo, pymysql
import re, time, random
import requests,json
from bs4 import BeautifulSoup
import numpy as np
from wechat_spider import wechatSpider
my_api = wechatSpider()

client = pymongo.MongoClient(host='localhost', port=27017)
wechat = client['wechat']  # database
user_info = wechat['wechat_user_info']  # user info table
sogou_article = wechat['sogou_article']

weixiaobao_user_info = wechat['weixiaobao_user_info']
weixiaobao_article = wechat['weixiaobao_article']

'''
通过 sougouwechat 采集微信公众号账户信息
wechat_id 见 本地 wechat_id.txt
'''
ip_ports = my_api.get_ip_port()
print(ip_ports[:20])
proxies={
    "http": "60.184.42.174:808",
    "https": "119.29.194.168:8080",
}
def get_history_article(name_lst):
  for i,wechat_id in enumerate(name_lst):
    # if i < 16:continue
    print('\ncurrent wechat_id is {1},{0}th,total gzh:{2}'.format(i+1,wechat_id,len(name_lst)))
    ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3)
    # ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3,proxies=proxies)
    try:
      articles = ws_api.get_gzh_article_by_history(wechat_id)['article']
      for dt in articles:
        print(dt['title'])
        sogou_article.update_one({'title':dt['title']},{"$set":dt},upsert=True)
    except:
      print('articles:',wechat_id)
    time.sleep(3)
      # print(dt)

if __name__ =='__main__':
  name_lst = my_api.get_wx_id()
  get_history_article(name_lst)

