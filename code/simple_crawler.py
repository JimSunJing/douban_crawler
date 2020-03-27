from bs4 import BeautifulSoup
import re
from time import sleep, ctime
import requests
import csv

headers0 = {'User-Agent':"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"}

def getList(doubanid,Type,subType,pageLimit=50,pageStart='0'):
    # 准备好session进行爬取
    sess = requests.Session()
    sess.headers.update(headers0)
    if (Type=='b'): sess.get('https://book.douban.com/people/'+doubanid)
    # 根据输入准备好URL模板
    prefix=''
    suffix=subType
    if Type=='f':
        prefix='movie'
    elif Type=='b':
        prefix='book'
    elif Type=='m':
        prefix='music'
    else:
        print("输入类型错误")
        return -1
    Module='https://'+prefix+'.douban.com/people/'+doubanid+'/'+\
        suffix+'?start={start}&sort=time&rating=all&filter=all&mode=list'
    # 获取第一页
    request=sess.get(Module.format(start=pageStart))
    page=1
    print(f'第{page}页',request.reason)
    List=[]
    soup=BeautifulSoup(request.text,'html.parser')
    dealWithSubjects(soup.find_all(class_='item-show'),List,subType)
    # 根据页面中的“下一页”判断是否继续爬取
    while page < pageLimit:
        try:
            if Type=='m':
                NextPage=soup.find(class_='next').link.get('href')
            else:
                NextPage='https://'+prefix+'.douban.com'+soup.find(class_='next').link.get('href')
        except:
            break
        else:
            request=sess.get(NextPage)
            page+=1
            print(f'第{page}页',request.reason)
            soup=BeautifulSoup(request.text,'html.parser')
            dealWithSubjects(soup.find_all(class_='item-show'),List,subType)
            sleep(1.3)
    fileName = '_'.join([doubanid,prefix,suffix,str(ctime())])+'.csv'
    with open(fileName.replace(':','-').replace(' ','_'),'w',encoding='UTF-8') as f:
        fieldName = list(List[0].keys())
        fieldName.append('Type')
        writer = csv.DictWriter(f,fieldnames = fieldName)
        writer.writeheader()
        for dic in List:
            dic.update({'Type':Type})
            writer.writerow(dic)


def dealWithSubjects(itemList,container,Type):
    # 负责将subject内容装入List
    for item in itemList:
        doubanId = item.find('a',href=re.compile("subject")).get('href').split('/')[-2]
        title = item.find('a',href=re.compile("subject")).get_text(strip=True)
        if (Type!='collect'):
            dic = {'doubanId':doubanId,'title':title}
        else:
            try:
                star = item.find_all('span')[-1]['class'][0][-3]
                if not str.isdigit(star): star = ''
            except:
                star = ''
            date = item.find(class_='date').get_text(strip=True)
            dic = {'doubanId':doubanId,'title':title,'date':date,'star':star}
        container.append(dic)



def main():
    if input("这是一个爬取豆瓣个人书影音记录的程序，如果要开始请输入y: ")!='y': return
    douid=input('请输入你的豆瓣id: ')
    Type=input('输入你要爬取的类型(图书=b,电影=f,音乐=m): ')
    subType=input('输入想要爬取的内容(想看/想读/想听=w,看过/听过=c): ')
    pageStart=input('有想从固定页面开始吗？如果有请输入（默认1）: ')
    pageLimit=input('限制爬取页数（默认50）: ')
    if pageLimit!='':
        pageLimit = int(pageLimit)
    else:
        pageLimit = 50
    if pageStart=='':
        pageStart = '0'
    else:
        pageStart = str((int(pageStart)-1)*30)
    if subType=='w':
        subType='wish'
    elif subType=='c':
        subType='collect'
    else:
        print("爬取内容（想看,看过...）输入错误")
        return

    # try:
    getList(douid,Type,subType,pageLimit,pageStart)
    print("应该保存成功，请在程序所在文件夹查找")
    # except Exception as e:
    #     print(e)
    #     print('出错，请联系开发者')
    
    input("程序结束，按任意键退出")
    

if __name__ == '__main__':
    main()