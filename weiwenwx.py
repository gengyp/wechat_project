# -*- coding:utf-8 -*-
from __future__ import print_function
import requests
import time,json
import numpy as np
from bs4 import BeautifulSoup
import bs4,re
import pandas as pd
import pymysql
connect = pymysql.connect(host='localhost',user='root',passwd='root',db='wechat',charset='utf8')
cursor = connect.cursor()
'''
说明：爬取微问微信文章
step1 爬取 top article，notop article，hot article
step2 爬取历史文章
'''
header2 = {
  'upgrade-insecure-requests': "1",
  'x-devtools-emulate-network-conditions-client-id': "36f14718-5727-402b-b741-9895d98840c0",
  'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
  'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
  'accept-encoding': "gzip, deflate",
  'accept-language': "zh-CN,zh;q=0.8",
  'cookie': "UM_distinctid=15e3720fe41652-0995d78db0f18-e313761-1fa400-15e3720fe42d89; Hm_lvt_8875c662941dbf07e39c556c8d97615f=1504177103; Hm_lpvt_8875c662941dbf07e39c556c8d97615f=1504177103; XSRF-TOKEN=eyJpdiI6Iis0VGhNYVI1UDMrT0Q5TTRneER1dXc9PSIsInZhbHVlIjoiVGNtRTZVYytCQ3dKWmp0RGpqcUhjVW9wWDVaUHBrODE4elBaTmJWYjIzR2NSRFwvRFA0SnZFc2RhbDg5QTA5eVBuN3gyNkFHZkw3b2lUdWhhUzZnbnlBPT0iLCJtYWMiOiI2MGViOTNjMjE0YzcyZTYzNTFiNzU1MGQ4ODYyNTFlNjgyMjcxYTA4NTY1NmI1ZDRiNTI3Yjk5OWMwZWMyYzhjIn0%3D; wewen=eyJpdiI6ImYwWnZmZnQ0bGF4NjBZMUVrYWlDbWc9PSIsInZhbHVlIjoiM3BOb0tHTWRRWGxMUUhFQWhGZ3M2dUpiZlZrUGluUEVpTzJPRW9uMFdaa2F4WUp2UjlZQVlEZUtiaGhkb2sySm5YeGUyVmd2VnR2akRQWUxYNUQ3dXc9PSIsIm1hYyI6ImFiYjAwNTg5YjQxODdmOGVjYTc3N2M5ZjY4Mjg3ZGU4ZTViYjg4YTc4NzM0ZWE4ZmZlZDRhOWEwZmU2N2JhYmYifQ%3D%3D; XSRF-TOKEN=eyJpdiI6ImtrK3FQZUFRUlc2MnNyQmxzckkweXc9PSIsInZhbHVlIjoiQWFyQk5GZkpmZEJtXC84Vnd1UXBZa0YrOGxcL2FHaVVicng2WTJLQUNOTlVSVFltYkMzZzNHOG9EQmF1XC9lRmczK2hGOGJRa2Nrc0pRTnJZTlhQV2QrK3c9PSIsIm1hYyI6IjFiOThkODY0ODQ3OTkzNDUxMzE3OGY5YTU0NzA1ZmNjYjYzZGU1NWQ5NTgwODBiZDEzMDEzOGMwMWE2MmQ1OTUifQ%3D%3D; wewen=eyJpdiI6Ik5hRUlQOVQ1VDBaaGZOOG1icFdXb3c9PSIsInZhbHVlIjoiTXlURGtkV3dkczVDNWNnTFBORGV5ZFFiWFRjZTFWREJCVzR1UmZBOXAzMGZicVVmdDBXcnZPNGNIV3NEVVIzVzF5Q1VMWkMxeCtsdGV4OHRvWTlFWWc9PSIsIm1hYyI6IjA2MDVhY2Q2OTEwMGRlNGQwOTZkNTliNTIzZDNhMDJhNzgyOTk1MzE1ODc1MjI0ZDg1Y2JhZDE4YWMxMzlhNWEifQ%3D%3D; CNZZDATA1260153014=317139307-1504159176-http%253A%252F%252Fwewen.io%252F%7C1504175424; Hm_lvt_5922d8d0079ee4675955290a48124be8=1504163463; Hm_lpvt_5922d8d0079ee4675955290a48124be8=1504179286",
  'cache-control': "no-cache",
  }

url2 = "http://news.wewen.io/"

def get_ip_port():
  ip_list = []
  try:
    import pymysql
    connect = pymysql.connect(host='localhost',user='root',password='root',database='scraping')
    cursor = connect.cursor()
    cursor.execute('SELECT content FROM %s where test_times>2' % 'valid_ip')
    result = cursor.fetchall()
    for i in result:
        ip_list.append(i[0])
    if len(ip_list) == 0:
        return
    return ip_list
  except:
    print('不能读取数据库 proxy！')
    return
  finally:
    cursor.close()
    connect.close()

ip_ports = get_ip_port()



