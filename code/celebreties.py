import requests
import re
from bs4 import BeautifulSoup
from time import sleep
from doubanUtils import *

user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36"
                ]
headers0 = {'User-Agent':user_agent_list[3]}



class Celebreties_Crawler:

    def __init__(self, url):
        self.s = requests.Session()
        self.s.headers.update(headers0)
        self.url = url
        self.list_name=''
        self.finalOutput = ''
        self.urlHead = url.split('?')[0]

    def saveItems(self,items):
        for item in items:
            title = item.h6.a.get_text(strip=True)
            link = item.h6.a.get('href')
            try:
                picList = item.img.get('src').split('.')[:-1]
                picList.append('jpg')
                picUrl = '.'.join(picList)
            except:
                picUrl = ''
            try:
                year = item.h6.span.get_text(strip=True).replace('(','').replace(')','')
            except:
                year = ""
            
            try:
                info1 = item.dl.dl.find_all('dd')[0].get_text(strip=True)
                info2 = item.dl.dl.find_all('dd')[1].get_text(strip=True)
            except:
                info1 = ''
                info2 = ''
            
            try:
                star = item.find(class_=re.compile('star')).find_all('span')[1].get_text(strip=True)
            except:
                star = ''
            
            res = [title,link,picUrl,star,year,info1,info2]
            row = '"' + '","'.join(res) + '"\n'
            self.finalOutput += row
            print(row)

    def walk_through(self):
        url = self.url
        req = self.s.get(url)
        page = 1 
        print(f'第{page}页：',req.status_code)
        soup=BeautifulSoup(req.text,'html.parser')
        self.list_name=soup.h1.text
        print('开始爬取豆列：'+self.list_name)
        items = soup.find(class_='grid_view').find('ul',class_='').find_all('li')
        self.saveItems(items)
        # 对每一页爬取
        while 1:
            sleep(2)
            try:
                page+=1
                soup=doubanUtils.nextPageLink(self.s,soup,page,self.urlHead)
            except:
                break
            else:
                items=soup.find(class_='grid_view').find('ul',class_='').find_all('li')
                self.saveItems(items)
        # 输出
        with open(fn(self.list_name)+'_subjects.csv','a',encoding='utf-8_sig') as f:
            f.write('电影名,豆瓣链接,封面,豆瓣评分,年份,导演,主演\n')
            f.write(self.finalOutput)

if __name__ == '__main__':
    print('这是一个爬取豆瓣导演/明星作品的程序，取决于作品的数量和内容可能会发出大量的请求，甚至可能被豆瓣屏蔽ip一段时间。')
    ch0=input('请确定你要备份豆列(yes/no)：')
    if ch0.lower()=='yes':
        URL=input('请输入需要备份的【网页地址】：')
        crawler=Celebreties_Crawler(URL)
        crawler.walk_through()
    print('\n问题反馈：jimsun6428@gmail.com | https://github.com/JimSunJing/douban_clawer')
    sleep(8)
    over=input('按任意键退出')