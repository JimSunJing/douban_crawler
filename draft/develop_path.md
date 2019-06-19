
## 想看列表爬取


```python
#豆瓣电影主页：https://movie.douban.com/people/91835006/
#想看首页url：https://movie.douban.com/people/91835006/wish
#按列表形式第一页：https://movie.douban.com/people/91835006/wish?start=0&sort=time&rating=all&filter=all&mode=list
#第二页: https://movie.douban.com/people/91835006/wish?start=30&sort=time&rating=all&filter=all&mode=list
#第三页: https://movie.douban.com/people/91835006/wish?start=60&sort=time&rating=all&filter=all&mode=list
import urllib.request
from bs4 import BeautifulSoup
import re
import time
import random
from selenium import webdriver
```


```python
url='https://movie.douban.com/people/91835006/wish?start=0&sort=time&rating=all&filter=all&mode=list'
request=urllib.request.urlopen(url=url)
data=request.read()
print('Status:',request.status,request.reason)
for k,v in request.getheaders():
    print('{}: {}'.format(k,v))
```

    Status: 200 OK
    Date: Tue, 18 Jun 2019 05:27:32 GMT
    Content-Type: text/html; charset=utf-8
    Transfer-Encoding: chunked
    Connection: close
    Vary: Accept-Encoding
    X-Xss-Protection: 1; mode=block
    X-Douban-Mobileapp: 0
    Expires: Sun, 1 Jan 2006 01:00:00 GMT
    Pragma: no-cache
    Cache-Control: must-revalidate, no-cache, private
    Set-Cookie: ll="118161"; domain=.douban.com; path=/; expires=Wed, 17-Jun-2020 05:27:32 GMT
    Set-Cookie: bid=7_GMh7XrBRc; Expires=Wed, 17-Jun-20 05:27:32 GMT; Domain=.douban.com; Path=/
    X-DOUBAN-NEWBID: 7_GMh7XrBRc
    X-DAE-Node: anson77
    X-DAE-App: movie
    Server: dae
    X-Content-Type-Options: nosniff
    


```python
html=BeautifulSoup(data)
items=html.find_all('a',href=re.compile("subject"))
wish=[]
for item in items:
    wish.append(item.string.replace(' ','').strip('\n'))
```


```python
str(wish[1])
```




    '纸月亮/PaperMoon'




```python
NextPage='https://movie.douban.com'+html.find(class_='next').link.get('href')
```


```python
lastp='https://movie.douban.com/people/91835006/wish?start=390&sort=time&rating=all&filter=all&mode=list'
lrequest=urllib.request.urlopen(url=lastp)
ldata=lrequest.read()
lasoup=BeautifulSoup(ldata)
```


```python
try:
    lasoup.find(class_='next').link.get('href')
except:
    print('No Next')
```

    No Next
    


```python

def getWishList(doubanid='91835006'):
    firstpage='https://movie.douban.com/people/'+doubanid+'/wish?start=0&sort=time&rating=all&filter=all&mode=list'
    request=urllib.request.urlopen(url=firstpage)
    print('Status:',request.status,request.reason)
    wish_list=[]
    soup=BeautifulSoup(request.read())
    for item in soup.find_all('a',href=re.compile("subject")):
        wish_list.append(item.string.replace(' ','').strip('\n'))
    while 1:
        try:
            NextPage='https://movie.douban.com'+soup.find(class_='next').link.get('href')
        except:
            break
        else:
            request=urllib.request.urlopen(url=NextPage)
            print('Status:',request.status,request.reason)
            soup=BeautifulSoup(request.read())
            for item in soup.find_all('a',href=re.compile("subject")):
                wish_list.append(item.string.replace(' ','').strip('\n'))
            time.sleep(0.5)
    fw=open(doubanid+'_Wish_List.txt','w',encoding='utf-8_sig')
    fw.write('中文名 / 原名 \n')
    for item in wish_list:
        fw.write(str(item)+'\n')
    return wish_list
```


```python
wishl=getWishList()
```

    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    

