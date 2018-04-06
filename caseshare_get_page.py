# coding:utf8

import time
import datetime
import requests
import threading
import os
import traceback
import random

from fake_useragent import UserAgent
from requests import Request
from bs4 import BeautifulSoup
from spider.case_share.crawl_case_share_tbl import CrawlCaseShare
from selenium import webdriver
from pyvirtualdisplay import Display
from spider.mongo_db.mongo_base import MongoBase

thread_local_data = threading.local()

class SpiderConf(object):
    # 最大能抓取到的数据条数
    MAX_TOTAL_RESULT = 15000
    chrome_driver_path = r"/Users/bashou/Documents/Dir/chromedriver"
    use_proxy = False
    no_monitor = False
    is_dial_server = False
    is_chrome = True

def crawl_data_without_retry(content_url,data,header,fail_flag):
    # header = ListContentHeader.header
    # init_proxy(thread_local_data)
    # init_cookies_for_content(header)

    result = crawl_data_once(content_url, data, header, fail_flag, timeout=20)
    if result != fail_flag:
        return result
    # change_proxy(thread_local_data)
    return fail_flag


def get_count(url,header,post_param,find_param):
    print 'get_count-------------'
    while True:
        page = crawl_data(url, header, post_param)
        if page == False:
            CrawlCaseShare.insert_param_error(find_param)
            return True
        else:
            soup = BeautifulSoup(page, 'html5lib')
            return int(soup.find('span',class_='total').get_text())

# def post_data_encode(post_data):
#     param_str = ''
#     for key in post_data:
#         param_str = param_str + key + '=' + str(post_data[key]) + '&'
#     return param_str

def is_contain_chinese(check_str):
    for ch in check_str.decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

# 不使用cookie
def crawl_data_once(url, header, data, fail_flag, **kwargs):
    try:
        for i in range(0, 3):
            print str(datetime.datetime.now()) + "开始发送网络请求,url是：" + str(url)
            if data is None:
                resp = requests.get(url)
            else:
                resp = requests.post(url, data=data, headers=header)
            result = resp.content
            time.sleep(1)
            if not is_contain_chinese(result):
                return fail_flag
            elif resp.status_code != 200:
                print "返回码不是200" + "是：" + str(resp.status_code)
                return fail_flag
            else:
                return result
        return fail_flag
    except Exception, e:
        print e
        return fail_flag


def crawl_data(crawl_url, header, data):
    for i in range(1, 10):
        print str(datetime.datetime.now()) + "进行第" + str(i) + "次抓取"
        result = crawl_data_once(crawl_url, header, data, False, timeout=20)
        if result != '' and result != False:
            print str(datetime.datetime.now()) + "第" + str(i) + "次抓取成功"
            return result
        print str(datetime.datetime.now()) + "第" + str(i) + "次抓取失败"
    return False
# end


