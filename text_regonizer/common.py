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
