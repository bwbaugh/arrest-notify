# -*- coding: utf-8 -*-
"""Logic for interacting with notification rules stored in the DB."""
import collections
import datetime
import uuid

import boto


class UniqueItemNameError(Exception):
    """Occurs when a unique item name could not be generated quickly.

    Usually the user should simply try again as this should be a very
    rare occurrence. This error could indicate a problem with either
    how the item names are generated or the number of items in the DB.
    """
    pass


class Rule(
    collections.namedtuple(
        'Rule',
        'given_name, surname, earliest_birthdate, latest_birthdate',
    ),
):
    """Rule with criteria for determining whether an arrest is a match.

    Attributes:
        given_name: String of a person's legal first name, lowercase.
        surname: String of a person's legal last name, lowercase.
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
        return cls(
            given_name.lower(),
            surname.lower(),
            earliest_birthdate,
            latest_birthdate,
        )


def get_rules_for_user(user_id):
    """Get all rules in the DB for a particular user.

    A random unique ID i.e., item name, will tried to be generated,
    however if there are too many items in the DB then this may fail.

    Args:
        user_id: String of the user-ID to associate the rule with in
            the DB. For instances of the User class from Stormpath,
            this is usually obtained by calling `user.get_id()`.

    Returns:
        Iterator of dictionary-like items from the DB.
    """
    sdb = boto.connect_sdb()
    # Save time by not sending a request that would ensure the domain exists.
    domain = sdb.get_domain('arrestnotify_rule', validate=False)
    items = domain.select(
        'select * from arrestnotify_rule where user_id = "{user_id}"'.format(
            user_id=user_id,
        )
    )
    return items


def save_rule_for_user(user_id, rule):
    """Store a rule in the DB to be used when matching

    A random unique ID i.e., item name, will tried to be generated,
    however if there are too many items in the DB then this may fail.

    Args:
        user_id: String of the user-ID to associate the rule with in
            the DB. For instances of the User class from Stormpath,
            this is usually obtained by calling `user.get_id()`.
        rule: Rule instance to be stored in the DB.

    Raises:
        UniqueItemNameError if a unique ID could not be generated.
    """
    sdb = boto.connect_sdb()
    # Save time by not sending a request that would ensure the domain exists.
    domain = sdb.get_domain('arrestnotify_rule', validate=False)
    for _ in xrange(3):
        # Try to generate a unique item name.
        item_name = _generate_item_name()
        if domain.get_item(item_name) is None:
            break
        # TODO(bwbaugh|2014-06-15): Log that a retry had to be made.
    else:
        # Couldn't generate a unique name.
        raise UniqueItemNameError('Could not generate a unique ID.')
    item = domain.new_item(item_name)
    item['user_id'] = user_id
    item.update(rule._asdict())
    item.save()


def _validate_date_string(date_string):
    """Validates a string is in `yyyy-mm-dd` format by parsing it.

    Raises:
        ValueError if the date_string is not in a valid format.

    Returns:
        String of the parsed date in ISO format.
    """
    date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
    return date.isoformat()


def _generate_item_name():
    """Generates an item name for use as the primary key in SimpleDB.

    Returns:
        String for the item name.
    """
    uid = uuid.uuid4()
    return uid.hex[-8:]
