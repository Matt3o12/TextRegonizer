import unittest
import io

from text_regonizer.actions import Action, WeatherAction

class TestAction(unittest.TestCase):
    def setUp(self):
        self.action = Action({})

    def test_dump_action(self):
        got = io.StringIO()
        self.action.dump_action(got)
        self.assertEqual('{"action": null}', got.getvalue())

    def test_get_action_name(self):
        self.assertEqual("action", self.action.get_action_name())
        


class TestWeatherAction(unittest.TestCase):
    def setUp(self):
        self.action = WeatherAction({})

    def test_get_action_name(self):
        self.assertEqual("weather_action", self.action.get_action_name())

    def test_do_action(self):
        # For now, let's only verify that it doesn't raise a 
        # NotImplementedError.
        self.action.do_action()
