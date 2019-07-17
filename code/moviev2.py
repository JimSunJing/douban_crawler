import requests
from bs4 import BeautifulSoup
import re
from time import sleep,perf_counter
from random import uniform,choice
user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; …) Gecko/20100101 Firefox/61.0",
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
                "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
                ]
headers0 = {'User-Agent':user_agent_list[3]}


def noco(txt):
    return txt.replace(',','、').replace('，','、').replace('\n','  ')

def timebar(scale,start,p):
    a='※'*round(p*scale)
    b='.'*(scale-round(p*scale))
    dur=(perf_counter()-start)/60
    print("\r{:^3.0f}%[{}->{}]已运行{:.2f}分钟".format(p*100,a,b,dur),end=' ')

class Douban_Movie:
    def __init__(self,doubanid):
        self.s=requests.Session()
        #加上头部
        self.s.headers.update(headers0)
        self.id=doubanid
        #wish dict format: {movieid:[影片名,上映日期,导演,编剧,主演,制片国家/地区,片长,评分,评分人数,标记日期]}
        self.wish_dict={}
        self.Keys=['影片名','上映日期','导演','编剧',\
                    '主演','制片国家/地区','片长','评分','评分人数']
        #saw dict format: {movieid:[影片名,上映日期,导演,编剧,主演,制片国家/地区,片长,评分,评分人数,用户评分,评论,标记日期]}
        self.saw_dict={}
    
    def Wish(self):
        print('\n开始爬取'+self.id+'的想看列表')
        beg=eval(input('请输入你要爬取的起始页码（比如1）：'))
        end=eval(input('请输入终止页码（建议一次爬取10页以下）：'))
        page=beg
        firstpage='https://movie.douban.com/people/'+self.id+'/wish?start='+str((beg-1)*30)+'&sort=time&rating=all&filter=all&mode=list'
        req=self.s.get(firstpage)
        soup=BeautifulSoup(req.text,'html.parser')
        print(f'第{page}页',req.status_code)
        #get movie name and id
        wish=soup.find_all('a',href=re.compile("subject"))
        for i in range(len(wish)):
            name=wish[i].get_text(strip=True)
            mid=wish[i].get('href').split('/')[-2]
            self.wish_dict[mid]={'影片名':name,'上映日期':'','导演':'','编剧':'',\
                                 '主演':'','制片国家/地区':'','片长':'','评分':'','评分人数':''}
        #get all wish list
        while 1:
            sleep(uniform(1.5,4))
            if page==end:
                break
            try:
                NextPage='https://movie.douban.com'+soup.find(class_='next').link.get('href')
            except:
                break
            else:
                req=self.s.get(NextPage)
                soup=BeautifulSoup(req.text,'html.parser')
                page+=1
                print(f'第{page}页',req.status_code)
                wish=soup.find_all('a',href=re.compile("subject"))
                for i in range(len(wish)):
                    name=wish[i].get_text(strip=True)
                    mid=wish[i].get('href').split('/')[-2]
                    self.wish_dict[mid]={'影片名':name,'上映日期':'','导演':'','编剧':'',\
                                 '主演':'','制片国家/地区':'','片长':'','评分':'','评分人数':''}
        #add feature for every movie
        count=0
        st=perf_counter()
        total=len(self.wish_dict)
        fail=[]
        for mid in self.wish_dict.keys():
            count+=1
            if count%50==0:
                sleep(15)
            sleep(uniform(1.5,4))
            timebar(30,st,count/total)
            fail.append(self.get_feature(mid,'wish'))
        print('\n再次尝试打开失败的电影页')
        sleep(10)
        for fmid in fail:
            if fmid!=None:
                sleep(2)
                print()
                self.get_feature(fmid,'wish')
        return self.wish_dict

            
    def get_feature(self,mid,ty):
        if ty=='wish':
            dic=self.wish_dict
        elif ty=='saw':
            dic=self.saw_dict
        head='https://movie.douban.com/subject/'
        try:
            req2=self.s.get(head+mid)
            print('  '+dic[mid]['影片名']+'  爬虫状态：',req2.status_code,end=' ')
            if req2.status_code == requests.codes.ok:
                soup2=BeautifulSoup(req2.text,'html.parser')
                c=soup2.find(id='info').text
                intro=c.split('\n')
                for i in intro:
                    if ':' in i :
                        key,value=i.split(':',1)
                        if key in self.Keys:
                            dic[mid][key]=value.strip(' ')
                try:
                    dic[mid]['评分']=soup2.find(property=re.compile('average')).text
                except:
                    dic[mid]['评分']=''
                try:
                    dic[mid]['评分人数']=soup2.find(class_="rating_people").span.text
                except:
                    dic[mid]['评分人数']='0'
        except:
            print('\r打开电影页失败，失败的电影链接：'+head+mid)
            self.switch_header()
            return mid
    
    def saw_get(self,saw):
        date=saw(class_=re.compile('date'))[0].get_text(strip=True)
        try:
            star=saw(class_=re.compile('rat'))[0]['class'][0][6]
        except:
            star=''
        try:
            comment=saw(class_=re.compile('comment'))[0].get_text(strip=True)
        except:
            comment=''
        try:
            owntag_list=saw.find(class_='tags').get_text(strip=True).split(': ',1)[1].split(' ')
            owntag='/'.join(owntag_list)
        except:
            owntag=''
        name=saw.find(href=re.compile('subject')).get_text(strip=True)
        mid=saw.find(href=re.compile('subject')).get('href').split('/')[-2]
        return date,star,comment,owntag,name,mid
    
    def Saw(self):
        print('\n开始爬取'+self.id+'的看过列表')
        beg=eval(input('请输入你要爬取的起始页码（比如1）：'))
        end=eval(input('请输入终止页码（建议一次爬取10页以下）：'))
        page=beg
        Sfirstpage='https://movie.douban.com/people/'+self.id+'/collect?start='+str((beg-1)*30)+'&sort=time&rating=all&filter=all&mode=list'
        req=self.s.get(Sfirstpage)
        soup=BeautifulSoup(req.text,'html.parser')
        print(f'第{page}页',req.status_code)
        #get movie name and id
        saw=soup.find_all(class_=['item'])
        for i in range(len(saw)):
            date,star,comment,owntag,name,mid=self.saw_get(saw[i])
            self.saw_dict[mid]={'影片名':name,'上映日期':'','导演':'','编剧':'',\
                                '主演':'','制片国家/地区':'','片长':'','评分':'',\
                                '评分人数':'','用户评分':star,'短评':comment,\
                                '用户标签':owntag,'标记日期':date}
        #get all saw list
        while 1:
            sleep(uniform(1.5,4))
            if page==end:
                break
            try:
                NextPage='https://movie.douban.com'+soup.find(class_='next').link.get('href')
            except:
                break
            else:
                req=self.s.get(NextPage)
                soup=BeautifulSoup(req.text,'html.parser')
                page+=1
                print(f'第{page}页',req.status_code)
                saw=soup.find_all(class_=['item'])
                for i in range(len(saw)):
                    date,star,comment,owntag,name,mid=self.saw_get(saw[i])
                    self.saw_dict[mid]={'影片名':name,'上映日期':'','导演':'','编剧':'',\
                                        '主演':'','制片国家/地区':'','片长':'','评分':'',\
                                        '评分人数':'','用户评分':star,'短评':comment,\
                                        '用户标签':owntag,'标记日期':date}
        #add feature for every movie
        count=0
        st=perf_counter()
        total=len(self.saw_dict)
        fail=[]
        for mid in self.saw_dict.keys():
            count+=1
            if count%50==0:
                sleep(10)
            sleep(uniform(1.5,4))
            timebar(30,st,count/total)
            fail.append(self.get_feature(mid,'saw'))
        print('再次尝试打开失败的电影页')
        sleep(10)
        for fmid in fail:
            if fmid!=None:
                sleep(2)
                print()
                self.get_feature(fmid,'saw')
        return self.saw_dict
    
    
    def save_as_csv(self,choice):
        id=self.id
        if choice in ['a','c']:
            #保存想看
            wish_dict=self.wish_dict
            fw=open(id+'想看plus.csv','a',encoding='utf-8_sig')
            fw.write('影片名,上映日期,导演,编剧,主演,制片国家/地区,片长,评分,评分人数\n')
            for mid in wish_dict.keys():
                fw.write(noco(wish_dict[mid]['影片名'])+','+wish_dict[mid]['上映日期']+\
                        ','+noco(wish_dict[mid]['导演'])+','+noco(wish_dict[mid]['编剧'])+','+\
                        noco(wish_dict[mid]['主演'])+','+noco(wish_dict[mid]['制片国家/地区'])+','+\
                        wish_dict[mid]['片长']+','+wish_dict[mid]['评分']+','+\
                        wish_dict[mid]['评分人数']+'\n')
            fw.close()
        if choice in ['b','c']:
            #保存看过
            saw_dict=self.saw_dict
            fw2=open(id+'看过plus.csv','a',encoding='utf-8_sig')
            fw2.write('影片名,上映日期,导演,编剧,主演,制片国家/地区,片长,评分,评分人数,用户评分,短评,用户标签,标记日期\n')
            for mid in saw_dict.keys():
                fw2.write(noco(saw_dict[mid]['影片名'])+','+saw_dict[mid]['上映日期']+\
                        ','+noco(saw_dict[mid]['导演'])+','+noco(saw_dict[mid]['编剧'])+','+\
                        noco(saw_dict[mid]['主演'])+','+noco(saw_dict[mid]['制片国家/地区'])+','+\
                        saw_dict[mid]['片长']+','+saw_dict[mid]['评分']+','+\
                        saw_dict[mid]['评分人数']+','+saw_dict[mid]['用户评分']+','+\
                        noco(saw_dict[mid]['短评'])+','+noco(saw_dict[mid]['用户标签'])+','+\
                        saw_dict[mid]['标记日期']+'\n')
            fw2.close()
    
    def switch_header(self):
        headers0['User-Agent']=choice(user_agent_list)
        self.s.headers.update(headers0)

