from enum import Enum
from text_regonizer.inputs import ArbitaryInput, TimeInput, InputType, StringInput
from text_regonizer.common import any_result
from text_regonizer import actions


class HandlerStatus(Enum):
    DONE = 1
    PROCESSING = 2
    NOT_FOUND = 3


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
        ahead_sentence = sentence.copy()

        if not intype.completable:
            raise InputTypeException("There was already an " +
                                     "uncompletable input type present.")

        for i, word in enumerate(ahead_sentence):
            subsentence = ahead_sentence[i:]
            parts = self._parse_intype(intype, subsentence)
            if parts is not None:
                del sentence[i:]
                return parts

        return False

    def _match_structure(self, sentence, structure):
        sentence = sentence.split(" ")
        results = {}

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
                lookahead_intype = structure[i + 1]
                lookahead_parts = self._lookahead(sentence, lookahead_intype)
                if not lookahead_parts:
                    return False

            parts = self._parse_intype(intype, sentence)
            if parts is None and intype.completable:
                return False

            intype.set_result(results, parts)
            if lookahead_parts:
                lookahead_intype.set_result(results, lookahead_parts)

        return results or True

    def _parse_intype(self, intype, sentence):
        parts = sentence.copy()
        status = None

        if not intype.completable:
            del sentence[:]
            return parts

        for i in range(len(sentence)):
            if self.handle_input_type(parts, intype) == HandlerStatus.DONE:
                del sentence[:-i]
                return parts

            parts.pop()

        return None

    def handle_input_type(self, parts, intype):
        if not intype.is_part_of_input(parts):
            return HandlerStatus.NOT_FOUND

        if intype.is_input_completed(parts):
            return HandlerStatus.DONE

        return HandlerStatus.PROCESSING

    def to_action(self, results):
        """
        Returns corresponding action. results are the
        results returned by match.
        """

        if results is True:
            # results is True if the command was a match
            # but no parts could be extracted (i.e. it was a
            # static command such as the weather command.
            results = {}

        return self.action_class(results)


class WeatherCommand(Command):
    structures = [(StringInput("show me the weather"),)]
    action_class = actions.WeatherAction


class ReminderCommand(Command):
    action_class = actions.ReminderAction
    structures = [
        (TimeInput("time"), StringInput("remind me to"),
         ArbitaryInput("reminder")),
        (StringInput("remind me to"), ArbitaryInput("reminder"),
         TimeInput("time")),
    ]


def is_command(sentence):
    commands = [ReminderCommand(), WeatherCommand()]
    foo = ReminderCommand().matches(sentence)
    key = lambda x: x and x[1]

    return any_result(((c, c.matches(sentence)) for c in commands), key)
