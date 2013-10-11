# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
from json import dumps
from functools import wraps
from datetime import datetime

from flask import Response

from presence_analyzer.main import app

from werkzeug.contrib.cache import SimpleCache

import threading

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103

mycache = SimpleCache()  # pylint: disable-msg=C0103


def cache(timeout=6):
    """
    Caches user data.
    """
    def wrap(wrapped_func):
        """
        Outer wrapper of cache.
        """
        lock = threading.Lock()

        def wrapped(*args, **kwargs):
            """
            Inner wrapper of cache.
            """
            with lock:
                response = mycache.get(1)
                if response is None:
                    response = wrapped_func()
                    mycache.set(1, wrapped_func(), timeout)
            return response
        return wrapped
    return wrap


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        Returns response result
        """
        return Response(dumps(function(*args, **kwargs)),
                        mimetype='application/json')
    return inner


@cache(20)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = {i: [] for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0


def group_by_weekday_presence(items):
    """
    Groups mean presence entries by weekday.
    """
    start_list = {i: [] for i in range(7)}
    end_list = {i: [] for i in range(7)}
    for date in items:
        start = seconds_since_midnight(items[date]['start'])
        end = seconds_since_midnight(items[date]['end'])
        start_list[date.weekday()].append(start)
        end_list[date.weekday()].append(end)

    mean_start_end = []
    for day in range(7):
        mean_start_end.append(
            [mean(start_list[day]), mean(end_list[day])]
        )

    return mean_start_end
