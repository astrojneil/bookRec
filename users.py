import sqlite3
from recommender import *

class User:
    def __init__(self):
        self.id = 0  #integer
        self.age = 0 #integer
        self.books = [] #list of isbns
        self.rates = {} #dict with isbn:rate

    def getUser(self, id, conn):
        self.id = id
        #connect to database
        #conn = sqlite3.connect("bookreviews.db")
        cursor = conn.cursor()

        #get age
        cursor.execute('SELECT age FROM user WHERE user.id = ?', (id,))
        if cursor.fetchone() is not None:
            self.age = cursor.fetchone()

        #get books read and ratings
        cursor.execute('SELECT isbn FROM reviewImp WHERE user_id = ?', (id,))
        booklist = cursor.fetchall()
        if booklist:
            self.books = [book[0] for book in booklist]

        cursor.execute('SELECT isbn, rate FROM reviewExp WHERE user_id = ?', (id,))
        ratelist = cursor.fetchall()
        if ratelist:
            for rate in ratelist:
                self.rates[rate[0]] = rate[1]

        #conn.close()
        return self


    def makeUser(self, conn, age = None, books= [], rates= {}):

        #conn = sqlite3.connect("bookreviews.db")
        cursor = conn.cursor()

        cursor.execute('SELECT MAX(user.id) FROM user')
        new_id = cursor.fetchone()[0]+1
        self.id = new_id

        #add user to user table
        if age is not None:
            cursor.execute('INSERT INTO user (id, age) VALUES (?, ?)', (new_id, age))
            self.age = age
        else:
            cursor.execute('INSERT INTO user (id, age) VALUES (?, 0)', (new_id,))
        print('New User created; id = {}'.format(new_id))


        #add any books read to reviewImp
        if books:
            for book in books:
                #add book to db
                cursor.execute('INSERT INTO reviewImp (isbn, user_id, rate) VALUES (?, ?, ?)', (book, self.id, 1))
                #add books to object
                self.books.append(book)
        #add any ratings to reviewExp
        if rates:
            for i, book in enumerate(rates):
                #add rates to db
                cursor.execute('INSERT INTO reviewExp (isbn, user_id, rate) VALUES (?, ?, ?)', (book, self.id, rates[book]))
                #add rates to object
                self.rates[book] = rates[book]

        conn.commit()
        #conn.close()
        return self

    def deleteUser(self, conn):
        id = self.id
        #conn = sqlite3.connect("bookreviews.db")
        cursor = conn.cursor()

        cursor.execute('DELETE FROM user WHERE user.id = ?', (id,))
        cursor.execute('DELETE FROM reviewImp WHERE reviewImp.user_id = ?', (id,))
        cursor.execute('DELETE FROM reviewExp WHERE reviewExp.user_id = ?', (id,))
        conn.commit()

        print('User {} deleted'.format(id))
        #conn.close()

    def deleteUser_id(self, id, conn):
        #conn = sqlite3.connect("bookreviews.db")
        cursor = conn.cursor()

        cursor.execute('DELETE FROM user WHERE user.id = ?', (id,))
        cursor.execute('DELETE FROM reviewImp WHERE reviewImp.user_id = ?', (id,))
        cursor.execute('DELETE FROM reviewExp WHERE reviewExp.user_id = ?', (id,))
        conn.commit()

        print('User {} deleted'.format(id))
        #conn.close()

    def addBooks(self, books, conn):
        #conn = sqlite3.connect("bookreviews.db")
        cursor = conn.cursor()
        for book in books:
            #add book to db
            cursor.execute('INSERT INTO reviewImp (isbn, user_id, rate) VALUES (?, ?, ?)', (book, self.id, 1))
            #add books to object
            self.books.append(book)
        conn.commit()
        #conn.close()

    def addRates(self, rates, conn):
        #conn = sqlite3.connect("bookreviews.db")
        cursor = conn.cursor()

        for i, book in enumerate(rates):
            #add rates to db
            cursor.execute('INSERT INTO reviewExp (isbn, user_id, rate) VALUES (?, ?, ?)', (book, self.id, rates[book]))
            #add rates to object
            self.rates[book] = rates[book]

        conn.commit()
        #conn.close()

    def deleteBook(self, isbn, conn):
        #conn = sqlite3.connect("bookreviews.db")
        cursor = conn.cursor()
        #remove from db
        cursor.execute('DELETE FROM reviewExp WHERE (isbn = ? AND user_id = ?)', (isbn, self.id))
        cursor.execute('DELETE FROM reviewImp WHERE (isbn = ? AND user_id = ?)', (isbn, self.id))
        #remove from user

        self.rates.pop(isbn, None)
        if isbn in self.books: self.books.remove(isbn)

        conn.commit()
        #conn.close()

    def recommend(self, conn):
        recommendbook(self, conn)
