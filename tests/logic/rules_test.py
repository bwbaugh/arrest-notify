# -*- coding: utf-8 -*-
import uuid

import boto
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
                str(mock.sentinel.given_name),
                str(mock.sentinel.surname),
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

    def test_given_name_lower(self):
        rule = rules.Rule.make(
            'Given_Name',
            str(mock.sentinel.surname),
            '2014-06-15',
            '2014-06-15',
        )
        assert rule.given_name == 'given_name'

    def test_surname_lower(self):
        rule = rules.Rule.make(
            str(mock.sentinel.given_name),
            'Surname',
            '2014-06-15',
            '2014-06-15',
        )
        assert rule.surname == 'surname'


class TestSaveRuleForUser(object):

    MOCK_RULE = rules.Rule.make(
        'Given_Name',
        'Surname',
        '2014-06-15',
        '2014-06-16',
    )

    @pytest.fixture
    def mock_sdb(self, monkeypatch):
        mock_sdb = mock.create_autospec(boto.connect_sdb)
        monkeypatch.setattr(boto, 'connect_sdb', mock_sdb)
        # By default, find a unique item name.
        mock_domain = mock_sdb.return_value.get_domain.return_value
        mock_domain.get_item.return_value = None
        return mock_sdb

    @pytest.fixture(autouse=True)
    def mock_generate_item_name(self, monkeypatch):
        mock_generate = mock.create_autospec(rules._generate_item_name)
        monkeypatch.setattr(rules, '_generate_item_name', mock_generate)
        return mock_generate

    def test_get_domain(self, mock_sdb):
        rules.save_rule_for_user(mock.sentinel.user_id, self.MOCK_RULE)
        mock_sdb().get_domain.assert_called_once_with(
            'arrestnotify_rule',
            validate=False,
        )

    def test_get_item(self, mock_sdb, mock_generate_item_name):
        rules.save_rule_for_user(mock.sentinel.user_id, self.MOCK_RULE)
        mock_sdb().get_domain().get_item.assert_called_once_with(
            mock_generate_item_name.return_value,
        )

    def test_item_user_id(self, mock_sdb):
        rules.save_rule_for_user(mock.sentinel.user_id, self.MOCK_RULE)
        mock_item = mock_sdb().get_domain().new_item()
        mock_item.__setitem__.assert_called_once_with(
            'user_id',
            mock.sentinel.user_id,
        )

    def test_item_update_with_rule(self, mock_sdb):
        rules.save_rule_for_user(mock.sentinel.user_id, self.MOCK_RULE)
        mock_item = mock_sdb().get_domain().new_item()
        mock_item.update.assert_called_once_with(self.MOCK_RULE._asdict())

    def test_item_saved(self, mock_sdb):
        rules.save_rule_for_user(mock.sentinel.user_id, self.MOCK_RULE)
        mock_item = mock_sdb().get_domain().new_item()
        mock_item.save.assert_called_once_with()


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


class TestGenerateItemName(object):

    @pytest.fixture
    def mock_uuid(self, monkeypatch):
        mock_uuid = mock.create_autospec(uuid.uuid4)
        monkeypatch.setattr(uuid, 'uuid4', mock_uuid)
        return mock_uuid

    def test_return_value(self, mock_uuid):
        result = rules._generate_item_name()
        assert result == mock_uuid.return_value.hex[:]
