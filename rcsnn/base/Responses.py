from enum import Enum


class Responses(Enum):
    NOP = "no_op"
    EXECUTING = "executing"
    DONE = "done"
    ERROR = "error"


class ResponseObject():
    serial = 0
    rsp = Responses.NOP
    parentname = "unset"
    childname = "unset"
    name = "unset"
    rsp_list = []

    def __init__(self, parentname: str, childname: str):
        self.reset()
        self.parentname = parentname
        self.childname = childname
        self.name = "RSP_{}_to_{}".format(childname, parentname)

    def reset(self):
        self.serial = 0
        self.rsp = Responses.NOP
        self.parentname = "unset"
        self.childname = "unset"
        self.name = "unset"
        self.rsp_list = []

    def set(self, rsp: Responses, serial: int = -1):
        self.rsp = rsp
        if serial > 0:
            self.serial = serial

    def get(self) -> Responses:
        return self.rsp

    def test(self, to_test: Responses) -> bool:
        return self.rsp == to_test

    def to_string(self) -> str:
        return "rsp = {}, serial = {}".format(self.rsp, self.serial)
