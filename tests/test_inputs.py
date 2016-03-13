import re
from text_regonizer import inputs
from unittest import TestCase, mock

from datetime import timedelta
from freezegun import freeze_time
from tests import TEST_TIME


class TestInputTypeMeta(type):

    def __new__(mcs, name, bases, namespace, **kwargs):

        def add(name, generator):
            for part in namespace.get(name.format("", "parts"), []):
                if isinstance(part, str):
                    part = part.split(" ")

                testname = name.format("test_", "_".join(part))
                namespace[testname] = generator(part)

        def gen_is_part(parts):

            def test_is_part_of_input(self):
                self.assertTrue(self.intype.is_part_of_input(parts))

            return test_is_part_of_input

        def gen_is_not_part(parts):

            def test_is_not_part_of_input(self):
                self.assertFalse(self.intype.is_part_of_input(parts))

            return test_is_not_part_of_input

        def gen_input_completed(parts):

            def test_is_input_completed(self):
                self.assertTrue(self.intype.is_input_completed(parts))

            return test_is_input_completed

        def gen_input_not_completed(parts):

            def test_is_input_not_completed(self):
                self.assertFalse(self.intype.is_input_completed(parts))

            return test_is_input_not_completed

        add("{}is_part_of_input_{}", gen_is_part)
        add("{}is_input_not_completed_{}", gen_input_not_completed)
        add("{}is_input_completed_{}", gen_input_completed)
        add("{}is_not_part_of_input_{}", gen_is_not_part)

        method_adder = namespace.get("add_methods", None)
        if method_adder:
            method_adder(mcs, name, bases, namespace, **kwargs)

        return type.__new__(mcs, name, bases, namespace, **kwargs)


class BaseInputTypeTestCase(metaclass=TestInputTypeMeta):

    def test_completeable(self):
        self.assertEqual(self.completable, self.intype.completable)


class TestInputType(BaseInputTypeTestCase, TestCase):
    completable = True

    is_input_completed_parts = [[], ["test"], "foo bar"]
    is_part_of_input_parts = is_input_completed_parts

    def setUp(self):
        self.intype = inputs.InputType()

    def test_key(self):
        intype = inputs.InputType("hello_world")
        self.assertEqual("hello_world", intype.key)
        self.assertIsNone(inputs.InputType().key)

    def test_set_result_no_key(self):
        results = {}
        status = self.intype.set_result(results, "hello world")
        self.assertFalse(status)
        self.assertEqual({}, results)

    def test_result(self):
        results = {"foo": "hello"}
        expected = {"foo": "hello", "bar": "world"}
        intype = inputs.InputType("bar")

        status = intype.set_result(results, "world")

        self.assertTrue(status)
        self.assertEqual(expected, results)

    def test_result_normalize_input(self):
        results = {"foo": "bar"}
        normalized = mock.Mock()
        expected = {"foo": "bar", "foobar": normalized}
        intype = inputs.InputType("foobar")
        intype.normalize_parts = mock.Mock(return_value=normalized)

        status = intype.set_result(results, "raw")
        self.assertTrue(status)
        self.assertEqual(expected, results)
        self.assertIs(normalized, results["foobar"])
        intype.normalize_parts.assert_called_once_with("raw")


class TestArbitaryInput(BaseInputTypeTestCase, TestCase):
    completable = False

    is_input_not_completed_parts = [[], "test", "foo bar"]
    is_part_of_input_parts = ["test", "foo bar"]

    def setUp(self):
        self.intype = inputs.ArbitaryInput()


class StringInput(BaseInputTypeTestCase, TestCase):
    completable = True

    is_input_completed_parts = ["hello world. test"]
    is_input_not_completed_parts = ["hello world. foo", "foo"]
    is_part_of_input_parts = ["hello", "hello world."]
    is_not_part_of_input_parts = ["hellz", "hello worlz.", "hello world",
                                  "hello world. foo"]

    def setUp(self):
        self.intype = inputs.StringInput("hello world. test")


@freeze_time(TEST_TIME)
class TestTimeInput(BaseInputTypeTestCase, TestCase):
    completable = True

    is_input_completed_parts = [
        "today",
        "tomorrow",
        "tonight",
        "at 3pm",
        "at 7pm",
        "at 2am",
        "at 2:30am",
        "at 4:20pm",
        "at 5:30am",
        "tonight at 10",
        "at 5",
        "at 9",
        "on monday",
        "on tuesday",
        "on wednesday",
        "on thursday",
        "on friday",
        "on saturday",
        "on sunday",
        "on tuesday at 3pm",
    ]
    is_input_not_completed_parts = [
        "at",
        "noon",
        "foo bar",
        "barz",
        "never",
        "at foo",
        "at bar",
        "tomorrow foo",
        "tomorrow at foo",
        "tomorrow noon",
        "noon at",
        "at tomorrow",
        "tommorow at 5pm bar",
        "sunday",
        "monday",
    ]

    is_part_of_input_parts = [
        "at",
        "tonight at",
        "tomorrow at",
        "on",
        "on sunday",
        "on sunday at",
        "on saturday",
    ]
    is_not_part_of_input_parts = [
        "hello",
        "foo bar",
        "tomorrow foo",
        "tomorrow at foo",
        "at foo",
        "at tomorrow",
        "tomorrow at 5pm foo",
        "saturday",
        "on saturday at foo",
    ]

    normalized_results = {
        "at 5pm": TEST_TIME.replace(hour=5 + 12),
        "at 1am": TEST_TIME.replace(hour=1),
        "at 2:30pm": TEST_TIME.replace(hour=2 + 12, minute=30),
        "at 1:14am": TEST_TIME.replace(hour=1, minute=14),
        "today": TEST_TIME.replace(hour=2 + 12),
        "tomorrow": TEST_TIME.replace(hour=9) + timedelta(days=1),
        "tonight": TEST_TIME.replace(hour=6 + 12),
        "tonight at 9": TEST_TIME.replace(hour=9 + 12),
        "tomorrow at 5pm": TEST_TIME.replace(hour=5 + 12) + timedelta(days=1),
        "on sunday at 3am": TEST_TIME.replace(hour=3, day=2),
        "on friday night at 6": TEST_TIME.replace(hour=6 + 12, day=7)
    }  # yapf: disable

    def add_methods(mcs, name, bases, namespace, **kwargs):

        def gen_normalized(raw, expected):

            def test_normalized_parts(self):
                got = self.intype.normalize_parts(raw.split(" "))
                self.assertEqual(expected, got)

            return test_normalized_parts

        name_regex = re.compile(r"[^a-z0-9]")
        for raw, expected in namespace["normalized_results"].items():
            test = gen_normalized(raw, expected)
            name = "test_normalized_parts_{}".format(name_regex.sub("_", raw))
            namespace[name] = test

    def setUp(self):
        self.intype = inputs.TimeInput()

    def test_normalize_parts_raise_exception(self):
        msg = "parts: '['invalid', 'time']' must be a valid TimeInput"
        expected = "^{}$".format(re.escape(msg))
        with self.assertRaisesRegex(inputs.InputTypeException, expected):
            self.intype.normalize_parts("invalid time".split(" "))
