# coding:utf8
import datetime
import math
import Queue
import sys
import pymongo
from bs4 import BeautifulSoup


reload(sys)
sys.setdefaultencoding('utf8')

from spider.case_share.caseshare_get_page import crawl_data
from spider.case_share.crawl_case_share_tbl import CrawlCaseShare
from spider.case_share.crawl_caseshare_param import url,header

def fill_queue(target_info,queue):
    count = target_info['COUNT']
    param = target_info['PARAM']
    max_index = int(math.floor(count / 10.0) + 1)
    if max_index > 100:
        max_index = 100
    if target_info.get('CURRENT_INDEX', -1) != -1:
        min_index = int(target_info['CURRENT_INDEX']) + 1
    else:
        min_index = 0
    for i in xrange(min_index, max_index):
        print "fill queue" + str(i)
        queue.put({
            'RecordSearchUrl': '/Search/RecordSearch?IsAdv=True',
            'IsAdv': 'True',
            'X-Requested-With': 'XMLHttpRequest',
            'AdvSearchDic.LastInstanceDate':param["LastInstanceDate"],
            'AdvSearchDic.Category':param["Category"],
            'AdvSearchDic.WritType':param["WritType"],
            'AdvSearchDic.LastInstanceCourt':param["LastInstanceCourt"],
            'Pager.PageIndex': str(i),
        })

def consume_queue(spider_queue,target_info):
    data = spider_queue.get()
    print datetime.datetime.now(), data

    page = crawl_data(url,header,data)
    if page is False:
        try:
            CrawlCaseShare.crawl_caseshare_list_error.insert(target_info)
        except pymongo.errors.DuplicateKeyError:
            pass
        return
    soup = BeautifulSoup(page, "html5lib")
    wrappers = soup.find("div", {"id": "dataList"}).find("ul").find_all("li")
    for wrapper in wrappers:
        try:
            caseTitle = wrapper.find("a").get_text()
            caseHref = wrapper.find("a")["href"]
            otherwrapper = wrapper.find("div",class_="annexInfo")
            otherInfo = otherwrapper.find_all("span")
            judgeTime = otherInfo[0].get_text()
            caseNo = otherInfo[1].get_text()
            courtName = otherwrapper.find("a").get_text()
            insert_obj = {}
            insert_obj['hasDoc'] = False
            insert_obj['caseHref'] = caseHref
            insert_obj['案件名称'] = caseTitle
            insert_obj['审判时间'] = judgeTime
            insert_obj['案号'] = caseNo
            # insert_obj['文书类型'] = referencedType
            # insert_obj['案由'] = reason
            insert_obj['法院名称'] = courtName
            insert_obj['alreadyExists'] = ""
            try:
                CrawlCaseShare.crawl_caseshare_data.insert(insert_obj)
            except pymongo.errors.DuplicateKeyError:
                CrawlCaseShare.crawl_caseshare_duplicate.insert_one(insert_obj)
        except pymongo.errors:
            print "其他异常捕获"
            CrawlCaseShare.crawl_caseshare_list_error.insert_one(data)
            return
        except Exception,e:
            print e
            pass
    currentIndex = data['Pager.PageIndex']
    target_info["CURRENT_INDEX"] = currentIndex
    CrawlCaseShare.update_current_targets(currentIndex, target_info["_id"])

def begin_crawl():
    print "开始抓取列表"
    param_queue = Queue.Queue()
    while True:
        try:
            target_info = CrawlCaseShare.get_next_targets()
            if target_info is None:
                break
            print str(target_info["PARAM"]) + ":" + str(target_info["COUNT"])
            fill_queue(target_info, param_queue)
            while not param_queue.empty():
                consume_queue(param_queue, target_info)
            CrawlCaseShare.crawlTargetsSuccess(target_info["_id"])
        except Exception, e:
            print e
            param_queue = Queue.Queue()
            continue

if __name__ == "__main__":
    begin_crawl()