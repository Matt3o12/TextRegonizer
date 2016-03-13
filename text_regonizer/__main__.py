import sys
from text_regonizer import commands

def eprint(*args, **kwargs):
    kwargs.setdefault("file", sys.stderr)
    return print(*args, **kwargs)

if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) < 1:
        eprint("No command given")
        sys.exit(1)

    command_string = " ".join(args)
    command, results = commands.is_command(command_string.lower()) or (None, {})
    if not command:
        eprint("'{}' is not a valid command.".format(command_string))
        sys.exit(1)

    action = command.to_action(results)
    action.dump_action(sys.stdout, indent=4)

