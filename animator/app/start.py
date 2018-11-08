import urllib.parse

import bs4
import requests

SITE_URL = 'https://myanimelist.net'

#  Есть сайт MyAnimeList.
#  На сайте люди делают себе профайлы.
#  Каждый профайл содержит в себе Anime List.


class MALProfile:

    def __init__(self, username):
        self.username = username
        self.site_url = 'https://myanimelist.net'
        self.anime_list_url = '/'.join((self.site_url, 'animelist', self.username))
        self.anime_list = None


class AnimeList:

    def __init__(self):
        pass


class MALParser:

    def __init__(self, username):
        self.profile = MALProfile(username)
        self.session = requests.Session()
        self.parser = 'lxml'

    def form_dataset(self):
        payload = {'status': '2', 'tag': ''}
        response = self.session.get(self.profile.anime_list_url, params=payload)
        data = response.text
        #  TODO: Add SoupStrainer.
        soup = bs4.BeautifulSoup(data, self.parser)
        anime_list = soup.find('div', attrs={'id': 'list_surround'})

        anime = {}
        for link in anime_list.find_all('a', attrs={'class': 'animetitle'}):
            #  TODO: Remove non ASCII characters from title.
            anime_title = link.span.text.strip()
            anime_url = urllib.parse.urljoin(self.profile.site_url, link.get('href'))
            parent = link.parent
            score_cell = parent.next_sibling.next_sibling
            anime_score = score_cell.text.strip()
            type_cell = score_cell.next_sibling.next_sibling
            anime_type = type_cell.text.strip()

            anime.setdefault('Title', []).append(anime_title)
            anime.setdefault('Score', []).append(anime_score)
            anime.setdefault('Type', []).append(anime_type)

            #  Anime page parse.
            response = self.session.get(anime_url)
            data = response.text
            strainer = bs4.SoupStrainer('div')
            soup = bs4.BeautifulSoup(data, 'lxml', parse_only=strainer)
            span_tags = soup.find_all('span', class_='dark_text')
            required_colons = ('Type:', 'Episodes:', 'Studios:', 'Source:', 'Genres:', 'Score:')
            colons = [colon for colon in span_tags if colon.text in required_colons]
            for tag in colons:
                if tag.next_sibling.next_sibling:
                    anime.setdefault(tag.text.strip(':'), []).append(tag.next_sibling.next_sibling.text)
                else:
                    anime.setdefault(tag.text.strip(':'), []).append(str(tag.next_sibling.strip()))
        self.profile.anime_list = anime
        return anime


if __name__ == '__main__':
    parser = MALParser('GachiM_n')
    dataset = parser.form_dataset()


