import requests
import re
from bs4 import BeautifulSoup


def nextPageLink(sess,soup,page,head=""):
    NextPage=soup.find(class_='next').link.get('href')
    req=sess.get(head + NextPage)
    print(f'第{page}页：',req.status_code)
    return BeautifulSoup(req.text,'html.parser')