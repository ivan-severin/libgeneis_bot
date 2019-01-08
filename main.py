#!/usr/bin/env python
from BookInfo import BookInfoProvider


if __name__ == '__main__':
    print('Hello Bot!')
    name = 'Dynamics of Surfaces and Reaction Kinetics in Heterogeneous Catalysis'
    book = BookInfoProvider(name, 'title')
    bookList = book.load_book_list()
    for book in bookList:
        print(book)


