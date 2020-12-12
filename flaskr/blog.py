#this is the blog Blueprint

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from users import User
from books import Book
from recommender import *


#without a url_prefix, each of these functions will have their own url
bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    print(g.user['tableid'])
    #find books for this user
    posts = db.execute(
        " SELECT title, author, rate FROM book b JOIN reviewExp r ON b.isbn = r.isbn WHERE r.user_id = ?", (g.user['tableid'], )).fetchall()
    print(posts[0]['title'])

    u = User()
    u.getUser(g.user['tableid'], db)
    rec = recommendbook(u, db)

    bookList = []
    for i, (rate, isbn) in enumerate(rec):
        book = Book()
        book.isbn_to_book(isbn, db)
        bookinfo = {}
        bookinfo['title'] = book.title
        bookinfo['author'] = book.author
        bookinfo['rate'] = "{:0.2f}".format(rate)
        bookList.append(bookinfo)

        #print("{} {} (expected rating {:0.2f})".format(i+1, book.title, rate))

    #books = db.execute(
    #    " SELECT title, author, rate FROM book b JOIN reviewExp r ON b.isbn = r.isbn WHERE r.user_id = 11676").fetchall()
    return render_template('blog/index.html', posts=posts, books=bookList)

@bp.route('/addbook', methods = ('GET', 'POST'))
@login_required
def addbooks():
    if request.method == 'POST':
        title = request.form['title']
        rate = request.form['rate']
        error = None

        if not title:
            title = 'No Title, can\'t save book'

        if not rate:
            error = "No rate, can\'t save book"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            b = Book()
            b.title_to_book(title, db)
            #handle book not found?

            u = User()
            u.getUser(g.user['tableid'], db)
            u.addRates({b.isbn: rate}, db)

            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            title = 'Untitled'

        if not body:
            error = "No text in body, can\'t save post"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
