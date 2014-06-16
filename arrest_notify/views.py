# -*- coding: utf-8 -*-
"""Vieows for the webapp.

TThe views here provide a bare-bones website that allows users to:

-   Create a new user account.
-   Log into an existing user account.
-   View a simple dashboard page with notification settings.
-   Log out of the website.
"""
from flask.ext import stormpath
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from stormpath.error import Error as StormpathError

from arrest_notify import app
from arrest_notify.logic import rules


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
    except StormpathError as err:
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


@app.route('/logout')
@stormpath.login_required
def logout():
    """Log out a logged in userand redirect them back to the main page."""
    stormpath.logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@stormpath.login_required
def dashboard():
    """This view renders a simple dashboard page for logged in users.

    Users can see their personal information on this page, as well as
    store additional data to their account.
    """
    user_rules = rules.get_rules_for_user(stormpath.user.get_id())
    return render_template('dashboard.html', user_rules=user_rules)


@app.route('/rule/create', methods=['GET', 'POST'])
@stormpath.login_required
def create_rule():
    """This view renders a simple dashboard page for logged in users.

    Users can see their personal information on this page, as well as
    store additional data to their account.
    """
    template_name = 'create-rule.html'
    if request.method == 'GET':
        return render_template(template_name)
    try:
        rule_params = dict(
            (key, request.form[key])
            for key in rules.Rule._fields
        )
    except KeyError as error:
        return render_template(
            template_name,
            error=(
                'Missing form parameter {field_name}. It looks like '
                'the form might be broken!'
            ),
        )
    try:
        rule = rules.Rule.make(**rule_params)
    except ValueError as error:
        return render_template(template_name, error=error)
    try:
        rules.save_rule_for_user(stormpath.user.get_id(), rule)
    except rules.UniqueItemNameError as error:
        return render_template(template_name, error=error)
    return redirect(url_for('dashboard'))
