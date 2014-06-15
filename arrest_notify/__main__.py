# -*- coding: utf-8 -*-
"""Run the flask app."""
from os import environ

from arrest_notify import app


app.run(
    host='0.0.0.0',
    port=int(environ.get('PORT', 5000)),
)
