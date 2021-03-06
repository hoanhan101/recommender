"""
    collaborative_filtering.py - Collaborative Filtering Algorithm
    Author: Hoanh An (hoanhan@bennington.edu)
    Date: 03/09/18

    Reference: https://www.udemy.com/recommendation-systems/
"""

import itertools
import numpy as np
import pandas as pd

from random import randint
from scipy.spatial.distance import correlation

# Here are the paths to our data
ratings_path = 'ml-latest-small/ratings.csv'
movies_path = 'ml-latest-small/movies.csv'

# Read CSV files
ratings_data = pd.read_csv(ratings_path)
movies_data = pd.read_csv(movies_path, usecols=[0, 1])

# Rename columns
ratings_data.columns = ['userID', 'movieID', 'rating', 'timestamp']
movies_data.columns = ['movieID', 'title']

# Make sure the data types are correct
if ratings_data.userID.dtypes != 'int64':
    raise TypeError

if ratings_data.movieID.dtypes != 'int64' and movies_data.movieID.dtypes != 'int64':
    raise TypeError

if ratings_data.rating.dtypes != 'float64':
    raise TypeError

if ratings_data.timestamp.dtypes != 'int64':
    raise TypeError

# ----------------
# HELPER FUNCTIONS
# ----------------

def find_top_favorite_movies(active_user, n):
    """
    Find the top n movies for a given user.
    Params:
        active_user (int): User ID
        n (n): Number of top movies

    Return:
        List of movies' titles

    Steps:
        Get a list of user that matched the ID
        Sort the list by rating in ascending order
        Return only the titles of the movies
    """
    top_movies = pd.DataFrame.sort_values(
        ratings_data[ratings_data.userID==active_user],
        ['rating'],
        ascending=[0]
    )[:n]
    return list(top_movies.title)


# -----------------------
# FINDING RECOMMENDATIONS
# -----------------------

# K NEAREST NEIGHBOURS
# -----------------------

# Start by using a neighbour based collaborative filtering model.
# Need to find the k nearest neighbours of a user and use their ratings to
# predict ratings of the active user for movies they haven't rated yet.

# Need to present each user as a vector.
# Each element of the vector will be their rating for 1 movie.
# When user doesn't have any rating for a movie, the corresponding component
# will be NaN, aka Not a Number.

# pivot_table in pandas is similar to Pivot table in Excel or GroupBy in SQL.
# Let userID be index row and movieID be column, value is the result of
# aggregated function to calculate the mean rating rating for that movie.
user_item_rating_matrix = pd.pivot_table(ratings_data,
                                         values='rating',
                                         index=['userID'],
                                         columns=['movieID']
                                        )

# Join on movieID to get ratings with movies info
ratings_data = pd.merge(ratings_data, movies_data, left_on='movieID',
                                 right_on='movieID')

# There are a lot of NaN here because it is expected that movies would not have
# been rated by multiple users or many users would not have rated a lot of
# movies.
# print(user_item_rating_matrix.head())

# Now each user has been represented using their ratings.
# Need to find the similarity between 2 users.
# Use a correlation.
def find_similarity(user_1, user_2):
    """
    Compute the similarity between 2 users.

    Params:
        user_1 (array): User 1's vector
        user_2 (array): User 2's vector

    Return:
        The correlation of these 2 vectors.
    """
    # Normalize for any biases that users might have.
    # For example:
    #   - some users might be bias by high ratings, they are just generous.
    #   - some are more ciritical so they give lower rating in general
    # Make sure that any bias which is specific to that user
    # is removed.
    # np.nanmean() returns the mean of an array after ignoring 
    user_1 = np.array(user_1) - np.nanmean(user_1)
    user_2 = np.array(user_2) - np.nanmean(user_2)

    # Subset each user to be represented only by the ratings for the movies
    # that both of them have rated.
    # This gives us movies for which both users have non NaN ratings.
    common_movieIDs = [i for i in range(len(user_1)) if user_1[i] > 0 and
                       user_2[i] > 0]

    if common_movieIDs == 0:
        # There are no movies in common
        return 0
    else:
        # Subset each of the user to have only the ratings for common movies,
        # then find the correlation between these 2 vectors.
        user_1 = np.array([user_1[i] for i in common_movieIDs])
        user_2 = np.array([user_2[i] for i in common_movieIDs])
        return correlation(user_1, user_2)

