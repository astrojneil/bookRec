import sqlite3
import pandas as pd
import numpy as np


def makeTables(cursor):
    #create the user table
    cursor.execute("""DROP TABLE IF EXISTS user;""")
    create_user = """CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

def cleanRatings(allratings, books):
    #only take ratings for books we have in the books table
    ratings_allbooks = allratings[allratings['ISBN'].isin(books['ISBN'])]
    #separate implicit and explicit ratings
    ratings_implicit = ratings_allbooks[ratings_allbooks["Book-Rating"] == 0]
    ratings_explicit = ratings_allbooks[ratings_allbooks["Book-Rating"] != 0]
    #set implicit ratings to 1, so that read = 1, unread = 0 later
    ratings_implicit["Book-Rating"] = np.ones(len(ratings_implicit['Book-Rating']))

    return ratings_implicit, ratings_explicit

def addToTables(cursor, csvTable, sqTable):
    if sqTable =='users':
        format_str = """INSERT INTO user (age) VALUES ("{age}");"""

        for i in range(len(csvTable)):
            sql_command = format_str.format(age=csvTable['Age'][i])
            cursor.execute(sql_command)

    if sqTable =='books':
        format_str = """INSERT INTO book (isbn, title, author, year) VALUES ("{isbn}", "{title}", "{author}", "{year}");"""

        for i in range(len(csvTable)):
            sql_command = format_str.format(isbn=csvTable['ISBN'][i], title=csvTable['Book-Title'][i],
            author=csvTable['Book-Author'], year=csvTable['Year-Of-Publication'][i])
            cursor.execute(sql_command)

    if sqTable == 'reviewExp':
        format_str = """INSERT INTO reviewExp (isbn, user_id, rate) VALUES ("{isbn}", "{user}", "{rate}");"""

        for i in range(len(csvTable)):
            sql_command = format_str.format(isbn=csvTable['ISBN'][i], user=csvTable['User-ID'][i],
            rate=csvTable['Book-Rating'][i])
            cursor.execute(sql_command)

    if sqTable == 'reviewImp':
        format_str = """INSERT INTO reviewImp (isbn, user_id, rate) VALUES ("{isbn}", "{user}", "{rate}");"""

        for i in range(len(csvTable)):
            sql_command = format_str.format(isbn=csvTable['ISBN'][i], user=csvTable['User-ID'][i],
            rate=csvTable['Book-Rating'][i])
            cursor.execute(sql_command)





if __name__ == "__main__":
    #open book files, drop unnecessary columns
    books = opencsv('BX-CSV-Dump/BX-Books.csv')
    books.drop(['Image-URL-S', 'Image-URL-M', 'Image-URL-L', 'Publisher'], axis=1, inplace=True)

    users = opencsv('BX-CSV-DUMP/BX-Users.csv')
    users.drop(['Location'], axis = 1, inplace=True)

    ratings = opencsv('BX-CSV-DUMP/BX-Book-Ratings.csv')

    rate_imp, rate_exp = cleanRatings(ratings, books)

    conn = sqlite3.connect("bookreviews.db")
    cursor = conn.cursor()
    makeTables(cursor)

    addToTables(cursor, users, 'users')
    addToTables(cursor, books, 'books')
    addToTables(cursor, rate_imp, 'reviewImp')
    addToTables(cursor, rate_exp, 'reviewExp')

    conn.commit()
    conn.close()
