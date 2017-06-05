# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 19:37:47 2017

@author: Home sweet Home
"""


import requests
from lxml import html
from lxml import *
from random import randint
import csv
import time


#Значение домена для парсинга
#Дальше можно сделать список доменов
DOMEN = 'https://babybox.itbox.ua/'

#Куда сохранять результат сбора тегов
FILE_NAME = 'babybox_tag_result_scraping.csv'
FOLDER = 'C:/Python/Service/ITbox/'

#Куда сохранять результат сбора links at page
FILE_NAME_URL = 'babybox_url_result_scraping.csv'

#Максимальный размер паузы
PAUSE = 3


#словарь из списков исходящих ссылок, ключ страница с которой ссылки
Site_Pages = {}
#множество уникальных страниц сайта от парсера
Uniq_Site_Page = set()
#список с очередью страниц для парсинга, уникальные страницы.
Line_To_Parse = []

#подставляем в запрос к сайту, чтобы притвориться браузером
headers_list = [ 
{
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
'Connection':'close'        
},

{
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:51.0) Gecko/20100101 Firefox/51.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
'Connection':'close'        
},

{
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.1144',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
'Connection':'close'        
},

{
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:52.0) Gecko/20100101 Firefox/52.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
'Connection':'close'        
},

{
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) AppleWebKit/537.36 (KHTML, like Gecko)',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
'Connection':'close'        
}
]

def tags_to_string(header_tag):
    string = ''
    print(len(header_tag))
    if len(header_tag) > 1:
        for tag in header_tag:
            if len(tag.strip()) > 5:
                string += str(tag).strip() + ' '
            else:
                string += 'no_tag_'               
#        print(string)
        return string
    elif len(header_tag) == 1:
        if len(header_tag[0].strip()) > 5:
            string = str(header_tag[0].strip())
        else:
            string = 'no_tag'            
        return string.strip()
    elif len(header_tag) == 0:
        string = 'no_tag'
        return string.strip()
         


def time_broker(PAUSE):
    '''
    Генерируем случайное время ожидания 
    перед забором следующей страницы с сайта
    '''
    time_to_pause = randint(0, PAUSE)
    print('Время ожидания: ', time_to_pause, '\n')
    return time_to_pause



def headers(headers_list):
    '''
    Закрываем соединение
    Подставляем случайное значение User Agent
    '''
    header_index = randint(0,len(headers_list)-1)
#    print(headers_list[header_index], header_index)
    return headers_list[header_index]


def only_links(page_url):
    '''
    Ищем в строке с урл начало ссылки
    Вырезаем из строки от начала до конца
    И возвращаем как ссылку
    '''
    url = page_url[page_url.rfind('http'):]
    return url

    
def ext_domen_filter(page_url, domen):
    '''
    Убираем из списка урл на странице внешние ссылки на счетчики и т.д.
    '''
    if 'http://' in page_url or 'https://' in page_url:
        if domen in page_url:
            result = page_url
        else:
            result = ''
    else:
        result = page_url
    return result

    
def tel_filter(page_url):
    '''
    Убираем из списка урл на странице активные номера телефонов, 
    отправку почты и ява-скрипты, конечные ссылки на картинки
    '''
    if 'tel:' not in page_url and 'mailto:' not in page_url and '/ru/' not in page_url and 'javascript:' not in page_url and '.jpg' not in page_url and '.png' not in page_url:
        result = page_url
    else:
        result = ''
    return result    

    
def url_filter(url_list_full, domen):
    normalize_url = []
#    url_list = list(set(url_list_full))
    for url in url_list_full:
        if len(url) > 1:
            if tel_filter(url):
                url = ext_domen_filter(only_links(url), domen)
                if url:
                    normalize_url.append(url)
    return normalize_url    

    
def get_title(parsed_body):
    '''
    Получаем тайтл из тега <title>
    '''
    try:
        title = parsed_body.xpath('//title/text()')[0]
    except:
        title = 'no_title'
    return title

    
def get_title_1(parsed_body):
    '''
    Получаем тайтл из тега <meta name = 'title' content = '...'>
    '''
    try:
        title = parsed_body.xpath('/html/head/meta[@name="title"]/@content')[0]
    except:
        title = 'no_title_1'
    return title

    
def get_description(parsed_body):
    '''
    Получаем description из тега <meta name = 'description' content = '...'>
    '''
    try:
        description = parsed_body.xpath('/html/head/meta[@name="description"]/@content')[0]
    except:
        description = 'no_description'
    return description


def get_keywords(parsed_body):
    '''
    Получаем тайтл из тега <meta name = 'keywords' content = '...'>
    '''
    try:
        keywords = parsed_body.xpath('/html/head/meta[@name="keywords"]/@content')[0]
    except:
        keywords = 'no_keywords'
    return keywords    


def get_h1(parsed_body):
    '''
    Получаем h1 из тега <h1>
    '''
    try:
        h1 = parsed_body.xpath('//h1/text()')
    except:
        h1 = ['no_h1']
    return tags_to_string(h1)


def get_h2(parsed_body):
    '''
    Получаем h2 из тега <h2>
    '''
    try:
        h2 = parsed_body.xpath('//h2/text()')
#        h2 = ' '.join(parsed_body.xpath('//h2/text()'))
    except:
        h2 = ['no_h2']
    return tags_to_string(h2)


def get_h3(parsed_body):
    '''
    Получаем h3 из тега <h3>
    '''
    try:
        h3 = parsed_body.xpath('//h3/text()')
#        h3 = ' '.join(parsed_body.xpath('//h3/text()'))
    except:
        h3 = ['no_h3']
    return tags_to_string(h3)

    
def get_h4(parsed_body):
    '''
    Получаем h4 из тега <h4>
    '''
    try:
        h4 = parsed_body.xpath('//h4/text()')
#        h4 = ' '.join(parsed_body.xpath('//h4/text()'))
    except:
        h4 = ['no_h4']
    return tags_to_string(h4)

    
def page_tags(parsed_body):
    '''
    Возвращает список тегов на странице
    title, title in meta, description, keywords
    h1, h2, h3, h4
    '''
    page_tags_list = []
    page_tags_list.append(get_title(parsed_body))
    page_tags_list.append(get_title_1(parsed_body))
    page_tags_list.append(get_description(parsed_body))
    page_tags_list.append(get_keywords(parsed_body))
    page_tags_list.append(get_h1(parsed_body))
    page_tags_list.append(get_h2(parsed_body))
    page_tags_list.append(get_h3(parsed_body))
    page_tags_list.append(get_h4(parsed_body))    
    return page_tags_list

    
def write_tags_to_csv(FILE_NAME, FOLDER, DOMEN, page_tags):
    '''
    Записываем значения тегов на странице
    title, title in meta, description, keywords
    h1, h2, h3, h4 в результирующий файл
    '''
    TAGS_LIST = page_tags(parsed_body)
    TAGS_LIST.insert(0, DOMEN)
    with open(FOLDER + FILE_NAME, 'a', newline='') as resultFile:
        wr = csv.writer(resultFile, dialect='excel', quoting=csv.QUOTE_ALL)
        try:
            wr.writerow(TAGS_LIST)
        except:
            pass
    
    
def write_page_links_to_csv(FILE_NAME_URL, FOLDER, LINE, Page_Links):
    '''
    Записываем значения очищенных ссылок на странице
    в результирующий файл.
    Ухудшается качество расчета
    '''
    Page_Links.insert(0, LINE)
    with open(FOLDER + FILE_NAME_URL, 'a', newline='') as resultFile:
        wr = csv.writer(resultFile, dialect='excel', quoting=csv.QUOTE_ALL)
        wr.writerow(Page_Links)
    
    

#start - first step to start parsing      
response = requests.get(DOMEN, headers = headers(headers_list))
parsed_body = html.fromstring(response.text)
parsed_body.make_links_absolute(DOMEN, resolve_base_href=True)
Page_Links = url_filter(parsed_body.xpath('//a/@href'), DOMEN)
Site_Pages[DOMEN] = Page_Links
Uniq_Site_Page.update(set(Page_Links))
Line_To_Parse = list(set(Page_Links))
#PAGE_TAGS = page_tags(parsed_body)
#print(PAGE_TAGS)
write_tags_to_csv(FILE_NAME, FOLDER, DOMEN, page_tags)
write_page_links_to_csv(FILE_NAME_URL, FOLDER, DOMEN, Page_Links)

#цикл обхода сайта по уникальным урл
while True:
    try:
        LINE = Line_To_Parse.pop(0)
    except:
        print('Очередь закончилась - страниц больше нет')
        break
    else:
        response = requests.get(LINE, headers = headers(headers_list))
        print(response.status_code)
        if response.status_code == 200:       
            parsed_body = html.fromstring(response.text)
            parsed_body.make_links_absolute(DOMEN, resolve_base_href=True)        
            Page_Links = url_filter(parsed_body.xpath('//a/@href'), DOMEN)
    #        PAGE_TAGS = page_tags(parsed_body)
    #        print(PAGE_TAGS)
            write_page_links_to_csv(FILE_NAME_URL, FOLDER, LINE, Page_Links)
            write_tags_to_csv(FILE_NAME, FOLDER, LINE, page_tags)
            print('Получено с сайта ссылок: ', len(Page_Links))
            Site_Pages[LINE] = Page_Links
            To_Line_Pages = {x for x in Page_Links if x not in list(Uniq_Site_Page)}
            print('Добавляем страницы в список сканирования: ', len(To_Line_Pages))        
            Uniq_Site_Page.update(set(Page_Links))
            print('Всего уникальных страниц на сайте: ', len(Uniq_Site_Page))
            Line_To_Parse.extend(list(To_Line_Pages))
            print('Длина очереди сканирования: ', len(Line_To_Parse))
            print('\n')
        else:
            Line_To_Parse.append(LINE)
            
    TIME_TO_SLEEP = time_broker(PAUSE)    
    if TIME_TO_SLEEP != 0:     
        for i in range(TIME_TO_SLEEP):        
            time.sleep(1)










#print(page_tags(parsed_body, DOMEN))
## Выполнение xpath в дереве элементов
##print(response.text)
##print(parsed_body.xpath())
#print(parsed_body.xpath('//title/text()')[0], '\n')     # Получить title страницы
#print(parsed_body.xpath('/html/head/meta[@name="title"]/@content')[0], '\n')
#print(parsed_body.xpath('/html/head/meta[@name="description"]/@content')[0], '\n')
#print(parsed_body.xpath('/html/head/meta[@name="keywords"]/@content')[0], '\n')
#print(parsed_body.xpath('//h1/text()')[0], '\n')     # Получить h1 страницы
#print('|'.join(parsed_body.xpath('//h2/text()')))     # Получить h2 страницы
#print('|'.join(parsed_body.xpath('//h3/text()')))     # Получить h3 страницы
#print('|'.join(parsed_body.xpath('//h4/text()')))     # Получить h4 страницы
#print(len(parsed_body.xpath('//a/@href')))            # Получить аттрибут href для всех ссылок
#for link in parsed_body.xpath('//a/@href'):
#    print(link)
#    



#response = requests.get('https://homebox.itbox.ua/product/Elektrochaynik_MIRTA_KT-1041_V_KT-1041V-p224000/', headers = headers(headers_list))
#
## Преобразование тела документа в дерево элементов (DOM)
#parsed_body = html.fromstring(response.text)
##print(parsed_body.resolve_base_href())
#parsed_body.make_links_absolute(DOMEN, resolve_base_href=True)
#
##tree = etree.fromstring(response.text)