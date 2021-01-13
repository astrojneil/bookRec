import sqlite3
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


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
        self.id = b[0]
        self.isbn = b[1]
        self.title = b[2]
        self.author = b[3]
        self.year = b[4]


        return self
