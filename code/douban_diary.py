import requests
import re
from bs4 import BeautifulSoup
import time

user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; …) Gecko/20100101 Firefox/61.0",
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
                "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
                ]

headers0 = {'User-Agent':user_agent_list[3]}

class diary:
    def __init__(self,doubanid,cookie=None):
        self.id=doubanid
        self.s=requests.Session()
        self.s.headers.update(headers0)
        self.NUs=[]
        self.NRs=[]
    
    def add_cookie(self,cookie):
        cookies=getCookie(cookie)
        self.s.cookies.update(cookies)
    
    def note_list(self):
        diary_url='https://www.douban.com/people/'+self.id+'/notes'
        res0=self.s.get(diary_url)
        soup=BeautifulSoup(res0.text,'html.parser')
        page=1
        print(f'第{page}页',res0.status_code)
        note_list=soup.find_all(id=re.compile('naf-'))
        self.NUs=[i.get('href') for i in note_list]
        while 1:
            time.sleep(1.5)
            try:
                next_url=soup.find(class_="next").link.get('href')
            except:
                break
            else:
                page+=1
                res=self.s.get(next_url)
                print(f'第{page}页',res.status_code)
                soup=BeautifulSoup(res.text,'html.parser')
                note_list=soup.find_all(id=re.compile('naf-'))
                for i in note_list:
                    self.NUs.append(i.get('href'))
        print('日记url如下：')
        print(self.NUs)
        print('开始访问每个日记...')
        for i in range(len(self.NUs)):
            if (i+1)%50==0:
                print('已经爬了50个日记，停2分钟')
                time.sleep(120)
            time.sleep(1.5)
            try:
                res=self.s.get(self.NUs[i])
                self.NRs.append(res.text)
                print(f'打开第{i}篇日记',res.status_code)
            except Exception as e:
                print(f'打开第{i}篇日记失败。\n',e)
    
    def deal_with_text(self,h):
        html=BeautifulSoup(h,'html.parser')
        time=html.find(class_='pub-date').text+'\n'
        nf=html.find(id=re.compile('full')).find(class_='note')
        words=str(nf(['p','blockquote','h2','h1','h3']))
        if words=='[]':
            note=nf.text
        else:
            note=words.replace('</p>, <p>','\n\n').replace('</p>, ','\n\n').replace('<p>','')\
                .replace('<span style="font-weight: bold;">','**').replace('</span>, ','\n\n').replace('</span>','')\
                .replace('<h2>','## ').replace('<h3>','### ').replace('<h1>','# ')\
                .replace('</h2>, ','\n\n').replace('</h3>, ','\n\n').replace('</h1>, ','\n\n')\
                .replace('<blockquote>','>').replace('</blockquote>, ','\n\n').replace('<a href=','\n')\
                .replace('</a>','\n').replace('&lt;','<').replace('&gt;','>').replace('[','').replace('</p>]','')\
                .replace('rel=“nofollow” target="_blank">','')
        return time+note
    
    def save_html(self):
        file_name=self.id+"'s_Diary"
        count=1
        with open (file_name.replace('/','_')+".html","wb") as f:
            for file_content in self.NRs:
                #写文件用bytes而不是str，所以要转码  
                f.write(bytes(file_content+'\n',encoding='utf-8'))
                print(f'第{count}页HTML完成')
                count+=1
    
    def save_text(self):
        count=0
        for n in self.NRs:
            count+=1
            with open(self.id+f'Diary_No.{count}.txt','w',encoding='utf-8_sig') as f:
                txt=self.deal_with_text(n)
                f.write(str(txt))
                print(f"第{count}个日记已保存")

def getCookie(raw_cookies):
    cookies={}
    for line in raw_cookies.split(';'):
        key,value=line.split('=',1) #1代表只分一次，得到两个数据
        cookies[key]=value
    return cookies                


def main():
    print('hello，这是一个备份豆瓣日记的程序。\n需要你自己的cookie用来爬取日记。')
    choice=input('该过程有风险，请确定你要开始备份(yes/no)：')
    if choice=='yes':
        doubanid=input('请输入你的豆瓣id：')
        private=input('请选择：\nA.只需要备份他人可见的日记\nB.需要备份包括自己可见的日记（需要你提供自己的cookie）\n')
        dclaw=diary(doubanid)
        if private.lower()=='b':
            raw_cookies=input('请输入你的cookie(最后不要带空格)：')
            dclaw.add_cookie(cookie=raw_cookies)
        dclaw.note_list()
        choice2=input('请选择你要输出html结果(a)还是文本txt结果(b)或者我全都要(all)：')
        choice2=choice2.lower()
        if choice2 == 'a':
            try:
                dclaw.save_html()
            except Exception as e:
                print(e)
                print('储存html文件出错')
            else:
                print('成功')
        elif choice2 == 'b':
            try:
                dclaw.save_text()
            except Exception as e:
                print(e)
                print('储存txt文件出错')
            else:
                print('成功')
        elif choice2 == 'all':
            try:
                dclaw.save_html()
                dclaw.save_text()
            except Exception as e:
                print(e)
                print('出错')
        print('程序结束，文件存在该exe目录中')
    print('问题反馈：jimsun6428@gmail.com | https://github.com/JimSunJing/douban_clawer')
    input('按任意键退出')

main()