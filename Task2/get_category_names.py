from pprint import pprint
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import re
import time


main_link = 'https://rskrf.ru/ratings/produkty-pitaniya/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/76.0.3809.100 Safari/537.36 OPR/63.0.3368.53'
}
products_url_block = []
products_url_list = []
subproducts_url_list = []
subcategory_list = []
category_list = []

html = requests.get(main_link, headers=headers)
if html.status_code is not requests.codes.ok:
    print('Страница ' + html.url + ' не доступна')
else:
    # делаем объект bs
    bsObj = bs(html.text, 'lxml')
    # ищем блок с ссылками на категории продуктов
    products_url_block = bsObj.findAll(class_="category-item")

for i, item in enumerate(products_url_block):
    products_url_list.append('https://rskrf.ru' + products_url_block[i].find('a').get('href'))

for url in products_url_list:
    html = requests.get(url)
    if html.status_code is not requests.codes.ok:
        print('Страница ' + html.url + ' не доступна')
        break
    # делаем объект bs
    bsObj = bs(html.text, 'lxml')
    subproducts_url_block = bsObj.findAll(class_="category-item")
    for i, item in enumerate(subproducts_url_block):
        subproducts_url_list.append('https://rskrf.ru' + subproducts_url_block[i].find('a').get('href'))

for url in subproducts_url_list:
    html2 = requests.get(url, headers=headers)
    html2.encoding = 'utf-8'
    if html2.status_code is not requests.codes.ok:
        print('Страница ' + html2.url + ' не доступна')
    else:
        bsObj = bs(html2.text, 'lxml')
        subcategory_name = bsObj.find(class_="breadcrumb-item active").getText()
        category_name = bsObj.findAll(class_="breadcrumb-item")[-2].getText()
        subcategory_list.append(subcategory_name)
        category_list.append(category_name)
    time.sleep(1)

s_subcat = pd.Series(subcategory_list)
s_cat = pd.Series(category_list)

df = pd.DataFrame()
df['category'] = s_cat
df['subcategory'] = s_subcat
df.to_csv('categories.csv', index=False, header=True, encoding='utf-8')
