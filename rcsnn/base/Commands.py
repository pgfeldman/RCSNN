from enum import Enum
from typing import Dict

'''
class Commands(Enum):
    NOP = "no_op"
    INIT = "init"
    RUN = "run"
    PAUSE = "pause"
    TERMINATE = "terminate"
    RESET = "reset"
    MOVE_TO_ANGLE = "move_to_angle"
    TARGET_SHIPS = "target_ships"
    MOVE_TO_TARGET = "move_to_target"
'''
class Commands():
    NOP = "no_op"
    INIT = "init"
    RUN = "run"
    PAUSE = "pause"
    TERMINATE = "terminate"
    RESET = "reset"
    MOVE_TO_ANGLE = "move_to_angle"
    TARGET_SHIPS = "target_ships"
    MOVE_TO_TARGET = "move_to_target"

    def __init__(self, new_var_list):
        v:str
        n:str
        for v in new_var_list:
            n = v.upper()
            setattr(self, n, v)

def main():
    c = Commands(["one", "two", "three"])
    print("{}, {}, {}".format(c.ONE, c.TWO, c.THREE))

if __name__ == "__main__":
    main()

