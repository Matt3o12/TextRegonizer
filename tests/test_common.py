import unittest

from text_regonizer.common import any_result, came2underscore


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

