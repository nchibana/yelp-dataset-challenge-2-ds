"""
Database
    Initialize and create connection control flow for database.
    Datase parameters must be set in config.py or directly in app.py
"""


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import *

import click
from flask import current_app, g
from flask.cli import with_appcontext

import logging


def get_db():
    """
    Returns current database connection.  If connection not present,
    initiates connection to configured database.  Default is non-authenticated SQL.
    Modifty g.db = *connect to match intended database connection.
    """
    db_logger = logging.getLogger(__name__ + '.getdb')
    if 'db' not in g:
        db_logger.info('DB connection not found. Attempting connection.')
        try:
            engine = create_engine(current_app.config['DATABASE_URI'], echo=True)
            g.db_engine = engine.connect()
            g.db = scoped_session(sessionmaker(bind=g.db_engine))  # Create thread-local session
        except:
            db_logger.error('Could not establish connection.  Aborting.')
            raise ConnectionError

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.remove()


def init_db():
    db = get_db()
    Base.metadata.create_all(g.db_engine)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create tables from models.py"""
    init_db()
    click.echo('Initialized the database')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def update_review(data):
    """Update review table
    """
    pass


def query_database(query):
    """Query handler for sqlalchemy database.  Parse tablename and direct query.
    """
    query_logger = logging.getLogger(__name__ + '.query_database')
    query_logger.info("Query Received.  DataType: {}".format(type(query)))
    query_logger.info(query)
    return {'message': 'query received'}


def write_database(query):
    """General function for db INSERT, UPDATE
    """
    raise NotImplementedError


def delete_record(query):
    """General function for db DELETE, DROP?
    """
    raise NotImplementedError