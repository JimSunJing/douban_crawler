import requests
import re
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
