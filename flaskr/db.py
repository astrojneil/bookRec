import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

#connect database to the app
def get_db():
    if 'db' not in g:
        #connect to database
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        #return rows like dicts
        g.db.row_factory = sqlite3.Row

    return g.db

#close the database
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
#open and the database
def init_db():
    db = get_db()

#customm commands for the command line
@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database!')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
