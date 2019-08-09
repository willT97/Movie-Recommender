from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)

from flaskr.auth import login_required
from flaskr.db import get_db

from scipy.sparse.linalg import svds

import pandas as pd
import numpy as np
import requests

bp = Blueprint('recommender', __name__)

# recommends movies for any user
# returns the movies with the highest predicted rating that the
# specified user hasn't already rated
# though i didnt user any explicit movie content features


def recommend_movies(predictions_df,
                     userID,
                     movies_df,
                     original_ratings_df,
                     num_recommendations=5):

    # Get and sort the user's predictions
    user_row_number = userID - 1  # UserID starts at 1, not 0
    sorted_user_predictions = predictions_df.iloc[user_row_number].sort_values(
        ascending=False)

    # Get the user's data and merge in the movie information.
    user_data = original_ratings_df[original_ratings_df.USERID == (userID)]
    user_full = (user_data.merge(
        movies_df, how='left', left_on='MOVIEID',
        right_on='MOVIEID').sort_values(['RATING'], ascending=False))

    print 'User {0} has already rated {1} movies.'.format(
        userID, user_full.shape[0])
    print 'Recommending the highest {0} predicted ratings movies not already rated.'.format(
        num_recommendations)

    # Recommend the highest predicted rating movies that the user hasn't seen yet.
    recommendations = (
        movies_df[~movies_df['MOVIEID'].isin(user_full['MOVIEID'])].merge(
            pd.DataFrame(sorted_user_predictions).reset_index(),
            how='left',
            left_on='MOVIEID',
            right_on='MOVIEID').rename(columns={
                user_row_number: 'Predictions'
            }).sort_values('Predictions',
                           ascending=False).iloc[:num_recommendations, :-1])

    return user_full, recommendations


@bp.route('/recommended', methods=['GET', 'POST'])
@login_required
def recommended():
    page = request.args.get('page', 1, type=int)

    if page is None:
        page = 1

    db = get_db()

    movie_df = pd.read_sql_query('SELECT * FROM movie', db)
    rating_df = pd.read_sql_query('SELECT * FROM review', db)

    # rename so they have the same stuff
    #movie_df.rename({"id":"MOVIEID", "title": "TITLE", "genres": "GENRES"}, axis=1)
    #rating_df.rename({"userID": "USERID", "movieID": "MOVIEID", "rating":"RATING" }, axis = 1)

    movie_df.columns = ['MOVIEID', 'TITLE', 'GENRES']
    rating_df.columns = ['USERID', 'MOVIEID', 'RATING']

    movie_df['MOVIEID'] = movie_df['MOVIEID'].apply(pd.to_numeric)

    # format matrix to be one row per user and one column per movie

    R_df = rating_df.pivot(
        index='USERID', columns='MOVIEID', values='RATING').fillna(0)

    # de - mean the data and convert it from a dataframe
    # to a numpy array

    R = R_df.as_matrix()
    user_ratings_mean = np.mean(R, axis=1)
    R_demeaned = R - user_ratings_mean.reshape(-1, 1)

    # Perform singular value decomposition
    # use scipys function for svds
    U, sigma, Vt = svds(R_demeaned, k=50)

    sigma = np.diag(sigma)

    all_user_predicted_ratings = np.dot(np.dot(U, sigma),
                                        Vt) + user_ratings_mean.reshape(-1, 1)
    preds_df = pd.DataFrame(all_user_predicted_ratings, columns=R_df.columns)

    already_rated, predictions = recommend_movies(preds_df, g.user['id'], movie_df, rating_df, 50)

    movies = predictions[page * 8: page * 8 + 8]

    #print(predictions['GENRES'])
    images = []
    #r = requests.get("https://api.themoviedb.org/3/search/movie?api_key=8d5d54aa72351ac3e821515d968260c5&language=en-US&query=Toy%20story&page=1&include_adult=true&year=1995")

    for i in range(len(movies.index)):
        title = movies.iloc[i]['TITLE']
        title = title.split('(')
        actual_title = title[0].rstrip()
        data = title[1][:-1]
        r = requests.get("https://api.themoviedb.org/3/search/movie?api_key=8d5d54aa72351ac3e821515d968260c5&language=en-US&query=" + actual_title + "&page=1&include_adult=true&year=" + data)

        poster_path = r.json()['results'][0]['poster_path']
        poster_path = 'https://image.tmdb.org/t/p/w500' + poster_path
        images.append(poster_path)

    #movies = predictions
    #for i in range(len(movies.index)):
    #    print(i)
    #    print(movies.iloc[i]['TITLE'])



    return render_template(
        'recommender/recommender.html', movies=movies, page=page, images=images)
    # get the two movie sets from the data base
