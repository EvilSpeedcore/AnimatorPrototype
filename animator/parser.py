#  TODO: Put classes into different files
import collections
import concurrent.futures
import time
import unicodedata

from jikanpy import Jikan


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
        self.anime_list = Jikan().user(username=user, request='animelist')['anime']
        self.completed_anime = [title for title in self.anime_list if title['watching_status'] == 2]
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = self.completed_anime[self._index]
        except IndexError:
            raise StopIteration
        self._index += 1
        title = unicodedata.normalize('NFC', item['title'])
        score = item['score'] if isinstance(item['score'], int) else 0
        return ListRecord(item['mal_id'], title, score)


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
                #  TODO: See on average number of allowed requests.
                counter += 1
                print(counter)
                for key, value in record.items():
                    data_set[key].append(value)
        return data_set

    @staticmethod
    def create_sample(record):
        time.sleep(1)
        try:
            anime_page = AnimePageInfo(record.mal_id)
        except Exception as e:
            print(e)
            time.sleep(5)
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
