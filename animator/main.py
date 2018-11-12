import time
import collections
import json
import urllib.parse

import bs4
import requests

SITE_URL = 'https://myanimelist.net'


def parse_anime_page(page_url):
    session = requests.session()
    response = session.get(page_url)
    data = response.text
    header = bs4.BeautifulSoup(data, 'lxml', parse_only=bs4.SoupStrainer('span'))
    title = header.find('span', attrs={'itemprop': 'name'}).text
    information = bs4.BeautifulSoup(data, 'lxml', parse_only=bs4.SoupStrainer('div'))
    span_tags = information.find_all('span', class_='dark_text')
    required_colons = ('Type:', 'Episodes:', 'Studios:', 'Source:', 'Genres:', 'Score:')
    colons = [colon for colon in span_tags if colon.text in required_colons]
    page_data = {'Title': title}
    for tag in colons:
        if tag.next_sibling.next_sibling:
            key = tag.text.strip(':')
            value = tag.next_sibling.next_sibling.text
            page_data[key] = value
        else:
            key = tag.text.strip(':')
            value = str(tag.next_sibling.strip())
            page_data[key] = value
    return page_data


class AnimeListRecord:

    def __init__(self, personal_score, url):
        self.personal_score = personal_score
        self.url = url

    def __str__(self):
        return 'AnimeListRecord({self.title}, {self.type}, {self.personal_score}, {self.url})'.format(self=self)


class Profile:

    def __init__(self, username):
        self.username = username
        self.anime_list = AnimeList(self.username)


class AnimeList:

    def __init__(self, username):
        self.owner = username
        self.url = '/'.join((SITE_URL, 'animelist', self.owner))
        self.anime = self.form_list()

    def form_list(self):
        session = requests.session()
        payload = {'status': '2', 'tag': ''}
        #  TODO: Add retry or sleep or something. How you handled this in old code?
        response = session.get(self.url, params=payload)
        data = response.text
        #  TODO: Add soup strainer.
        soup = bs4.BeautifulSoup(data, 'lxml')
        anime_list = soup.find('div', attrs={'id': 'list_surround'})

        anime_lst = []
        for link in anime_list.find_all('a', attrs={'class': 'animetitle'}):
            #  TODO: Remove non ASCII characters from title.
            url = urllib.parse.urljoin(SITE_URL, link.get('href'))
            parent = link.parent
            score_cell = parent.next_sibling.next_sibling
            score = score_cell.text.strip()
            anime_lst.append(AnimeListRecord(score, url))
        return anime_lst


def convert_anime_list_into_json(username):

    #  TODO: Not working for new anime lists

    profile = Profile(username)

    data = collections.defaultdict(list)
    for record in profile.anime_list.anime:
        page_data = parse_anime_page(record.url)
        if page_data:
            page_data.update({'Personal score': record.personal_score})
            for key, value in page_data.items():
                data[key].append(value)
    data_set = json.dumps(data)
    return data_set