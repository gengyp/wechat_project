# -*- coding:utf-8 -*-
from __future__ import print_function
import requests
import time,json
import numpy as np
from bs4 import BeautifulSoup
import bs4,re,pymongo
import pandas as pd
from lxml import etree

from wechat_spider import wechatSpider
my_api = wechatSpider()
'''
说明：爬取微小宝微信文章
'''
client = pymongo.MongoClient(host='localhost', port=27017)
wechat = client['wechat']  # database
user_info = wechat['wechat_user_info']  # user info table
sogou_article = wechat['sogou_article']

weixiaobao_user_info = wechat['weixiaobao_user_info']
weixiaobao_article = wechat['weixiaobao_article']

def get_article(gzh):
  # gzh = 'rmrbwx'
  wxb_wxname = weixiaobao_user_info.find_one({'wx_alias':gzh})['wx_origin_id']
  # step1 get total page num
  url = "http://data.wxb.com/details/postRead"
  querystring = {"id":wxb_wxname}
  header1 = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
   'Accept-Encoding':'gzip, deflate',
   'Accept-Language':'zh-CN,zh;q=0.8',
   'Cache-Control':'no-cache',
   'Connection':'keep-alive',
   'Cookie':'wxb_fp_id=360706689; visit-wxb-id=170b7985e4f37dd203136480744c1edd; PHPSESSID=otd52jeo90n0jivm41u4vhtjk0; IESESSION=alive; pgv_pvi=9513126912; pgv_si=s2795355136; tencentSig=3565446144; _qddamta_4009981236=3-0; 6aHW_e4af_saltkey=WJkkh8O3; 6aHW_e4af_lastvisit=1508461949; 6aHW_e4af_sid=pILudb; 6aHW_e4af_lastact=1508465549%09uc.php%09; 6aHW_e4af_auth=972dQGI6XKM2dMX2bEcu9ePMd0Ntz2pf2Sj5WfcS083I8sDTOj%2F5JfO71PPbc4pckoImYrWioyq8Wl0Erlo%2Fa1hcG74; wxb_fp_id=360706689; Hm_lvt_5859c7e2fd49a1739a0b0f5a28532d91=1508221733,1508465501; Hm_lpvt_5859c7e2fd49a1739a0b0f5a28532d91=1508468864; _qddaz=QD.krd8tb.6sy7p6.j8v8a16m; _qdda=3-1.41iu70; _qddab=3-c3y00z.j8z9fa46',
   'Host':'data.wxb.com',
   'Pragma':'no-cache',
   'Referer':'http://data.wxb.com/searchResult?kw='+gzh,
   'Upgrade-Insecure-Requests':'1',
   'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
  html = my_api.getHtml(url,header1,querystring)
  soup = BeautifulSoup(html,'lxml')
  try:
    total_num = eval(soup('ul',{'class':'ant-pagination ant-table-pagination'})[0]('li')[-2].text)
    print('current gzh is:',gzh,total_num)
  except:
    print(gzh,'暂无数据')
    return

  # step2 spider article
  for i in range(total_num):
    url = "http://data.wxb.com/account/statArticles/"+wxb_wxname
    header2 = {'Accept':'application/json, text/plain, */*',
     'Accept-Encoding':'gzip, deflate',
     'Accept-Language':'zh-CN,zh;q=0.8',
     'Cache-Control':'no-cache',
     'Connection':'keep-alive',
     'Cookie':'visit-wxb-id=170b7985e4f37dd203136480744c1edd; PHPSESSID=otd52jeo90n0jivm41u4vhtjk0; IESESSION=alive; pgv_pvi=9513126912; pgv_si=s2795355136; tencentSig=3565446144; 6aHW_e4af_saltkey=WJkkh8O3; 6aHW_e4af_lastvisit=1508461949; 6aHW_e4af_sid=pILudb; 6aHW_e4af_lastact=1508465549%09uc.php%09; 6aHW_e4af_auth=972dQGI6XKM2dMX2bEcu9ePMd0Ntz2pf2Sj5WfcS083I8sDTOj%2F5JfO71PPbc4pckoImYrWioyq8Wl0Erlo%2Fa1hcG74; wxb_fp_id=360706689; _qddamta_4009981236=3-0; Hm_lvt_5859c7e2fd49a1739a0b0f5a28532d91=1508221733,1508465501; Hm_lpvt_5859c7e2fd49a1739a0b0f5a28532d91=1508475318; _qddaz=QD.krd8tb.6sy7p6.j8v8a16m; _qdda=3-1.3fv2dn; _qddab=3-nbmosv.j8zeg3ss',
     'Host':'data.wxb.com',
     'Pragma':'no-cache',
     'Referer':'http://data.wxb.com/details/postRead?id='+wxb_wxname,
     'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
     'X-Requested-With':'XMLHttpRequest'}
    querystring = {"period":"30","page":str(i+1),"sort":""}
    html = my_api.getHtml(url,header2,querystring)
    for dt in json.loads(html)['data']:
      weixiaobao_article.update_one({"url":dt['url']},{"$set":dt},upsert=True)
      # lst.append(list(dt.values()))
      # print(dt)

if __name__ == '__main__':
  name_lst = my_api.get_wx_id()
  print(name_lst)
  # gzh = 'rmrbwx'
  for i,gzh in enumerate(name_lst):
    print('\ncurrent is:',gzh,i+1,len(name_lst))
    try:
      get_article(gzh)
    except:
      print(gzh,'有错误')









