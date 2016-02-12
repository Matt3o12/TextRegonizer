def any_result(iterable, key=None):
    if key is None:
        key = lambda x: x

    for element in iterable:
        if key(element):
            return element

    return False
