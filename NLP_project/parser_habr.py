from platform import machine
import pandas as pd
import numpy as np
import requests
import random
import bs4
from time import sleep
import urllib
import re

base_url = 'https://habr.com'
headers = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
'Connection': 'keep-alive',
'Sec-Fetch-Dest': 'document',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-Site': 'none',
'Sec-Fetch-User': '?1',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',}

urls = ['https://habr.com/ru/search/page{}/?q=data%20science&target_type=posts&order=date', 
        'https://habr.com/ru/search/page{}/?q=machine%20learning&target_type=posts&order=date', 
        'https://habr.com/ru/search/page{}/?q=data%20analytics%20&target_type=posts&order=date',
        'https://habr.com/ru/hub/natural_language_processing/page{}/',
        'https://habr.com/ru/hub/data_engineering/page{}/']
def parsing():
    hrefs = []
    dts = []
    text = []
    scores = []
    comments = []
    bookmarks = []
    views = []
    users = []
    hubs = []
    for url in urls:
        for i in range(1,51):
            page = requests.get(url.format(i), headers=headers, proxies=urllib.request.getproxies())
            if page.status_code == 200:
                print('url: ', url.format(i))
                sleep(1)
                soup = bs4.BeautifulSoup(page.content, "lxml")
                articles = soup.find_all('article', attrs={'class': 'tm-articles-list__item'})
                for article in articles:
                    n_view = article.find('span', attrs={'class': 'tm-icon-counter__value'}).text
                    score = article.find('span', attrs={'class': re.compile(r'tm-votes-meter')}).text
                    n_bookmark = article.find('span', attrs={'class': 'bookmarks-button__counter'}).text
                    n_comment = article.find('span', attrs={'class': 'tm-article-comments-counter-link__value'}).text
                    dt = article.find('time')['datetime']
                    
                    
                    href_obj = article.find('a', attrs={'class': 'tm-article-snippet__title-link'})
                    if href_obj is None:
                        continue

                    href = base_url + href_obj['href']
                    print('href: ', href)
                    sleep(1)
                    article_page = requests.get(href, headers=headers, proxies=urllib.request.getproxies())
                    article_soup = bs4.BeautifulSoup(article_page.content, "lxml")
                    text_body = article_soup.find('div', attrs={'class': re.compile(r'article-formatted-body article-formatted-body article-formatted-body_version')})
                    ps = [p.text for p in text_body.find_all('p')]
                    article_text= ' '.join(ps)
                    
                    user = article_soup.find('a', attrs={'class': 'tm-user-info__username'}).text

                    hubs_obj =  article_soup.find_all('li', attrs={'class': re.compile(r'tm-separated-list__item')})
                    hubs_list = []
                    for h in hubs_obj:
                        hubs_list.append(h.find('a').text.strip())
                    hubs_text = ','.join(hubs_list)

                    hrefs.append(href)
                    dts.append(dt)
                    text.append(article_text)
                    scores.append(score)
                    bookmarks.append(n_bookmark.strip())
                    comments.append(n_comment.strip())
                    views.append(n_view)
                    users.append(user.strip())
                    hubs.append(hubs_text)

                    pd.DataFrame({  'href': hrefs, 'dt': dts, 'article_text': text, 
                                    'score':scores, 'bookmark': bookmarks, 'comment': comments, 
                                    'view': views, 'user': users, 'hub_tags': hubs}).to_csv('habr.csv')
            else:
                break

parsing()