import sqlite3
import pandas as pd
import numpy as np


def makeTables(cursor):
    #create the user table
    cursor.execute("""DROP TABLE IF EXISTS user;""")
    create_user = """CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    age INTEGER
    );"""
    cursor.execute(create_user)

    #create the book table
    cursor.execute("""DROP TABLE IF EXISTS book;""")
    create_book = """CREATE TABLE book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    year INT
    );"""
    cursor.execute(create_book)

    #create the implicit review table
    cursor.execute("""DROP TABLE IF EXISTS reviewImp;""")
    create_review = """CREATE TABLE reviewImp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    rate INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (isbn) REFERENCES book (isbn)
    );"""
    cursor.execute(create_review)

    #create the implicit review table
    cursor.execute("""DROP TABLE IF EXISTS reviewExp;""")
    create_review = """CREATE TABLE reviewExp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    rate INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (isbn) REFERENCES book (isbn)
    );"""
    cursor.execute(create_review)

    return

def opencsv(csvname):
    csv = pd.read_csv(csvname, sep=';', error_bad_lines = False, encoding='latin-1')
    return csv

def compactBooks(book, ratings):
    #count entries with same name and same author
    bookgroups = book.groupby(["title", "author"])

    booksort = bookgroups.size().sort_values(ascending=False)
    for i, ind in enumerate(booksort.index):
        #look only at the ones with counts > 1
        if booksort.values[i] == 1:
            continue
        else:
            thisgroup = bookgroups.groups[ind[0], ind[1]]
            firstind = thisgroup[0]
            firstisbn = book['isbn'][firstind]  #get isbn for book with this index
            #loop through others in groups
            for i in thisgroup[1:]:
                #change isbns in *ratings* of group to firstisbn
                copyisbn = book['isbn'][i]
                ratingsOnCopy = np.where(ratings['isbn']==copyisbn)
                ratings['isbn'][ratingsOnCopy[0]] = firstisbn

                #drop row of book copy
                book.drop([i], inplace=True)

    return book, ratings


def cleanData(users, books, ratings):
    #change column names
    users.columns = ['id', 'age']
    books.columns= ['isbn', 'title', 'author', 'year']
    ratings.columns = ['user_id', 'isbn', 'rate']

    ### USERS ###
    #only keep users we have ratings for
    users = users[users['id'].isin(ratings['user_id'])]
    #fill Nan ages with the median age
    users['age'] = users['age'].where(pd.notnull(users['age']), int(users['age'].mean()))

    ### BOOKS ###
    #compact books with the same title and author
    books, ratings = compactBooks(books, ratings)

    ### RATINGS ###

    #only take ratings for books we have in the books table
    ratings_allbooks = ratings[ratings['isbn'].isin(books['isbn'])]
    #separate implicit and explicit ratings
    ratings_implicit = ratings_allbooks[ratings_allbooks["rate"] == 0]
    ratings_explicit = ratings_allbooks[ratings_allbooks["rate"] != 0]

    #remove duplicates if users read multiple versions of the same book
    ratings_implicit.drop_duplicates(subset=['ISBN', 'User-ID'], inplace=True)
    ratings_explicit.drop_duplicates(subset=['ISBN', 'User-ID'], inplace=True)

    #set implicit ratings to 1, so that read = 1, unread = 0 later
    ratings_implicit["rate"] = np.ones(len(ratings_implicit['rate']))

    return users, books, ratings_implicit, ratings_explicit


if __name__ == "__main__":
    #open book files, drop unnecessary columns
    users = opencsv('BX-CSV-DUMP/BX-Users.csv')
    users.drop(['Location'], axis = 1, inplace=True)

    books = opencsv('BX-CSV-Dump/BX-Books.csv')

    books.drop(['Image-URL-S', 'Image-URL-M', 'Image-URL-L', 'Publisher'], axis=1, inplace=True)
    ratings = opencsv('BX-CSV-DUMP/BX-Book-Ratings.csv')

    users, books, rate_imp, rate_exp = cleanData(users, books, ratings)

    #connect to database
    conn = sqlite3.connect("bookreviews.db")
    cursor = conn.cursor()
    makeTables(cursor)

    #conver pandas tables to sql tables
    users.to_sql('user',con=conn, if_exists='append', index=False)
    books.to_sql('book',con=conn,if_exists='append', index = False)
    rate_imp.to_sql('reviewImp', con=conn, if_exists='append', index = False)
    rate_exp.to_sql('reviewExp', con=conn, if_exists='append', index = False)

    cursor.execute("SELECT * FROM user")
    res = cursor.fetchone()
    print(res)

    cursor.execute("SELECT * FROM book")
    res = cursor.fetchone()
    print(res)

    cursor.execute("SELECT * FROM reviewImp")
    res = cursor.fetchone()
    print(res)

    cursor.execute("SELECT * FROM reviewExp")
    res = cursor.fetchone()
    print(res)

    conn.commit()
    conn.close()
