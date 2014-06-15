# -*- coding: utf-8 -*-
"""Vieows for the webapp.

TThe views here provide a bare-bones website that allows users to:

-   Create a new user account.
-   Log into an existing user account.
-   View a simple dashboard page with notification settings.
-   Log out of the website.
"""
from flask.ext import stormpath
from flask import (
    redirect,
    render_template,
    request,
    url_for,
)
from stormpath.error import Error as StormpathError

from arrest_notify import app


stormpath_manager = stormpath.StormpathManager(app)
stormpath_manager.login_view = '.login'


@app.route('/')
def index():
    """Basic home page."""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Allows a user to register for the site.

    This will create a new User, and then log the user into their new
    account immediately (no email verification required).
    """
    if request.method == 'GET':
        return render_template('register.html')
    try:
        # Create a new Stormpath User.
        user = stormpath_manager.application.accounts.create({
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'given_name': request.form.get('given_name'),
            'surname': request.form.get('surname'),
        })
        user.__class__ = stormpath.User
    except StormpathError, err:
        # If something fails, we'll display a user-friendly error message.
        return render_template('register.html', error=err.message)
    stormpath.login_user(user, remember=True)
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs in a user given an email address and password.

    This works by querying Stormpath with the user's credentials, and
    either getting back the User object itself, or an exception (in
    which case well tell the user their credentials are invalid).

    If the user is valid, we'll log them in and store their session.
    """
    if request.method == 'GET':
        return render_template('login.html')
    try:
        user = stormpath.User.from_login(
            request.form.get('email'),
            request.form.get('password'),
        )
    except StormpathError as err:
        return render_template('login.html', error=err.message)
    stormpath.login_user(user, remember=True)
    return redirect(request.args.get('next') or url_for('dashboard'))


@app.route('/dashboard', methods=['GET', 'POST'])
@stormpath.login_required
def dashboard():
    """This view renders a simple dashboard page for logged in users.

    Users can see their personal information on this page, as well as
    store additional data to their account.
    """
    if request.method == 'POST':
        for key in ['notification_settings']:
            value = request.form.get(key)
            if value is not None:
                stormpath.user.custom_data[key] = value
        stormpath.user.save()
    return render_template('dashboard.html')


@app.route('/logout')
@stormpath.login_required
def logout():
    """Log out a logged in userand redirect them back to the main page."""
    stormpath.logout_user()
    return redirect(url_for('index'))
