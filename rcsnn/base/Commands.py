from enum import Enum

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

