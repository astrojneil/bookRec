#functions for actual recommender!
import sqlite3
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import correlation, cosine
from scipy import optimize
import random
import numpy as np


#function to retrieve reviews from sql table
def getReviewTable(rateType, user, conn):
    #conn = sqlite3.connect("bookreviews.db")

    if rateType == 'exp':
        execute_string2 = 'SELECT isbn, user_id, rate FROM reviewExp'
        execute_string = 'SELECT isbn, user_id, rate FROM reviewExp WHERE user_id IN (SELECT DISTINCT user_id FROM reviewExp WHERE ( '
        booklist = []
        for i, isbn in enumerate(user.rates):
            if i == 0:
                execute_string = execute_string+'isbn = ? '
            else:
                execute_string = execute_string+'OR isbn = ? '
            booklist.append(isbn)
        execute_string = execute_string+'))'

        #reviews = pd.read_sql(execute_string, conn, params=booklist)
        reviews = pd.read_sql(execute_string2, conn)
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


#function to retrieve reviews from sql table
def simpivot(rateType, user_ids, conn):
    #conn = sqlite3.connect("bookreviews.db")

    if rateType == 'exp':
        execute_string = 'SELECT isbn, user_id, rate FROM reviewExp WHERE ( '
        idlist = []
        for i, uid in enumerate(user_ids):
            if i == 0:
                execute_string = execute_string+'user_id = ? '
            else:
                execute_string = execute_string+'OR user_id = ? '
            idlist.append(uid)
        execute_string = execute_string+')'

        reviews = pd.read_sql(execute_string, conn, params=idlist)
        #reviews = pd.read_sql('SELECT isbn, user_id, rate FROM reviewExp', conn)
    else:
        execute_string = 'SELECT isbn, user_id, rate FROM reviewImp WHERE ( '
        idlist = []
        for i, uid in enumerate(user_ids):
            if i == 0:
                execute_string = execute_string+'user_id = ? '
            else:
                execute_string = execute_string+'OR user_id = ? '
            idlist.append(uid)
        execute_string = execute_string+')'

        reviews = pd.read_sql(execute_string, conn, params=idist)
        #reviews = pd.read_sql('SELECT isbn, user_id, rate FROM reviewImp', conn)
    return makeMatrix(reviews)


#create pivot table
def makeMatrix(rates):
    rates = rates.pivot(index='user_id', columns='isbn', values='rate')
    rates = rates.where(pd.notnull(rates), 0)
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
    top100 = books[:len(user_inds)*15]
    bookIds = []
    bookValues = []
    for i, ind in enumerate(top100.index):
        bookIds.append(ratings_matrix.columns[ind])
        bookValues.append(top100.values[i])
    return bookIds, bookValues


def cofiCostFunc(params, Y, R, num_books, num_users,
                      num_features, lambda_=0.0):

    # Unfold the U and W matrices from params
    X = params[:num_users*num_features].reshape(num_users, num_features)
    Theta = params[num_users*num_features:].reshape(num_books, num_features)

    J = 0
    X_grad = np.zeros(X.shape)
    Theta_grad = np.zeros(Theta.shape)

    J = 0.5*np.sum(np.multiply(R, (np.dot(X, np.transpose(Theta)) - Y)**2)) + (lambda_/2)*np.sum(Theta**2) + (lambda_/2)*np.sum(X**2)

    for i in range(Y.shape[0]):
        for j in range(Y.shape[1]):

            #all j's where R = 1 on ith row
            idx = np.where(R[i, :] == 1)[0]
            #select theta at these j
            Theta_temp = Theta[idx, :]
            #select Y at these j for ith row
            Y_temp = Y[i, idx]
            #x_grad
            X_grad[i, :] = np.dot(np.dot(X[i, :], Theta_temp.T) - Y_temp, Theta_temp) + lambda_*X[i,:]

            #all i's where R =1 on jth col
            idx = np.where(R[:, j] == 1)[0]
            #select theta at these i
            X_temp = X[idx, :]
            #select Y at these j for ith row
            Y_temp = Y[idx, j]
            #x_grad
            Theta_grad[j, :] = np.dot(np.dot(X_temp, Theta[j, :].T) - Y_temp, X_temp) +lambda_*Theta[j, :]

    grad = np.concatenate([X_grad.ravel(), Theta_grad.ravel()])
    return J, grad


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
    dist, indices = knn_model.kneighbors(user_vec, n_neighbors= 8)

    #ignore the first item, it is the original user
    sims = 1-dist.flatten() #most similar is closest to 1
    sim_user_ind = indices.flatten()

    #list books similar users have read
    simUserBooks, bookValues = findBooks(sim_user_ind, ratings_matrix)
    ids = ratings_matrix.index[sim_user_ind].values

    #new recommender"
    #array of ratings, books bv users
    sim_matrix =simpivot(rateType, ratings_matrix.index[sim_user_ind], conn)

    Y = sim_matrix.values.T
    R = np.ones(Y.shape)*Y.astype(bool).astype(int)
    #  Normalize Ratings
    m, n = Y.shape
    Ymean = np.zeros(m)
    Ynorm = np.zeros(Y.shape)

    for i in range(m):
        idx = R[i, :] == 1
        Ymean[i] = np.mean(Y[i, idx])
        Ynorm[i, idx] = Y[i, idx] - Ymean[i]

    #  Useful Values
    num_books, num_users= Y.shape
    num_features = 10

    # Set Initial Parameters (Theta, X)
    X = np.random.randn(num_books, num_features)
    Theta = np.random.randn(num_users, num_features)

    initial_parameters = np.concatenate([X.ravel(), Theta.ravel()])

    # Set options for scipy.optimize.minimize
    options = {'maxiter': 100}

    # Set Regularization
    lambda_ = 10
    res = optimize.minimize(lambda x: cofiCostFunc(x, Ynorm, R, num_users,
                                               num_books, num_features, lambda_),
                        initial_parameters,
                        method='TNC',
                        jac=True,
                        options=options)
    theta = res.x

    # Unfold the returned theta back into U and W
    X = theta[:num_books*num_features].reshape(num_books, num_features)
    Theta = theta[num_books*num_features:].reshape(num_users, num_features)

    #print('Recommender system learning completed.')
    p = np.dot(X, Theta.T)
    R_inv = np.where((R==0), 1, 0)

    my_predictions = p[:, 0] + Ymean
    #find books that have not been read
    recs = np.multiply(my_predictions, R_inv[:, 0])

    predictions = []
    for i, rate in enumerate(recs):
        isbn = sim_matrix.columns[i]
        predictions.append((rate, isbn))

    predictions = pd.Series(predictions)
    predictions = predictions.sort_values(ascending=False)
    recommend = predictions[:10]

    return recommend
