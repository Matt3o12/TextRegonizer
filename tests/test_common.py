import unittest
from datetime import timedelta

from dateutil.parser import parse as parse_time
from text_regonizer.common import (any_result,
                                   came2underscore,
                                   next_weekday,
                                   weekday_to_num,)


class TestAnyResult(unittest.TestCase):
    needle = "I'm what ya lookin for"

    def test_no_input(self):
        self.assert_no_result([])

    def test_falsy_input(self):
        self.assert_no_result([False])
        self.assert_no_result([False, False])
        self.assert_no_result([False, None, "", [], {}])

    def assert_needle(self, *values):
        self.assertEqual(self.needle, any_result(*values))

    def assert_no_result(self, *values):
        self.assertFalse(any_result(*values))

    def test_input(self):
        self.assert_needle([self.needle])
        self.assert_needle([self.needle, False])
        self.assert_needle([False, "", None, self.needle, {}])

    def test_input_with_key(self):
        self.needle = (False, "hello world")
        key = lambda x: x[1]
        self.assert_needle([self.needle], key)
        self.assert_needle([self.needle, (False, False)], key)
        self.assert_needle([(True, False), (False, False), self.needle], key)

    def test_input_with_key_invalid(self):
        key = lambda x: x[0]
        self.assert_no_result([], key)
        self.assert_no_result([(False, False)], key)
        self.assert_no_result([(False, True), (False, False)], key)


class TestCamleCaseToUnderscore(unittest.TestCase):

    def test_came_to_underscore(self):
        self.assertEqual("test", came2underscore("Test"))
        self.assertEqual("hello_world", came2underscore("HelloWorld"))
        self.assertEqual("foo_bar", came2underscore("fooBar"))
        self.assertEqual("foo_bar_hello_test_bar_foo",
                         came2underscore("fooBarHelloTestBarFoo"))


class TestWeekdayToNum(unittest.TestCase):

    def assert_weekday(self, weekday, expected):
        self.assertEqual(expected, weekday_to_num(weekday))

    def assert_not_weekday(self, weekday):
        self.assertEqual(-1, weekday_to_num(weekday))

    def test_abbr(self):
        self.assert_weekday("Mon", 0)
        self.assert_weekday("Tue", 1)
        self.assert_weekday("Wed", 2)
        self.assert_weekday("Thu", 3)
        self.assert_weekday("Fri", 4)
        self.assert_weekday("Sat", 5)
        self.assert_weekday("Sun", 6)

    def test_abbr_mixed_case(self):
        self.assert_weekday("MoN", 0)
        self.assert_weekday("wed", 2)
        self.assert_weekday("SUN", 6)

    def test_names(self):
        self.assert_weekday("Monday", 0)
        self.assert_weekday("Tuesday", 1)
        self.assert_weekday("Wednesday", 2)
        self.assert_weekday("Thursday", 3)
        self.assert_weekday("Friday", 4)
        self.assert_weekday("Saturday", 5)
        self.assert_weekday("Sunday", 6)

    def test_names_mixed_case(self):
        self.assert_weekday("monday", 0)
        self.assert_weekday("MonDaY", 0)
        self.assert_weekday("sunDay", 6)

    def test_not_found(self):
        self.assert_not_weekday("Mo")
        self.assert_not_weekday("foo")
        self.assert_not_weekday("bar")


class TestNextWeekday(unittest.TestCase):
    range_err = "weekday is not within range 0..6"

    def setUp(self):
        self.default = parse_time("Thu, Feb 4 2016")

    def next_weekday(self, weekday):
        return next_weekday(self.default, weekday)

    def test_same_day(self):
        self.assertEqual(self.default, self.next_weekday("Thu"))
        self.assertEqual(self.default, self.next_weekday("Thursday"))
        self.assertEqual(self.default, self.next_weekday(3))

    def test_next_weekday(self):
        d = lambda n: self.default + timedelta(days=n)
        self.assertEqual(d(1), self.next_weekday("Fri"))
        self.assertEqual(d(2), self.next_weekday("Sat"))
        self.assertEqual(d(3), self.next_weekday("Sun"))
        self.assertEqual(d(4), self.next_weekday("Mon"))
        self.assertEqual(d(5), self.next_weekday("Tue"))
        self.assertEqual(d(6), self.next_weekday("Wed"))

    def assert_invalid_weekday(self, weekday, msg):
        with self.assertRaises(ValueError) as exc:
            self.next_weekday(weekday)

        self.assertEqual(msg, str(exc.exception))

    def test_next_weekday_value_error_str(self):
        self.assert_invalid_weekday("foo", "Not a weekday: 'foo'")

    def test_next_weekday_value_error_positive(self):
        self.assert_invalid_weekday(7, self.range_err)
        self.assert_invalid_weekday(8, self.range_err)
        self.assert_invalid_weekday(9, self.range_err)
        self.assert_invalid_weekday(10, self.range_err)

    def test_next_weekday_value_error_negative(self):
        self.assert_invalid_weekday(-1, self.range_err)
        self.assert_invalid_weekday(-10, self.range_err)
