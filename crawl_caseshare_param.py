# coding:utf8

import datetime
import calendar

from spider.case_share.crawl_case_share_tbl import CrawlCaseShare
from spider.case_share.caseshare_get_page import get_count

header = {
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
    'Cache-Control':'no-cache',
    'Connection':'keep-alive',
    # 'Content-Length':'497',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie':"bdshare_firstime=1508215566218; Hm_lvt_e76455ef4ced7982d257cd9ce7649100=1508125180; Hm_lpvt_e76455ef4ced7982d257cd9ce7649100=1508375724",
    'Host':'www.caseshare.cn',
    'Origin':'http://www.caseshare.cn',
    'Pragma':'no-cache',
    'Referer':'http://www.caseshare.cn/search/adv',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest'
}

last_instance_date = {  #审判时间
    "Start":"",
    "End":""
}

param = {
    'RecordSearchUrl':'/Search/RecordSearch?IsAdv=True',
    'IsAdv':'True',
    'AdvSearchDic.LastInstanceDate':"", #审判时间
    'Pager.PageIndex':'0', #页码减一
    'X-Requested-With':'XMLHttpRequest'
}

url = "http://www.caseshare.cn/Search/RecordSearch?IsAdv=True"

# 最多能翻到第100页，抓到第1000条
Max_Total_Result = 1000

def time_strftime(year,month,days):
    return datetime.datetime(year,month,days).strftime('%Y%m%d')

def get_year_list(start_date,end_date):
    date_list = []
    for date in range(int(start_date), int(end_date) + 1):
        start_time = time_strftime(date, 1, 1)
        end_time = time_strftime(date, 12, 31)
        date_list.append({"start_date": start_time, "end_date": end_time})
    return date_list

def get_days_list(this_year,month,month_end):
    days_list = []
    start_day = 1
    for day in [10,20,month_end]:
        start_time = time_strftime(this_year,month,start_day)
        end_time = time_strftime(this_year,month,day)
        start_day = start_day + 10
        days_list.append({"start_date": start_time, "end_date": end_time})
    return days_list

def add_param(post_param,find_param, final_param):
    crawl_data = CrawlCaseShare.find_by_param(find_param)
    if crawl_data is not None:
        return crawl_data["COUNT"] <= Max_Total_Result
    result_count = get_count(url,header,post_param,find_param)
    if result_count is True:
        return True
    print(str(post_param) + ": " + str(result_count))
    result_lte_max = result_count <= Max_Total_Result
    if result_lte_max:
        final_param = True
    CrawlCaseShare.crawl_db_insert_new(find_param, result_count, final_param)
    return result_lte_max

def crawl_param(begin_date,end_date,Category="",WritType="",LastInstanceCourt="",final_param = False):
    last_instance_date['Start'] = begin_date
    last_instance_date['End'] = end_date
    param['AdvSearchDic.LastInstanceDate'] = str(last_instance_date)
    param['AdvSearchDic.Category'] = Category
    param['AdvSearchDic.WritType'] = WritType
    param['AdvSearchDic.LastInstanceCourt'] = LastInstanceCourt
    return add_param(param,{"LastInstanceDate":str(last_instance_date),"Category":Category,"WritType":WritType,"LastInstanceCourt":LastInstanceCourt},final_param)

def crawl_param_by_year():
    year_list = get_year_list(1997, 2015)
    for year in year_list:
        result = crawl_param(year["start_date"], year["end_date"])
        if result is False:
            print "数量大于1000 按每三个月抓取"
            crawl_param_by_three_months(int(year["start_date"][:4]))

def crawl_param_by_three_months(this_year):
    for month in [0,3,6,9]:
        start_date = time_strftime(this_year,month+1,1)
        month_end = calendar.monthrange(this_year,month+3)[1]
        end_date = time_strftime(this_year,month+3,month_end)
        result = crawl_param(start_date,end_date)
        if result is False:
            print "数量大于1000 按每个月抓取"
            crawl_param_by_month(this_year,month)

def crawl_param_by_month(this_year,start_month):
    for month in range(start_month,start_month + 3):
        this_month = month + 1
        start_date = time_strftime(this_year,this_month,1)
        month_end = calendar.monthrange(this_year,this_month)[1]
        end_date = time_strftime(this_year,this_month,month_end)
        result = crawl_param(start_date, end_date)
        if result is False:
            print "数量大于1000 按每10天抓取"
            crawl_param_by_ten_days(this_year, this_month, month_end)

def crawl_param_by_ten_days(this_year, this_month, month_end):
    days_list = get_days_list(this_year,this_month,month_end)
    for days in days_list:
        result = crawl_param(days["start_date"], days["end_date"])
        if result is False:
            print "数量大于1000 按每天抓取"
            crawl_param_by_day(this_year,this_month,int(days["start_date"][-2:]),int(days["end_date"][-2:]))

def crawl_param_by_day(this_year,this_month,start_day,end_day):
    for day in range(start_day,end_day+1):
        this_date = time_strftime(this_year, this_month, day)
        result = crawl_param(this_date, this_date)
        if result is False:
            print "数量大于1000 按案由顺序抓取"
            crawl_param_by_reason(this_date)

def crawl_param_by_reason(this_date):
    #刑事：001  民事：002 知识产权：003 行政：005 执行：006 国家赔偿：007
    reason_list = ["001","002","003","005","006","007"]
    for reason in reason_list:
        result = crawl_param(this_date,this_date,reason)
        if result is False:
            print "数量大于1000 按文书性质顺序抓取"
            crawl_param_by_writeType(this_date,reason)

def crawl_param_by_writeType(this_date,reason):
    #判决书：001 裁定书：002 决定书：003 调解书：004 其他文书：005
    type_list = ["001","002","003","004","005"]
    for type in type_list:
        result = crawl_param(this_date,this_date,reason,type)
        if result is False:
            print "数量大于1000 按法院省份顺序抓取"
            crawl_param_by_court(this_date,reason,type)

def crawl_param_by_court(this_date,reason,type):
    #法院省份  最高人民法院：01  北京市：02 天津市：03  上海市：04  重庆市：05 河北省：06  山西省：07  内蒙古自治区：08  辽宁省：09  吉林省：10  黑龙江省：11
    #         江苏省：12  浙江省：13  安徽省：14  福建省：15  江西省：16  山东省：17  河南省：18  湖北省：19  湖南省：20  广东省：21  广西壮族自治区：22
    #         海南省：23  四川省：24  贵州省：25  云南省：26  西藏自治区：27  陕西省：28 甘肃省：29  宁夏回族自治区：30  青海省：31  新疆维吾尔自治区：32
    #         铁路法院：33  海事法院：34  军事法院：35  知识产权法院：36
    court_list = ["01","02","03","04","05","06","07","08","09","10",
                  "11","12","13","14","15","16","17","18","19","20",
                  "21","22","23","24","25","26","27","28","29","30",
                  "31","32","33","34","35","36"]
    for court in court_list:
        crawl_param(this_date,this_date,reason,type,court,final_param=True)

def crawl_old():
    begin_date = ""
    end_date = time_strftime(1996,12,31)
    crawl_param(begin_date,end_date,final_param=True)

def begin_crawl():
    print "开始抓取条件"
    while True:
        # 抓取1996年12月31日之前的
        crawl_old()
        # 抓取1997年1月1日以后的
        crawl_param_by_year()
        break


if __name__ == "__main__":
    begin_crawl()