import requests
import csv, os, os.path, re
from functools import reduce
from bs4 import BeautifulSoup
from time import localtime,strftime,perf_counter,strptime

user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; …) Gecko/20100101 Firefox/61.0",
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36 Edg/84.0.522.63",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
                "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
                ]

def getAgent(n=3):
    return user_agent_list[n]

def hasNextPage(soup):
    try:
        NextPage=soup.find(class_='next').link.get('href')
        return NextPage
    except:
        return False

def nextPageLink(sess,soup,page,head=""):
    NextPage=soup.find(class_='next').link.get('href')
    req=sess.get(head + NextPage)
    print(f'第{page}页：',req.status_code)
    return BeautifulSoup(req.text,'html.parser')

# file name
def fn(name):
    return name.replace('\\','-').replace('/','-')\
        .replace(':','-').replace('*','-').replace('"','“')\
        .replace('<','《').replace('>','》').replace('|','-').replace('?','？')

# page control
def pageControl(limit=50):
    beg=eval(input('请输入你要爬取的起始页码（比如1）：'))
    end=eval(input('请输入终止页码（建议一次爬取{}页以下）：'.format(limit)))
    return beg, end


def timebar(scale,start,p):
    a='※'*round(p*scale)
    b='.'*(scale-round(p*scale))
    dur=(perf_counter()-start)/60
    print("\r{:^3.0f}%[{}->{}]已运行{:.2f}分钟"\
        .format(p*100,a,b,dur),end=' ')

def noco(txt):
    if len(txt)==0: return '...'
    return txt.replace(',','、').replace('，','、').replace('\n','  ')


def getFormatTime():
    return strftime("%Y-%m-%d %H-%M-%S", localtime())

def string2Time(s):
    return strptime(s, '%Y-%m-%d %H-%M-%S')

def fileTimeCompare(fn1, fn2):
    fn1 = fn1.replace(".csv","").split('-',1)[1][:-6]
    fn2 = fn2.replace(".csv","").split('-',1)[1][:-6]
    return string2Time(fn1) > string2Time(fn2) 

def getLastBackUpItem(douId,Type):
    # 获取上次文件
    matchFiles = []
    # 文件名
    fnMatch = r"iiid-\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}tttypeplus.csv"\
        .replace('iiid',douId).replace('tttype',Type)
    for _, _, files in os.walk("."):
        for file in files:
            # print(file)
            if re.match(fnMatch,file):
                matchFiles.append(file)
    ## 得到最新的电影名
    if len(matchFiles) != 0:
        latest = reduce(lambda x,y: x if fileTimeCompare(x,y) else y,\
            matchFiles)
        with open(latest, 'r', encoding='utf-8_sig') as f:
            reader = csv.DictReader(f)
            # 获取第一行电影的id
            try:
                row = reader.__next__()
                return row['subjectId']
            except:
                return None
    else: 
        return None 

def getCookie(raw_cookies):
    cookies={}
    for line in raw_cookies.split(';'):
        key,value=line.split('=',1) 
        cookies[key]=value
    return cookies   

def getYear(raw):
    yearRex = r'([1|2][9|0]\d{2})'
    res = re.match(yearRex,raw)
    try:
        return res.group(1)
    except:
        return ''

def getShortComments(comments):
    res = ''
    for com in comments:
        # 先得到评价用户名
        user = com.find(class_="comment-info").get_text(strip=True).replace('\xa0','').replace('\n','')
        res += user
        res += '：'
        short = com.find(class_="short").get_text(strip=True).replace('\xa0','').replace('\n','')
        res += short
        res += '；  |  '
    return res.replace("看过"," ")