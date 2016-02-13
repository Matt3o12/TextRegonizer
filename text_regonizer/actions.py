from text_regonizer.common import came2underscore
import json


class Action:

    def __init__(self, inputs):
        self.inputs = inputs

    def get_action_name(self):
        return came2underscore(type(self).__name__)

    def do_action(self):
        raise NotImplementedError("do_action needs to implemented.")

    def dump_action(self, stream, **kwargs):
        json.dump(
            {
                "action": self.get_action_name(),
                "inputs": self.inputs
            }, stream, **kwargs)

    def __eq__(self, other):
        if isinstance(other, Action):
            return self.inputs == other.inputs

        return False

    def __repr__(self):
        c = type(self)
        return "{}.{}({!r})".format(self.__module__, c.__name__, self.inputs)


class WeatherAction(Action):

    def do_action(self):
        pass


class ReminderAction(Action):
    pass
