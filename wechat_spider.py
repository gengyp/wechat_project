# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author GengYanpeng
@software:PyCharm Community Edition
@time:2017/10/21 10:42
"""
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

client = pymongo.MongoClient(host='localhost', port=27017)
wechat = client['wechat']  # database
user_info = wechat['wechat_user_info']  # user info table
sogou_article = wechat['sogou_article']

weixiaobao_user_info = wechat['weixiaobao_user_info']
weixiaobao_article = wechat['weixiaobao_article']

class wechatSpider(object):
  """爬取微信文章
  本文分别从四个网址对微信文章进行爬取
  1。新榜微信包含：7天热门和最新发布 各10篇,用于每天更新
  包含：url,likeCount,pubulictime,order,click,title,summary
  需要加入 wechat_id
  2。清博微信
  3。搜狗微信
  4。微小宝微信

  考虑到后续更新增加如下函数：
  1.返回爬取微信文章的id
  2.返回数据库中可用代理ip_ports
  2.代理请求网址的函数 get post 请求
  3.更新未插入 user_info、weixiaobao_user_info 的 gzh

  """
  def __init__(self):
    # super(ClassName, self).__init__()
    # self.arg = arg
    # self.ip_ports =
    global  ip_ports
    ip_ports = self.get_ip_port()
    pass

  def get_wx_id(self):
    # 返回未插入数据库的信息
    name_lst = []
    with open('wechat_id.txt', 'r') as f:
      for line in f.readlines():
        # print(line.strip())
        name_lst.append(line.strip())
    return set(name_lst)

  def get_ip_port(self):
    ip_list = []
    try:
      import pymysql
      connect = pymysql.connect(host='localhost', user='root', password='root', database='scraping')
      cursor = connect.cursor()
      cursor.execute('SELECT content FROM %s where score>5' % 'valid_ip')
      result = cursor.fetchall()
      for i in result:
        ip_list.append(i[0])
      return ip_list
    except:
      print('不能读取数据库 proxy！')
      return
    finally:
      cursor.close()
      connect.close()

  def getHtml(self, url, header, querystring):
    try:
      # querystring = {"field":"article_nonTop"}
      # print(ip_ports)
      ip_port = np.random.choice(ip_ports)
      # print(ip_port)
      r = requests.get(url, headers=header, params=querystring, proxies={'proxy': 'http://' + ip_port})
      # r = requests.get(url, headers=header, params=querystring)
      print('request url:', r.status_code, r.request.url)
      time.sleep(2)
      r.encoding = r.apparent_encoding
      return r.text
    except:
      print('request failed!')
      return

  def postJson(self, url, header, payload):
    try:
      # payload = {"field":"article_nonTop"}
      ip_port = np.random.choice(ip_ports)
      r = requests.post(url,headers=header,data=payload,proxies={'proxy':'http://' + ip_port})
      # r = requests.post(url, headers=header, data=payload)
      time.sleep(2)
      return r.text
    except:
      print('post failed!')
      return

  def get_usr_info(self, name_lst):
    # 根据公众号列表 和 wechatsogou api，爬取公众号信息入库
    exist_name = []
    for a in user_info.find():
      exist_name.append(a['wechat_id'])
    name_lst = name_lst - set(exist_name)
    print('add new user info start...', len(name_lst))
    ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3)
    for i, gzh in enumerate(name_lst):
      try:
        dt = ws_api.get_gzh_info(gzh)
        print('insert gzh info:', gzh,dt)
        user_info.update_one({"wechat_id": gzh}, {"$set": dt}, upsert=True)
        time.sleep(3)
      except:
        print('gzh info insert error!', gzh)
    self.update_qr(self.get_wx_id())

  def get_weixiaobao_wxinfo(self, name_lst):
    print('更新微小宝 gzh 信息...', len(name_lst))
    exist_name = []
    for a in weixiaobao_user_info.find():
      exist_name.append(a['wx_alias'])
    name_lst = name_lst - set(exist_name)
    print('更新微小宝 gzh 信息...', len(name_lst))

    # gzh = 'shuobo100'
    url = 'http://data.wxb.com/search'

    for gzh in name_lst:
      try:
        header_info = {'Accept': 'application/json, text/plain, */*',
                       'Accept-Encoding': 'gzip, deflate',
                       'Accept-Language': 'zh-CN,zh;q=0.8',
                       'Cache-Control': 'no-cache',
                       'Connection': 'keep-alive',
                       'Cookie': 'visit-wxb-id=170b7985e4f37dd203136480744c1edd; PHPSESSID=otd52jeo90n0jivm41u4vhtjk0; IESESSION=alive; pgv_pvi=9513126912; pgv_si=s2795355136; tencentSig=3565446144; 6aHW_e4af_saltkey=WJkkh8O3; 6aHW_e4af_lastvisit=1508461949; 6aHW_e4af_sid=pILudb; 6aHW_e4af_lastact=1508465549%09uc.php%09; 6aHW_e4af_auth=972dQGI6XKM2dMX2bEcu9ePMd0Ntz2pf2Sj5WfcS083I8sDTOj%2F5JfO71PPbc4pckoImYrWioyq8Wl0Erlo%2Fa1hcG74; _qddamta_4009981236=3-0; wxb_fp_id=360706689; Hm_lvt_5859c7e2fd49a1739a0b0f5a28532d91=1508221733,1508465501,1508480184,1508480196; Hm_lpvt_5859c7e2fd49a1739a0b0f5a28532d91=1508557541; _qddaz=QD.krd8tb.6sy7p6.j8v8a16m; _qdda=3-1.1; _qddab=3-hqx9fq.j90s6udk; _qddac=3-2-1.1.hqx9fq.j90s6udk',
                       'Host': 'data.wxb.com',
                       'Pragma': 'no-cache',
                       'Referer': 'http://data.wxb.com/searchResult?kw=' + gzh,
                       'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                       'X-Requested-With': 'XMLHttpRequest'}
        querystring = {"page": "1", "page_size": "10", "kw": gzh, "category_id": "", "start_rank": "*", "end_rank": "*",
                       "fans_min": "", "fans_max": "", "sort": "", "is_verify": "0", "is_original": "0",
                       "is_continuous": "0"}
        # r = requests.get(url, headers=header_info, params=querystring)
        # dt = json.loads(r.text)['data'][0]
        html = self.getHtml(url,header_info,querystring)
        dt = json.loads(html)['data'][0]
        print('current update info:', gzh,dt)
        weixiaobao_user_info.update_one({"wx_alias": gzh}, {"$set": dt}, upsert=True)
      except:
        print('没有收录该 gzh!', gzh)
        continue

  def update_qr(self,name_lst):
    # 用下面链接更新 user_info 搜狗微信二维码
    # http://open.weixin.qq.com/qr/code/?username=zhanhao668
    print('Update wechat qrcode...')
    for gzh in name_lst:
      try:
        dt = {"qrcode":'http://open.weixin.qq.com/qr/code/?username='+gzh}
        # print(dt)
        user_info.update_one({"wechat_id":gzh},{"$set":dt},upsert=True)
      except:
        print(gzh)

if __name__=='__main__':
  # step1 初始化用户信息（只需运行一次）
  # 用户信息表的完善
  my_api = wechatSpider()
  names = my_api.get_wx_id()
  print(names, len(names))
  # my_api.get_usr_info(names)
  my_api.update_qr(names)
  # my_api.get_weixiaobao_wxinfo(names)
  # my_api.getHtml('http://www.baidu.com',header=None,querystring=None)