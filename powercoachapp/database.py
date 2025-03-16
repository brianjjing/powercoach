import sqlite3
from datetime import datetime

import click
from flask import current_app, g

#Returns a database connection, executes commands from the db file
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
        
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

#Defines a decorator/modifier for the init_db, which shows a success message after the database is initialized in init_db.
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

#Tells Python how to interpret timestamp vals in the database
sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

#Tells app when to use close_db and init_db_command, so that you don't have to manually run that every time
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)