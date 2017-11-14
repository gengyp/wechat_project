# -*- coding:utf-8 -*-
from __future__ import print_function
# import requests
import time, json
# import numpy as np
import re, pymongo
# from get_user_info import get_wx_id
# from weiwenwx import get_ip_port,getHtml
from wechat_spider import wechatSpider

my_api = wechatSpider()
'''
说明：爬取 新榜 微信文章

'''

client = pymongo.MongoClient(host='localhost', port=27017)
wechat = client['wechat']  # database
user_info = wechat['wechat_user_info']  # user info table
newrank_article = wechat['newrank_article']

def update_uuid(wechat_ids):
  # update uuid to user_info, exist skip
  exist_name = []
  for info in user_info.find():
    try:
      if info['newrank_uuid']:
        exist_name.append(info['wechat_id'])
        # print(info['wechat_id'],info['newrank_uuid'])
    except:
      continue
  wechat_ids = wechat_ids - set(exist_name)
  print('update uuid start:', len(wechat_ids))

  failed_lst = []
  url = 'http://www.newrank.cn/public/info/detail.html'
  header = {
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'accept-encoding': "gzip, deflate",
    'accept-language': "zh-CN,zh;q=0.8",
    'cookie': "UM_distinctid=15e03041da442b-05e9f950f59012-31627c01-13c680-15e03041da5335; __root_domain_v=.newrank.cn; tt_token=true; openid=oFCwWw27DF7P2XJ_PDF-CjzJB5jM; token=BB3C6FC73FCCE8024CD19906150D0518; _qddamta_2852150610=3-0; CNZZDATA1253878005=663781030-1503284121-http%253A%252F%252Fwww.newrank.cn%252F%7C1508547924; Hm_lvt_a19fd7224d30e3c8a6558dcb38c4beed=1506175376,1508222986,1508297490,1508480210; Hm_lpvt_a19fd7224d30e3c8a6558dcb38c4beed=1508548797; _qddaz=QD.k20y9m.4haxwa.j6lnjseo; _qdda=3-1.3jevv2; _qddab=3-93lcta.j90ls2z0"
    }
  for gzh in wechat_ids:
    # gzh = 'rmrbwx'
    querystring = {'account': gzh}
    try:
      html = my_api.getHtml(url, header, querystring)
      # "uuid":"02D257A6DE7455AA233A8693D85CD3B1"
      uuid = re.search(r'\"uuid\":\"(.*?)\"', html).group(1)
      user_info.update_one({'wechat_id': gzh}, {'$set': {'newrank_uuid': uuid}})
      print('current update {}\'s uuid successed!'.format(gzh))
    except:
      user_info.update_one({'wechat_id': gzh}, {'$set': {'newrank_uuid': None}})
      print('*******failed!*******', gzh)
      failed_lst.append(gzh)
  print('failed_lst', failed_lst)

def get_article(wechat_ids):
  url = "http://www.newrank.cn/xdnphb/detail/getAccountArticle"
  for gzh in wechat_ids:
    try:
      uuid = user_info.find_one({'wechat_id': gzh})['newrank_uuid']
      if uuid is None:
        print('uuid is None',gzh)
        continue
    except:
      print('该gzh不存在！')
      continue

    headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.8',
               'Cache-Control': 'no-cache',
               'Connection': 'keep-alive',
               'Content-Length': '100',
               'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'Cookie': 'UM_distinctid=15e03041da442b-05e9f950f59012-31627c01-13c680-15e03041da5335; __root_domain_v=.newrank.cn; tt_token=true; openid=oFCwWw27DF7P2XJ_PDF-CjzJB5jM; token=BB3C6FC73FCCE8024CD19906150D0518; _qddamta_2852150610=3-0; _qddaz=QD.k20y9m.4haxwa.j6lnjseo; _qdda=3-1.3qikar; _qddab=3-ine5gx.j8zi64vv; CNZZDATA1253878005=663781030-1503284121-http%253A%252F%252Fwww.newrank.cn%252F%7C1508477708; Hm_lvt_a19fd7224d30e3c8a6558dcb38c4beed=1506175376,1508222986,1508297490,1508480210; Hm_lpvt_a19fd7224d30e3c8a6558dcb38c4beed=1508481687; tt_token=true; openid=oFCwWw27DF7P2XJ_PDF-CjzJB5jM; token=BB3C6FC73FCCE8024CD19906150D0518; UM_distinctid=15e03041da442b-05e9f950f59012-31627c01-13c680-15e03041da5335; __root_domain_v=.newrank.cn; tt_token=true; openid=oFCwWw27DF7P2XJ_PDF-CjzJB5jM; token=BB3C6FC73FCCE8024CD19906150D0518; _qddamta_2852150610=3-0; _qddaz=QD.k20y9m.4haxwa.j6lnjseo; _qdda=3-1.3jevv2; _qddab=3-93lcta.j90ls2z0; CNZZDATA1253878005=663781030-1503284121-http%253A%252F%252Fwww.newrank.cn%252F%7C1508542524; Hm_lvt_a19fd7224d30e3c8a6558dcb38c4beed=1506175376,1508222986,1508297490,1508480210; Hm_lpvt_a19fd7224d30e3c8a6558dcb38c4beed=1508546905',
               'Host': 'www.newrank.cn',
               'Origin': 'http://www.newrank.cn',
               'Pragma': 'no-cache',
               'Referer': 'http://www.newrank.cn/public/info/detail.html?account=' + gzh,
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest'
               }
    try:
      payload = {'flag': 'true', 'uuid': uuid}
      html = my_api.postJson(url, headers, payload)
      print('更新新榜最近十条信息...', gzh, uuid)
      for dt in json.loads(html)['value']['lastestArticle']:
        # newrank_article.insert_one(dt)
        dt['wechat_id'] = gzh
        newrank_article.update_one({'url': dt['url']}, {'$set': dt}, upsert=True)
      print('更新新榜热门十条信息...', gzh, uuid)
      for dt in json.loads(html)['value']['topArticle']:
        # newrank_article.insert_one(dt)
        dt['wechat_id'] = gzh
        newrank_article.update_one({'url': dt['url']}, {'$set': dt}, upsert=True)
    except:
      print(gzh)

if __name__ == '__main__':
  wechat_ids = my_api.get_wx_id()
  print(wechat_ids)
  # update_uuid(wechat_ids)
  get_article(wechat_ids)
