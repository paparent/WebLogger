# -*- coding: utf-8 -*-
"""
    weblogger
    ~~~~~~~~~

    :copyright: 2011 PA Parent
    :license: MIT, see LICENSE for more information
"""

from __future__ import with_statement
from contextlib import closing
import sqlite3

from flask import Flask, g, render_template, request

# Config
DATABASE = 'logs.db'
DEBUG = True


app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.route("/")
def home():
    entries = query_db('SELECT * FROM entries')
    return render_template('show_entries.html', entries=entries)


@app.route("/endpoint/", methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route("/endpoint/<path:other>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def endpoint(other=None):
    host = request.remote_addr
    user = request.remote_user or ''
    method = request.method
    url = request.url
    headers = str(request.headers)
    payload = str(request.data)

    g.db.execute("insert into entries " \
                 "(timestamp, host, user, method, url, headers, payload) " \
                 "VALUES(datetime('now'), ?, ?, ?, ?, ?, ?)",
                 [host, user, method, url, headers, payload])

    g.db.commit()

    return "1"


if __name__ == '__main__':
    app.run()
