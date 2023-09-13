import sqlite3

import click
from flask import current_app, g

INIT_SCRIPT = """
CREATE TABLE user (
  id TEXT PRIMARY KEY UNIQUE NOT NULL,
  auth_type INTEGER NOT NULL DEFAULT 0,
  request_state INTEGER NOT NULL,
  request_time TEXT NOT NULL
);

CREATE TABLE notify (
  dest_id TEXT PRIMARY KEY NOT NULL,
  tempature INTEGER,
  notify_when_leave INTEGER
);

CREATE TABLE otp (
  auth_type INTEGER PRIMARY KEY,
  password TEXT,
  expired_time TEXT NOT NULL
);

CREATE TABLE photo (
  shooting_time TEXT PRIMARY KEY NOT NULL,
  deletehash TEXT,
  uri TEXT
);
"""

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def init_db():
    db = get_db()
    db.executescript(INIT_SCRIPT)
    
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()