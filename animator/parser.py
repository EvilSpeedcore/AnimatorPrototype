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

    @property
    def synopsis(self):
        return self.anime_info['synopsis']

    @property
    def image_url(self):
        return self.anime_info['image_url']

    @property
    def url(self):
        return self.anime_info['url']


class AnimeList:

    jikan = Jikan()

    def __init__(self, user):
        self.owner = user
        self.anime_list = self.form_list()
        self._index = 0

    def form_list(self):
        records = []
        page = 1
        while True:
            lst = AnimeList.jikan.user(username=self.owner, request='animelist', argument='completed', page=page)
            anime = lst['anime']
            if anime:
                for each in anime:
                    title = unicodedata.normalize('NFC', each['title'])
                    score = each['score'] if each['score'] else 5
                    records.append(ListRecord(each['mal_id'], title, score))
                page += 1
            else:
                break
        return records

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


def rand(filename, is_header, page, start):
    import csv
    import time
    from jikanpy import Jikan, exceptions
    jikan = Jikan()

    def write_row(info, fieldnames, writer):
        f = (info.title, info.type, info.episodes, info.studio, info.source,
             info.genre, info.score, info.synopsis, info.url, info.image_url)
        row = {x: y for x, y in zip(fieldnames, f)}
        writer.writerow(row)
        #  time.sleep(15)

    with open(filename, 'a', newline='', encoding='UTF-8') as csvfile:
        fieldnames = ['title', 'type', 'episodes', 'studio', 'src', 'genre', 'score', 'synopsis', 'url', 'image_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if is_header:
            writer.writeheader()

        top_anime = jikan.top(type='anime')
        for index, each in enumerate(top_anime['top'][start:]):
            print('Processing anime number [{}].'.format(index+start))
            try:
                info = AnimePageInfo(each['mal_id'])
            except exceptions.APIException:
                print('FAIL.')
                exit(1)
            else:
                write_row(info, fieldnames, writer)
