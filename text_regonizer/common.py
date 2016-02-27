import itertools
import calendar

from datetime import timedelta


def any_result(iterable, key=None):
    if key is None:
        key = lambda x: x

    for element in iterable:
        if key(element):
            return element

    return False


def came2underscore(sentence):
    new = []
    for i, char in enumerate(sentence):
        if char.isupper() and i != 0:
            new.append("_")

        new.append(char.lower())

    return "".join(new)


def weekday_to_num(weekday):
    l = lambda l: (w.lower() for w in l)
    weekdays = zip(l(calendar.day_name), l(calendar.day_abbr))
    for n, values in enumerate(weekdays):
        if weekday.lower() in values:
            return n

    return -1


# Taken from: http://stackoverflow.com/a/6558571/1493365
def next_weekday(date, weekday):
    org = weekday
    if isinstance(weekday, str):
        weekday = weekday_to_num(weekday)

    if not 0 <= weekday <= 6:
        if isinstance(org, str):
            raise ValueError("Not a weekday: '{}'".format(org))

        raise ValueError("weekday is not within range 0..6")

    days_ahead = weekday - date.weekday()
    if days_ahead < 0:  # Target day already happened this week but not that day
        days_ahead += 7

    return date + timedelta(days_ahead)
