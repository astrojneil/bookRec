#functions for actual recommender!
import sqlite3
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import correlation, cosine
import random

#function to retrieve reviews from sql table
def getReviewTable():
    conn = sqlite3.connect("bookreviews.db")
    reviews = pd.read_sql('SELECT isbn, user_id, rate FROM reviewExp', conn)
    conn.close()
    return reviews


#create pivot table
def makeMatrix(rates):
    rates = rates.pivot(index='user_id', columns='isbn', values='rate')
    rates = rates.where(pd.notnull(rates), 0)
    print('Matrix shape {}'.format(rates.shape))
    return ratess

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


#find the most likely to be read over all books
def recommendbook(user):
    #read in review table
    ratings_matrix = makeMatrix(getReviewTable())
    rateType = 'exp'

    if rateType != 'imp' and rateType != 'exp':
        print('Unknown rating type!')
        return

    knn_model = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
    knn_model.fit(ratings_matrix)

    #change this to use user functions to get user id and list of ratings
    #so that this can work with a user that's not already in the table?
    user_loc = ratings_matrix.index.get_loc(user_id)
    user_vec = ratings_matrix.iloc[user_loc, :].values.reshape(1, -1)

    #find similar users
    dist, indices = knn_model.kneighbors(user_vec, n_neighbors= 10)

    #ignore the first item, it is the original user
    sims = 1-dist.flatten()[1:] #most similar is closest to 1
    sim_user_ind = indices.flatten()[1:]
    print(sims)

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

    for i, (rate, book) in enumerate(recommend):
        bookTitle = findTitle(book)
        print("{} {} (expected rating {:0.2f})".format(i+1, bookTitle, rate))

    return recommend


if __name__ == '__main__':
    r = getReviewTable()
    m = makeMatrix(r)
    print(m.head(10))
