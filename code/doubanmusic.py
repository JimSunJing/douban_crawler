from bs4 import BeautifulSoup
import re
import time
import requests

headers0 = {'User-Agent':"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"}

def Musappend(Mdict,Items):
    for it in Items:
        title=it('a')[0].get_text(strip=True)
        date=it(class_=re.compile('date'))[0].get_text(strip=True)
        try:
            stars=it(class_=re.compile('rat'))[0]['class'][0][6]
        except:
            stars='Nah'
        try:
            comment=it(class_=re.compile('comm'))[0].get_text(strip=True).replace('\n','-')
        except:
            comment='Nah'
        try:
            intro=it(class_='intro')[0].get_text(strip=True)
        except:
            intro='Nah'
        Mdict[title]=[intro,date,stars,comment]

def HeardList(doubanid):
    firstpage='https://music.douban.com/people/'+doubanid+'/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count'
    sess = requests.Session()
    sess.headers.update(headers0)
    request=sess.get(firstpage)
    soup=BeautifulSoup(request.text,'html.parser')
    items=soup.find_all(class_=re.compile('item'),id=re.compile('li'))
    heard_dic={}
    Musappend(Mdict=heard_dic,Items=items)
    page=1
    print(f'第{page}页',request.reason)
    while 1:
        time.sleep(1)
        try:
            NextPage=soup.find(class_='next').link.get('href')
        except:
            print('已到最终页')
            break
        else:
            request=sess.get(NextPage)
            soup=BeautifulSoup(request.text,'html.parser')
            items=soup.find_all(class_=re.compile('item'),id=re.compile('li'))
            Musappend(Mdict=heard_dic,Items=items)
            page+=1
            print(f'第{page}页',request.reason)
    fw=open(doubanid+'_Heard_List.csv','w',encoding='utf-8_sig')
    fw.write('专辑/单曲,简介,日期,评分,短评\n')
    for title in heard_dic.keys():
        fw.write(title.replace(',','、').replace('，','、')+','+heard_dic[title][0].replace(',','、').replace('，','、')+\
                 ','+heard_dic[title][1]+','+heard_dic[title][2]+\
                 ','+heard_dic[title][3].replace(',','、').replace('，','、')+'\n')
    fw.close()

def WMusappend(Mdict,Items):
    for it in Items:
        title=it('a')[0].get_text(strip=True)
        date=it(class_=re.compile('date'))[0].get_text(strip=True)
        try:
            comment=it(class_=re.compile('comm'))[0].get_text(strip=True).replace('\n','-')
        except:
            comment='Nah'
        try:
            intro=it(class_='intro')[0].get_text(strip=True)
        except:
            intro='Nah'
        Mdict[title]=[intro,date,comment]


def WHeardList(doubanid):
    firstpage='https://music.douban.com/people/'+doubanid+'/wish?sort=time&start=0&filter=all&mode=list&tags_sort=count'
    sess = requests.Session()
    sess.headers.update(headers0)
    request=sess.get(firstpage)
    soup=BeautifulSoup(request.text,'html.parser')
    items=soup.find_all(class_=re.compile('item'),id=re.compile('li'))
    whear_dic={}
    WMusappend(Mdict=whear_dic,Items=items)
    page=1
    print(f'第{page}页',request.reason)
    while 1:
        time.sleep(1)
        try:
            NextPage=soup.find(class_='next').link.get('href')
        except:
            print('已到最终页')
            break
        else:
            request=sess.get(NextPage)
            soup=BeautifulSoup(request.text,'html.parser')
            items=soup.find_all(class_=re.compile('item'),id=re.compile('li'))
            Musappend(Mdict=whear_dic,Items=items)
            page+=1
            print(f'第{page}页',request.reason)
    fw=open(doubanid+'_MusicWish_List.csv','w',encoding='utf-8_sig')
    fw.write('专辑/单曲,简介,日期,留言\n')
    for title in whear_dic.keys():
        fw.write(title.replace(',','、').replace('，','、')+','+whear_dic[title][0].replace(',','、').replace('，','、')+\
                 ','+whear_dic[title][1]+','+whear_dic[title][2].replace(',','、').replace('，','、')+'\n')
    fw.close()


def main():
    print('本程序备份用户的豆瓣音乐')
    choice=input('请确定你要备份(yes/no)：')
    if choice == 'yes':
        id=input('请输入你的豆瓣ID：')
        print('开始备份听过列表')
        HeardList(doubanid=id)
        time.sleep(2)
        print('开始备份想听列表')
        WHeardList(doubanid=id)
        print('备份已存在该exe所在目录下（如果没出错的话）')
        print('问题反馈：jimsun6428@gmail.com | https://github.com/JimSunJing/douban_clawer')
        input('按任意键退出')
    else:
        print('bye')

main()