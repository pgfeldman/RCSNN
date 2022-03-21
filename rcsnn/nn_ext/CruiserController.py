from rcsnn.base.BaseController import BaseController
from rcsnn.base.DataDictionary import DataDictionary
from rcsnn.base.CommandObject import CommandObject
from rcsnn.base.Commands import Commands
from rcsnn.base.ResponseObject import ResponseObject
from rcsnn.base.Responses import Responses
from rcsnn.base.States import States
from rcsnn.base.DataDictionary import DataDictionary, DictionaryEntry, DictionaryTypes

import random

class CruiserController(BaseController):
    target_pos:DictionaryEntry
    missile_cmd_obj:CommandObject
    nav_cmd_obj:CommandObject
    missile_rsp_obj:ResponseObject
    nav_rsp_obj:ResponseObject

    def __init__(self, name: str, ddict: DataDictionary):
        super().__init__(name, ddict)
        self.heading = DictionaryEntry("target_pos", DictionaryTypes.LIST, [(0, 0), (1, 1)])
        self.ddict.add_entry(self.heading)

    def pre_process(self):
        self.nav_cmd_obj = self.ddict.get_entry("CMD_ship-controller_to_navigate-controller").data
        self.missile_cmd_obj = self.ddict.get_entry("CMD_ship-controller_to_missile-controller").data
        self.nav_rsp_obj = self.ddict.get_entry("RSP_navigate-controller_to_ship-controller").data
        self.missile_rsp_obj = self.ddict.get_entry("RSP_missile-controller_to_ship-controller").data

    def run_task(self):
        # S0: ask MissileControler how far away a 90% accuracy shot is
        # S1: Plot a destination and ask the NavigateController for the time to reach
        # S3: Jump forward in time and ask the MissileController to fire a missile and if it hit
        # S4: Evaluate and re-fire as needed
        # S5: Report back success or failure
        print("{} run_task(): elapsed = {})".format(self.name, self.elapsed))
        if self.cur_state == States.NEW_COMMAND:
            print("{} is running".format(self.name))
            self.nav_cmd_obj.set(Commands.MOVE_TO_TARGET, self.nav_cmd_obj.next_serial())
            self.target_ships()
            self.cur_state = States.S0
            self.elapsed = 0
            self.rsp.set(Responses.EXECUTING, self.cmd.serial)
        elif self.cur_state == States.S0 and self.nav_rsp_obj.get() == Responses.DONE:
            self.cur_state = States.S1
            self.missile_cmd_obj.set(Commands.TARGET_SHIPS, self.missile_cmd_obj.next_serial())
        elif self.cur_state == States.S1 and self.nav_rsp_obj.get() == Responses.DONE:
            self.cur_state = States.NOP
            self.rsp.set(Responses.DONE, self.cmd.serial)


    def target_ships(self):
        scalar = 10
        self.heading.data = [
            ((random.random()-0.5) * scalar, (random.random()-0.5) * scalar),
            ((random.random()-0.5) * scalar, (random.random()-0.5) * scalar)
                            ]