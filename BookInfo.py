import re
import urllib.request
from bs4 import BeautifulSoup


class BookInfo:
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
    publisher: {publisher},
    title: {title},
    pages: {pages},
    format: {format},
    year: {year},
    links: {links}\
    '''.format(author=self.authors,
               publisher=self.publisher,
               title=self.title,
               pages=self.pages,
               format=self.format,
               year=self.year,
               links= self.download_links)

        return text_str


class BookInfoProvider:
    DOMAIN = 'http://libgen.io'
    URL = DOMAIN + '/search.php?req={}&open=0&view=simple&phrase=1&column={}'

    def __init__(self, search_query, search_type):
        self.query = search_query.strip().replace(" ", "+")
        self.type = search_type

    def load_book_list(self):
        request = urllib.request.Request(BookInfoProvider.URL.format(self.query, self.type))
        print(BookInfoProvider.URL.format(self.query, self.type))
        response = urllib.request.urlopen(request)

        soup = BeautifulSoup(response, 'html.parser')
        table = soup.find('table', attrs={'class': 'c'})
        table_rows = table.findAll('tr', recursive=False)[1:]
        book_list = list()
        for row in table_rows:
            book_list.append(BookInfo(self.extract_book(row)))

        return book_list

    def extract_book(self, table_row):
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
                links.append(link['href'])

            book['links'] = links
        except Exception as e:
            print('Got error:', e)

        return book
