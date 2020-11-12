import sqlite3


class User:
    def __init__(self):
        self.id = 0  #integer
        self.age = 0 #integer
        self.books = [] #list of isbns
        self.rates = {} #dict with isbn:rate

    def getuser(self, id):
        self.id = id
        #connect to database
        conn = sqlite3.connect("bookreviews.db")
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

        conn.close()


    def makeUser(self,age = None, books= [], rates= {}):

        conn = sqlite3.connect("bookreviews.db")
        cursor = conn.cursor()

        cursor.execute('SELECT MAX(user.id) FROM user')
        new_id = cursor.fetchone()[0]+1

        #add user to user table
        if age is not None:
            cursor.execute('INSERT INTO user (id, age) VALUES (?, ?)', (new_id, age))
        else:
            cursor.execute('INSERT INTO user (id, age) VALUES (?, 0)', (new_id,))
        print('New User created; id = {}'.format(new_id))


        #add any books read to reviewImp
        if books:
            #loop through books (isbns)
            for book in books:
                cursor.execute('INSERT INTO reviewImp (isbn, user_id, rate) VALUES (?, ?, ?)', (book, new_id, 1))

        #add any ratings to reviewExp
        if rates:
            #loop through books
            for i, book in enumerate(rates):
                cursor.execute('INSERT INTO reviewExp (isbn, user_id, rate) VALUES (?, ?, ?)', (book, new_id, rates[book]))

        conn.commit()
        conn.close()



    def deleteUser(self, id):
        conn = sqlite3.connect("bookreviews.db")
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user WHERE user.id = ?', (id,))
        cursor.execute('DELETE FROM reviewImp WHERE reviewImp.user_id = ?', (id,))
        cursor.execute('DELETE FROM reviewExp WHERE reviewExp.user_id = ?', (id,))
        conn.commit()
        print('User {} deleted'.format(id))
        conn.close()


#add a book to list of books
#add book/rate to rates
#recommend books for this user ** big one! will need to call functions for actual recommender


if __name__ == '__main__':

    u = User()
    u.getuser(2)
    print(u.books)
    u.getuser(276726)
    print(u.rates)
    u.makeUser(rates = {'0195153448':3, '0155061224':6}, books = ['0195153448', '0155061224'], age= 34)
    u.deleteUser(278855)
