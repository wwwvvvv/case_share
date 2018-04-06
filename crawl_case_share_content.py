# coding:utf8
import datetime
import time
import pymongo
from bson import ObjectId
import sys

from spider.case_share.crawl_case_share_tbl import CrawlCaseShare
from spider.case_share.caseshare_get_page import crawl_data_without_retry
from spider.case_share.crawl_caseshare_param import header
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf8')

def begin_crawl_content():
    print "开始抓取详情"
    while True:
        try:
            print "—————————————————抓取一百条无详情的开始处理—————————————————"
            docs = CrawlCaseShare.find_none_doc()
            if docs.count(with_limit_and_skip=True) == 0:
                break
            for doc in docs:
                currentDoc = CrawlCaseShare.find_content_byId(doc["_id"])
                if currentDoc["hasDoc"] == True:
                    continue
                print str(datetime.datetime.now()) + "开始更新docId是: " + str(doc["_id"]) + "的文书"
                doc_data = crawl_data_without_retry("http://www.caseshare.cn" + str(doc["caseHref"]),None,header,False)
                if doc_data == False:
                    continue
                soup = BeautifulSoup(doc_data, 'html5lib')
                text = soup.find("div",class_='fullCon').decode_contents(formatter="html")
                if text == "":
                    text = u"文书内容为空"
                CrawlCaseShare.update_doc_data(ObjectId(doc['_id']), text)
                print str(datetime.datetime.now()) + "docId是: " + str(doc["_id"]) + "的文书更新完成"
                # time.sleep(0.3)
        except pymongo.errors, e:
            print "捕获mongo异常"
            print e
            continue
        except StandardError, e:
            print "捕获了standard异常"
            print e
            continue
        except Exception, e:
            print e
            continue
    print "抓取详情结束"




if __name__ == "__main__":
    begin_crawl_content()