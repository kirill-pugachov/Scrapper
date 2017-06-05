# -*- coding: utf-8 -*-
"""
Created on Fri May 26 15:24:25 2017

@author: Kirill
"""

# -*- coding: utf-8 -*-
"""
Created on Thu May 18 10:47:23 2017

@author: Kirill
"""

'''
Сборщик страниц по сайту
Строит структуру рубрикатора? каталога?
Заходит с главной
Иерархию строит по содержимому хлебных крошек на странице
Страницы объявлений отбрасывает
Работает на 1 домене - на поддомены не ходит
'''

from urllib.request import urlopen, Request 
from bs4 import BeautifulSoup
import time
from random import randint
import csv
import requests

#подставляем в запрос к сайту, чтобы притвориться браузером
#при необходимости можно расширять список хедеров для разнообразия запросов
headers_list = [ 
{
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3', 'Host':'rambler.ru',
'Connection':'close', 'Referer':'https://www.google.com.ua/search?num=30&biw=1600&bih=737&q=%D0%BA%D1%83%D0%BF%D0%B8%D1%82%D1%8C+%D1%82%D0%B5%D0%BB%D0%B5%D1%84%D0%BE%D0%BD+%D0%B1%D1%83+%D0%BF%D1%80%D0%BE%D0%BC&oq=%D0%BA%D1%83%D0%BF%D0%B8%D1%82%D1%8C+%D1%82%D0%B5%D0%BB%D0%B5%D1%84%D0%BE%D0%BD+%D0%B1%D1%83+%D0%BF%D1%80%D0%BE%D0%BC&gs_l=serp.3...17362.18139.0.19526.5.5.0.0.0.0.255.533.0j2j1.3.0....0...1.1.64.serp..2.2.277...0j0i22i30k1.-R4cXbRC9os'        
},

{
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:51.0) Gecko/20100101 Firefox/51.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3', 'Host':'bing.com',
'Connection':'close', 'Referer':'https://www.google.com.ua/search?num=30&biw=1600&bih=737&q=%D0%BA%D1%83%D0%BF%D0%B8%D1%82%D1%8C+%D1%81%D0%BC%D0%B0%D1%80%D1%82%D1%84%D0%BE%D0%BD+%D0%B2+%D1%83%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B5+%D0%B4%D0%BE+1000+%D0%B3%D1%80%D0%BD&oq=%D0%BA%D1%83%D0%BF%D0%B8%D1%82%D1%8C+%D1%82%D0%B5%D0%BB%D0%B5%D1%84%D0%BE%D0%BD+%D0%B1%D1%83+%D0%BF%D1%80%D0%BE%D0%BC&gs_l=serp.1.1.0i71k1l8.0.0.0.109385.0.0.0.0.0.0.0.0..0.0....0...1..64.serp..0.0.0.LoKbEudqtXc'       
},

{
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.1144',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3', 'Host':'yandex.ru',
'Connection':'close', 'Referer':'https://www.google.com.ua/search?num=30&biw=1600&bih=737&q=%D0%BE%D0%B1%D0%BE%D0%B8+%D0%BF%D0%BE%D0%B4+%D0%BF%D0%BE%D0%BA%D1%80%D0%B0%D1%81%D0%BA%D1%83+%D0%BA%D0%B8%D1%80%D0%BF%D0%B8%D1%87&oq=%D0%BE%D0%B1%D0%BE%D0%B8+%D0%BF%D0%BE%D0%B4+%D0%BF%D0%BE%D0%BA%D1%80%D0%B0%D1%81%D0%BA%D1%83+&gs_l=serp.3.9.0l10.21101.26257.0.37273.5.5.0.0.0.0.136.583.0j5.5.0....0...1.1.64.serp..0.5.580...0i131i10i1k1j0i131k1j0i10i1k1j0i10i1i67k1j0i67k1j0i1k1.0BMhfqX_PlM'         
},

{
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:52.0) Gecko/20100101 Firefox/52.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3', 'Host':'www.w3.org',
'Connection':'close', 'Referer':'https://duckduckgo.com/?q=%D0%BA%D1%83%D0%BF%D0%B8%D1%82%D1%8C+%D0%B1%D0%B5%D1%82%D0%BE%D0%BD%D0%BE%D0%BC%D0%B5%D1%88%D0%B0%D0%BB%D0%BA%D1%83&t=h_&ia=web'        
},

