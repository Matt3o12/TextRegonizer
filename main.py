from text_regonizer import commands

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]

    if len(args) < 1:
        print("No command given")
        sys.exit(1)
    else:
        r = commands.is_command(" ".join(args).lower())
        print(r if r else "Not a valid command")
