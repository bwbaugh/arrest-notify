# -*- coding: utf-8 -*-
"""Flask based web application for managing notification settings."""
from os import environ

from flask import Flask


app = Flask(__name__)
app.debug = bool(int(environ.get('DEBUG', 0)))
app.config['SECRET_KEY'] = environ['SECRET_KEY']
app.config['STORMPATH_APPLICATION'] = environ['STORMPATH_APPLICATION']
app.config['STORMPATH_API_KEY_ID'] = environ['STORMPATH_API_KEY_ID']
app.config['STORMPATH_API_KEY_SECRET'] = environ['STORMPATH_API_KEY_SECRET']


import arrest_notify.views  # NOQA
