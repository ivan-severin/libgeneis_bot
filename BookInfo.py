# -*- coding: utf-8 -*-

import re
import urllib.parse
import urllib.request
import urllib.error
import bitly_api
from common import BITLY_USER, BITLY_API_KEY
from bs4 import BeautifulSoup


class BookInfo:
    """Class for storing book information"""
    def __init__(self, book):
        self.title = book.get('title', None)
        self.authors = book.get('authors', None)
        self.id = book.get('id', None)
        self.publisher = book.get('publisher', None)
        self.pages = book.get('pages', None)
        self.format = book.get('format', None)
        self.year = book.get('year', None)
        self.language = book.get('language', None)
        self.year = book.get('year', None)
        self.size = book.get('size', None)

        self.download_links = book.get('links', list())

    def __repr__(self):
        return 'BookInfo(author: {}, title: {}...)'.format(self.author, self.title[:15])

    def __str__(self):
        text_str = '''\
Book:
    author: {author},
    title: {title},
    publisher: {publisher},
    pages: {pages},
    format: {format},
    year: {year},
    size: {size},
    links: {links}\
    '''.format(author=self.authors,
               publisher=self.publisher,
               title=self.title,
               pages=self.pages,
               format=self.format,
               year=self.year,
               size=self.size,
               links=self.download_links)

        return text_str


class BookInfoProvider:
    """Class which loads book information"""
    DOMAIN = 'http://libgen.io'
    URL = DOMAIN + '/search.php?req={}&open=0&view=simple&phrase=1&column={}'

    def __init__(self):
        self.bitly = bitly_api.Connection(BITLY_USER, BITLY_API_KEY)

    def load_book_list(self, search_query, search_type):
        """Loads books with search_query and search_type. Returns list()"""
        search_query = search_query.strip().replace(" ", "+")
        search_query = urllib.parse.quote(search_query)

        request = urllib.request.Request(self.URL.format(search_query, search_type))
        response = urllib.request.urlopen(request)

        soup = BeautifulSoup(response, 'html.parser')
        table = soup.find('table', attrs={'class': 'c'})
        table_rows = table.findAll('tr', recursive=False)[1:]
        book_list = list()
        for row in table_rows[:5]:
            book_list.append(BookInfo(self.__extract_book(row)))

        return book_list

    def __extract_book(self, table_row):
        """Extract book information from piece of html page. Returns dictionary"""
        book = dict()

        domains = table_row.find_all('td')
        it = iter(domains)

        try:
            book['id'] = next(it).contents[0]
            book['authors'] = ''.join([i.text for i in next(it).find_all('a', href=re.compile("author"))])

            # extract some info from Title domain (possible more)
            title_domain = next(it)
            series = title_domain.find('a', href=re.compile("series"))
            book['series'] = series.text if series is not None else None
            book['title'] = title_domain.find('a', href=re.compile("book")).contents[0]

            # Just text fields
            book['publisher'] = next(it).text
            book['year'] = next(it).text
            book['pages'] = next(it).text
            book['language'] = next(it).text
            book['size'] = next(it).text
            book['format'] = next(it).text

            # Get download links
            links = list()
            for link in next(it).find_all('a'):
                download_link = self.__get_download_link(link['href'])
                if download_link is not None:
                    links.append(download_link)

            book['links'] = links
        except Exception as e:
            print('Got gggg error:', e)
            raise(e)
        return book

    def __get_download_link(self, book_link):
        download_link = None
        request = urllib.request.Request(book_link)
        try:
            response = urllib.request.urlopen(request)
            soup = BeautifulSoup(response, 'html.parser')

            long_link = soup.find_all('a', href=True, text='GET')[0]['href']
            download_link = self.bitly.shorten(long_link)['url']

        except urllib.error.HTTPError as e:
            # Return code error (e.g. 404, 501, ...)
            # ...
            print('HTTPError: ', e.code)
        except urllib.error.URLError as e:
            # Not an HTTP-specific error (e.g. connection refused)
            # ...
            print('URLError: ', e.reason)
        except bitly_api.BitlyError as e:
            # this fucking bit.ly
            print('BitlyError: ', e)
        except  Exception as e:
            # this another shit
            print('Some Another error:', e)
        return download_link
