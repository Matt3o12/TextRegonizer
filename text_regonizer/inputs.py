import re
from datetime import datetime, timedelta
from enum import Enum


class InputTypeException(Exception):
    def __init__(self, message=None, parts=None):
        if parts is not None:
            parts = parts.split(" ") if isinstance(parts, str) else parts
            message = "parts: '{}' must be a valid TimeInput"
            message = message.format(parts)

        super().__init__(message)


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


class dict_copy_value(dict):
    """
    Dict that copys the value on get
    """

    def __getitem__(self, key):
        return super().__getitem__(key).copy()

class TimeInput(InputType):
    beginning_times = dict_copy_value({
        "today": {"hour": 2 + 12},
        "tonight": {"hour": 6 + 12,
                    "night": True},
        "tomorrow": {"hour": 9,
                     "delta": timedelta(days=1)},
    })

    terminal_times = dict_copy_value({"noon": {"hour": 12},})

    terminal_regex = re.compile(
        r"^(?P<hour>[0-9]{1,2})" +
        "(?:\:(?P<minute>[]0-9]{2}))?(?P<period>am|pm)?$")

    time_regexes = [
        r"^at (?P<hour>[0-9]{1,2})" +
        "(?:\:(?P<minute>[]0-9]{2}))?(?P<period>am|pm)$",
    ]

    def _replace_time(self, time, replacements):
        delta = replacements.pop("delta", timedelta())
        return time.replace(**replacements) + delta

    def _replace_regex(self, time, parts, current, night=False):
        match = self.terminal_regex.match(current)
        if not match:
            raise InputTypeException(parts=parts)

        parsed = match.groupdict()
        replacements = {"hour": int(parsed["hour"])}
        if parsed.get("period", "am") == "pm" or night:
            replacements["hour"] += 12

        replacements["minute"] = int(parsed.get("minute", None) or 0)
        return time.replace(**replacements)

    def _parse_input(self, parts):
        """
        Returns the time for the given parts. False if the input is not
        complete and raises InputTypeException if the input is invalid.
        """

        terminal_input = False
        completable = False
        time = datetime.now()
        night = False
        for i, part in enumerate(parts):
            if part == "at":
                terminal_input = True
                completable = False
            elif terminal_input:
                if i + 1 < len(parts):
                    raise InputTypeException(parts=parts)

                if part in self.terminal_times:
                    return self._replace_time(time, self.terminal_times[part])

                return self._replace_regex(time, parts, part, night)
            else:
                if part in self.beginning_times:
                    replacements = self.beginning_times[part]
                    night = replacements.pop("night", False)
                    time = self._replace_time(time, replacements)
                    completable = True
                else:
                    raise InputTypeException(parts=parts)

        return time if completable else False

    def _get_matches(self, parts):
        for test in self.time_regexes:
            matches = re.match(test, parts)
            if matches:
                return matches

        return None
    
    def normalize_parts(self, parts):
        time = self._parse_input(parts)
        if time is False:
            msg = "Input not completed, parts: {}"
            raise InputTypeException(msg.format(parts))

        return time

    def is_input_completed(self, parts):
        try:
            return bool(self._parse_input(parts))
        except InputTypeException:
            return False

    def is_part_of_input(self, parts):
        try:
            self._parse_input(parts)
            return True
        except InputTypeException:
            return False