def get_history_article():
  # step1 get page number
  wxgzh = "shuobo100"
  querystring = {"author":wxgzh}
  html = getHtml(url2,header2,querystring)
  soup = BeautifulSoup(html,'lxml')
  tail_url = soup.select('#_framework > div.ui.container.main > div > div > div > \
    div.ui.pagination.green.menu > a:nth-of-type(7)')[0]['href']
  total_page = eval(re.search(r'page=(\d{1,3})',tail_url).group(1))
  print('current spider gzh is:{},total pages:{}'.format(wxgzh,total_page))

  # step2 spider every page article info
  for page_num in range(total_page):
    lst = []
    querystring = {"author":wxgzh,"page":str(page_num+1)}
    html = getHtml(url2,header2,querystring)
    soup = BeautifulSoup(html,'lxml')
    divs = soup.select('#_framework > div.ui.container.main > div > div > div > div.ui.very.relaxed.divided.unstackable.items')[0]('div',{'class':'item'})
    for div in divs:
      try:
        # 分别获取文章、封面、摘要、点赞、阅读、标题信息
        content_url = div.a['href']
        cover = div.img['data-original']
        digest = div.select('div > div.description > p')[0].text.strip()
        num_text = div.select('div > div.extra > div')[0].text.replace(' ','')
        like_num = re.findall(r'.*?(\d+)',num_text)[0]
        read_num = re.findall(r'.*?(\d+)',num_text)[1]
        title = div.select('div > a')[0].text.strip()
        print([content_url,cover,digest,like_num,read_num,title])
        # sql = 'insert into weiwen_article(title,digest,likenum,readnum,cover,contenturl) values("{}","{}","{}","{}","{}","{}")'.format(title,digest,like_num,read_num,cover,content_url)
        # print(sql)
        # cursor.execute(sql)
        # connect.commit()
        # lst.append([content_url,cover,digest,like_num,read_num,title])
        # print([content_url,cover,digest,like_num,read_num,title])
      except:
        print('插入食物')
        pass


def main():
  try:
    get_history_article()
    # pd.DataFrame(lst).to_csv('123.csv',encoding='utf-8')
    # for row in lst:
    #   print(row)
  except:
    pass
  finally:
    cursor.close()
    connect.close()

if __name__ == '__main__':
  main()



# # 以下分别为头条、非头条、热门文章，考虑到历史文章有包含故不爬取

# header1 = {
#   'accept': "*/*",
#   'x-devtools-emulate-network-conditions-client-id': "36f14718-5727-402b-b741-9895d98840c0",
#   'x-csrf-token': "h0yko0SDt601MfgpEO0aUvUrIbxzVpqc5P2bwRr4",
#   'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
#   'x-requested-with': "XMLHttpRequest",
#   'referer': "http://wewen.io/analysis/rmrbwx",
#   'accept-encoding': "gzip, deflate",
#   'accept-language': "zh-CN,zh;q=0.8",
#   'cookie': "UM_distinctid=15e3720fe41652-0995d78db0f18-e313761-1fa400-15e3720fe42d89; CNZZDATA1260153014=482187331-1504159176-null%7C1504175424; Hm_lvt_5922d8d0079ee4675955290a48124be8=1504163463; Hm_lpvt_5922d8d0079ee4675955290a48124be8=1504179171; XSRF-TOKEN=eyJpdiI6ImNBNzZYV085bEZcL1wvMEp6TXdDTlplZz09IiwidmFsdWUiOiIrYno0NUxlMjJ0ZDdCUWo5eTBYV1dZS0xkTHVIZTQxSFwvNHBXSTdOQnhGNzV4YU41Q25rejBGMkw1RnZSaFVpRE5jVHplWEsxSUFiT2w4TERyVGxVTEE9PSIsIm1hYyI6IjQzZDFhNmNmNzExYWEzNTI5YzI3OWQ5OThlMDc5YWJjM2EyNDUyZmYzMjdkNjE0ZmE1ZDFjNTQzZmMzMzZkYTEifQ%3D%3D; wewen=eyJpdiI6IkgzVXNpMXI0VnJ2SXJDeEpMRzVlT2c9PSIsInZhbHVlIjoieFI1RlwvaEE3YjluMFd0b3d0TTFSYjl2QXBzZFc2a0NFYjg2QUNJVFFCMnJ5eEt1ZzZGOUJIYTJ1b3BHOFZiTlJjXC9qeVdtME9HRG50K0p3VEdFU0VGdz09IiwibWFjIjoiMzJjMDkyMGM3Y2E1MTE0YzIzNzdjNzJjNzY2YWIzNjI4MDBhMDFlZDc1Yzk5MGMyNGFkNTliNzUxOWYzY2IzYyJ9",
#   'cache-control': "no-cache"
#   }
# url1 = "http://wewen.io/analysis/rmrbwx"

# def get_top_article():
#   lst= []
#   querystring = {"field":"article_top"}
#   html = getHtml(url1,header1,querystring)
#   for dt in json.loads(html)['data']:
#     lst.append(list(dt.values()))
#     print(dt.values())
#   return list(dt.keys()),lst

# def get_notop_article():
#   lst = []
#   querystring = {"field":"article_nonTop"}
#   html = getHtml(url1,header1,querystring)
#   for dt in json.loads(html)['data']:
#     lst.append(list(dt.values()))
#     print(dt.values())
#   return list(dt.keys()),lst

# def get_hot_article():
#   lst = []
#   querystring = {"field":"article_hot"}
#   html = getHtml(url1,header1,querystring)
#   for dt in json.loads(html)['data']:
#     lst.append(list(dt.values()))
#     print(dt.values())
#   return list(dt.keys()),lst
