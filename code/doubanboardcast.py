from bs4 import BeautifulSoup
import re
import time
import requests
import random

def getwords(item):
    txt=item.get_text(strip=False).replace(' ','').replace('\r','\n')\
          .replace('\n\n\n\n\n\n','\$#n').replace('\n\n\n\n',' ').replace('\n','')\
          .replace('$#','').replace('\xa0','').replace('\\n','\n').replace('+','')
    try:
        pic=item(class_=re.compile('view-large'))[0]['href']
    except:
        pic=''
    return txt+pic

def madeBox(txt):
    box='\t------------------------------------------------------------------------------------------\n'+'\t'+\
        txt+'\n\t'+'------------------------------------------------------------------------------------------\n'
    return box

def dealwithshare(txt1,txt2):
    li=txt1.split('\n')
    li[-4]=li[-4]+' @'+li[-3]
    for word in li:
        word.replace(' ','')
    li.remove(li[-3])
    li2=txt2.split('\n')
    li.insert(-2,madeBox(''.join(li2[0:-3])))
    return '\n'.join(li)



headers = {
    'Uesr-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
}
rawji_america='ll="108297"; bid=TFLDE9t44mY; _pk_ses.100001.8cb4=*; __utmc=30149280; __utma=30149280.995009761.1561041533.1561041533.1561042634.2; __utmz=30149280.1561042634.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt=1; dbcl2="198268851:+gNufdpzGAw"; ck=AnNe; ap_v=0,6.0; douban-profile-remind=1; push_noty_num=0; push_doumail_num=0; __utmv=30149280.19826; __yadk_uid=nFY3eG607ZoqEtBaMMWYVuqNCXZIycd6; douban-fav-remind=1; __utmb=30149280.12.10.1561042634; _pk_id.100001.8cb4=9f8810e4b7a61874.1561041531.1.1561043477.1561041531.'
rawji='ll="108297"; bid=BQLi_2UIMh8; __utmc=30149280; __yadk_uid=Fl0aRuIUatWP1JCilVDTUzW1h2R71qWN; push_noty_num=0; push_doumail_num=0; __utmv=30149280.19826; ps=y; _vwo_uuid_v2=DD4476A9DC58A854DCFFF0D91547908DA|534c6354fc5886543fd8704a8eb02aeb; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1561087673%2C%22https%3A%2F%2Faccounts.douban.com%2Faccounts%2Fsafety%2Funlock_phone%22%5D; _pk_ses.100001.8cb4=*; __utma=30149280.1984600914.1561080464.1561080464.1561087675.2; __utmz=30149280.1561087675.2.2.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/accounts/safety/unlock_phone; __utmt=1; dbcl2="198268851:Co+RFApa9xQ"; ck=g0Bz; douban-profile-remind=1; ap_v=0,6.0; douban-fav-remind=1; __gads=ID=750f05eb1a424666:T=1561087843:S=ALNI_MaWUrys775-4HBWVFaGDarZgSJRCA; _pk_id.100001.8cb4=3db8de030f64f76f.1561080462.2.1561087888.1561080727.; __utmb=30149280.21.10.1561087675'

def getCookie(raw_cookies):
    cookies={}
    for line in raw_cookies.split(';'):
        key,value=line.split('=',1) #1代表只分一次，得到两个数据
        cookies[key]=value
    return cookies


def getHtml(douid,raw_cookies=rawji,beg=1,end=10):
    html_list=[]
    cookies={}
    cookies=getCookie(raw_cookies)
    firstpage='https://www.douban.com/people/'+douid+'/statuses?p='+str(beg)
    s=requests.Session()
    res=s.get(firstpage,headers=headers,cookies=cookies)
    html_list.append(res.text)
    print(f'第{beg}页',res.status_code,res.reason)
    while beg<end:
        beg+=1
        time.sleep(random.uniform(1,5))
        try:
            nextpage='https://www.douban.com/people/'+douid+'/statuses?p='+str(beg)
            res2=s.get(nextpage,headers=headers,cookies=cookies)
            soup=BeautifulSoup(res2.text,"html.parser")
            items=soup.find_all(class_=re.compile('status-item'))
            print(f'第{beg}页',res2.status_code,res.reason)
        except:
            print('网页请求错误')
        else:
            html_list.append(res2.text)
    return html_list

def saveHtml(douid,html_list,beg,end):  
    file_name=douid+"'s_board_cast_page_"+str(beg)+'-'+str(end)
    with open (file_name.replace('/','_')+".html","wb") as f:
        for file_content in html_list:
            #写文件用bytes而不是str，所以要转码  
            f.write(bytes(file_content+'\n',encoding='utf-8'))
            print(f'第{beg}页HTML完成')
            beg+=1

def saveTXT(douid,htmlList,beg,end):
    with open(douid+'board_cast_'+str(beg)+'-'+str(end)+'.txt','w',encoding='utf-8_sig') as f:
        for text in htmlList:
            soup=BeautifulSoup(text,"html.parser")
            items=soup.find_all(class_=re.compile('status-item'))
            t=0
            for i in range(len(items)):
                if t>=len(items):
                    break
                txt=getwords(items[t])
                if '转发:' in txt:
                    origin=getwords(items[t+1])
                    txt=dealwithshare(txt,origin)
                    t+=1
                f.write(str(txt)+'\n')
                t+=1
            print(f'第{beg}页TXT完成')
            beg+=1

def main():
    print('hello，这是一个备份豆瓣广播的程序。\n需要你自己的cookie用来爬取广播。')
    choice=input('该过程有风险，请确定你要开始备份(yes/no)：')
    if choice=='yes':
        user_raw=input('请输入你的cookie(最后不要带空格)：')
        doubanid=input('请输入你的豆瓣id：')
        begin=eval(input('请输入你开始备份的页码(比如1)：'))
        endpage=eval(input('请输入你结束备份的页码：'))
        Hlist=getHtml(douid=doubanid,raw_cookies=user_raw,beg=begin,end=endpage)
        print(type(Hlist[0]))
        print(f'爬取了{len(Hlist)}页')
        choice2=input('请选择你要输出html结果(a)还是文本txt结果(b)或者我全都要(all)：')
        choice2=choice2.lower()
        if choice2 == 'a':
            try:
                saveHtml(doubanid,Hlist,beg=begin,end=endpage)
            except Exception as e:
                print(e)
                print('储存html文件出错')
                print('问题反馈：jimsun6428@gmail.com | https://github.com/JimSunJing/douban_clawer')
                over=input('按任意键退出')
            else:
                print('成功')
        elif choice2 == 'b':
            try:
                saveTXT(doubanid,Hlist,beg=begin,end=endpage)
            except Exception as e:
                print(e)
                print('储存txt文件出错')
                print('问题反馈：jimsun6428@gmail.com | https://github.com/JimSunJing/douban_clawer')
                over=input('按任意键退出')
            else:
                print('成功')
        elif choice2 == 'all':
            try:
                saveHtml(doubanid,Hlist,beg=begin,end=endpage)
                saveTXT(doubanid,Hlist,beg=begin,end=endpage)
            except Exception as e:
                print(e)
                print('出错')
        print('程序结束，文件已存在该exe目录中')
        print('问题反馈：jimsun6428@gmail.com | https://github.com/JimSunJing/douban_clawer')
        over=input('按任意键退出')

main()