看过LIST


```python
url='https://movie.douban.com/people/91835006/collect'
request=urllib.request.urlopen(url=url)
print('Status:',request.status,request.reason)
soup=BeautifulSoup(request.read())
```

    Status: 200 OK
    


```python
titandcom=soup.find_all(class_=['item'])
```


```python
def TCappend(TC,titandcom):
    for i in range(len(titandcom)):
        title=titandcom[i].em.text
        date=titandcom[i](class_=re.compile('date'))[0].text
        try:
            star=titandcom[i](class_=re.compile('rat'))[0]['class'][0][6]
        except:
            star='Nah'
        try:
            comment=titandcom[i](class_=re.compile('comment'))[0].text
        except:
            comment='Nah'
        TC[title]=[date,star,comment]
```


```python
def getSawList(doubanid='91835006'):
    firstpage='https://movie.douban.com/people/'+doubanid+'/collect'
    request=urllib.request.urlopen(url=firstpage)
    print('Status:',request.status,request.reason)
    saw_dic={}
    soup=BeautifulSoup(request.read())
    tandc=soup.find_all(class_=['item'])
    TCappend(TC=saw_dic,titandcom=tandc)
    while 1:
        try:
            NextPage='https://movie.douban.com'+soup.find(class_='next').link.get('href')
        except:
            break
        else:
            request=urllib.request.urlopen(url=NextPage)
            print('Status:',request.status,request.reason)
            soup=BeautifulSoup(request.read())
            tandc=soup.find_all(class_=['item'])
            TCappend(saw_dic,titandcom=tandc)
            time.sleep(0.5)
    fw=open(doubanid+'_Watched_List.csv','w',encoding='utf-8_sig')
    fw.write('中文名/原名,标记日期,评分,短评\n')
    for title in saw_dic.keys():
        fw.write(title.replace(',','、').replace('，','、')+','+saw_dic[title][0]+\
                 ','+saw_dic[title][1]+','+saw_dic[title][2].replace(',','、').replace('，','、')+'\n')
    return saw_dic
```


```python
saw=getSawList()
```

    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    Status: 200 OK
    


```python
fw=open('91835006_Watched_List.csv','w',encoding='utf-8')
fw.write('中文名/原名,标记日期,评分,短评\n')
for title in saw.keys():
    fw.write(title.replace(',','、').replace('，','、')+','+saw[title][0]+','+\
                 saw[title][1]+','+saw[title][2].replace(',','、').replace('，','、')+'\n')
```


```python
import pandas as pd
```


```python
data=pd.read_csv('_Watched_List.csv')
```


