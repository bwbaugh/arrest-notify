# -*- coding: utf-8 -*-
"""Logic for interacting with notification rules stored in the DB."""
import collections
import datetime


class Rule(
    collections.namedtuple(
        'Rule',
        'given_name, surname, earliest_birthdate, latest_birthdate',
    ),
):
    """Rule with criteria for determining whether an arrest is a match.

    Attributes:
        given_name: String of a person's legal first name.
        surname: String of a person's legal last name.
        earliest_birthdate: String in the format `yyyy-mm-dd`. For
            `datetime.date` instances, this can be obtained by calling
            the `isoformat()` method.
    """
    @classmethod
    def make(cls, given_name, surname, earliest_birthdate, latest_birthdate):
        """Simple validator that returns an instance if validation passes.

        See the class docstring for argument information.

        Raises:
            ValueError if validation fails.
        """
        if not all(
            [given_name, surname, earliest_birthdate, latest_birthdate]
        ):
            # Very simple validation to ensure there is *some* value.
            raise ValueError('At least one empty value for rule.')
        earliest_birthdate = _validate_date_string(earliest_birthdate)
        latest_birthdate = _validate_date_string(latest_birthdate)
        return cls(given_name, surname, earliest_birthdate, latest_birthdate)


def save_rule_for_user(user_id, rule):
    """Store a rule in the DB to be used when matching

    Args:
        user_id: String of the user-ID to associate the rule with in
            the DB. For instances of the User class from Stormpath,
            this is usually obtained by calling `user.get_id()`.
        rule: Rule instance to be stored in the DB.
    """
    raise NotImplementedError


def _validate_date_string(date_string):
    """Validates a string is in `yyyy-mm-dd` format by parsing it.

    Raises:
        ValueError if the date_string is not in a valid format.

    Returns:
        String of the parsed date in ISO format.
    """
    date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
    return date.isoformat()
