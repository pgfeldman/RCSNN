from enum import Enum


class Commands(Enum):
    NOP = "no_op"
    INIT = "init"
    RUN = "run"
    PAUSE = "pause"
    TERMINATE = "terminate"
    RESET = "reset"
    MOVE_TO_ANGLE = "move_to_angle"


class CommandObject():
    serial = 0
    cmd = Commands.NOP
    parentname = "unset"
    childname = "unset"
    new_command = False
    name = "unset"
    cmd_list = []

    def __init__(self, parentname: str, childname: str):
        self.reset()
        self.parentname = parentname
        self.childname = childname
        self.name = "CMD_{}_to_{}".format(parentname, childname)

    def reset(self):
        self.serial = 0
        self.cmd = Commands.NOP
        self.parentname = "unset"
        self.childname = "unset"
        self.new_command = False
        self.name = "unset"
        self.cmd_list = []

    def next_serial(self):
        return self.serial + 1

    def set(self, cmd: Commands, serial: int):
        if serial != self.serial:
            self.new_command = True
            self.cmd = cmd
            self.serial = serial

    def get(self) -> Commands:
        self.new_command = False
        return self.cmd

    def test(self, to_test: Commands) -> bool:
        return self.cmd == to_test

    def to_string(self) -> str:
        return "cmd = {}, serial = {}".format(self.cmd, self.serial)