# We have a function to compute the similarity between 2 users, we can use this
# to computer the similarity between the active user and every other users and
# find the nearest neighbours of the active user.
def find_nearest_neighbour_ratings(active_user, k):
    """
    Find k nearest neighbour of the active user then use their ratings to
    predict the active users rating for other movies.

    Params:
        active_user (array): User's vector
        k (int): Number of nearest neighbour we have to find

    Return:
        DataFrame of predicted ratings.
    """
    # Create an empty matrix who row index is user ID and the value will be the
    # similarity of that user to the active user
    similarity_matrix = pd.DataFrame(index=user_item_rating_matrix.index,
                                    columns=['Similarity'])

    for i in user_item_rating_matrix.index:
        similarity_matrix.loc[i] = find_similarity(
                                        user_item_rating_matrix.loc[active_user],
                                        user_item_rating_matrix.loc[i])

    # Sort the similarity matrix in the descending other of similarity
    similarity_matrix = pd.DataFrame.sort_values(similarity_matrix,
                                                ['Similarity'],
                                                ascending=[0])

    # Get only the top k numbers of nearest neighbours
    nearest_neighbours = similarity_matrix[:k]

    # Use their ratings to predict active users' rating for every movie
    neightbour_items_ratings = user_item_rating_matrix.loc[nearest_neighbours.index]

    # This is a placeholder for the predicted items ratings.
    # Its row index is the list of movies IDs
    predicted_ratings = pd.DataFrame(index=user_item_rating_matrix.columns,
                                        columns=['Rating'])

    for i in user_item_rating_matrix.columns:
        # Start with the average rating of the user
        predicted_rating = np.nanmean(user_item_rating_matrix.loc[active_user])

        # For each neighbour in the nearest neighbours list
        for j in neightbour_items_ratings.index:
            # If the neighbour has rated that movie, 
            # add the rating of the neighbour for that movie, 
            # adjusted by the average rating of that neighbour,
            # weighted by the similarity of the neighbour to the active user
            if user_item_rating_matrix.loc[j, i] > 0:
                predicted_rating += (
                    user_item_rating_matrix.loc[j, i]
                    - np.nanmean(user_item_rating_matrix.loc[j])
                ) * nearest_neighbours.loc[j, 'Similarity']

        # Add the rating to the predicted rating matrix
        predicted_ratings.loc[i, 'Rating'] = predicted_rating

    return predicted_ratings

def find_top_n_recommendations(active_user, n):
    """
    Find n top recommendations for the active user.

    Params:
        active_user (int): User's ID
        n (int): Number of recommendations

    Return:
        List of recommendations titles (string)
    """
    # Use the 10 nearest neighbours to find the predicted ratings
    predicted_ratings = find_nearest_neighbour_ratings(active_user, 10)

    # Drop all the movies that user has already watched
    # First, subset the user item rating matrix,
    # through the active user's rating
    # From that row, check which movies have rating > 0,
    # put them into a list,  drop the corresponding row
    watched_movies = list(
        user_item_rating_matrix.loc[
            active_user
        ].loc[user_item_rating_matrix.loc[active_user]>0].index
    )

    predicted_ratings = predicted_ratings.drop(watched_movies)

    # This gives us the list of movies IDs which are top recommendations
    top_recommendations = pd.DataFrame.sort_values(predicted_ratings,
                                                   ['Rating'],
                                                   ascending=[0])[:n]

    top_recommendations_titles = (
        movies_data.loc[
            movies_data.movieID.isin(top_recommendations.index)
        ]
    )

    return list(top_recommendations_titles.title)


