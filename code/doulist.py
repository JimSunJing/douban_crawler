import requests
import re
from bs4 import BeautifulSoup
from time import sleep,perf_counter
from random import uniform,choice
from os import mkdir,getcwd,path
from doubanUtils import fn
user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36"
                ]
headers0 = {'User-Agent':user_agent_list[3]}

def clean_abstract(text):
    res = text.replace(',','，').replace('\n  ',',').replace(' ','').replace(',,',',')
    if res[-1] == ',':
        return res[:-1]
    return res

class Douban_List:
    def __init__(self,listid):
        self.id=listid
        self.list_name=''
        self.s=requests.Session()
        self.s.headers.update(headers0)
        self.notes=[]
        self.album=[]
        self.boardcast=[]
        self.groups=[]
        self.others=[]
        self.skip_douxi=False
        self.match={'日记':self.notes,'评论':self.notes,'讨论':self.groups,\
                    '相册':self.album,'小组':self.groups,'广播':self.boardcast,\
                    '电影':'','音乐':'','读书':''}
    
    def classify(self,item):
        try:
            source=item.find(class_='source').get_text(strip=True)
            if '东西' in source and self.skip_douxi:
                return
        except:
            return
        for n in self.match.keys():
            if n in source:
                try:
                    #看是否有标题
                    link=item.find(class_='title').a.get('href')
                    title=item.find(class_='title').get_text(strip=True)
                except:
                    try:
                        link=item.find('div',class_='title').a.get('href')
                        title=item.find('div',class_='title').get_text(strip=True)
                    except:
                        try:
                            #可能是广播
                            link=item.find(class_='status-content').a.get('href')
                            title=item.find(class_='status-content').a.get_text(strip=True)
                        except:
                            #可能是单张图片
                            link=item.find(class_='pic-wrap').img.get('src')
                            title='one_pic'
                print(title)
                if 'subject' in link and 'discussion' not in link:
                    picList = item.find(class_='post').img.get('src').split('.')[:-1]
                    picList.append('jpg')
                    picUrl = '.'.join(picList)
                    abstract = item.find(class_='abstract').get_text()
                    # 获取评分
                    try:
                        rating = item.find(class_='rating_nums').get_text(strip=True)
                    except:
                        rating = 'nan'
                    ## 文字保存条目
                    txt='\n          '+link + abstract
                    with open(fn(self.list_name+'_subjects.txt'),'a',encoding='utf-8_sig') as f:
                        f.write('\n          '+title+txt+'\n\n———————————————————————')
                    ## csv保存条目
                    row = '"' + title + '"' + ',' + link + ',' + picUrl + ',' + rating + clean_abstract(abstract) + '\n'
                    with open(fn(self.list_name+'_subjects.csv'),'a',encoding='utf-8_sig') as f:
                        f.write(row)

                else:
                    self.match[n].append((fn(title),link))
                return
        link=item.find(class_='title').a.get('href')
        title=item.find(class_='title').a.get_text(strip=True)
        print(title)
        self.others.append((fn(title),link))
        return
    
    def get_urls(self):
        url='https://www.douban.com/doulist/'+self.id
        req=self.s.get(url)
        page=1
        print(f'第{page}页：',req.status_code)
        soup=BeautifulSoup(req.text,'html.parser')
        self.list_name=soup.h1.text
        print('开始爬取豆列：'+self.list_name)
        items=soup.find_all(class_='doulist-item')
        for i in items:
            self.classify(i)
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
                items=soup.find_all(class_='doulist-item')
                for i in items:
                    self.classify(i)
    
    def switch_headers(self):
        self.s.headers.update({'User-Agent':choice(user_agent_list)})

class Note:
    def __init__(self,S,title,url):
        self.title=title
        self.s=S
        self.url=url
        self.NR=self.s.get(self.url)
    
    def deal_with_text(self):
        html=BeautifulSoup(self.NR.text,'html.parser')
        try:
            time=html.find(class_='pub-date').text+'\n\n'
        except:
            try:
                time=html.find(class_='main-meta').text+'\n\n'
            except:
                pass
        try:
            nf=html.find(id=re.compile('full')).find(class_='note')
        except:
            nf=html.find(id='review-content')
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
        file_name=self.title
        with open (file_name+".html","wb") as f:
            #写文件用bytes而不是str，所以要转码  
            f.write(bytes(self.NR.text,encoding='utf-8_sig'))
            print(self.title+' HTML完成')
    
    def save_text(self):
        with open(self.title+'.txt','w',encoding='utf-8_sig') as f:
            txt=self.deal_with_text()
            f.write(str(txt))
            print(self.title+" TXT已保存")

    def claw(self):
        self.save_html()
        try:
            self.save_text()
            print(self.title+'  OK')
        except:
            print(self.title+'  纯文字爬取失败')

