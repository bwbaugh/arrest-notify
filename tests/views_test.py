# -*- coding: utf-8 -*-
class TestIndex(object):

    def test_getting_started(self, app):
        response = app.get('/')
        assert 'Getting Started' in str(response.data)


class TestRegister(object):

    def test_confirm_your_email_address(self, app):
        response = app.get('/register')
        assert 'confirm your email address' in str(response.data)


class TestLogin(object):

    def test_status_code(self, app):
        response = app.get('/login')
        assert response.status == '200 OK'


class TestLogout(object):

    def test_not_logged_in_status_code(self, app):
        response = app.get('/logout')
        assert response.status == '302 FOUND'


class TestDashboard(object):

    def test_not_logged_in_status_code(self, app):
        response = app.get('/dashboard')
        assert response.status == '302 FOUND'

    # TODO(bwbaugh|2014-06-15): Test match rules table.


class TestCreateRule(object):

    def test_not_logged_in_status_code(self, app):
        response = app.get('/rule/create')
        assert response.status == '302 FOUND'
