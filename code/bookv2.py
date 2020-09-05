import requests, traceback
from bs4 import BeautifulSoup
from time import sleep
from random import uniform,choice
from doubanUtils import *

headers0 = {'User-Agent':getAgent()}

class Douban_Book:
    def __init__(self,doubanid):
        self.s=requests.Session()
        #加上头部
        self.s.headers.update(headers0)
        self.id=doubanid
        #wish dict format: {bookid:[书名,作者,译者,原作名,出版社,出版年,页数,ISBN,评分,评分人数]}
        self.wish_dict={}
        self.itemKeys=['subjectId','书名','封面','作者','译者','原作名','丛书',\
                    '出版社','出版年','页数','ISBN','评分','评分人数','标记日期','短评们']
        #saw dict format: {bookid:[书名,作者,译者,出版社,出版年,页数,ISBN,评分,评分人数,用户评分,评论,标记日期]}
        self.sawKeys = self.itemKeys + ['用户标签','用户评分','短评']
        self.saw_dict={}
        self.head='https://book.douban.com/subject/'

    def get_soup(self,url):
        req = self.s.get(url)
        return BeautifulSoup(req.text,'html.parser'), req.status_code
    
    def wish_get(self,item):
        date = item(class_=re.compile('date'))[0].get_text(strip=True)
        name = item(href=re.compile('subject'))[0].get_text(strip=True)
        url = item.find(href=re.compile('subject')).get('href')
        bid = url.split('/')[-2]
        return date,name,url,bid

    def wish_store(self,wishes,lastBid):
        for item in wishes:
            date,name,url,bid = self.wish_get(item)
            if (lastBid == str(bid)):
                return -1
            self.wish_dict[bid]={'书名':name,'豆瓣链接':url,\
                '标记日期':date,'subjectId':bid}

    def Wish(self):
        # 豆瓣图书反爬机制
        homepage='https://book.douban.com/people/'+self.id
        self.s.get(homepage)
        self.s.get(homepage+'/wish')

        print('\n开始爬取'+self.id+'的想读列表')
        beg,end = pageControl(10)
        page=beg
        firstpage='https://book.douban.com/people/'+self.id+\
            '/wish?sort=time&start='+str((beg-1)*30)\
            +'&filter=all&mode=list&tags_sort=count'
        soup, status = self.get_soup(firstpage)
        print(f'第{page}页',status)

        lastBid = getLastBackUpItem(self.id,"想读")

        #get book name and id
        if (self.wish_store(soup.find_all(class_='item'),lastBid) == -1):
            self.feature_helper(self.wish_dict)
            return self.wish_dict
        next_ = hasNextPage(soup)

        #get all wish list
        while (next_!=False) and (page < end):
            NextPage = 'https://book.douban.com'+next_
            soup, status = self.get_soup(NextPage)
            page += 1
            print(f'第{page}页',status)
            if (self.wish_store(soup.find_all(class_='item'),lastBid) == -1):
                self.feature_helper(self.wish_dict)
                return self.wish_dict
            next_ = hasNextPage(soup)

        #add feature for every book
        self.feature_helper(self.wish_dict)
        return self.wish_dict

    def feature_helper(self, dic):
        #add feature for every book
        print('一共有{}本书'.format(len(dic.keys())))
        count=0
        st=perf_counter()
        total=len(dic)
        fail=[]
        for bid in dic.keys():
            count+=1
            if count%50==0:
                sleep(10)
            sleep(uniform(1,2))
            timebar(30,st,count/total)
            fail.append(self.get_feature(bid,dic))
        print('\n再次尝试打开失败的书籍页')
        # sleep(10)
        for fbid in fail:
            if fbid!=None:
                sleep(2)
                print()
                self.get_feature(fbid,dic)
            
    def get_feature(self,bid,dic):
        head=self.head
        try:
            req2=self.s.get(head+bid)
            print('  '+dic[bid]['书名']+' 状态：',req2.status_code,end=' ')
            if req2.status_code == requests.codes.ok:
                soup2=BeautifulSoup(req2.text,'html.parser')
                c=soup2.find(id='info').text.replace('\xa0','').replace('\n   ','')
                intro=c.split('\n')
                for i in intro:
                    if ':' in i :
                        i=i.replace(' ','')
                        key,value=i.split(':',1)
                        dic[bid][key]=value
                dic[bid]['封面']=soup2.find('img').get('src')
                dic[bid]['出版年']=getYear(dic[bid]['出版年'])
                try:
                    dic[bid]['短评们']=getShortComments(soup2.findAll(class_="comment"))
                except:
                    dic[bid]['短评们']='...'
                try:
                    dic[bid]['评分']=soup2.find(property=re.compile('average')).text.strip(' ')
                except:
                    dic[bid]['评分']=''
                try:
                    dic[bid]['评分人数']=soup2.find(class_="rating_people").span.text.strip(' ')
                except:
                    dic[bid]['评分人数']='0'
        except Exception as e:
            print('\r打开书籍页失败，失败的书籍链接：'+head+bid)
            print(e)
            self.switch_header()
            return bid
    
    def saw_store(self,saw,lastBid):
        for item in saw:
            date,star,comment,owntag,name,bid=self.saw_get(item)
            if (lastBid == str(bid)):
                return -1
            self.saw_dict[bid]={'书名':name,'封面':'','豆瓣链接':self.head+bid,\
                '标记日期':date,'用户评分':star,'短评':comment,\
                '用户标签':owntag,'subjectId':bid}

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
        bid=saw.find(href=re.compile('subject')).get('href').split('/')[-2]
        return date,star,comment,owntag,name,bid
    
    def Saw(self):
        # 豆瓣图书反爬机制
        homepage='https://book.douban.com/people/'+self.id
        self.s.get(homepage)

        print('\n开始爬取'+self.id+'的读过列表')
        beg, end = pageControl(10)
        page=beg
        
        Sfirstpage='https://book.douban.com/people/'+self.id+\
            '/collect?&sort=time&start='+str((beg-1)*30)+\
            '&filter=all&mode=list'
        soup, status = self.get_soup(Sfirstpage)
        print(f'第{page}页',status)

        lastBid = getLastBackUpItem(self.id,"读过")

        #get book name and id
        if (self.saw_store(soup.find_all(class_='item'),lastBid) == -1):
            self.feature_helper(self.saw_dict)
            return self.saw_dict
        next_ = hasNextPage(soup)

        #get all saw list
        while (next_ != False) and (page < end):
            sleep(1.3)
            NextPage='https://book.douban.com'+next_
            soup, status = self.get_soup(NextPage)
            page += 1
            print(f'第{page}页',status)
            if (self.saw_store(soup.find_all(class_='item'),lastBid) == -1):
                self.feature_helper(self.saw_dict)
                return self.saw_dict
            next_ = hasNextPage(soup)

        #add feature for every book
        self.feature_helper(self.saw_dict)
        return self.saw_dict
    
    def save_helper(self, dic, Type):
        with open(fn(self.id+'-'+getFormatTime()+Type+'plus.csv'),\
            'a',encoding='utf-8_sig') as f:
            fieldNames = self.sawKeys if Type == '读过' else self.itemKeys
            writer = csv.DictWriter(f, fieldnames=fieldNames, restval="...", extrasaction='ignore')
            writer.writeheader()
            for bid in dic.keys():
                writer.writerow(dic[bid])
    
    def save_as_csv(self,choice):
        if choice in ['a','c']:
            self.save_helper(self.wish_dict, '想读')
        if choice in ['b','c']:
            self.save_helper(self.saw_dict, '读过')
    
    def switch_header(self):
        headers0['User-Agent']=choice(user_agent_list)
        self.s.headers.update(headers0)

    def add_cookies(self,raw_cookies):
        cookies=getCookie(raw_cookies)
        self.s.cookies.update(cookies)


    def main(self):
        print('''
        以下为选项
            A：想读列表
            B：读过列表
            C：想读+读过''')
        ans2=input('请输入你需要爬取的内容：')
        ans2=ans2.lower()
        if ans2=='a':
            self.Wish()
        elif ans2=='b':
            self.Saw()
        elif ans2=='c':
            self.Wish()
            self.Saw()
        self.save_as_csv(choice=ans2)

def main():
    print('嘿，据说你想要备份你的豆瓣书籍记录？')
    print('''你需要知道：
    1. 本程序是一个爬虫程序，在爬取书籍条目特征时会产生大量的网页访问，爬完后你的ip也许会被豆瓣封一段时间（登陆账号还是可以用啦）。
    2. 大量的网页访问意味着需要大量的流量。
    3. 爬取成功后，你的文件(csv)会被存储在该exe目录下，请不要在压缩包内使用该程序，解压后再使用。
    4. 可能会比较耗时。''')
    ans1=input('请确定你要开始备份(yes/no)： ')
    if ans1=='yes':
        Douid=input('请输入你的豆瓣id： ')
        clawer=Douban_Book(doubanid=Douid)
        # book.douban.com 有反爬，需要cookies
        print("由于豆瓣图书的防爬虫机制，需要你提供cookies")
        raw_cookies=input('输入cookies: ')
        clawer.add_cookies(raw_cookies)
        clawer.main()
    print('\n问题反馈：jimsun6428@gmail.com | https://github.com/JimSunJing/douban_clawer')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
    finally:
        sleep(10)
        over=input('按任意键退出')