```python
data.head(10)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>中文名/原名</th>
      <th>标记日期</th>
      <th>评分</th>
      <th>短评</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>来自未来的故事 / Stories from Our Future</td>
      <td>2019-06-16</td>
      <td>4/5</td>
      <td>第一集挺有趣</td>
    </tr>
    <tr>
      <th>1</th>
      <td>办公室   第二季 / The Office Season 2</td>
      <td>2019-06-15</td>
      <td>4/5</td>
      <td>「当你入聘一家公司、发现大部分工作是babysitting你的小老板」</td>
    </tr>
    <tr>
      <th>2</th>
      <td>黑镜 第五季 / Black Mirror Season 5</td>
      <td>2019-06-07</td>
      <td>4/5</td>
      <td>麦粒这集很棒呀、有种童话故事的感觉、善恶分明的故事果然非常满足观众。但转念一想、麦粒这集是很...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>切尔诺贝利 / Chernobyl</td>
      <td>2019-06-05</td>
      <td>5/5</td>
      <td>向敢于直面真相的人致敬！鄙视那些掩盖真相的国家机器。</td>
    </tr>
    <tr>
      <th>4</th>
      <td>杀死伊芙 第二季 / Killing Eve Season 2</td>
      <td>2019-05-31</td>
      <td>4/5</td>
      <td>Nah</td>
    </tr>
    <tr>
      <th>5</th>
      <td>女巫 / The VVitch: A New-England Folktale</td>
      <td>2019-05-21</td>
      <td>4/5</td>
      <td>弟弟caleb好可爱啊、大女儿也美的发光。</td>
    </tr>
    <tr>
      <th>6</th>
      <td>海蒂和爷爷 / Heidi</td>
      <td>2019-05-19</td>
      <td>4/5</td>
      <td>真的是童话一般啊～淳朴的民风和善良的有钱人。希望世界真的如此美好、灯光一亮、梦醒了。</td>
    </tr>
    <tr>
      <th>7</th>
      <td>绑定 第一季 / Bonding Season 1</td>
      <td>2019-05-16</td>
      <td>4/5</td>
      <td>警察一般把我们看作是妓女女主的这句话同时也描述了在大众眼光中、BDSM是怎样的形象。导演以如...</td>
    </tr>
    <tr>
      <th>8</th>
      <td>大侦探皮卡丘 / Pokémon Detective Pikachu</td>
      <td>2019-05-12</td>
      <td>2/5</td>
      <td>Nah</td>
    </tr>
    <tr>
      <th>9</th>
      <td>性爱自修室 第一季 / Sex Education Season 1</td>
      <td>2019-05-09</td>
      <td>5/5</td>
      <td>该死的校长！成年人的欺诈、偏执都在他身上淋漓尽致体现了。编剧第二季给我搞他！</td>
    </tr>
  </tbody>
</table>
</div>




```python
page=0
print(f'第{page}页')
```

    第0页
    

## 豆瓣读书

### 想读列表


```python
bookurl='https://book.douban.com/people/91835006/wish?sort=time&start=0&filter=all&mode=list&tags_sort=count'
response=urllib.request.Request(url=bookurl,headers=headers)
request=urllib.request.urlopen(response)
soup=BeautifulSoup(request.read())
print('Status:',request.status,request.reason)
```

    Status: 200 OK
    


```python
items=soup.find_all(class_='item')
```


```python
items
```




    [<li class="item" id="list26004211">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/26004211/">
                             数值最优化方法
                         </a>
     </div>
     <div class="date">
                     2019-06-06
                     </div>
     </div>
     <div class="hide" id="grid26004211">
     <div class="grid-date">
     <span class="intro">高立 / 北京大学出版社 / 2014-9 / 28</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list3535331">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/3535331/">
                             食经
                         </a>
     </div>
     <div class="date">
                     2019-06-06
                     </div>
     </div>
     <div class="hide" id="grid3535331">
     <div class="grid-date">
     <span class="intro">陈梦因 / 百花文艺出版社 / 2009-1 / 78.00元</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list1465543">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/1465543/">
                             异端的权利
                         </a>
     </div>
     <div class="date">
                     2019-05-29
                     </div>
     </div>
     <div class="hide" id="grid1465543">
     <div class="grid-date">
     <span class="intro">[奥] 斯·茨威格 / 赵台安 / 生活·读书·新知三联书店 / 1986-12 / 1.40元</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list27077129">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/27077129/">
                             华氏451
                         </a>
     </div>
     <div class="date">
                     2019-05-27
                     </div>
     </div>
     <div class="hide" id="grid27077129">
     <div class="grid-date">
     <span class="intro">[美] 雷·布拉德伯里 / 于而彦 / 上海译文出版社 / 2017-7 / 45.00</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list26641665">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/26641665/">
                             切尔诺贝利的悲鸣
                         </a>
     </div>
     <div class="date">
                     2019-05-27
                     </div>
     </div>
     <div class="hide" id="grid26641665">
     <div class="grid-date">
     <span class="intro">S. A. 阿列克谢耶维奇 / 方祖芳 / 郭成业 / 花城出版社 / 2015-11 / 42</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list1089142">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/1089142/">
                             消费社会
                         </a>
     </div>
     <div class="date">
                     2019-05-22
                     </div>
     </div>
     <div class="hide" id="grid1089142">
     <div class="grid-date">
     <span class="intro">[法] 让·波德里亚 / 刘成富 / 南京大学出版社 / 2001-5 / 28.00元</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list30393937">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/30393937/">
                             Upheaval
                         </a>
     </div>
     <div class="date">
                     2019-05-21
                     </div>
     </div>
     <div class="hide" id="grid30393937">
     <div class="grid-date">
     <span class="intro">Jared Diamond / Allen Lane / 2019-5-7 / GBP 25.00</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list19977684">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/19977684/">
                             酒国
                         </a>
     </div>
     <div class="date">
                     2019-05-17
                     </div>
     </div>
     <div class="hide" id="grid19977684">
     <div class="grid-date">
     <span class="intro">莫言 / 上海文艺出版社 / 2012-10 / 35.00元</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list1896853">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/1896853/">
                             The Ballad of the Sad Cafe and other Stories
                         </a>
     </div>
     <div class="date">
                     2019-05-13
                     </div>
     </div>
     <div class="hide" id="grid1896853">
     <div class="grid-date">
     <span class="intro">Carson McCullers / Penguin Books Ltd / 2001-3 / GBP 9.99</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list2973335">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/2973335/">
                             微暗的火
                         </a>
     </div>
     <div class="date">
                     2019-05-13
                     </div>
     </div>
     <div class="hide" id="grid2973335">
     <div class="grid-date">
     <span class="intro">[美]弗拉基米尔·纳博科夫 / 梅绍武 / 上海译文 / 2008-1 / 26.00元</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list27094706">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/27094706/">
                             财富自由之路
                         </a>
     </div>
     <div class="date">
                     2019-05-11
                     </div>
     </div>
     <div class="hide" id="grid27094706">
     <div class="grid-date">
     <span class="intro">李笑来 / 电子工业出版社 / 2017-8 / 79.00</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list20036150">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/20036150/">
                             Principles
                         </a>
     </div>
     <div class="date">
                     2019-05-11
                     </div>
     </div>
     <div class="hide" id="grid20036150">
     <div class="grid-date">
     <span class="intro">Ray Dalio / Simon &amp; Schuster / 2017-9-19 / USD 30.00</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list7060185">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/7060185/">
                             江城
                         </a>
     </div>
     <div class="date">
                     2019-05-05
                     </div>
     </div>
     <div class="hide" id="grid7060185">
     <div class="grid-date">
     <span class="intro">[美] 彼得·海斯勒 / 李雪顺 / 上海译文出版社 / 2012-1 / 36.00元</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list33401937">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/33401937/">
                             Find Me
                         </a>
     </div>
     <div class="date">
                     2019-05-04
                     </div>
     </div>
     <div class="hide" id="grid33401937">
     <div class="grid-date">
     <span class="intro">André Aciman / Farrar, Straus and Giroux / 2019-10-29 / USD 26.00</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list1092290">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/1092290/">
                             语言研究
                         </a>
     </div>
     <div class="date">
                     2019-04-23
                     </div>
     </div>
     <div class="hide" id="grid1092290">
     <div class="grid-date">
     <span class="intro">George Yule / 牛津大学出版社 / 2000-8-1 / 28.90</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list1856494">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/1856494/">
                             卡拉马佐夫兄弟
                         </a>
     </div>
     <div class="date">
                     2019-04-23
                     </div>
     </div>
     <div class="hide" id="grid1856494">
     <div class="grid-date">
     <span class="intro">[俄] 费奥多尔·陀思妥耶夫斯基 / 荣如德 / 上海译文出版社 / 2006-8 / 25.00元</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list2243692">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/2243692/">
                             潜水钟与蝴蝶
                         </a>
     </div>
     <div class="date">
                     2019-04-22
                     </div>
     </div>
     <div class="hide" id="grid2243692">
     <div class="grid-date">
     <span class="intro">[法] 让-多米尼克·鲍比 / 邱瑞銮 / 南海出版公司 / 2007-9 / 20.00元</span><br/>
     </div>
     <div class="comment">
                         原来世上存在有这么励志的书……
                         
                     </div>
     </div>
     </li>, <li class="item" id="list4578536">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/4578536/">
                             阿司匹林传奇
                         </a>
     </div>
     <div class="date">
                     2019-04-19
                     </div>
     </div>
     <div class="hide" id="grid4578536">
     <div class="grid-date">
     <span class="intro">(英) 杰弗里斯 / 暴永宁 / 生活·读书·新知三联书店 / 2010-7 / 38.00元</span><br/>
     <span class="tags">标签: 英国</span>
     </div>
     </div>
     </li>, <li class="item" id="list1219421">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/1219421/">
                             实验心理学
                         </a>
     </div>
     <div class="date">
                     2019-04-19
                     </div>
     </div>
     <div class="hide" id="grid1219421">
     <div class="grid-date">
     <span class="intro">M.Kimberly MacLin / 张奇 / 中国轻工业出版社 / 2004-9 / 28.00元</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list1758235">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/1758235/">
                             Linear Algebra and Its Applications, 4e
                         </a>
     </div>
     <div class="date">
                     2019-04-12
                     </div>
     </div>
     <div class="hide" id="grid1758235">
     <div class="grid-date">
     <span class="intro">Gilbert Strang / Brooks Cole / 2005-07-19 / USD 220.95</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list30199434">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/30199434/">
                             原生家庭
                         </a>
     </div>
     <div class="date">
                     2019-04-10
                     </div>
     </div>
     <div class="hide" id="grid30199434">
     <div class="grid-date">
     <span class="intro">（美）苏珊·福沃德博士 / 黄姝 / 北京时代华文书局│阳光博客 / 2018-8 / 58.00</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list25914783">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/25914783/">
                             你好小朋友
                         </a>
     </div>
     <div class="date">
                     2019-04-10
                     </div>
     </div>
     <div class="hide" id="grid25914783">
     <div class="grid-date">
     <span class="intro">秋山 亮二 / 小西六写真工业株式会社 / 1983-4-12 / JPY 3087</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list4822685">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/4822685/">
                             编码
                         </a>
     </div>
     <div class="date">
                     2019-04-07
                     </div>
     </div>
     <div class="hide" id="grid4822685">
     <div class="grid-date">
     <span class="intro">[美] Charles Petzold / 左飞 / 电子工业出版社 / 2010 / 55.00元</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list30367015">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/30367015/">
                             守夜
                         </a>
     </div>
     <div class="date">
                     2019-03-25
                     </div>
     </div>
     <div class="hide" id="grid30367015">
     <div class="grid-date">
     <span class="intro">[英] 萨拉·沃特斯 / 阿朗 / 世纪文景|上海人民出版社 / 2019-2 / 59.00</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list27010229">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/27010229/">
                             通向奴役之路
                         </a>
     </div>
     <div class="date">
                     2019-03-24
                     </div>
     </div>
     <div class="hide" id="grid27010229">
     <div class="grid-date">
     <span class="intro">海耶克 / 滕維藻 / 商務印書館(香港)有限公司 / 2017-3-20 / HK$ 128.00</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list1025723">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/1025723/">
                             潜规则
                         </a>
     </div>
     <div class="date">
                     2019-03-22
                     </div>
     </div>
     <div class="hide" id="grid1025723">
     <div class="grid-date">
     <span class="intro">吴思 / 云南人民出版社 / 2001-1 / 16.00元</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list25943061">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/25943061/">
                             孤独、团结与反抗
                         </a>
     </div>
     <div class="date">
                     2019-03-22
                     </div>
     </div>
     <div class="hide" id="grid25943061">
     <div class="grid-date">
     <span class="intro">(法) 加缪 / 郭宏安 / 花城出版社 / 2014-11 / 43.00</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list22806583">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/22806583/">
                             国家的常识
                         </a>
     </div>
     <div class="date">
                     2019-03-22
                     </div>
     </div>
     <div class="hide" id="grid22806583">
     <div class="grid-date">
     <span class="intro">[美]迈克尔·罗斯金(Michael G. Roskin) / 杨勇 / 世界图书出版公司 / 2013-4 / 68.00元</span><br/>
     </div>
     </div>
     </li>, <li class="item" id="list27021785">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/27021785/">
                             游戏设计、原型与开发
                         </a>
     </div>
     <div class="date">
                     2019-03-09
                     </div>
     </div>
     <div class="hide" id="grid27021785">
     <div class="grid-date">
     <span class="intro">【美】Jeremy Gibson / 刘晓晗 / 电子工业出版社 / 2017-5 / 128</span><br/>
     </div>
     </div>
     </li>, <li class="item last" id="list26313534">
     <div class="item-show">
     <div class="title">
     <a href="https://book.douban.com/subject/26313534/">
                             Unity游戏设计与实现
                         </a>
     </div>
     <div class="date">
                     2019-03-09
                     </div>
     </div>
     <div class="hide" id="grid26313534">
     <div class="grid-date">
     <span class="intro">[日]加藤政树 / 罗水东 / 人民邮电出版社 / 2015-2 / 79.00元</span><br/>
     </div>
     </div>
     </li>]




```python
items[4](href=re.compile('subject'))[0].get_text(strip=True)
```




    '切尔诺贝利的悲鸣'




```python
items[2](class_='intro')[0].get_text(strip=True).split('/')
```




    ['[奥] 斯·茨威格 ', ' 赵台安 ', ' 生活·读书·新知三联书店 ', ' 1986-12 ', ' 1.40元']




```python
soup.find(class_='next').link.get('href')
```




    '/people/91835006/wish?start=30&sort=time&rating=all&filter=all&mode=list'




```python
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

