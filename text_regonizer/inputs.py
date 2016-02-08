import re

class InputTypeException(Exception):
    pass

class InputType:
    completable = True

    def is_part_of_input(self, parts):
        return True

    def is_input_completed(self, parts):
        return True


class StringInput(InputType):
    def __init__(self, expected_parts):
        self.expected_parts = expected_parts
        if isinstance(self.expected_parts, str):
            self.expected_parts = self.expected_parts.split(" ")

    def is_input_completed(self, parts):
        return parts == self.expected_parts

    def is_part_of_input(self, parts):
        return self.expected_parts[:len(parts)] == parts


class ArbitaryInput(InputType):
    completable = False

    def is_input_completed(self, parts):
        return False


class TimeInput(InputType):
    fixed_times = {"today": "2:00pm", "tonight": "6:00pm", "tomorrow": "9am",}

    time_regexes = [
        r"^at (?P<hour>[0-9]{1,2})" +
        "(?:\:(?P<mintue>[]0-9]{2}))?(?P<period>am|pm)$",
        # Do more like tomorrow, on sunday, on sunday 9pm, ...
    ]

    def is_part_of_input(self, parts):
        return (len(parts) == 1 and parts[0] == "at"
                or self.is_input_completed(parts))

    def is_input_completed(self, parts):
        parts = " ".join(parts)
        if parts in self.fixed_times:
            return True

        for test in self.time_regexes:
            if re.match(test, parts):
                return True

        return False
