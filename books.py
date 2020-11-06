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