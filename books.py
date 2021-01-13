import sqlite3
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import requests
import pandas as pd
import json

apikey =pd.read_csv('apikey.txt')

class Book:
    def __init__(self):
        self.id = 0
        self.isbn = ''
        self.title = ''
        self.author = ''
        self.year = ''

    #find a book by isbn
    def isbn_to_book(self, isbn, conn):
        self.isbn = isbn
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM book WHERE  book.isbn = ?', (isbn,))
        b = cursor.fetchone()
        self.id = b[0]
        self.title = b[2]
        self.author = b[3]
        self.year = b[4]

        return self


    #find a book by id
    def id_to_book(self, id, conn):
        self.id = id
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM book WHERE  book.id = ?', (id,))
        b = cursor.fetchone()
        self.isbn = b[1]
        self.title = b[2]
        self.author = b[3]
        self.year = b[4]

        return self


    def title_to_book(self, title, conn):
        #parse title to core words
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(title.lower())

        filtered_title = [w for w in words if not w in stop_words]

        cursor = conn.cursor()

        #create the sql command to find where title contains these words
        execute_string = 'SELECT * FROM book WHERE '
        for i, word in enumerate(filtered_title):
            if i == 0:
                execute_string = execute_string+'LOWER(book.title) LIKE ? '
            else:
                execute_string = execute_string+'and LOWER(book.title) LIKE ? '
            filtered_title[i] = '%'+word+'%'


        #find book where title contains core words
        cursor.execute(execute_string, tuple(filtered_title))
        b = cursor.fetchone()
<<<<<<< HEAD
        print(b)
        if b == None:
            self.findNewBook(title, conn)
        else:
            self.id = b[0]
            self.isbn = b[1]
            self.title = b[2]
            self.author = b[3]
            self.year = b[4]

        #conn.close()

    def findNewBook(self, title, conn):
        cursor = conn.cursor()
        titlestr = title.replace(' ', '+')

        url = "https://www.googleapis.com/books/v1/volumes?q=intitle:"+titlestr+"&key="+apikey['key'][0]
        loaded = requests.get(url).text

        html = json.loads(loaded)
        self.title = html['items'][0]['volumeInfo']['title']
        self.author = html['items'][0]['volumeInfo']['authors'][0]
        self.isbn = html['items'][0]['volumeInfo']['industryIdentifiers'][1]['identifier']
        self.year = html['items'][0]['volumeInfo']['publishedDate'][:4]

        cursor.execute('INSERT INTO book (isbn, title, author, year) VALUES (?, ?, ?, ?)', (self.isbn, self.title, self.author, self.year))
        conn.commit()
        cursor.execute("SELECT id FROM book WHERE (isbn = ? AND title = ? AND author = ? AND year = ?)", (self.isbn, self.title, self.author, self.year))
        b = cursor.fetchone()
        self.id = b
=======
        self.id = b[0]
        self.isbn = b[1]
        self.title = b[2]
        self.author = b[3]
        self.year = b[4]


        return self
>>>>>>> main