def main():
    print('嘿，据说你想要备份你的豆瓣电影记录？')
    print('''你需要知道：
    1. 本程序是一个爬虫程序，在爬取电影条目特征时会产生大量的网页访问，爬完后你的ip也许会被豆瓣封一段时间（登陆账号还是可以用啦）。
    2. 大量的网页访问意味着需要大量的流量。
    3. 爬取成功后，你的文件(csv)会被存储在该exe目录下，请不要在压缩包内使用该程序，解压后再使用。
    4. 可能会比较耗时。''')
    ans1=input('请确定你要开始备份(yes/no)： ')
    if ans1=='yes':
        Douid=input('请输入你的豆瓣id： ')
        clawer=Douban_Movie(doubanid=Douid)
        print('''
以下为选项
    A：想看列表
    B：看过列表
    C：想看+看过''')
        ans2=input('请输入你需要爬取的内容：')
        ans2=ans2.lower()
        if ans2=='a':
            clawer.Wish()
        elif ans2=='b':
            clawer.Saw()
        elif ans2=='c':
            clawer.Wish()
            clawer.Saw()
        clawer.save_as_csv(choice=ans2)
    print('\n问题反馈：jimsun6428@gmail.com | https://github.com/JimSunJing/douban_clawer')


main()
sleep(10)
over=input('按任意键退出')