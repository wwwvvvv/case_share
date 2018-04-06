# coding:utf8
import datetime
from spider.case_share.crawl_case_share_tbl import CrawlCaseShare

def begin_filter():
    print "开始筛选CaseShare的文书"
    while True:
        print "—————————————————————开始筛选CaseShare的文书1000条—————————————————————"
        case_share_docs = CrawlCaseShare.find_batch_doc_in_caseShare()
        if case_share_docs.count(with_limit_and_skip=True) == 0:
            break
        for doc in case_share_docs:
            title = doc[u'案件名称']
            case_no = doc[u'案号']
            doc_id = doc["_id"]
            print str(datetime.datetime.now()) + " docId 是 " + str(doc_id) + "的文书开始更新"
            exits_doc = CrawlCaseShare.find_one_doc_in_wenshu(case_no, title)
            if exits_doc is None:
                CrawlCaseShare.update_doc_in_caseShare(doc_id,False)
            else:
                CrawlCaseShare.update_doc_in_caseShare(doc_id,True)
            print str(datetime.datetime.now()) + "docId 是 " + str(doc_id) + "的文书更新完成"
    print "CaseShare的文书筛选完成"


if __name__ == "__main__":
    begin_filter()