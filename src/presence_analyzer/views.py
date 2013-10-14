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
from flask import render_template


import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('presence_weekday.html')


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
        return [["Weekday", "Presence (s)"],
                ["Mon", 0], ["Tue", 0],
                ["Wed", 0], ["Thu", 0],
                ["Fri", 0], ["Sat", 0],
                ["Sun", 0]]

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
        return [["Mon", 0, 0],
                ["Tue", 0, 0],
                ["Wed", 0, 0],
                ["Thu", 0, 0],
                ["Fri", 0, 0],
                ["Sat", 0, 0],
                ["Sun", 0, 0]]

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

    url = data.find('.//protocol').text + "://" + data.find('.//host').text

    return [{'user_id': i.get('id'), 'name': i.find('.//name').text,
             'avatar': url + i.find('.//avatar').text}
            for i in data.findall('.//user')]


@app.route("/presence_start_end.html")
def presence_start_end():
    """
    Renders template file for present start/end page
    """
    return render_template('presence_start_end.html')


@app.route("/presence_weekday.html")
def presence_weekday():
    """
    Renders template file for weekday presence page
    """
    return render_template('presence_weekday.html')


@app.route("/mean_time_weekday.html")
def mean_time_weekday():
    """
    Renders template file for mean weekday time page
    """
    return render_template('mean_time_weekday.html')
