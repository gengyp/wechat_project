# coding:utf-8
from __future__ import print_function
import requests
import pymysql,json,time
from weiwenwx import get_ip_port
import numpy as np
from wechat_spider import wechatSpider
my_api = wechatSpider()

def get_links():
  links = []
  connect = pymysql.connect(host='192.168.36.38',user='root',passwd='123456',db='wechat',charset='utf8')
  cursor = connect.cursor()
  sql = 'select url from wechat_content where read_num=0'
  # sql = 'select url,read_num from wechat_content where id = 3302'
  cursor.execute(sql)
  connect.commit()
  values = cursor.fetchall() # tuple's tuple
  for v in values:
    if 'http' not in v[0]:
      a = 'http:' + v[0]
      links.append(a)
    else:
      links.append(v[0])
  cursor.close()
  connect.close()
  return links

def update_num(link):
  # link = 'http://mp.weixin.qq.com/s?__biz=MjM5ODgwODY2MA==&mid=2736788380&idx=4&sn=8d4ed88c07c3519e80b8b7fe361df0ba&scene=0#wechat_redirect'
  payload = "{\"url\":\"" + link + "\"}"
  ip_port = np.random.choice(ip_ports)
  print(ip_port)
  # r = requests.request("POST", url, data=payload, headers=headers)
  r = requests.request("POST", url, data=payload, headers=headers,proxies={'https':'http://' + ip_port})
  print('current request url:',r.request.url,r.status_code)
  try:
    info = json.loads(r.text)['data']['appmsgstat']
    print(info)
    read_num = info['read_num']
    like_num = info['like_num']

    connect = pymysql.connect(host='192.168.36.38',user='root',passwd='123456',db='wechat',charset='utf8')
    cursor = connect.cursor()
    sql = 'update wechat_content set read_num="{}",like_num="{}" where url="{}"'.format(read_num,like_num,link)
    # print(sql)
    cursor.execute(sql)
    connect.commit()
  except:
    print(link,'\n','数据不完整：',r.text)
    return

def test_one():
  url = "http://101.132.66.174:3000/crawl/getReadAndLike"

  link = 'http://mp.weixin.qq.com/s?__biz=MjM5ODgwODY2MA==&mid=2736788380&idx=4&sn=8d4ed88c07c3519e80b8b7fe361df0ba&scene=0#wechat_redirect'
  # link = 'http://mp.weixin.qq.com/s?__biz=MjI3Njc0NTk4MQ==&mid=2649919710&idx=5&sn=67ac79557889f42a43ebcd499f057b18&scene=0#wechat_redirect'
  payload = "{\"url\":\"" + link + "\"}"
  print(payload)
  headers = {
      'content-type': "application/json",
      'cache-control': "no-cache",
      'postman-token': "5bce0a68-8c13-774c-33e4-3f5071f96f2c"
      }

  response = requests.request("POST", url, data=payload, headers=headers)

  print(response.text)

if __name__ == '__main__':
  ip_ports = my_api.get_ip_port()
  url = "http://101.132.66.174:3000/crawl/getReadAndLike"
  headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "5bce0a68-8c13-774c-33e4-3f5071f96f2c"
    }
  links = get_links()
  print('waite update link num:',len(links))
  for i,link in enumerate(links):
    print('\n**current degree:',i,len(links))
    update_num(link)
    time.sleep(2)







