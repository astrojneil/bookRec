#functions for actual recommender!
import sqlite3
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import correlation, cosine
import random
import numpy as np


#function to retrieve reviews from sql table
def getReviewTable(rateType, user, conn):
    #conn = sqlite3.connect("bookreviews.db")

    if rateType == 'exp':
        execute_string = 'SELECT isbn, user_id, rate FROM reviewExp WHERE user_id IN (SELECT DISTINCT user_id FROM reviewExp WHERE ( '
        booklist = []
        for i, isbn in enumerate(user.rates):
            if i == 0:
                execute_string = execute_string+'isbn = ? '
            else:
                execute_string = execute_string+'OR isbn = ? '
            booklist.append(isbn)
        execute_string = execute_string+'))'

        reviews = pd.read_sql(execute_string, conn, params=booklist)
        #reviews = pd.read_sql('SELECT isbn, user_id, rate FROM reviewExp', conn)
    else:
        execute_string = 'SELECT isbn, user_id, rate FROM reviewImp WHERE user_id IN (SELECT DISTINCT user_id FROM reviewImp WHERE ( '
        booklist = []
        for i, isbn in enumerate(user.books):
            if i == 0:
                execute_string = execute_string+'isbn = ? '
            else:
                execute_string = execute_string+'OR isbn = ? '
            booklist.append(isbn)
        execute_string = execute_string+'))'

        reviews = pd.read_sql(execute_string, conn, params=booklist)
        #reviews = pd.read_sql('SELECT isbn, user_id, rate FROM reviewImp', conn)
    return reviews


#create pivot table
def makeMatrix(rates):
    rates = rates.pivot(index='user_id', columns='isbn', values='rate')
    rates = rates.where(pd.notnull(rates), 0)
    print('Matrix shape {}'.format(rates.shape))
    return rates

#find the mean rating for a given user, only looking at book which they've rated
def calcMean(user_loc, ratings_matrix):
    user_ratings = ratings_matrix.iloc[user_loc, :]
    #select only where rating != 0
    user_ratings = user_ratings[user_ratings != 0]

    mean = np.sum(user_ratings)/len(user_ratings)
    return mean

#predict rating for a specific item/user
def predict_rating_explicit(user_loc, item_loc, sim_user_ind, sims, matrix):
    mean_rating_user = calcMean(user_loc, matrix)
    sim_sum = np.sum(sims)
    rate_sum = 0
    #loop through similar users
    for i, sim_user in enumerate(sim_user_ind):
        product = matrix.iloc[sim_user, item_loc]*sims[i]
        rate_sum=rate_sum+product

    prediction = (rate_sum/sim_sum)
    return prediction

#predict rating for a specific item/user
def predict_rating_implicit(user_loc, item_loc, sim_user_ind, sims, bookvalue, matrix):
    mean_rating_user = calcMean(user_loc, matrix)
    sim_sum = np.sum(sims)
    rate_sum = 0
    #loop through similar users
    for i, sim_user in enumerate(sim_user_ind):
        product= matrix.iloc[sim_user, item_loc]*sims[i]  #weight rating by similarity
        rate_sum=rate_sum+product

    prediction = (rate_sum/sim_sum)
    return prediction

def findBooks(user_inds, ratings_matrix):
    books = np.zeros(ratings_matrix.iloc[0, :].values.shape)
    for ids in user_inds:
        user_vec = ratings_matrix.iloc[ids, :].values
        books = books + user_vec

    books = pd.Series(books)
    books = books.sort_values(ascending=False)
    top100 = books[:100]
    bookIds = []
    bookValues = []
    for i, ind in enumerate(top100.index):
        bookIds.append(ratings_matrix.columns[ind])
        bookValues.append(top100.values[i])
    return bookIds, bookValues


#find the most likely to be read over all books
def recommendbook(user, conn):
    rateType = 'exp'
    if rateType != 'imp' and rateType != 'exp':
        print('Unknown rating type!')
        return

    #read in review table
    ratings_matrix = makeMatrix(getReviewTable(rateType, user, conn))

    user_loc = ratings_matrix.index.get_loc(user.id)
    user_books = user.rates #dictionary of books created; turn this into a vector by looking up isbns in matrix

    knn_model = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
    knn_model.fit(ratings_matrix)

    #change this to use user functions to get user id and list of ratings
    #so that this can work with a user that's not already in the table?
    user_vec = ratings_matrix.iloc[user_loc, :].values.reshape(1, -1)

    #find similar users
    dist, indices = knn_model.kneighbors(user_vec, n_neighbors= 10)

    #ignore the first item, it is the original user
    sims = 1-dist.flatten()[1:] #most similar is closest to 1
    sim_user_ind = indices.flatten()[1:]

    #list books similar users have read
    simUserBooks, bookValues = findBooks(sim_user_ind, ratings_matrix)

    predictions = []
    for i, book in enumerate(simUserBooks):
        item_loc = ratings_matrix.columns.get_loc(book)
        if (ratings_matrix.iloc[user_loc, item_loc] == 0):
            if rateType == 'imp':
                predictions.append((predict_rating_implicit(user_loc, item_loc, sim_user_ind, sims, bookValues[i], ratings_matrix), book))
            else:
                predictions.append((predict_rating_explicit(user_loc, item_loc, sim_user_ind, sims, ratings_matrix), book))
        else:
            predictions.append((-1, book)) #already read

    predictions = pd.Series(predictions)
    predictions = predictions.sort_values(ascending=False)
    recommend = predictions[:10]

    return recommend
