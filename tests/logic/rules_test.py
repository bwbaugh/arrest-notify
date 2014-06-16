# -*- coding: utf-8 -*-
import mock
import pytest

from arrest_notify.logic import rules


class TestRuleMake(object):

    @pytest.fixture
    def mock_date_validate(self):
        with mock.patch.object(
            rules, '_validate_date_string', autospec=True,
        ) as mock_date_validate:
            rules.Rule.make(
                mock.sentinel.given_name,
                mock.sentinel.surname,
                mock.sentinel.earliest_birthdate,
                mock.sentinel.latest_birthdate,
            )
        return mock_date_validate

    def test_validates_earliest_birthdate(self, mock_date_validate):
        mock_date_validate.assert_any_call(mock.sentinel.earliest_birthdate)

    def test_validates_latest_birthdate(self, mock_date_validate):
        mock_date_validate.assert_any_call(mock.sentinel.latest_birthdate)

    def test_empty_given_name(self):
        with pytest.raises(ValueError) as excinfo:
            rules.Rule.make(
                '',
                mock.sentinel.surname,
                mock.sentinel.earliest_birthdate,
                mock.sentinel.latest_birthdate,
            )
        assert str(excinfo.value) == 'At least one empty value for rule.'


class TestSaveRuleForUser(object):

    def test_not_implemented(self):
        with pytest.raises(NotImplementedError):
            rules.save_rule_for_user(mock.sentinel.user_id, mock.sentinel.rule)


class TestValidateDateString(object):

    def test_valid_date(self):
        date_string = '2014-06-15'
        assert rules._validate_date_string(date_string) == date_string

    def test_invalid_date(self):
        date_string = '__invalid__'
        with pytest.raises(ValueError) as excinfo:
            rules._validate_date_string(date_string)
        expected = "time data '__invalid__' does not match format '%Y-%m-%d'"
        assert str(excinfo.value) == expected
