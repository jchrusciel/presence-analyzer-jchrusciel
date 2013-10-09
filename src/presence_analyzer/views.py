# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify, get_data, mean, group_by_weekday, group_by_weekday_presence,
    read_user_data
)

from lxml import etree

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/static/presence_weekday.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [{'user_id': i, 'name': 'User {0}'.format(str(i))}
            for i in data.keys()]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday_presence(data[user_id])

    result = []
    for day_number, day in enumerate(weekdays):
        if day:
            result.append([calendar.day_abbr[day_number], day[0], day[1]])
        else:
            result.append([calendar.day_abbr[day_number], 0, 0])

    return result

@app.route('/api/v1/users_data')
@jsonify
def view_users_data():
    """
    Users detailed data listing for dropdown.
    """
    data = read_user_data()

    #print len(data.findall('.//user'))

    #for users in data.findall('.//user'):
    #    print users.get('id')
    #    print users.find('.//avatar').text
    #    print users.find('.//name').text

    return [{'user_id': i.get('id'), 'name': i.find('.//name').text, 'avatar': i.find('.//avatar').text}
            for i in data.findall('.//user')]


