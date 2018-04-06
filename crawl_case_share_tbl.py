# coding:utf8

import pymongo
from spider.mongo_db.mongo_base import MongoBase

# db.getCollection("crawl_caseshare_data").createIndex({"案号": 1, "案件名称": 1}, {"unique": true});
# db.getCollection("crawl_caseshare_data").createIndex({"案号": 1});
# db.getCollection("crawl_caseshare_data").createIndex({"案件名称": 1});
# db.getCollection("crawl_caseshare_data").createIndex({"hasDoc": 1});
# db.getCollection("crawl_caseshare_data").createIndex({"caseHref": 1});

# db.getCollection("crawl_caseshare_param").createIndex({"IS_CRAWL": 1});
# db.getCollection("crawl_caseshare_param").createIndex({"COUNT": 1});
# db.getCollection("crawl_caseshare_param").createIndex({"PARAM": 1});
# db.getCollection("crawl_caseshare_param").createIndex({"FINAL_PARAM": 1});

class CrawlCaseShare(MongoBase):
    wfuu_db = MongoBase.wfuu_db
    crawl_db = MongoBase.crawl_db
    crawl_caseshare_data = wfuu_db["crawl_caseshare_data"]
    # crawl_caseshare_data = crawl_db["crawl_caseshare_data"]
    crawl_caseshare_param = crawl_db["crawl_caseshare_param"]
    crawl_caseshare_duplicate = crawl_db["crawl_caseshare_duplicate"]
    crawl_caseshare_list_error = crawl_db["crawl_caseshare_list_error"]
    wenshu_doc = wfuu_db["crawl_data"]


    @staticmethod
    def find_by_param(find_param, mongo_tbl=crawl_caseshare_param):
        return  mongo_tbl.find_one({'PARAM': find_param})

    @staticmethod
    def crawl_db_insert_new(find_param,count,final_param=True,mongo_tbl=crawl_caseshare_param):
        is_crawl = 0
        if count == 0 or (count > 1000 and final_param is False):
            is_crawl = 10
        try:
            insert_obj = {
                "PARAM": find_param ,
                "FINAL_PARAM": final_param,
                "COUNT": count,
                "IS_CRAWL": is_crawl
            }
            mongo_tbl.insert(insert_obj)
            print "插入数据库成功"
        except pymongo.errors.DuplicateKeyError,e:
            print "continue"

    @staticmethod
    def get_next_targets(mongo_tbl = crawl_caseshare_param):
        query_param = {"$query": {"IS_CRAWL": 0, "COUNT": {"$gt": 0}},"$orderby": {"_id": 1}}
        return mongo_tbl.find_one(query_param)

    @staticmethod
    def crawlTargetsSuccess(id,mongo_tbl=crawl_caseshare_param):
        result = mongo_tbl.update_one({"_id": id}, {"$set": {"IS_CRAWL": 10}})
        return result

    @staticmethod
    def update_current_targets(currentIndex,id,mongo_tbl=crawl_caseshare_param):
        return mongo_tbl.update_one({"_id": id}, {"$set": {"CURRENT_INDEX": currentIndex}})

    @staticmethod
    def find_none_doc():
        query_param = {"hasDoc": False}
        return CrawlCaseShare.crawl_caseshare_data.find(query_param).limit(1000)

    @staticmethod
    def update_doc_data(_id, doc_content, mongo_tbl=crawl_caseshare_data):
        mongo_tbl.update_one({'_id': _id}, {'$set': {'DocContent': doc_content, 'hasDoc': True}})

    @staticmethod
    def insert_param_error(find_param,mongo_tbl=crawl_caseshare_param):
        try:
            insert_obj = {
                "PARAM":find_param,
                "COUNT":-1,
                "IS_CRAWL":0,
                "HAS_ERROR":True,
                "FINAL_PARAM":False
            }
            mongo_tbl.insert_one(insert_obj)
        except pymongo.errors.DuplicateKeyError, e:
            print "continue"


    @staticmethod
    def find_none_doc_with_skip(mongo_tbl=crawl_caseshare_data):
        query_param = {"hasDoc": False,"alreadyExists":False}
        return mongo_tbl.find(query_param).skip(2000).limit(1000)

    @staticmethod
    def find_content_byId(id,mongo_tbl=crawl_caseshare_data):
        return mongo_tbl.find_one({"_id": id})

    @staticmethod
    def find_batch_doc_in_caseShare(mongo_tbl= crawl_caseshare_data):
        query_param = {"alreadyExists": ""}
        return mongo_tbl.find(query_param).limit(1000)

    @staticmethod
    def find_one_doc_in_wenshu(case_no,title,mongo_tbl = wenshu_doc):
        return mongo_tbl.find_one({u'案号': case_no, u'案件名称': title})

    @staticmethod
    def update_doc_in_caseShare(id,exists_status,mongo_tbl=crawl_caseshare_data):
        mongo_tbl.update_one({'_id':id},{'$set':{"alreadyExists":exists_status}})

