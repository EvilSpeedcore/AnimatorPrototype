from collections import deque


class Page:

    def __init__(self, page_number, titles):
        self.page_number = page_number
        self.titles = titles

    def __iter__(self):
        return iter(self.titles)


class TitlePaginator:

    PAGE_SIZE = 18

    def __init__(self, titles):
        self.titles = titles
        self.sep_titles = [self.titles[i:i+self.PAGE_SIZE] for i in range(0, len(self.titles), self.PAGE_SIZE)]

    @property
    def pages(self):
        for index, titles in enumerate(self.sep_titles, start=1):
            yield Page(index, titles)

    def find(self, page_number):
        page = [page for page in self.pages if page.page_number == page_number]
        return next(iter(page))

    def flip_forward(self, n):
        d = deque(self.pages)
        d.rotate(-n)
        return next(iter(d))

    def flip_backwards(self, n):
        d = deque(self.pages)
        d.rotate(-n+2)
        return next(iter(d))
