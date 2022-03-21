import math
from rcsnn.base.BaseController import BaseController
from rcsnn.base.DataDictionary import DataDictionary, DictionaryEntry, DictionaryTypes
from rcsnn.base.States import States
from rcsnn.base.CommandObject import CommandObject
from rcsnn.base.Commands import Commands
from rcsnn.base.ResponseObject import ResponseObject
from rcsnn.base.Responses import Responses

class NavigateController(BaseController):
    heading:DictionaryEntry

    def __init__(self, name: str, ddict: DataDictionary):
        super().__init__(name, ddict)

        self.heading = DictionaryEntry("nav-heading", DictionaryTypes.FLOAT, 0)
        self.ddict.add_entry(self.heading)

    def pre_process(self):
        self.heading.data = math.sin(self.elapsed)
        print("NavigateController heading = {}".format(self.heading.data))

    def decision_process(self):
        command = self.evaluate_cmd()
        if command == Commands.INIT:
            self.init_task()
        elif command == Commands.MOVE_TO_TARGET:
            self.move_to_target_task()
        elif command == Commands.TERMINATE:
            self.terminate_task()
        
    def move_to_target_task(self):
        run_time_limit = 0.3
        print("{} run_task(): elapsed = {:.2f} of {} ({:.2f} remaining)".format(self.name, self.elapsed, run_time_limit, (run_time_limit-self.elapsed)))
        if self.cur_state == States.NEW_COMMAND:
            print("{} is running".format(self.name))
            self.set_all_child_cmd(Commands.RUN)
            self.cur_state = States.S0
            self.elapsed = 0
            self.rsp.set(Responses.EXECUTING, self.cmd.serial)
        elif self.cur_state == States.S0 and self.elapsed >= run_time_limit and self.test_all_child_rsp(Responses.DONE):
            print("{} has finished running".format(self.name))
            self.cur_state = States.NOP
            self.rsp.set(Responses.DONE)

    def query_nn(self):
        # results = my_nn.predict()
        pass

    def load_nn(self):
        pass