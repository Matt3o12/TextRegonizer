from enum import Enum
from text_regonizer.inputs import ArbitaryInput, TimeInput, InputType, StringInput


class HandlerStatus(Enum):
    DONE = 1
    PROCESSING = 2
    NOT_FOUND = 3


def any_result(iterable):
    for element in iterable:
        if element:
            return element

    return False


class Command:
    structures = None

    def matches(self, sentence):
        i = any_result(self._match_structure(sentence, s)
                       for s in self.structures)
        return i

    def _lookahead(self, sentence, intype):
        # We need to look ahead and check when the next input starts
        # We do that best by starting to check at the last element
        # and going to the next element till we find a match.
        reversed_sentence = sentence.copy()
        reversed_sentence.reverse()

        if not intype.completable:
            raise InputTypeException("There was already an " +
                                     "uncompletable input type present.")

        for i in range(1, len(reversed_sentence)):
            subsentence = reversed_sentence[:i]
            subsentence.reverse()

            parts = self._parse_intype(intype, subsentence)
            if parts is not None:
                del sentence[i + 1:]
                return parts

        return False

    def _match_structure(self, sentence, structure):
        sentence = sentence.split(" ")
        result = []

        uncompletable_input_present = False
        lookahead_parts = None
        for i, intype in enumerate(structure):
            if lookahead_parts:
                # Last iteration, we did a successful lookahead.
                # Let's now clean the lookahead_parts so it won't get
                # added the next time and skip this iteration because we
                # have already processed that structure ;)
                lookahead_parts = None
                continue

            if not intype.completable and uncompletable_input_present:
                raise InputTypeException("There was already an uncompletable " +
                                         "input type present.")
            elif not intype.completable and i + 1 < len(structure):
                lookahead_parts = self._lookahead(sentence, structure[i + 1])
                if not lookahead_parts:
                    return False

            parts = self._parse_intype(intype, sentence)
            if parts is None and intype.completable:
                return False

            result.append((type(intype).__name__, " ".join(parts) if parts else
                           parts))
            if lookahead_parts:
                result.append((type(structure[i + 1]).__name__, lookahead_parts
                              ))

        return result

    def __move_parts_back(self, parts, sentence):
        for i, part in enumerate(parts):
            sentence.insert(i, part)

    def _parse_intype(self, intype, sentence):
        parts = []
        status = None
        while True:
            if len(sentence) == 0 and not intype.completable:
                return parts

            if len(sentence) == 0:
                self.__move_parts_back(parts, sentence)
                return None

            parts.append(sentence.pop(0))
            status = self.handle_input_type(parts, intype)
            # print(" Parts: {}; Remaining: {}; intype: {}".format(
            #     parts, sentence,
            #     type(intype).__name__ if isinstance(intype, InputType) else intype
            # ))
            if status == HandlerStatus.DONE:
                return parts

        self.__move_parts_back(parts, sentence)

    def handle_input_type(self, parts, intype):
        if not intype.is_part_of_input(parts):
            return HandlerStatus.NOT_FOUND

        if intype.is_input_completed(parts):
            return HandlerStatus.DONE

        return HandlerStatus.PROCESSING


class WeatherCommand(Command):
    structures = [(StringInput("show me the weather"),)]


class ReminderCommand(Command):
    structures = [
        (TimeInput(), StringInput("remind me to"), ArbitaryInput()),
        (StringInput("remind me to"), ArbitaryInput(), TimeInput()),
    ]


def is_command(sentence):
    commands = [ReminderCommand(), WeatherCommand()]
    return any_result(c.matches(sentence) for c in commands)
