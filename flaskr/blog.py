from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import requests

bp = Blueprint('blog', __name__)

# change this to all movies
# also allow this to change if a search is done on the title or genre
# some how display the results in pages?
@bp.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)

    db = get_db()

    if page is None:
        page = 1

    if g.user:
        movies = db.execute(
            # get all of the movies they haven't rated
            'SELECT id, title, genres '
            'FROM movie '
            'EXCEPT '
            'SELECT m.id, m.title, m.genres '
            'FROM movie m '
            'INNER JOIN '
            'review r '
            'ON r.userID = ? '
            'and m.id = r.movieID '
            ' LIMIT ? OFFSET ?',
            (g.user['id'], '8', str((page - 1) * 8), )).fetchall()
    else:
        movies = db.execute(
            # 'SELECT p.id, title, body, created, author_id, username'
            # ' FROM post p JOIN user u ON p.author_id = u.id'
            # ' ORDER BY created DESC'
            # gets all of the movies
            'SELECT id, title, genres '
            'FROM movie LIMIT ? OFFSET ?', ('8', str((page - 1) * 8), )).fetchall()

    images = []
    #r = requests.get("https://api.themoviedb.org/3/search/movie?api_key=8d5d54aa72351ac3e821515d968260c5&language=en-US&query=Toy%20story&page=1&include_adult=true&year=1995")

    for movie in movies:
        title = movie['title']
        title = title.split('(')
        actual_title = title[0].rstrip()
        data = title[1][:-1]
        r = requests.get("https://api.themoviedb.org/3/search/movie?api_key=8d5d54aa72351ac3e821515d968260c5&language=en-US&query=" + actual_title + "&page=1&include_adult=true&year=" + data)

        poster_path = r.json()['results'][0]['poster_path']
        poster_path = 'https://image.tmdb.org/t/p/w500' + poster_path
        images.append(poster_path)

    listas = zip(movies, images)

    return render_template('blog/index.html', movies=movies, page = page, listas=listas)


# lists all of the films that the current user has already rated
@bp.route('/rated')
@login_required
def rated():
    page = request.args.get('page', 1, type=int)

    if page is None:
        page = 1

    db = get_db()
    ratings = db.execute(
        'SELECT m.id, m.title, m.genres, r.rating '
        'FROM movie m '
        'INNER JOIN '
        'review r '
        'ON r.userID = ? '
        'and m.id = r.movieID'
        ' LIMIT ? OFFSET ?',
        (g.user['id'], '8', str((page - 1) * 8), )).fetchall()

    images = []

    for movie in ratings:
        title = movie['title']
        title = title.split('(')
        actual_title = title[0].rstrip()
        data = title[1][:-1]
        r = requests.get("https://api.themoviedb.org/3/search/movie?api_key=8d5d54aa72351ac3e821515d968260c5&language=en-US&query=" + actual_title + "&page=1&include_adult=true&year=" + data)

        poster_path = r.json()['results'][0]['poster_path']
        poster_path = 'https://image.tmdb.org/t/p/w500' + poster_path

        images.append(poster_path)

    listas = zip(ratings, images)
    return render_template('blog/ratings.html', ratings=ratings, page=page, listas=listas)


# updates the rating of a film you have watched
@bp.route('/<int:id>/update', methods=('POST', ))
@login_required
def update(id):
    # value to change the rating to
    db = get_db()
    db.execute(
        'UPDATE review '
        'SET rating = ?'
        'WHERE userID = ? '
        'AND movieID = ? ', (request.form['value'], g.user['id'], id))
    db.commit()
    return redirect(url_for('blog.rated'))


# removes a post from seen and rated to not rated anymore
@bp.route('/<int:id>/remove', methods=('POST', ))
@login_required
def remove(id):
    db = get_db()
    db.execute('DELETE FROM review '
               'WHERE userID = ? '
               'AND movieID = ?', (g.user['id'], id))
    db.commit()
    return redirect(url_for('blog.rated'))


# adding a rating to a film moves it to rated films with that rating
@bp.route('/<int:id>/add', methods=('POST', ))
@login_required
def add(id):
    print(request.form['value'])
    db = get_db()
    db.execute(
        'INSERT INTO review '
        '(userID, movieID, rating) '
        'VALUES (?, ?, ?)', (g.user['id'], id, request.form['value']))
    db.commit()
    print(url_for('index'))
    return redirect(url_for('index'))
