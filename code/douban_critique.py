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


class critique:
    def __init__(self,doubanid):
        self.id=doubanid
        self.s=requests.Session()
        self.s.headers.update(headers0)
        self.CUs=[]
        self.CRs=[]

    def critique_list(self):
        review_url='https://www.douban.com/people/'+self.id+'/reviews'
        res0=self.s.get(review_url)
        soup=BeautifulSoup(res0.text,'html.parser')
        critique_list=soup.find_all('h2')
        self.CUs=[i.a.get('href') for i in critique_list]
        while 1:
            time.sleep(1.5)
            try:
                next_url='https://www.douban.com/people/'+self.id+'/'+soup.find(class_="next").link.get('href')
            except:
                break
            else:
                res=self.s.get(next_url)
                soup=BeautifulSoup(res.text,'html.parser')
                critique_list=soup.find_all('h2')
                for i in critique_list:
                    self.CUs.append(i.a.get('href'))
        print('评论url如下：')
        print(self.CUs)
        print('开始访问每个评论...')
        for i in range(len(self.CUs)):
            if (i+1)%50==0:
                print('已经爬了50个评论，停2分钟')
                time.sleep(120)
            time.sleep(1.5)
            try:
                res=self.s.get(self.CUs[i])
                self.CRs.append(res.text)
                print(f'打开第{i}篇评论',res.status_code)
            except Exception as e:
                print(f'打开第{i}篇评论失败。\n',e)
    
    def deal_with_text(self,h):
        html=BeautifulSoup(h,'html.parser')
        time=html.find(class_='main-meta').text+'\n'
        nf=html.find(id='link-report')
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
        file_name=self.id+"'s_Critique"
        count=1
        with open (file_name.replace('/','_')+".html","wb") as f:
            for file_content in self.CRs:
                #写文件用bytes而不是str，所以要转码  
                f.write(bytes(file_content+'\n',encoding='utf-8'))
                print(f'第{count}页HTML完成')
                count+=1
    
    def save_text(self):
        count=0
        for n in self.CRs:
            count+=1
            with open(self.id+f'Critique_No.{count}.txt','w',encoding='utf-8_sig') as f:
                txt=self.deal_with_text(n)
                f.write(str(txt))
                print(f"第{count}个评论已保存")

def critique_main():
    print('hello，这是一个备份豆瓣评论的程序。\n需要你自己的cookie用来爬取评论。')
    choice=input('该过程有风险，请确定你要开始备份(yes/no)：')
    if choice=='yes':
        doubanid=input('请输入你的豆瓣id：')
        Cclaw=critique(doubanid)
        Cclaw.critique_list()
        choice2=input('请选择你要输出html结果(a)还是文本txt结果(b)或者我全都要(all)：')
        choice2=choice2.lower()
        if choice2 == 'a':
            try:
                Cclaw.save_html()
            except Exception as e:
                print(e)
                print('储存html文件出错')
            else:
                print('成功')
        elif choice2 == 'b':
            try:
                Cclaw.save_text()
            except Exception as e:
                print(e)
                print('储存txt文件出错')
            else:
                print('成功')
        elif choice2 == 'all':
            try:
                Cclaw.save_html()
                Cclaw.save_text()
            except Exception as e:
                print(e)
                print('出错')
        print('程序结束，文件存在该exe目录中')
    print('问题反馈：jimsun6428@gmail.com | https://github.com/JimSunJing/douban_clawer')
    input('按任意键退出')

critique_main()