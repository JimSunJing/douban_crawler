from bs4 import BeautifulSoup
import re
from time import sleep, ctime
import requests

headers0 = {'User-Agent':"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"}

def getList(doubanid,Type,subType,pageLimit=50,pageStart='0'):
    # 准备好session进行爬取
    sess = requests.Session()
    sess.headers.update(headers0)
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
    dealWithSubjects(soup.find_all('a',href=re.compile("subject")),List)
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
            dealWithSubjects(soup.find_all('a',href=re.compile("subject")),List)
            sleep(1)
    fileName = '_'.join([doubanid,prefix,suffix,str(ctime())])+'.csv'
    with open(fileName.replace(':','-').replace(' ','_'),'w',encoding='UTF-8') as f:
        f.write('doubanId,Type,title\n')
        for dic in List:
            f.write(','.join([dic['doubanId'],Type,dic['title']])+'\n')

def dealWithSubjects(itemList,container):
    # 负责将subject内容装入List
    for item in itemList:
        dic={'doubanId':item.get('href').split('/')[-2],\
            'title':item.get_text(strip=True)}
        container.append(dic)

def main():
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

    try:
        getList(douid,Type,subType,pageLimit,pageStart)
        print("应该保存成功，请在程序所在文件夹查找")
    except Exception as e:
        print(e)
        print('出错，请联系开发者')
    
    input("程序结束，按任意键退出")
    

if __name__ == '__main__':
    main()