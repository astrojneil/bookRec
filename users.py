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
        self.age = cursor.fetchone()[0]

        #get books read and ratings
        cursor.execute('SELECT isbn FROM reviewImp WHERE user_id = ?', (id,))
        booklist = cursor.fetchall()
        self.books = [book[0] for book in booklist]

        cursor.execute('SELECT isbn, rate FROM reviewExp WHERE user_id = ?', (id,))
        ratelist = cursor.fetchall()
        for rate in ratelist:
            self.rates[rate[0]] = rate[1]

        conn.close()
    def makeUser(age = None):





        print('New User created; id = {}'.format(user_id))


if __name__ == '__main__':
    u = User()
    u.getuser(2)
    print(u.books)
    u.getuser(276726)
    print(u.rates)
