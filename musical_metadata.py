# -*- coding: utf-8 -*-
"""
Scrapes web pages or load stored files with music metadata

"""

import requests
from bs4 import BeautifulSoup
import datetime

data_path = 'Data/'

file_names = ['countries', 'eras', 'genres', 'languages', 'moods', 'ensembles']


def load_data(scrape=False):
    if scrape:
        scrape_data()
    data_dict = {}
    for file_name in file_names:
        with open(data_path + file_name + '.txt', 'r', encoding='utf-8') as f:
            data_dict[file_name] = [info for info in f.read().splitlines()]
    return data_dict


def scrape_data():
    data_dict = {}

    # country
    url = 'https://en.wikipedia.org/wiki/List_of_sovereign_states'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html5lib')
    data_dict['country'] = []
    for row in soup.find('tbody').findAll('tr'):
        try:
            link = row.find('td').find('a')
        except:
            continue
        if link:
            text = link.text
            if text == 'UN member states':
                continue
            if ',' in text:
                pos = text.find(',')
                text = text[pos+2:] + ' ' + text[:pos]
            text = text.strip()
            data_dict['country'].append(text)

    # era
    year = datetime.datetime.now().year
    year = year - year % 10
    data_dict['era'] = [str(era) for era in range(1400, year+1, 10)]

    # genres
    url = 'https://musicbrainz.org/genres'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html5lib')
    data_dict['genre'] = []
    for base in soup.find('div', attrs={'id': 'content'}).findAll('li'):
        data_dict['genre'].append(base.find('a').text)

    # languages
    url = 'https://en.wikipedia.org/wiki/List_of_official_languages'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html5lib')
    data_dict['language'] = []
    for p in soup.find('div', attrs={'id': 'mw-content-text'}).findAll('p'):
        b = p.find('b')
        if b:
            link = b.find('a')
            if link:
                text = link.text
                if ',' in text:
                    text = text[:text.find(',')]
                if '(' in text:
                    text = text[:text.find('(')]
                data_dict['language'].append(text)

    # moods
    url = 'https://moodlist.net/'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html5lib')
    data_dict['mood'] = []
    for p in soup.find('div', attrs={'class': 'entry-content'}).findAll('p'):
        for mood in p.get_text().split('\n'):
            if mood == 'This is a list of moods.':
                continue
            data_dict['mood'].append(mood.strip())

    for file_name in file_names:
        with open(data_path+file_name+'.txt', 'w+', encoding='utf-8') as f:
            for info in data_dict[file_name]:
                f.write(info+'\n')
