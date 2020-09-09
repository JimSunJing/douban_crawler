# Douban Crawler


## What is it?

  It is a very simple crawler in order to back-up one's DouBan account considering douban accounts might be blocked without any notification in Douban.

  为了防止被豆瓣未告知便封禁账号，写了这个简单的爬虫脚本。


## Function

* DouBan Movie Back-up
* DouBan Reading Back-up
* DouBan Music Back-up
* DouBan Broadcast clawer
* DouBan Diary Back-up
* DouBan Critique Back-up
* Movie label feature
* Book label feature
* DouBan Dou-List back-up


## Install

- 安装python、pip
- 切换项目目录

```shell
cd {project_path}/douban_crawler
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python personalCrawler.py

```

## Application

### [DouBan Run Away Plan](https://www.notion.so/jimsun6428/for-Share-26945cf67a2a407cb9f381109dd438a1)
use `personalCrawler.py` backup douban book+movie marking and import csv into Notion.

### Book, Movie, Music [Planing System](https://www.notion.so/jimsun6428/for-Share-9248be8af2144960858de9cb9a3e75c2) base on Douban & Notion
use `doulist.py` download doulist, import into notion calender template create a planing system.


## About

* 这个小小的项目结束~~