# MATRIX FACTORIZATION
# -----------------------
# Identify some hidden factors which influence user's ratings of a movie.
# We don't know these factors are. We are not using any movies' descriptions
# data. We only have the movies' titles, movies IDs, and ratings from
# different users.
# The way to do it is to decompose a user's item raing matrix into 2 user
# matrices. One is the user-factor matrix and one is user-item matrix.
# Each row in the user-factor matrix maps the user onto the hidden factor.
# Each row in the user-item matrix maps the item onto the hidden factor.
# These factor may or may not have any meaning in real life. They might have some
# abstract meaning. We have no ideas until we have the right factorization.
# This operation will be pretty expensive because it will effectively give us
# the factor vectors needed to find the rating of any item by any user.
# It will only perform once and then we will have all the ratings for all the
# users. We then can update the matrix along the way.
# In the previous case, we only compute for only 1 user.
def perform_matrix_factorization(R, K, steps=10, gamma=0.001, lamda=0.02):
    """
    Perform matrix factorization algorithm.

    Details:
        In user item rating matrix R, each row represent an user, each column 
        represent a user's rating for an item.
        We use Stochastic gradient descent (SGD) to find the factor vectors.
        Steps, gamma, lamda are parameters that SGD will use.

    Params:
        R (array): User-item rating matrix 
        K (int): Number of factors we will find
        steps (int): Number of steps
        gamma (float): Size of the step
        lamda (float): Value of regularization

    Return:
        P and Q matrix
    """
    # N is the number of users, M is the number of items.
    N = len(R.index)
    M = len(R.columns)

    # We decompose R into P and Q matrix, where P is the user-facotr matrix, Q
    # is the user-item matrix.

    # P has N rows for users and K columns for items.
    # We initialize this matrix with some random numbers, then we iteratively
    # adjust the value of P so it moves to a place where the dot product of P
    # and Q will be very close the the user-item matrix.
    P = pd.DataFrame(np.random.rand(N, K), index=R.index)

    # Q has M rows for items.
    Q = pd.DataFrame(np.random.rand(M, K), index=R.columns)

    # SGD loops through the ratings in the user-item rating matrix.
    # It will do this as many times as we specify or until the error we are
    # minimizing reaches a certain threshold.
    for step in range(steps):
        for i in R.index:
            for j in R.columns:
                # For each rating that exists in the training set
                if R.loc[i,j] > 0:
                    # This is the error for one rating.
                    # It is the difference between the actual value of the
                    # rating and the predicted value (dot product of the
                    # corresponding user-factor vector and item-factor vector)
                    eij = R.loc[i, j] - np.dot(P.loc[i], Q.loc[j])

                    # We have an error function to minimize.
                    # The Ps and Qs should be moved in the downward direction
                    # of the slope of the vector at the current point.
                    # The value in the brackets is the partial derivative of
                    # the error function, i.e the slope.
                    # Lamda is the value of the regularization parameter which
                    # penalizes the model for the number of factors we are
                    # finding.
                    P.loc[i] = P.loc[i] + gamma*(eij*Q.loc[j] - lamda*P.loc[i])
                    Q.loc[j] = Q.loc[j] + gamma*(eij*P.loc[i] - lamda*Q.loc[j])

        # We have looped through all the rating once.
        # Check the value of the error function to see if we have
        # reached the threshold at which we want to stop, else we will
        # repeat the process.
        e = 0
        for i in R.index:
            for j in R.columns:
                if R.loc[i, j] > 0:
                    e = e + pow(
                        R.loc[i,j] - np.dot(P.loc[i], Q.loc[j]), 2
                        ) + lamda*(
                            pow(
                                np.linalg.norm(P.loc[i]), 2
                            ) + pow(
                                np.linalg.norm(Q.loc[j]), 2
                            )
                        )

        if e < 0.001:
            break

        print('.', end='', flush=True)

    return P, Q

