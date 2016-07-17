#!/usr/bin/python3

import unittest as ut
from unittest.mock import patch, MagicMock

from radio_watcher import Period

class TestPeriod(ut.TestCase):

    def test_single_value(self):
        p1 = Period(4, None, None,
                    True, 80)
        p1._apply_settings = MagicMock(return_value=True)
        p1._check_settings_valid = MagicMock(return_value=False)
        self.assertTrue(p1.check(4, 0, 0))
        p1._apply_settings.assert_called()

    def test_within_interval(self):
        p1 = Period((2, 6), None, (0, 15),
                    True, 80)
        p1._apply_settings = MagicMock(return_value=True)
        p1._check_settings_valid = MagicMock(return_value=False)
        # tests
        self.assertTrue(p1.check(2, 5, 15))
        p1._apply_settings.assert_called()
        self.assertTrue(p1.check(6, 5, 15))
        p1._apply_settings.assert_called()
        self.assertTrue(p1.check(4, 5, 15))
        p1._apply_settings.assert_called()
        self.assertFalse(p1.check(7, 5, 15))
        p1._apply_settings.assert_not_called()
        self.assertFalse(p1.check(4, None, 16))
        p1._apply_settings.assert_not_called()

class TestSubPeriod(ut.TestCase):
        
    def test_subperiod(self):
        p1 = Period(4, None, None,
                    True, 80) 
        p1._apply_settings = MagicMock(return_value=True)
        p1._check_settings_valid = MagicMock(return_value=False)
        p2 = Period(4, (12, 13), None, True, 80)
        p2._apply_settings = MagicMock(return_value=True)
        p2._check_settings_valid = MagicMock(return_value=False)
        # test
        self.assertTrue(p1.check(4, 12, None))
        # checks
        p1._apply_settings.assert_not_called()
        p2._apply_settings.assert_called()

    def test_multiple_subperiods(self):
        parent_period = Period((0,5), None, None, None, None)
        parent_period._apply_settings = MagicMock(return_value=True)
        parent_period._check_settings_valid = MagicMock(return_value=False)
        # children periods
        
if __name__ == '__main__':
    ut.main()
