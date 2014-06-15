# -*- coding: utf-8 -*-
import pytest

from arrest_notify import views


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Prevent outbound requests during tests, mainly the user auth."""
    monkeypatch.delattr('requests.Session.request')


@pytest.fixture
def app():
    views.app.testing = True
    return views.app.test_client()
