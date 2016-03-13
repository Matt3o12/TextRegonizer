import io
import datetime
import unittest

from text_regonizer.actions import Action, ReminderAction, WeatherAction


class TestAction(unittest.TestCase):

    def setUp(self):
        self.action = Action({})

    def test_dump_action_empty(self):
        got = io.StringIO()
        self.action.dump_action(got, sort_keys=True)
        self.assertEqual('{"action": "action", "inputs": {}}', got.getvalue())

    def test_dump_action(self):
        got = io.StringIO()
        self.action.inputs = {'foo': None, 'bar': 123, 'hello': 'world'}
        expected = ('{"action": "action", "inputs": {"bar": 123, '
                    '"foo": null, "hello": "world"}}')

        self.action.dump_action(got, sort_keys=True)
        self.assertEqual(expected, got.getvalue())

    def test_get_action_name(self):
        self.assertEqual("action", self.action.get_action_name())


class BaseActionTestCase:
    default_input = {}

    def test_get_action_name(self):
        self.assertEqual(self.expected_name, self.action.get_action_name())

    def setUp(self):
        self.action = self.action_class(self.default_input)


class TestWeatherAction(BaseActionTestCase, unittest.TestCase):
    expected_name = "weather_action"
    action_class = WeatherAction

    def test_do_action(self):
        # For now, let's only verify that it doesn't raise a 
        # NotImplementedError.
        self.action.do_action()


class TestReminderAction(BaseActionTestCase, unittest.TestCase):
    expected_name = "reminder_action"
    action_class = ReminderAction
    default_input = {
        'time': datetime.datetime(2005, 5, 3, 2 + 12, 30, 45),
        'reminder': ['do', 'some', 'and', 'awesome', 'stuff']
    }

    def test_dump_action(self):
        expected = ('{"action": "reminder_action", "inputs": '
                    '{"reminder": ["do", "some", "and", "awesome", "stuff"], '
                    '"time": "2005-05-03T14:30:45"}}')
        got = io.StringIO()
        self.action.dump_action(got, sort_keys=True)
        self.assertEqual(expected, got.getvalue())