```


```python
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
    return bookwishdict
```


```python

```


```python

```


```python
k=bookwish(doubanid='thucydides')
```

    第1页 OK
    第2页 OK
    第3页 OK
    第4页 OK
    第5页 OK
    第6页 OK
    第7页 OK
    第8页 OK
    第9页 OK
    第10页 OK
    第11页 OK
    第12页 OK
    第13页 OK
    第14页 OK
    第15页 OK
    


```python
#加浏览器信息和换代理（弃用）
hds = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
proxy='117.68.236.91:8118'
readurl='https://book.douban.com/people/91835006/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count'
'''
urlhandle = urllib.request.ProxyHandler({'http': proxy})
opener = urllib.request.build_opener(urlhandle)
urllib.request.install_opener(opener)

response=urllib.request.Request(url=readurl,headers=headers)
request=urllib.request.urlopen(response)
soup=BeautifulSoup(request.read())

print('Status:',request.status,request.reason)
for k,v in request.getheaders():
    print('{}: {}'.format(k,v))
'''
```




    "\nurlhandle = urllib.request.ProxyHandler({'http': proxy})\nopener = urllib.request.build_opener(urlhandle)\nurllib.request.install_opener(opener)\n\nresponse=urllib.request.Request(url=readurl,headers=headers)\nrequest=urllib.request.urlopen(response)\nsoup=BeautifulSoup(request.read())\n\nprint('Status:',request.status,request.reason)\nfor k,v in request.getheaders():\n    print('{}: {}'.format(k,v))\n"



### 读过列表


```python
bookurl='https://book.douban.com/people/silenceapostle'
read='https://book.douban.com/people/silenceapostle/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count'
browser = webdriver.Chrome()
browser.get(bookurl)
browser.get(read)
soup = BeautifulSoup(browser.page_source, "html.parser")
```


```python
items=soup.find_all(class_=re.compile('item'),id=re.compile('li'))
```


```python
items[5](class_=re.compile('rat'))[0]['class'][0][6]
```




    '4'




```python
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
```


```python
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
```


```python
dick=ReadBookList(doubanid='91835006')
```

    浏览器处理第1页
    浏览器处理第2页
    

## MUSIC


```python
musicurl='https://music.douban.com/people/174132109/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count'
request=urllib.request.urlopen(url=musicurl)
soup=BeautifulSoup(request.read())
print('Status:',request.status,request.reason)
```

    Status: 200 OK
    


```python
items=soup.find_all(class_=re.compile('item'),id=re.compile('li'))
```


```python
items[10](class_='intro')[0].get_text(strip=True)
```




    'Celine Dion / 1998-01-05 / 单曲 / CD / 流行'




```python
soup.find(class_='next').link.get('href')
```




    'https://music.douban.com/people/174132109/collect?start=30&sort=time&rating=all&filter=all&mode=list'




```python
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
        intro=it(class_='intro')[0].get_text(strip=True)
        Mdict[title]=[intro,date,stars,comment]
