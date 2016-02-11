import unittest
import re

from unittest import mock

from text_regonizer.commands import *
from text_regonizer import inputs


class BaseCommandTestCase:
    pass


class TestAnyResult(unittest.TestCase):
    needle = "I'm what ya lookin for"

    def test_no_input(self):
        self.assertFalse(any_result([]))

    def test_falsy_input(self):
        self.assertFalse(any_result([False]))
        self.assertFalse(any_result([False, False]))
        self.assertFalse(any_result([False, None, "", [], {}]))

    def assert_needle(self, values):
        self.assertEqual(self.needle, any_result(values))

    def test_input(self):
        self.assert_needle([self.needle])
        self.assert_needle([self.needle, False])
        self.assert_needle([False, "", None, self.needle, {}])


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

    def prep_intype(self, part_of_input, completed):
        intype = mock.Mock(inputs.InputType)
        intype.is_part_of_input.return_value = part_of_input
        intype.is_input_completed.return_value = completed

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


class CommandFunctionalTestsMeta(type):

    def __new__(mcs, name, bases, namespace, **kwargs):

        def gen_valid_commands(command):

            def test_command_valid(self):
                self.assertTrue(self.command.matches(command))

            return test_command_valid

        def gen_invalid_commands(command):

            def test_command_invalid(self):
                self.assertFalse(self.command.matches(command))

            return test_command_invalid

        name_regex = re.compile(r"[^a-z0-9]")

        def adder(generator, commands, name):
            for command in commands:
                test = generator(command)
                namespace[name.format(name_regex.sub("_", command))] = test

        valid = namespace.get("valid_commands", [])
        invalid = namespace.get("invalid_commands", [])

        adder(gen_valid_commands, valid, "test_valid_command_{}")
        adder(gen_invalid_commands, invalid, "test_invalid_command_{}")

        return type.__new__(mcs, name, bases, namespace, **kwargs)


class CommandFunctionalTests(metaclass=CommandFunctionalTestsMeta):

    def setUp(self):
        self.command = self.command_class()


class TestWeatherCommand(CommandFunctionalTests, unittest.TestCase):
    command_class = WeatherCommand
    valid_commands = ["show me the weather"]
    invalid_commands = ["foo", "foo bar", "show me", "show me the",]


class TestReminderCommand(CommandFunctionalTests, unittest.TestCase):
    command_class = ReminderCommand
    valid_commands = [
        "remind me to do something tomorrow",
        "tomorrow remind me to do something",
        "at 5:30am remind me to do some cool and awesome stuff",
        "remind me to do some cool and and awesome stuff at 5pm",
    ]

    invalid_commands = [
        "foo",
        "foo bar"
        "remind me to do something",
        "remid me to do something tomorrow",
        "5pm remind me to do something",
    ]
