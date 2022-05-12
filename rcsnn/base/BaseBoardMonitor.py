from rcsnn.base.DataDictionary import DataDictionary, DictionaryTypes, DictionaryEntry
from rcsnn.base.CommandObject import CommandObject
from rcsnn.base.Commands import Commands
from rcsnn.base.ResponseObject import ResponseObject
from rcsnn.base.Responses import Responses
from rcsnn.base.States import States
from rcsnn.base.BaseController import BaseController

from typing import Dict

class BaseBoardMonitor:
    current_step : int
    name = 'BaseBoardMonitor'
    ddict : DataDictionary
    elapsed_time_entry : DictionaryEntry
    controller_dict:Dict

    def setup(self):
        self.controller_dict = {}
        self.ddict = DataDictionary()
        self.elapsed_time_entry = DictionaryEntry("elapsed-time", DictionaryTypes.FLOAT, 0)
        self.ddict.add_entry(self.elapsed_time_entry)

    def start(self):
        self.current_step = 0

    def get_cmd_str(self, controller_name:str) -> str:
        if controller_name in self.controller_dict:
            ctrl:BaseController = self.controller_dict[controller_name]
            return ctrl.cmd.cmd
        return "NOP"

    def get_state_str(self, controller_name:str) -> str:
        if controller_name in self.controller_dict:
            ctrl:BaseController = self.controller_dict[controller_name]
            return ctrl.cur_state
        return "NOP"

    def get_rsp_str(self, controller_name:str) -> str:
        if controller_name in self.controller_dict:
            ctrl:BaseController = self.controller_dict[controller_name]
            return ctrl.rsp.rsp
        return "NOP"

    def step(self) -> bool:
        done = False
        self.elapsed_time_entry.data += 0.1
        self.ddict.store(skip = 1)
        self.current_step += 1

    def decision_process(self) -> bool:
        return False

    def terminate(self):
        print("{} terminating".format(self.name))

def main():
    """
    Exercise the class in a toy hierarchy that initializes, runs, and terminates. The hierarchy is controlled from the
    main loop and has two controllers, a "parent" and a "child"
    """
    bdmon = BaseBoardMonitor()
    bdmon.setup()
    bdmon.start()
    done = False
    while not done:
        done = bdmon.step()

    bdmon.terminate()

if __name__ == "__main__":
    main()