{
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) AppleWebKit/537.36 (KHTML, like Gecko)',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3', 'Host':'proglib.io',
'Connection':'close', 'Referer':'https://www.google.com.ua/search?num=30&biw=1600&bih=737&q=%D0%BF%D1%80%D0%BE%D0%BC%D1%8B%D0%B2%D0%BA%D0%B0+%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D1%8B+%D0%BE%D1%85%D0%BB%D0%B0%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F+%D0%BF%D1%80%D0%BE%D0%BC&oq=%D0%BF%D1%80%D0%BE%D0%BC%D1%8B%D0%B2%D0%BA%D0%B0+%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D1%8B+%D0%BE%D1%85%D0%BB%D0%B0%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F+%D0%BF%D1%80%D0%BE%D0%BC&gs_l=serp.3...92092.105982.0.106760.18.15.3.0.0.0.266.1929.1j12j1.14.0....0...1.1.64.serp..1.15.1676.0..0j0i131k1j0i10i1i67k1j0i67k1j0i10i1k1j0i131i10i1k1j0i131i10i67k1j0i22i30k1.0AfKDK21mw4'         
}
]


#Список проксей
proxies = {
    'http': 'socks5://localhost:9050',
    'https': 'socks5://localhost:9050'
}



#список тестовых урл, чтобы не гонять по сайту для скраппинга
test_url = ["https://prom.ua/Sportivnye-kofty-svitera", "https://prom.ua/Sportivnaya-odezhda-i-obuv", "https://prom.ua/Avtoinstrument", "https://prom.ua/Odezhda", "https://prom.ua/Avto--moto", "https://prom.ua/Mototehnika", "https://prom.ua/Motobuksirovschik", "https://prom.ua/Stroitelstvo", "https://prom.ua/Otdelochnye-materialy-1"]

#Базовая урл сайта
base_url = 'https://web.archive.org/web/20170421070032/http://prom.ua' #'https://prom.ua'

#Урл с которой начинается сканирование
start_url = '/Odezhda' #'/b2b/Stroitelstvo'  '/Odezhda''/Avtoaksessuary' '/Sportivnaya-odezhda-i-obuv' '/' '/Sportivnye-kofty-svitera'

#Словарь для записи результатов
total_structure = dict()

#Множество урл сайта - содержит уникальное множество урл уже собранных на сайте
uniq_url_set = set()

#Очередь на основе списка - содержит урл для сканирования
line_to_scrap = []

#Максимальный размер паузы
PAUSE = 15

#Размер куска для сброса на диск результатов
pice_max = 700

#Куда пишем результирующий файл
FOLDER = 'C:/Python/Service/'
FILE_NAME_URL = 'prom_ua_structure_scraping'
FILE_EXT = '.csv'




def headers(headers_list):
    '''
    Закрываем соединение
    Подставляем случайное значение User Agent
    '''
#    header_index = randint(0,len(headers_list)-1)
#    print(headers_list[header_index], header_index)
    return headers_list[randint(0,len(headers_list)-1)]


def vector_str(bsObj):
    '''
    разбираются хлебные крошки на странице
    результат записывается в список, состоящий из словаря
    где ключи - урл страниц, а значения списко из двух элементов
    анкор(название страницы) в крошке, путь до страницы от домена 
    (сам домен не указывается)
    '''
    result_vector = []
    bread_scrumbs = bsObj.find_all('div', {"class":"x-breadcrumb__item"})
    bread_scrumbs = bread_scrumbs[1:]
    full_path = ''
    for scrumb in bread_scrumbs:
        anchor = scrumb.a['href']
        anchor_text = scrumb.a.get_text()
        full_path += anchor
        result_vector.append({anchor:[anchor_text, full_path]})   
    return result_vector

    
def structure_fill(total_structure, result_vector):
    '''
    на основе содержимого крошки на странице
    заполняется запись о структуре данных
    если нужного уровня вложенности нет
    он добавляется, если есть ничего не изменяется
    '''
    try:
        total_structure[list(result_vector[0].keys())[0]]
        structure_fill(total_structure[list(result_vector[0].keys())[0]], result_vector[1:len(result_vector)])
    except KeyError:
        total_structure[list(result_vector[0].keys())[0]] = {'value':list(result_vector[0].values())[0]}
        structure_fill(total_structure[list(result_vector[0].keys())[0]], result_vector[1:len(result_vector)])
    except IndexError:
        return total_structure
    return total_structure


def get_url_from_breadscrumbs(result_vector):
    res = []
    for result in result_vector:
        res.append(list(result.keys())[0])
    return res

            
def url_on_page_find(bsObj):
    '''
    извлекает все урл на странице из списка li под
    классом x-category-tile__item
    и записывает в список
    '''
    links_at_page_vector = []
    links_at_page = []
    links_at_page = bsObj.find_all('li', {"class":"x-category-tile__item"})
    for links in links_at_page:
        link_url = links.a['href']
        links_at_page_vector.append(link_url.split('/')[-1:][0])
    return links_at_page_vector
           
