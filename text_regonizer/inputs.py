import re
from datetime import datetime


class InputTypeException(Exception):
    pass


class InputType:
    completable = True

    def __init__(self, key=None):
        self.key = key

    def is_part_of_input(self, parts):
        return True

    def is_input_completed(self, parts):
        return True

    def set_result(self, results, parts):
        if self.key:
            results[self.key] = self.normalize_parts(parts)
            return True

        return False

    def normalize_parts(self, parts):
        return parts


class StringInput(InputType):

    def __init__(self, expected_parts):

        # StringInput doesn't need a key since it does
        # not map to any values.
        super().__init__(None)

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
    fixed_times = {
        "today": "at 2:00pm",
        "tonight": "at 6:00pm",
        "tomorrow": "at 9am",  # TODO: add support for adding one day.
    }

    time_regexes = [
        r"^at (?P<hour>[0-9]{1,2})" +
        "(?:\:(?P<minute>[]0-9]{2}))?(?P<period>am|pm)$",
        # Do more like tomorrow, on sunday, on sunday 9pm, ...
    ]

    def is_part_of_input(self, parts):
        return (len(parts) == 1 and parts[0] == "at" or
                self.is_input_completed(parts))

    def _get_matches(self, parts):
        for test in self.time_regexes:
            matches = re.match(test, parts)
            if matches:
                return matches

        return None

    def is_input_completed(self, parts):
        parts = " ".join(parts)
        if parts in self.fixed_times:
            return True

        return bool(self._get_matches(parts))

    def normalize_parts(self, parts):
        parts = " ".join(parts)
        parts = self.fixed_times.get(parts, parts)

        matches = self._get_matches(parts)
        if not matches:
            msg = "parts: '{}' must be a valid TimeInput"
            raise InputTypeException(msg.format(parts.split(" ")))

        parsed = matches.groupdict()
        replacements = {"hour": int(parsed["hour"])}
        if parsed["period"] == "pm":
            replacements["hour"] += 12

        replacements["minute"] = int(parsed.get("minute", 0) or 0)

        return datetime.now().replace(**replacements)