#
# def list_data_handle(header,post_data):
#     init_cookies(header, 2)
#     try:
#         post_data = post_data_encode(post_data)
#     except Exception, e:
#         return None, None
#     return post_data,header
#
# def init_cookies(header,cookie_type = 1):
#     print 'init_cookie'
#     try:
#         thread_local_data.session
#     except Exception:
#         requests.adapters.DEFAULT_RETRIES = 5
#         thread_local_data.session = requests.Session()
#         thread_local_data.session.keep_alive = False
#
#     # 在去请求之前先得到cookie
#     if header["Cookie"] is None:
#         header["Cookie"] = get_cookie_with_retry(cookie_type)
#         header['User-Agent'] = UserAgent().random
#         thread_local_data.session.headers.update(header)
#         # thread_local_data.session.cookies.update(get_cookie_dict_from_str(header['Cookie']))
#     return
#
#    # 重新进行拨号连接
# def redial(sh_name='reconnect'):
#     if SpiderConf.is_dial_server:
#         print str(datetime.datetime.now()) + "开始重新pppoe连接"
#         MongoBase.mongo_client.close()
#         sh_file = '/usr/bin/bash /root/' + sh_name + '.sh'
#         print sh_file
#         os.system(sh_file)
#         time.sleep(10)
#         print str(datetime.datetime.now()) + "重新pppoe连接完成"
#
# def get_cookie_with_retry(cookie_type):
#     for i in range(0, 20):
#         cookies = get_cookie_by_selenium(cookie_type)
#         if cookies != '':
#             return cookies
#         if SpiderConf.use_proxy:
#             pass
#         else:
#             redial("redial")
#     return ''
#
# def get_cookie_by_selenium(cookie_type,use_global_proxy_conf=True):
#     print 'get_cookie_by_selenium-----------'
#     # NOTE: 这儿的try...except...finally 是必须的，否则一旦这儿出错或者发生超时，都会导致浏览器窗口无法关闭（还得写crontab去定期杀掉defunct的chromium）
#     driver = None
#     display = None
#     try:
#         display, driver = get_chrome_driver(use_global_proxy_conf)
#         if not driver:
#             return ""
#         # driver.implicitly_wait(60)
#         doc_id_list = [
#             "117454892", "117454780","117536090",
#             "117454619", "117454813","117536362"
#         ]
#         if cookie_type == 1:
#             driver.get("http://www.caseshare.cn/full/" + random.choice(doc_id_list)) + ".html"
#         elif cookie_type == 2:
#             driver.get("http://www.caseshare.cn/search/adv")
#         time.sleep(1)
#         cookie_list = driver.get_cookies()
#         cookie_str_list = []
#         for cookie_dict in cookie_list:
#             cookie_str_list.append("{0}={1};".format(cookie_dict["name"], cookie_dict["value"]))
#         cookie_str = " ".join(cookie_str_list)
#         print("Cookie str:", cookie_str)
#     except Exception as e:
#         print "lxw get_cookie_by_selenium Exception: {0}\n{1}\n{2}\n\n".format(e, traceback.format_exc(), "--" * 30)
#         return ""
#     else:
#         return cookie_str
#     finally:
#         if driver:
#             driver.quit()
#         if display:
#             display.stop()
#
# def get_chrome_driver(use_global_proxy_conf=True):
#     display = None
#     driver = None
#     try:
#         options = webdriver.ChromeOptions()
#         options.add_argument('lang=zh_CN.UTF-8')
#         # 更换头部
#         # options.add_argument(
#         #     'user-agent = Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36')
#         # prefs = {"profile.managed_default_content_settings.images": 2}
#         # options.add_experimental_option("prefs", prefs)
#         options.add_argument("--no-sandbox")
#         if SpiderConf.no_monitor:
#             display = Display(visible=0, size=(800, 800))
#             display.start()
#         if SpiderConf.is_chrome:
#             driver = webdriver.Chrome(executable_path=SpiderConf.chrome_driver_path,
#                                       chrome_options=options)
#         else:
#             driver = webdriver.Firefox()
#         # 设置超时时间
#         driver.set_page_load_timeout(20)
#         driver.set_script_timeout(20)  # 这两种设置都进行才有效
#     except Exception as e:
#         print "lxw get_chrome_driver() Exception: {0}\n{1}\n{2}\n\n".format(e, traceback.format_exc(),
#                                                                             "--" * 30)
#         if display:
#             display.stop()
#         if driver:
#             driver.quit()
#         return None, None
#     else:
#         return display, driver
#
# def crawl_data(crawl_url,header,data):
#     for i in range(1, 3):
#         print str(datetime.datetime.now()) + "进行第" + str(i) + "次抓取"
#         post_data, header = list_data_handle(header,data)
#         if post_data is None:
#             continue
#         result = crawl_data_once(crawl_url,data, False, timeout=20)
#         if result != False:
#             print str(datetime.datetime.now()) + "第" + str(i) + "次抓取成功"
#             return result
#         print str(datetime.datetime.now()) + "第" + str(i) + "次抓取失败"
#         return False
# # 使用cookie
# def crawl_data_once(url,data,fail_flag,**kwargs):
#     try:
#         for i in range(0, 3):
#             print str(datetime.datetime.now()) + "开始发送网络请求,url是：" + str(url)
#             session = thread_local_data.session
#             if data is None:
#                 req = Request("GET", url=url)
#             else:
#                 req = Request("POST", url=url, data=data)
#             prepped = session.prepare_request(req)
#             if SpiderConf.use_proxy:
#                 print "proxy:" + thread_local_data.proxy_str
#                 resp = session.send(prepped, proxies=thread_local_data.proxy, **kwargs)
#             else:
#                 resp = session.send(prepped, **kwargs)
#             result = resp.content
#             time.sleep(0.2)
#             if resp.status_code != 200:
#                 print "返回码不是200" + "是：" + str(resp.status_code)
#                 return fail_flag
#             else:
#                 return result
#         return fail_flag
#     except Exception, e:
#         print e
#         return fail_flag