import requests
import re
from bs4 import BeautifulSoup
from time import sleep
from random import uniform,choice
user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36"
                ]
headers0 = {'User-Agent':user_agent_list[3]}


def fn(name):
    return name.replace('\\','-').replace('/','-')\
        .replace(':','-').replace('*','-').replace('"','“')\
        .replace('<','《').replace('>','》').replace('|','-').replace('?','？')


class Series_Crawler:
    
    def __init__(self,seriesId):
        self.id=seriesId
        self.list_name=''
        self.s=requests.Session()
        self.s.headers.update(headers0)
        self.finalOutput = ''
    
    def switch_headers(self):
        self.s.headers.update({'User-Agent':choice(user_agent_list)})

    def get_urls(self):
        url='https://book.douban.com/series/'+self.id
        req=self.s.get(url)
        page=1
        print(f'第{page}页：',req.status_code)
        soup=BeautifulSoup(req.text,'html.parser')
        self.list_name=soup.h1.text
        print('开始爬取豆列：'+self.list_name)
        items=soup.find_all(class_='subject-item')
        for i in items:
            self.saveItem(i)
        while 1:
            sleep(2)
            try:
                NextPage=soup.find(class_='next').link.get('href')
                req=self.s.get(NextPage)
                page+=1
                print(f'第{page}页：',req.status_code)
                soup=BeautifulSoup(req.text,'html.parser')
            except:
                break
            else:
                items=soup.find_all(class_='subject-item')
                for i in items:
                    self.saveItem(i)
        # 输出
        with open(fn(self.list_name)+'_subjects.csv','a',encoding='utf-8_sig') as f:
            f.write('书名,豆瓣链接,豆瓣评分,作者,出版信息,简介\n')
            f.write(self.finalOutput)

    def saveItem(self,item):
        title = item.h2.get_text(strip=True)
        link = item.h2.a.get('href')
        # 获取评分
        try:
            rating = item.find(class_='rating_nums').get_text(strip=True)
        except:
            rating = 'nan'
        # 获取出版信息
        try:
            info = item.find(class_='pub').get_text(strip=True)
            # 将第一个信息，一般是作者名分离出来
            info = '","'.join(info.split('/',1))
        except:
            info = 'nan","nan'
        # 获得简介
        try:
            desc = item.find('p').get_text(strip=True).replace('\n',' ')
        except:
            desc = 'nan'
        li = [title,link,rating,info,desc]
        row = '"' + '","'.join(li) + '"' + '\n'
        self.finalOutput += row
        print(row)


if __name__ == '__main__':
    print('这是一个爬取豆瓣丛书信息的程序，取决于丛书的大小和内容会发出大量的请求，甚至可能被豆瓣屏蔽ip一段时间。')
    ch0=input('请确定你要备份豆列(yes/no)')
    if ch0.lower()=='yes':
        listid=input('请输入需要备份丛书的id：')
        crawler=Series_Crawler(listid)
        crawler.get_urls()
    print('\n问题反馈：jimsun6428@gmail.com | https://github.com/JimSunJing/douban_clawer')
    sleep(10)
    over=input('按任意键退出')