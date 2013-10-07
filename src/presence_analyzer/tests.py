# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday_view(self):
        """
        Test mean presence time of given user grouped by weekday.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertListEqual(data[0], [u'Mon', 0])
        self.assertListEqual(data[1], [u'Tue', 30047.0])
        self.assertListEqual(data[2], [u'Wed', 24465.0])
        self.assertListEqual(data[3], [u'Thu', 23705.0])
        self.assertListEqual(data[4], [u'Fri', 0])
        self.assertListEqual(data[5], [u'Sat', 0])
        self.assertListEqual(data[6], [u'Sun', 0])

    def test_presence_weekday_view(self):
        """
        Test total presence time of given user grouped by weekday.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertListEqual(data[0], [u'Weekday', u'Presence (s)'])
        self.assertListEqual(data[1], [u'Mon', 0])
        self.assertListEqual(data[2], [u'Tue', 30047])
        self.assertListEqual(data[3], [u'Wed', 24465])
        self.assertListEqual(data[4], [u'Thu', 23705])
        self.assertListEqual(data[5], [u'Fri', 0])
        self.assertListEqual(data[6], [u'Sat', 0])
        self.assertListEqual(data[7], [u'Sun', 0])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_group_by_weekday(self):
        """
        Test grouping items
        """

        data = {
            10: {
                datetime.date(2013, 9, 10): {
                    'start': datetime.time(9, 39, 5),
                    'end': datetime.time(17, 59, 52)},
                datetime.date(2013, 9, 12): {
                    'start': datetime.time(10, 48, 46),
                    'end': datetime.time(17, 23, 51)},
                datetime.date(2013, 9, 11): {
                    'start': datetime.time(9, 19, 52),
                    'end': datetime.time(16, 7, 37)},
                datetime.date(2013, 9, 17): {
                    'start': datetime.time(9, 39, 5),
                    'end': datetime.time(18, 19, 52)},
                datetime.date(2013, 9, 19): {
                    'start': datetime.time(10, 48, 46),
                    'end': datetime.time(17, 53, 51)},
                datetime.date(2013, 9, 18): {
                    'start': datetime.time(9, 19, 52),
                    'end': datetime.time(16, 47, 37)}
                }
            }

        weekdays = utils.group_by_weekday(data[10])
        self.assertEqual(len(weekdays), 7)
        self.assertEqual(weekdays[0], [])
        self.assertEqual(weekdays[1], [30047, 31247])
        self.assertEqual(weekdays[2], [24465, 26865])
        self.assertEqual(weekdays[3], [23705, 25505])
        self.assertEqual(weekdays[4], [])
        self.assertEqual(weekdays[5], [])
        self.assertEqual(weekdays[6], [])

    def test_group_by_weekday_presence(self):
        """
        Test grouping by weekday presence
        """

        data = {
            10: {
                datetime.date(2013, 9, 10): {
                    'start': datetime.time(9, 39, 5),
                    'end': datetime.time(17, 59, 52)},
                datetime.date(2013, 9, 12): {
                    'start': datetime.time(10, 48, 46),
                    'end': datetime.time(17, 23, 51)},
                datetime.date(2013, 9, 11): {
                    'start': datetime.time(9, 19, 52),
                    'end': datetime.time(16, 7, 37)},
                datetime.date(2013, 9, 17): {
                    'start': datetime.time(9, 39, 5),
                    'end': datetime.time(18, 19, 52)},
                datetime.date(2013, 9, 19): {
                    'start': datetime.time(10, 48, 46),
                    'end': datetime.time(17, 53, 51)},
                datetime.date(2013, 9, 18): {
                    'start': datetime.time(9, 19, 52),
                    'end': datetime.time(16, 47, 37)}
                }
            }

        weekdays = utils.group_by_weekday_presence(data[10])
        self.assertEqual(len(weekdays), 7)
        self.assertEqual(weekdays[0], [0, 0])
        self.assertEqual(weekdays[1], [34745.0, 65392.0])
        self.assertEqual(weekdays[2], [33592.0, 59257.0])
        self.assertEqual(weekdays[3], [38926.0, 63531.0])
        self.assertEqual(weekdays[4], [0, 0])
        self.assertEqual(weekdays[5], [0, 0])
        self.assertEqual(weekdays[6], [0, 0])

    def test_seconds_since_midnight(self):
        """
        Test calculating time
        """
        value = utils.seconds_since_midnight(datetime.time(9, 39, 5))
        self.assertEqual(value, 34745)

        value = utils.seconds_since_midnight(datetime.time(17, 59, 52))
        self.assertEqual(value, 64792)

        value = utils.seconds_since_midnight(datetime.time(0, 0, 0))
        self.assertEqual(value, 0)

    def test_interval(self):
        """
        Test if interval is returned properly
        """
        value = utils.interval(datetime.time(9, 39, 5),
                               datetime.time(17, 59, 52))
        self.assertEqual(value, 30047)

        value = utils.interval(datetime.time(9, 19, 52),
                               datetime.time(16, 7, 37))
        self.assertEqual(value, 24465)

        value = utils.interval(datetime.time(0, 0, 0),
                               datetime.time(23, 59, 59))
        self.assertEqual(value, 86399)

        value = utils.interval(datetime.time(0, 0, 0), datetime.time(0, 0, 0))
        self.assertEqual(value, 0)

    def test_mean(self):
        """
        Test if mean is returned corretly
        """
        self.assertEqual(utils.mean([0]), 0)
        self.assertEqual(utils.mean([0, 0]), 0)
        self.assertEqual(utils.mean([300, 400]), 350.0)

        sample_data = [0, 30047, 24465, 23705, 0, 0, 0]
        self.assertEqual(utils.mean(sample_data), 11173.857142857143)


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