def uniqe_url(links_at_page, uniq_url_set):
    '''
    строит пересечение списка урл полученного при скрапинге
    и множества уже собранных урл на сайте
    возвращает список урл не входящих в множество уже собранных
    '''
    uniq_url_list = []
    for links in links_at_page:
        if links not in uniq_url_set:
            uniq_url_list.append(links)
    return uniq_url_list
            

def line_to_scrap_update(line_to_scrap, uniqe_links):
    '''
    добавляет вниз очереди урл на сканирование
    список уникальных урл полученных при скрапинге
    из функции uniqe_url
    '''
    for uniqe in uniqe_links:
        line_to_scrap.append(uniqe)
    return line_to_scrap
        

def create_line_to_scrap(uniqe_url, line_to_scrap_update, line_to_scrap, uniq_url_set, links_from_page):
    uniqe_links = uniqe_url(links_from_page, uniq_url_set)
    line_to_scrap = line_to_scrap_update(line_to_scrap, uniqe_links)  
    return line_to_scrap
    
        
def time_broker(PAUSE):
    '''
    Генерируем случайное время ожидания в с
    перед забором следующей страницы с сайта
    '''
    time_to_pause = randint(0, PAUSE)
    print('Время ожидания: ', time_to_pause)
    return time_to_pause

    
def time_to_sleep(pause_time):
    '''
    ждем заданное время ожидания
    '''
    if pause_time != 0:
        for i in range(pause_time):
            time.sleep(1)

                        
def list_modify(result_list):
    '''
    разбирает наборный урл глубины вложенности
    вида /consumer-goods/Avto--moto/Avtoaksessuary
    на отдельные элементы в список и дополняет последним
    элементом названием страницы в крошке
    '''
    res = result_list[1].split('/')
    res.append(result_list[0])
#    res.append(result_list[0])
    return res[1:]
        
        
def write_to_disk(result):
    '''
    разбирает полученный словарь
    на элементы, по всей глубине вложенности
    '''
    for key in result:
        if key == 'value':
            write_to_file(result[key])
        else:
            write_to_disk(result[key])
                    

def write_to_file(result_list):
    '''
    записывает полученные при скраппинге данные
    в результирующий файл, раскладывает по глубине
    вложенности
    '''
    result_list_modify = list_modify(result_list)
    print(result_list_modify)
    with open(FOLDER + FILE_NAME_URL + [x.replace(':', '_') for x in (time.asctime()).split(' ') if ':' in x][0] + FILE_EXT, 'a', newline='') as resultFile:
        wr = csv.writer(resultFile, dialect='excel', quoting=csv.QUOTE_ALL)
        wr.writerow(result_list_modify)         


line_to_scrap.append(start_url)          

while True:
    try:
        url = line_to_scrap.pop(0)
    except:
        print('Очередь закончилась - страниц больше нет')
        break
    else:
#        url_1 = ('https://translate.google.com/translate?sl=en&tl=ru&js=y&prev=_t&hl=ru&ie=UTF-8&u=https%3A%2F%2Fprom.ua' + url)
#        print(url_1)
#        print(headers(headers_list))
        html = requests.get(base_url + url, headers=headers(headers_list)) #headers=headers(headers_list))#, proxies=proxies)
#        req = Request(base_url + url, headers = headers(headers_list))
#        html = urlopen(req)

        
#        html = urlopen(base_url + url)
        if html.status_code == 200:            
#            print(html.url, html.status_code, html.msg)
            bsObj = BeautifulSoup(html.text, "lxml")
            result_vector = vector_str(bsObj)
            result = structure_fill(total_structure, result_vector)
            line_to_scrap = create_line_to_scrap(uniqe_url, line_to_scrap_update, line_to_scrap, uniq_url_set, get_url_from_breadscrumbs(result_vector))
            uniq_url_set.update(get_url_from_breadscrumbs(result_vector)) 
            links_from_page = url_on_page_find(bsObj)
            line_to_scrap = create_line_to_scrap(uniqe_url, line_to_scrap_update, line_to_scrap, uniq_url_set, links_from_page)
            uniq_url_set.update(links_from_page)
        else:
            line_to_scrap.append(url)
    print('Получено ссылок со страницы:', len(links_from_page))
    print('Кол-во страниц в списке для сканирования:', len(line_to_scrap), '\n')
    time_to_sleep(time_broker(PAUSE))
    if len(line_to_scrap)%pice_max == 0:
        write_to_disk(result)
        