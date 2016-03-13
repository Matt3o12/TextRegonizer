import unittest
import re

from unittest import mock

from tests import TEST_TIME
from text_regonizer.commands import *
from text_regonizer import inputs, actions

from freezegun import freeze_time
from datetime import timedelta


class BaseCommandTestCase:
    pass


class TestCommand(unittest.TestCase):

    def setUp(self):
        self.command = Command()

    def assert_handler(self, status, parts, intype):
        if isinstance(parts, str):
            parts = parts.split(" ")

        got = self.command.handle_input_type(parts, intype)

        intype.is_part_of_input.assert_called_once_with(parts)
        if status != HandlerStatus.NOT_FOUND:
            intype.is_input_completed.assert_called_once_with(parts)

        self.assertEqual(status, got)

    def prep_intype(self, part_of_input, completed, **attrs):
        intype = mock.Mock(inputs.InputType)
        intype.is_part_of_input.return_value = part_of_input
        intype.is_input_completed.return_value = completed
        intype.configure_mock(**attrs)

        return intype

    def test_handle_input_type_not_found(self):
        s = HandlerStatus.NOT_FOUND
        self.assert_handler(s, "hello world", self.prep_intype(False, True))
        self.assert_handler(s, "hello world", self.prep_intype(False, False))

    def test_handle_input_type_done(self):
        self.assert_handler(HandlerStatus.DONE, "test",
                            self.prep_intype(True, True))

    def test_handle_input_type_processing(self):
        self.assert_handler(HandlerStatus.PROCESSING, "foo bar",
                            self.prep_intype(True, False))

    def mock_handle_intype(self, return_values=None, **kwargs):
        if return_values and isinstance(return_values, list):
            kwargs["side_effect"] = return_values
        elif return_values:
            kwargs["return_value"] = return_values

        self.command.handle_input_type = mock.Mock(**kwargs)

    def test_parse_intype_empty_sentence(self):
        intype = self.prep_intype(False, False)
        self.mock_handle_intype()
        self.assertIsNone(self.command._parse_intype(intype, []))
        self.command.handle_input_type.assert_not_called()

    def test_parse_intype_not_completeable_empty_sentence(self):
        intype = self.prep_intype(False, False, completable=False)
        self.mock_handle_intype()
        self.assertEqual([], self.command._parse_intype(intype, []))
        self.command.handle_input_type.assert_not_called()

    def __get_statuses(self):
        return (HandlerStatus.NOT_FOUND, HandlerStatus.PROCESSING,
                HandlerStatus.DONE)

    def test_parse_intype_out_of_text(self):
        intype = self.prep_intype(True, False)
        self.mock_handle_intype(HandlerStatus.PROCESSING)
        s = ["foo", "bar", "test"]
        s_bck = s.copy()

        self.assertIsNone(self.command._parse_intype(intype, s))
        self.assertEqual(s_bck, s)
        self.assertEqual(2, len(self.command.handle_input_type.call_args))

    def test_to_action(self):
        mocked_action = mock.Mock(actions.Action)
        self.command.action_class = mock.Mock(return_value=mocked_action)
        inputs = mock.Mock(dict)

        self.assertIs(mocked_action, self.command.to_action(inputs))
        self.command.action_class.assert_called_once_with(inputs)

    def test_to_action_true(self):
        action = mock.Mock(actions.Action)
        self.command.action_class = mock.Mock(return_value=action)

        self.assertIs(action, self.command.to_action(True))
        self.command.action_class.assert_called_once_with({})


class CommandFunctionalTestsMeta(type):

    def __new__(mcs, name, bases, namespace, **kwargs):

        def gen_valid_commands(sentence, expected):

            def test_command_valid(self):
                result = self.command.matches(sentence)
                self.assertEqual(expected, result)

            return test_command_valid

        def gen_invalid_commands(sentence):

            def test_command_invalid(self):
                self.assertFalse(self.command.matches(sentence))

            return test_command_invalid

        def gen_is_command(sentence):

            def test_is_command(self):
                command, matches = is_command(sentence) or (None, None)
                self.assertIsNotNone(command, "No command found")
                self.assertIsNotNone(matches, "No command found")

                msg = "Matches: {}".format(matches)
                self.assertIsInstance(command, self.command_class, msg)
                self.assertTrue(matches)

            return test_is_command

        name_regex = re.compile(r"[^a-z0-9]")

        def adder(generator, commands, name):
            for command in commands:
                args = command if isinstance(command, tuple) else (command,)
                test = generator(*args)
                namespace[name.format(name_regex.sub("_", args[0]))] = test

        valid = namespace.get("valid_commands", {})
        invalid = namespace.get("invalid_commands", [])

        adder(gen_valid_commands, valid.items(), "test_valid_command_{}")
        adder(gen_invalid_commands, invalid, "test_invalid_command_{}")
        adder(gen_is_command, valid, "test_is_command_{}")

        return type.__new__(mcs, name, bases, namespace, **kwargs)


class CommandFunctionalTests(metaclass=CommandFunctionalTestsMeta):

    def setUp(self):
        self.command = self.command_class()


class TestWeatherCommand(CommandFunctionalTests, unittest.TestCase):
    command_class = WeatherCommand
    valid_commands = {"show me the weather": True}
    invalid_commands = ["foo", "foo bar", "show me", "show me the",]

    def test_to_action(self):
        result = self.command.matches("show me the weather")
        action = self.command.to_action(result)
        self.assertEqual(actions.WeatherAction({}), action)


@freeze_time(TEST_TIME)
class TestReminderCommand(CommandFunctionalTests, unittest.TestCase):
    command_class = ReminderCommand
    valid_commands = {
        "remind me to do something tonight": {
            "time": TEST_TIME.replace(hour=6 + 12),
            "reminder": ["do", "something"]
        },
        "tonight remind me to do something": {
            "time": TEST_TIME.replace(hour=6 + 12),
            "reminder": ["do", "something"]
        },
        "at 5:30am remind me to do some cool and awesome stuff": {
            "time": TEST_TIME.replace(hour=5, minute=30),
            "reminder": ["do", "some", "cool", "and", "awesome", "stuff"],
        },
        "remind me to do some cool and awesome stuff at 5pm": {
            "time": TEST_TIME.replace(hour=5 + 12),
            "reminder": ["do", "some", "cool", "and", "awesome", "stuff"]
        },
        "remind me to do my homework tomorrow at 5pm": {
            "time": TEST_TIME.replace(hour=5 + 12) + timedelta(days=1),
            "reminder": ["do", "my", "homework"],
        },
        "tomorrow at 5am remind me to do my homework": {
            "time": TEST_TIME.replace(hour=5) + timedelta(days=1),
            "reminder": ["do", "my", "homework"],
        },
        "remind me to do my homework on sunday": {
            "time": TEST_TIME.replace(hour=2 + 12, day=2),
            "reminder": ["do", "my", "homework"],
        },
        "remind me to do my homework on friday": {
            "time": TEST_TIME.replace(hour=2 + 12, day=7),
            "reminder": ["do", "my", "homework"],
        },
    }  # yapf: disable

    invalid_commands = [
        "foo",
        "foo bar"
        "remind me to do something",
        "remid me to do something tomorrow",
        "5pm remind me to do something",
    ]

    def test_to_action(self):
        results = {'time': ['tomorrow'], 'reminder': ['do', 'something']}
        action = self.command.to_action(results)
        self.assertEqual(actions.ReminderAction(results), action)