class DG:
    def __init__(self,S,title,url):
        self.s=S
        self.title=title
        self.url=url
        self.req=self.s.get(self.url)
        
    def save_html(self):
        file_name=self.title
        with open (file_name+".html","wb") as f:
            #写文件用bytes而不是str，所以要转码  
            f.write(bytes(self.req.text+'\n',encoding='utf-8'))
            print(self.title+'  HTML完成')
    
    def save_url(self):
        open(self.title+'.txt','w',encoding='utf-8_sig').write('链接：'+self.url)

    def claw(self):
        self.save_html()
        self.save_url()

class Album:
    def __init__(self,S,title,url):
        self.s=S
        self.title=title
        self.url=url
        self.req=self.s.get(url)
    
    def save_album(self):
        try:
            mkdir(self.title)
        except:
            sleep(1)
        sloc=getcwd()+'\\\\'+self.title
        soup=BeautifulSoup(self.req.text,'html.parser')
        imgs=soup.find_all(class_='photo_wrap')
        for IMG in imgs:
            pu=IMG.img.get('src').replace('/m/','/l/')
            self.save_pic(pu,loc=sloc)
        while 1:
            sleep(2)
            try:
                NextPage=soup.find(class_='next').a.get('href')
                req=self.s.get(NextPage)
                soup=BeautifulSoup(req.text,'html.parser')
            except:
                break
            else:
                imgs=soup.find_all(class_='photo_wrap')
                for IMG in imgs:
                    pu=IMG.img.get('src').replace('/m/','/l/')
                    self.save_pic(pu,loc=sloc)

    def save_pic(self,purl,loc=''):
        sleep(2)
        preq=self.s.get(purl)
        name=purl.split('/')[-1].replace('.jpg','')
        if loc!='':
            name=loc+'\\\\'+name
        open(name+'.jpg','wb').write(preq.content)
        print(name+'    Saved')
    
    def claw(self):
        if self.title=='one_pic':
            self.save_pic(self.url)
        else:
            choice=input(self.title+' 相册需要爬取吗(yes/no)：')
            if choice=='yes':
                self.save_album()
        
class Boardcast:
    def __init__(self,S,title,url):
        self.s=S
        self.title=title
        self.url=url
        self.req=self.s.get(url)
    
    def save_html(self):
        file_name=self.title
        with open (file_name+".html","ab") as f:
            #写文件用bytes而不是str，所以要转码  
            f.write(bytes(self.req.text,encoding='utf-8'))
            print(self.title+'HTML完成')
    
    def save_text(self):
        soup=BeautifulSoup(self.req.text,'html.parser')
        try:
            t=soup.find_all('blockquote')[0].get_text(strip=True)
        except:
            return
        with open(self.title+'.txt','a',encoding='utf-8_sig') as f:
            f.write(str(t))
            print(self.title+"TXT已保存")
    
    def claw(self):
        self.save_text()
        self.save_html()


def main():
    print('这是一个备份豆列的程序，取决于豆列的大小和内容会发出大量的请求，甚至可能被豆瓣屏蔽ip一段时间。')
    ch0=input('请确定你要备份豆列(yes/no)(备份相册请按0)：')
    if ch0.lower()=='yes':
        listid=input('请输入需要备份豆列的id：')
        clawer=Douban_List(listid)
        skip=input('是否需要跳过“东西”条目？(yes/no):')
        if skip=='yes':
            clawer.skip_douxi=True
        clawer.get_urls()
        for item in clawer.notes:
            if path.exists(item[0]+'.html'):
                continue
            sleep(2)
            Note(clawer.s,item[0],item[1]).claw()
        clawer.switch_headers()
        #for item in clawer.album:
            #sleep(2)
            #Album(clawer.s,item[0],item[1]).claw()
        clawer.switch_headers()
        for item in clawer.boardcast:
            sleep(2)
            Boardcast(clawer.s,item[0],item[1]).claw()
        clawer.switch_headers()
        for item in clawer.groups:
            sleep(2)
            DG(clawer.s,item[0],item[1]).claw()
        clawer.switch_headers()
        for item in clawer.others:
            sleep(2)
            DG(clawer.s,item[0],item[1]).claw()
    elif ch0=='0':
        S=requests.Session()
        S.headers.update({'User-Agent':choice(user_agent_list)})
        aid=input('请输入相册id：')
        aurl='https://www.douban.com/photos/album/'+aid
        r=S.get(aurl)
        soup=BeautifulSoup(r.text,'html.parser')
        title=soup.find('h1').get_text(strip=True)
        Album(S,title,aurl).claw()
    print('\n问题反馈：jimsun6428@gmail.com | https://github.com/JimSunJing/douban_clawer')


main()
sleep(10)
over=input('按任意键退出')