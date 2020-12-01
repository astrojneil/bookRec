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


if __name__ == '__main__':
    r = getReviewTable()
    #m = makeMatrix(r)
    print(r.shape)
