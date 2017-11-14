# -*- coding:utf-8 -*-
from __future__ import print_function
import requests
import time,json
import numpy as np
from bs4 import BeautifulSoup
import bs4,re
import pandas as pd
from lxml import etree
import pymongo

from wechat_spider import wechatSpider

my_api = wechatSpider()
'''
说明：爬取清博微信文章,最近更新的 10 篇，每天定时更新
'''


client = pymongo.MongoClient(host='localhost',port=27017)
wechat = client['wechat'] # database
user_info = wechat['wechat_user_info']  # user info table
qingbo_article = wechat['qingbo_article']

def insert_qingbo_wxname(name_lst):
  exist_name = []
  for info in user_info.find():
    try:
      if info['qbjm_wxname']:
        exist_name.append(info['wechat_id'])
        print(info['wechat_id'],info['qbjm_wxname'])
    except:
      continue
  name_lst = name_lst - set(exist_name)

  print('插入清博加密微信名...', len(name_lst))
  url = 'http://www.gsdata.cn/query/wx'
  for gzh in name_lst:
    try:
      header = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
       'Accept-Encoding':'gzip, deflate',
       'Accept-Language':'zh-CN,zh;q=0.8',
       'Cache-Control':'no-cache',
       'Connection':'keep-alive',
       'Cookie':'acw_tc=AQAAAMpC+HnEyQkAosrhekJB0hTI9iB9; _csrf-frontend=5034a3892055da330dea12e3861d1682ff617e77e51892ac02f9d759346b8b87a%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22_csrf-frontend%22%3Bi%3A1%3Bs%3A32%3A%224BRjqvTgv5FQQTuEw5psd4gBLshSwZHp%22%3B%7D; bdshare_firstime=1506175578484; PHPSESSID=ip3edmkncqe1af7lg98vm9oat7; Hm_lvt_293b2731d4897253b117bb45d9bb7023=1506175573,1508036276,1508342579,1508564236; Hm_lpvt_293b2731d4897253b117bb45d9bb7023=1508565555',
       'Host':'www.gsdata.cn',
       'Pragma':'no-cache',
       'Referer':'http://www.gsdata.cn/',
       'Upgrade-Insecure-Requests':'1',
       'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
      querystring = {'q':gzh}
      html = my_api.getHtml(url,header,querystring)
      jmwxname = re.search(r'wxdetail\?wxname=(.*?)\"',html).group(1)
      print('gzh',gzh,jmwxname)
      user_info.update_one({"wechat_id":gzh},{"$set":{'qbjm_wxname':jmwxname}},upsert=True)
    except:
      print('该没有收录:',gzh)
      user_info.update_one({"wechat_id": gzh}, {"$set": {'qbjm_wxname': ''}}, upsert=True)
      continue

def get_article(name_lst):
  url = "http://www.gsdata.cn/rank/toparc"
  not_exists = []
  for dt in user_info.find():
    try:
      print('* '*20)
      wx = dt['wechat_id']
      wxname = dt['qbjm_wxname']
      print('cur wechat_id is:',wx)
      # querystring = {"wxname":"cQmB1DySYJnqdi4n","wx":"rmrbwx","sort":"-1"}
      headers = {
        'accept': "*/*",
        'origin': "http://www.gsdata.cn",
        'x-devtools-emulate-network-conditions-client-id': "b45f962a-54d6-4328-91f2-d874d0c58470",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        'referer': "http://www.gsdata.cn/rank/wxdetail?wxname="+wxname,
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.8",
        'cookie': "bdshare_firstime=1493023553998; acw_tc=AQAAAPkNWm99MA8AosrheuWGVf5qOd78; _csrf-frontend=fca0b986ab2a5e6b3bf13c04e2d96acf180467b2af27c25e0a6e88beb636f18ca%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22_csrf-frontend%22%3Bi%3A1%3Bs%3A32%3A%22ZGSnjYX7LDWNeENePNa_zIhWxJpSZcF1%22%3B%7D; PHPSESSID=fo2k8ha7trb8pblibu6l7uqcc7; _gsdataCL=WyI4MzIwNSIsIjE3ODI2ODUzMjM2IiwiMjAxNzA5MDExMTA5MTYiLCJiOGE5YWM5ZjQ3YTRhZmJiOTJlZjgzODlmNzU4MjQwNiIsIjUzNzcyIl0%3D; _identity-frontend=fc8fb83572f89d942fa14af4dcc7557dd46e14867bf842cc14f2d0b2de64ce30a%3A2%3A%7Bi%3A0%3Bs%3A18%3A%22_identity-frontend%22%3Bi%3A1%3Bs%3A26%3A%22%5B83205%2C%22test+key%22%2C2592000%5D%22%3B%7D; Hm_lvt_293b2731d4897253b117bb45d9bb7023=1503983279,1504235105; Hm_lpvt_293b2731d4897253b117bb45d9bb7023=1504243890",
        'cache-control': "no-cache"
        # 'postman-token': "4976427c-873e-d814-ee88-a0b67f53fba6"
        }
      querystring = {"wxname":wxname,"wx":wx,"sort":"-1"}
      html = my_api.getHtml(url,headers,querystring)
      for dt in json.loads(html)['data']:
        qingbo_article.update_one({"url":dt['url']},{"$set":dt},upsert=True)
    except:
      print('* * this wechat_id not find article:',wx)
      not_exists.append(wx)
      continue
  print('不存在的 wechat_id:',not_exists,len(not_exists))


if __name__ == '__main__':
  name_lst = my_api.get_wx_id()
  print(name_lst)
  # # step1 更新 清博加密微信名，只需执行一次
  # insert_qingbo_wxname(name_lst)
  # step2 更新文章
  get_article(name_lst)



