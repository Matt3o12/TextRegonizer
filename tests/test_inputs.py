from text_regonizer import inputs
from unittest import TestCase


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


class TestTimeInput(BaseInputTypeTestCase, TestCase):
    completable = True

    is_input_completed_parts = [
        "today", "tomorrow", "tonight", "at 3pm", "at 7pm", "at 2am",
        "at 2:30am", "at 4:20pm"
    ]
    is_input_not_completed_parts = [
        "at 5", "at 5:20", "at", "noon", "foo bar", "barz", "never"
    ]

    is_part_of_input_parts = ["at"]
    is_not_part_of_input_parts = ["hello", "foo bar"]

    def setUp(self):
        self.intype = inputs.TimeInput()
