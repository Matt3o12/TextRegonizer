from commands import is_command

if __name__ == "__main__":
    sentences = [
        "tomorrow remind me to do something",
        "tomorrow remnd me to do something",
        "show me the weather",
        "remind me to do something tomorrow",
    ]

    for s in sentences[:]:
        matches = is_command(s)
        print("'{}' is {}a match".format(s, "" if matches else "not "))
        print("> {}".format(matches))
        print()
