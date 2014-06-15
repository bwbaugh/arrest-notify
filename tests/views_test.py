# -*- coding: utf-8 -*-
class TestIndex(object):

    def test_getting_started(self, app):
        response = app.get('/')
        assert 'Getting Started' in response.data


class TestRegister(object):

    def test_confirm_your_email_address(self, app):
        response = app.get('/register')
        assert 'confirm your email address' in response.data


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
