# coding:utf8

import datetime
import pymongo
import sys

from bson import ObjectId
from bs4 import BeautifulSoup
from spider.case_share.crawl_case_share_tbl import CrawlCaseShare
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from spider.case_share.crawl_caseshare_param import header
from spider.case_share.caseshare_get_page import crawl_data_without_retry


reload(sys)
sys.setdefaultencoding("utf8")


def crawl_content(doc):
    currentDoc = CrawlCaseShare.find_content_byId(doc["_id"])
    if currentDoc["hasDoc"] == True:
        return
    print str(datetime.datetime.now()) + "开始更新docId是: " + str(doc["_id"]) + "的文书"
    doc_data = crawl_data_without_retry("http://www.caseshare.cn" + str(doc["caseHref"]), None, header, False)
    if doc_data == False:
        return
    soup = BeautifulSoup(doc_data, 'html5lib')
    text = soup.find("div", class_='fullCon').decode_contents(formatter="html")
    if text == "":
        text = u"文书内容为空"
    CrawlCaseShare.update_doc_data(ObjectId(doc['_id']), text)
    print str(datetime.datetime.now()) + "docId是: " + str(doc["_id"]) + "的文书更新完成"


def begin_crawl():
    print "开始抓取详情 skip2000"
    while True:
        try:
            print "--------------抓取一百条无详情的开始处理----------"
            docs = CrawlCaseShare.find_none_doc_with_skip()
            if docs.count(with_limit_and_skip=True) == 0:
                break

            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_content = {executor.submit(crawl_content, doc): doc['_id'] for doc in
                                     docs}
                for future in as_completed(future_to_content):
                    doc_id = future_to_content[future]
                    #     content = future.result()
                    #     if content is False:
                    #         continue
                    #     text = content['Html']
                    #     if text == '':
                    #         text = u"文书内容为空"
                    #     print str(datetime.datetime.now()) + "开始更新docId是: " + str(doc_id) + "的文书内容"
                    #     CrawlData.update_doc_content(doc_id, text, content['PubDate'])
                    print str(datetime.datetime.now()) + "docId是: " + str(doc_id) + "的content已执行---------"
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
    begin_crawl()