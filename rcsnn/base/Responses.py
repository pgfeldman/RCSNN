from enum import Enum


class Responses(Enum):
    NOP = "no_op"
    EXECUTING = "executing"
    DONE = "done"
    ERROR = "error"


