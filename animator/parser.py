#  TODO: Put classes into different files
import collections
import concurrent.futures
import pathlib
import time
import unicodedata
import urllib.parse

import bs4
from jikanpy import Jikan
import requests


ListRecord = collections.namedtuple('ListRecord', ['mal_id', 'title', 'personal_score'])


class AnimePageInfo:

    def __init__(self, anime_id):
        self.anime_id = anime_id
        self.anime_info = Jikan().anime(self.anime_id)

    @property
    def title(self):
        return self.anime_info['title']

    @property
    def type(self):
        return self.anime_info['type']

    @property
    def episodes(self):
        return self.anime_info['episodes']

    @property
    def studio(self):
        studios = self.anime_info.get('studios')
        return studios[0]['name'] if studios else 'None found'

    @property
    def source(self):
        return self.anime_info['source']

    @property
    def genre(self):
        return self.anime_info['genres'][0]['name']

    @property
    def score(self):
        return self.anime_info['score']


class AnimeList:

    def __init__(self, user):
        self.owner = user
        self.site_url = 'https://myanimelist.net'
        self.url = '/'.join((self.site_url, 'animelist', self.owner))
        self.anime_list = self.form_list()
        self._index = 0

    def form_list(self):
        session = requests.session()
        response = session.get(self.url, params={'status': '2', 'tag': ''})
        data = response.text
        #  TODO: Add soup strainer.
        soup = bs4.BeautifulSoup(data, 'lxml')
        anime_list = soup.find('div', attrs={'id': 'list_surround'})
        anime = []
        for link in anime_list.find_all('a', attrs={'class': 'animetitle'}):
            title = unicodedata.normalize('NFC', link.text.strip())
            url = urllib.parse.urljoin(self.site_url, link.get('href'))
            anime_id = pathlib.Path(url).parts[3]
            score_cell = link.parent.next_sibling.next_sibling
            score = score_cell.text.strip()
            score = int(score) if score.isdigit() else 0
            anime.append(ListRecord(anime_id, title, score))
        return anime

    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = self.anime_list[self._index]
        except IndexError:
            raise StopIteration
        self._index += 1
        return item


class MALUser:

    def __init__(self, username):
        self.username = username
        self.anime_list = AnimeList(self.username)


class DataSetConstructor:

    def __init__(self, anime_list):
        self.anime_list = anime_list

    def create_data_set(self):
        #  TODO: Think about putting ProcessPullExecutor part outside of class to keep track of progress.
        data_set = collections.defaultdict(list)
        counter = 0
        with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
            for record in executor.map(DataSetConstructor.create_sample, self.anime_list):
                counter += 1
                print(counter)
                for key, value in record.items():
                    data_set[key].append(value)
                if counter % 100 == 0:
                    time.sleep(15)
        return data_set

    @staticmethod
    def create_sample(record):
        time.sleep(1)
        try:
            anime_page = AnimePageInfo(record.mal_id)
        except Exception as e:
            print(e)
            time.sleep(15)
            return DataSetConstructor.create_sample(record)
        else:
            #  TODO: It is cumbersome to list all properties. Put them into structure in AnimePagInfo class?
            record = {'Title': anime_page.title,
                      'Type': anime_page.type,
                      'Episodes': anime_page.episodes,
                      'Studios': anime_page.studio,
                      'Source': anime_page.source,
                      'Genres': anime_page.genre,
                      'Score': anime_page.score,
                      'Personal score': record.personal_score}
            return record
