from text_regonizer.common import came2underscore
import json


class Action:

    def __init__(self, inputs):
        self.inputs = inputs

    def get_action_name(self):
        return came2underscore(type(self).__name__)

    def do_action(self):
        raise NotImplementedError("do_action needs to implemented.")

    def dump_action(self, stream):
        json.dump({"action": None}, stream)


class WeatherAction(Action):

    def do_action(self):
        pass
