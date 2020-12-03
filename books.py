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
    def isbn_to_book(self, isbn):
        self.isbn = isbn
        conn = sqlite3.connect("bookreviews.db")
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM book WHERE  book.isbn = ?', (isbn,))
        b = cursor.fetchone()
        self.id = b[0]
        self.title = b[2]
        self.author = b[3]
        self.year = b[4]

        conn.close()

    #find a book by id
    def id_to_book(self, id):
        self.id = id
        conn = sqlite3.connect("bookreviews.db")
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM book WHERE  book.id = ?', (id,))
        b = cursor.fetchone()
        print(b)
        self.isbn = b[1]
        self.title = b[2]
        self.author = b[3]
        self.year = b[4]

        conn.close()

    def title_to_book(self, title):
        #parse title to core words
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(title.lower())

        filtered_title = [w for w in words if not w in stop_words]

        conn = sqlite3.connect("bookreviews.db")
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
        print(b)
        self.id = b[0]
        self.isbn = b[1]
        self.title = b[2]
        self.author = b[3]
        self.year = b[4]

        conn.close()



if __name__ == '__main__':
    b = Book()
    b.isbn_to_book('0155061224')
    print(b.id)
    print(b.isbn)
    print(b.title)
    print(b.author)
    print(b.year)

    b.id_to_book(225817)
    print(b.id)
    print(b.isbn)
    print(b.title)
    print(b.author)
    print(b.year)

    b.title_to_book('Carnival of the Spirit')
    print(b.id)
    print(b.isbn)
    print(b.title)
    print(b.author)
    print(b.year)

    conn = sqlite3.connect("bookreviews.db")
    cursor = conn.cursor()

    cursor.execute('SELECT isbn FROM book LIMIT 10')
    b = cursor.fetchall()
    print(b)