```


```python
def HeardList(doubanid):
    firstpage='https://music.douban.com/people/'+doubanid+'/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count'
    request=urllib.request.urlopen(url=firstpage)
    soup=BeautifulSoup(request.read())
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
            request=urllib.request.urlopen(url=NextPage)
            soup=BeautifulSoup(request.read())
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
    return heard_dic
```


```python
dic=HeardList(doubanid='91835006')
```

    第1页 OK
    第2页 OK
    第3页 OK
    第4页 OK
    第5页 OK
    第6页 OK
    已到最终页
    


```python
wantmurl='https://music.douban.com/people/174132109/wish?sort=time&start=0&filter=all&mode=list&tags_sort=count'
request=urllib.request.urlopen(url=wantmurl)
soup=BeautifulSoup(request.read())
print('Status:',request.status,request.reason)
```

    Status: 200 OK
    


```python
items=soup.find_all(class_=re.compile('item'),id=re.compile('li'))
```


```python
def WMusappend(Mdict,Items):
    for it in Items:
        title=it('a')[0].get_text(strip=True)
        date=it(class_=re.compile('date'))[0].get_text(strip=True)
        try:
            comment=it(class_=re.compile('comm'))[0].get_text(strip=True).replace('\n','-')
        except:
            comment='Nah'
        intro=it(class_='intro')[0].get_text(strip=True)
        Mdict[title]=[intro,date,comment]
