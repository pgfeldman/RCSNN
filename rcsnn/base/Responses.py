from enum import Enum


class Responses():
    NOP = "no_op"
    EXECUTING = "executing"
    DONE = "done"
    ERROR = "error"

    def __init__(self, new_var_list):
        v:str
        n:str
        for v in new_var_list:
            n = v.upper()
            setattr(self, n, v)