# ASSOCIATION RULE
# -----------------------
# Association rule normally make sense with purchases/transactions dataset.
# The rule won't have much meaning in here, except to say a person who watched
# movie A will also be likely to have watched B.
# We will implement the Apriori algorithm.

# How many transactions are there in R which contains the item in the set
# that we are looking at. In order word, how many items are contained in the
# item set? Of all users, how many have watched movies from the movie set?
def support(items):
    """
    Support is the propotions of all users who have watched this set of movies.
    
    Note:
        This is a bit confusing because we kind of mix the term array/list and
        set together.
        TODO: Clarify this.

    Params:
        items (array): Set of items

    Return:
        A float value
    """
    users = user_item_rating_matrix.index
    number_of_users = len(users)
    rating_matrix = user_item_rating_matrix

    for item in items:
        # Subset the rating matrix to the set of users who have rated this item
        rating_matrix = rating_matrix.loc[rating_matrix.loc[:, item]:0]
        users = rating_matrix.index

    # We are now left with the users who have rated all the items in the set
    return float(len(users)) / float(number_of_users)


if __name__ == "__main__":
    # Nearest neighbours technique
    active_user = 10
    limit = 10
    collision = []
    nearest_neighbours_store = {}

    movies = find_top_favorite_movies(active_user, limit)
    recommendations = find_top_n_recommendations(active_user, limit)

    print('Here are user #\'s {} top {} movies:'.format(active_user, limit))
    for movie in movies:
        print('- {}'.format(movie))

    print('')
    print('Using nearest neighbours technique, we found:')
    for item in recommendations:
        nearest_neighbours_store[item] = 1
        print('- {}'.format(item))


    # Latent factor technique
    # Ideally we should run this over the entire matrix for a few 1000 steps.
    # This will be pretty expensive. For now, we just run it over a part of the
    # matrix to see how it works.
    (P, Q) = perform_matrix_factorization(
        user_item_rating_matrix.iloc[:100, :100], 2, 20
    )

    predicted_ratings = pd.DataFrame(
        np.dot(P.loc[active_user], Q.T), index=Q.index, columns=['Rating']
    )

    # We found the ratings of all movies by the active user and 
    # then sorted them to find the top n movies 
    top_recommendations = pd.DataFrame.sort_values(
        predicted_ratings, ['Rating'], ascending=[0]
    )[:limit]
    top_recommendations_titles = movies_data.loc[
        movies_data.movieID.isin(top_recommendations.index)
    ]

    print('')
    print('Using latent factor technique, we found:')
    for item in list(top_recommendations_titles.title):
        if item in nearest_neighbours_store:
            collision.append(item)

        print('- {}'.format(item))

    print('')
    if len(collision) == 0:
        print('There is no collision')
    else:
        print('Here are the same items that occured in both techniques:')
        for item in collision:
            print('- {}'.format(item))

    """
    # Association rule
    # Number of movies is watched by at least x% of the users.
    all_items = []

    # Minimum threshold
    min_support = 0.3

    for item in list(user_item_rating_matrix.columns):
        items = [item]
        if support(items) > min_support:
            all_items.append(item)

    # We are left with the items which have been rated at least by 30% of the
    # users
    # print(len(all_items))

    # Generate rules, test again for support and confidence

    # How strong the confidence between 2 items is
    min_confidence = 0.1
    assoc_rules = []
    i = 2

    # Generate all possible permutations of 2 items from the remaining list of
    # movies
    for rule in itertools.permutations(all_items, 2):
        # Each rule is a tuple of 2 items
        from_item = [rule[0]]
        to_item = rule

        confidence = support(to_item) / support(from_item)

        if confidence > min_confidence and support(to_item) > min_support:
            assoc_rules.append(rule)

    # This will generate all possible 2-item rules which satisfy the support
    # and confidence constraints.
    # We can continute to write a similar bit of code for finding 3-item rules
    # or n-item rules. At each step, make sure that every step satisfies the
    # min confidence and min support.

    print(assoc_rules)
    """
