import urllib.request
from bs4 import BeautifulSoup
import re
import time
import random
from selenium import webdriver

headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}

def BWappend(BWdict,Items):
    for i in range(len(Items)):
        try:
            title=Items[i](href=re.compile('subject'))[0].get_text(strip=True)
            intro=Items[i](class_='intro')[0].get_text(strip=True).split('/')
            author=intro[0]
            publisher=intro[-3]
            translater='/'.join(intro[1:-3])
            BWdict[title]=[author,translater,publisher]
        except:
            title=Items[i](href=re.compile('subject'))[0].get_text(strip=True)
            intro=Items[i](class_='intro')[0].get_text(strip=True).split(';')
            author=intro[0]
            publisher=intro[-1]
            translater='/'.join(intro[1:-1])
            BWdict[title]=[author,translater,publisher]

def bookwish(doubanid):
    firstpage='https://book.douban.com/people/'+doubanid+'/wish?sort=time&start=0&filter=all&mode=list&tags_sort=count'
    request=urllib.request.urlopen(url=firstpage)
    soup=BeautifulSoup(request.read())
    page=1
    print(f'第{page}页',request.reason)
    bookwishdict={}
    items=soup.find_all(class_='item')
    BWappend(BWdict=bookwishdict,Items=items)
    while 1:
        try:
            Nextpage='https://book.douban.com'+soup.find(class_='next').link.get('href')
        except:
            print('已到最终页')
            break
        else:
            response=urllib.request.Request(url=Nextpage,headers=headers)
            request=urllib.request.urlopen(response)
            soup=BeautifulSoup(request.read())
            page+=1
            print(f'第{page}页',request.reason)
            items2=soup.find_all(class_='item')
            BWappend(BWdict=bookwishdict,Items=items2)
            time.sleep(1)
    fw=open(doubanid+'_TOread_List.csv','w',encoding='utf-8_sig')
    fw.write('书名,作者,译者,出版社\n')
    for title in bookwishdict.keys():
        fw.write(title.replace(',','、').replace('，','、')+','+bookwishdict[title][0]+\
                 ','+bookwishdict[title][1]+','+bookwishdict[title][2].replace(',','、').replace('，','、')+'\n')
    fw.close()

def BRappend(BRdict,Items):
    for i in range(len(Items)):
        title=Items[i]('a')[0].get_text(strip=True)
        date=Items[i](class_=re.compile('date'))[0].get_text(strip=True)
        try:
            intro=Items[i](class_=re.compile('intro'))[0].get_text(strip=True).split('/')
            author=intro[0]
            publisher=intro[-3]
            translater='/'.join(intro[1:-3])
        except:
            intro=Items[i](class_=re.compile('intro'))[0].get_text(strip=True).replace(';','/').split('/')
            author=intro[0]
            publisher=intro[-1]
            translater='/'.join(intro[1:-1])
        try:
            comment=Items[i](class_=re.compile('comm'))[0].get_text(strip=True).replace('\n','-')
        except:
            comment='Nah'
        try:
            stars=Items[i](class_=re.compile('rat'))[0]['class'][0][6]
        except:
            stars='Nah'
        BRdict[title]=[author,translater,publisher,stars,date,comment]

def ReadBookList(doubanid):
    mainpage='https://book.douban.com/people/'+doubanid
    firstpage='https://book.douban.com/people/'+doubanid+'/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count'
    browser = webdriver.Chrome()
    browser.get(mainpage)
    browser.get(firstpage)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    items=soup.find_all(class_=re.compile('item'),id=re.compile('li'))
    read_book={}
    BRappend(BRdict=read_book,Items=items)
    page=1
    print(f"浏览器处理第{page}页")
    while 1:
        time.sleep(2)
        try:
            NextPage='https://book.douban.com'+soup.find(class_='next').link.get('href')
        except:
            print('已到最终页')
            break
        else:
            browser.get(NextPage)
            soup=BeautifulSoup(browser.page_source,"html.parser")
            items=soup.find_all(class_=re.compile('item'),id=re.compile('li'))
            page+=1
            print(f"浏览器处理第{page}页")
            BRappend(BRdict=read_book,Items=items)
    fw=open(doubanid+'_READ_List.csv','w',encoding='utf-8_sig')
    fw.write('书名,作者,译者,出版社,评分,日期,短评\n')
    for title in read_book.keys():
        fw.write(title.replace(',','、').replace('，','、')+','+read_book[title][0]+\
                 ','+read_book[title][1]+','+read_book[title][2].replace(',','、').replace('，','、')+\
                 ','+read_book[title][3]+','+read_book[title][4]+','+read_book[title][5].replace(',','、').replace('，','、')+'\n')
    fw.close()
    return read_book


def main():
    print('注意：本脚本将会使用自动打开chrome浏览器的方法获取豆瓣阅读已读list')
    print('''你的电脑应该需要装一个chrome，
第一次运行时可能会弹出防火墙提示导致失败，请选择信任再次运行该脚本''')
    choice=input('请确定你要运行此脚本(yes/no):')
    if choice=='yes':
        douid=input('请输入想备份的豆瓣id：')
        print('开始备份-想读-列表')
        bookwish(doubanid=douid)
        time.sleep(2)
        print('开始备份-已读-列表')
        ReadBookList(doubanid=douid)
        print('程序结束，文件已存在该exe目录中')
        print('问题反馈：jimsun6428@gmail.com | https://github.com/JimSunJing/douban_clawer')
        end=input('按任意键退出')
    else:
        print('bye')

main()