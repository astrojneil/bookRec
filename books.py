import sqlite3

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
        print(b)
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

    def title_to_book(self, title1, title2, author):
        #parse title to core words


        conn = sqlite3.connect("bookreviews.db")
        cursor = conn.cursor()
        #find book where title contains core words
        cursor.execute('SELECT * FROM book WHERE LOWER(book.title) LIKE ? and LOWER(book.title) LIKE ? and lower(book.author) LIKE ?', (title1, title2, author))
        b = cursor.fetchall()
        print(b)
        #self.isbn = b[1]
        #self.title = b[2]
        #self.title = id
        #self.author = b[3]
        #self.year = b[4]

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

    b.title_to_book('%rites%', '%passage%', '%william golding%')
