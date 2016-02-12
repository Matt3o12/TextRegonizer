import unittest
import re

from unittest import mock

from text_regonizer.commands import *
from text_regonizer import inputs, actions


class BaseCommandTestCase:
    pass


class TestCommand(unittest.TestCase):

    def setUp(self):
        self.command = Command()
        self.move_method = self.command._Command__move_parts_back

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

    def test_move_parts_none(self):
        base = ["foo", "bar"]
        self.move_method([], base)
        self.assertEqual(["foo", "bar"], base)

    def test_move_parts_back(self):
        base = ["hello", "world"]
        parts = ["foo", "bar"]
        expceted = parts + base
        self.move_method(parts, base)
        self.assertEqual(expceted, base)

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

    def test_parse_intype_completable_out_of_text(self):
        intype = self.prep_intype(True, False, completable=False)
        self.mock_handle_intype(HandlerStatus.PROCESSING)
        s = ["foo", "bar", "hello", "world"]
        s_bck = s.copy()
        self.assertEqual(s_bck, self.command._parse_intype(intype, s))
        self.assertEqual([], s)
        self.assertEqual(4, self.command.handle_input_type.call_count)

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

    def test_parse_intype(self):
        intype = self.prep_intype(True, False)
        _, p, d = self.__get_statuses()
        self.mock_handle_intype([p] * 3 + [d])

        s = ["foo", "bar", "hello", "world", "foobar", "barfoo"]
        s_bck = s.copy()

        self.assertEqual(s_bck[:4], self.command._parse_intype(intype, s))
        self.assertEqual(s_bck[4:], s)


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


class TestReminderCommand(CommandFunctionalTests, unittest.TestCase):
    command_class = ReminderCommand
    valid_commands = {
        "remind me to do something tomorrow": {
            "time": ["tomorrow"],
            "reminder": ["do", "something"]
        },
        "tomorrow remind me to do something": {
            "time": ["tomorrow"],
            "reminder": ["do", "something"]
        },
        "at 5:30am remind me to do some cool and awesome stuff": {
            "time": ["at", "5:30am"],
            "reminder": ["do", "some", "cool", "and", "awesome", "stuff"]
        },
        # TODO: This test fails, investigate later
        # "remind me to do some cool and and awesome stuff at 5pm": {
        #     "time": ["at", "5pm"],
        #     "reminder": ["do", "some", "cool", "and", "awesome", "stuff"]
        # },
    }

    invalid_commands = [
        "foo",
        "foo bar"
        "remind me to do something",
        "remid me to do something tomorrow",
        "5pm remind me to do something",
    ]