```


```python
def WHeardList(doubanid):
    firstpage='https://music.douban.com/people/'+doubanid+'/wish?sort=time&start=0&filter=all&mode=list&tags_sort=count'
    request=urllib.request.urlopen(url=firstpage)
    soup=BeautifulSoup(request.read())
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
            request=urllib.request.urlopen(url=NextPage)
            soup=BeautifulSoup(request.read())
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
    return whear_dic
```


```python
WHeardList(doubanid='91835006')
```

    第1页 OK
    已到最终页
    




    {'Honeybloom': ['Choker / 2018-08-03 / 专辑 / 数字(Digital) / 流行',
      '2018-10-15',
      'Nah'],
     'Black Origami': ['Jlin / 2017-05-19 / 专辑 / Audio CD / 电子',
      '2017-05-28',
      'Nah'],
     'Either/Or: Expanded Edition / 模棱两可': ['Elliott Smith / 2017-03-10 / 专辑 / CD / 民谣',
      '2017-03-19',
      'Nah'],
     'In Colour / 多采多姿': ['Jamie XX / 2015-06-01 / 专辑 / CD / 电子',
      '2016-01-01',
      'Nah'],
     'Seven Lions': ['Seven Lions / 2012-10-16 / EP / 数字(Digital) / 电子',
      '2015-07-12',
      'Nah'],
     'Who You Are Is Not Enough': ['Athletics / 2012-06-26 / EP / 数字(Digital) / 摇滚',
      '2015-04-17',
      'Nah'],
     '天宫图': ['窦唯,莫西子诗,子枫 / 2014-04-14 / 专辑 / CD / 电子', '2015-02-08', 'Nah'],
     'All Is Wild, All Is Silent / 四野俱寂': ['Balmorhea / 2009-03-10 / 专辑 / Audio CD',
      '2015-01-31',
      'Nah'],
     'Enochian': ['Dry River / 2014-01-20 / 专辑 / 数字(Digital) / 摇滚',
      '2014-12-21',
      'Nah']}




```python

```
