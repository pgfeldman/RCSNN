from rcsnn.base.Commands import Commands, CommandObject
from rcsnn.base.DataDictionary import DataDictionary, DictionaryEntry, DictionaryTypes
from rcsnn.base.Responses import Responses, ResponseObject
from rcsnn.base.States import States

from typing import Union

class BaseController():
    cmd: CommandObject = Union[CommandObject, None]
    rsp: ResponseObject = Union[ResponseObject, None]
    cur_state = States.NOP
    ddict: DataDictionary = Union[DataDictionary, None]
    name = "unset"
    clock = 0
    dclock = 0
    elapsed = 0
    child_cmd_dict = {}
    child_rsp_dict = {}

    def __init__(self, name: str, ddict: DataDictionary):
        self.reset()
        self.name = name
        self.ddict = ddict
        self.add_init()

    def reset(self):
        self.name = "unset"
        self.clock = 0
        self.dclock = 0
        self.elapsed = 0
        self.cmd: CommandObject = None
        self.rsp: ResponseObject = None
        self.child_cmd_dict = {}
        self.child_rsp_dict = {}
        self.add_reset()

    def add_init(self):
        pass

    def add_reset(self):
        pass

    def set_cmd_obj(self, co: CommandObject):
        self.cmd = co

    def set_rsp_obj(self, ro: ResponseObject):
        self.rsp = ro

    def add_child_cmd(self, cmd: CommandObject):
        self.child_cmd_dict[cmd.name] = cmd

    def add_child_rsp(self, rsp: ResponseObject):
        self.child_rsp_dict[rsp.name] = rsp

    def set_all_child_cmd(self, cmd: Commands):
        for co in self.child_cmd_dict.values():
            co.set(cmd, co.next_serial())

    def test_all_child_rsp(self, rsp: Responses) -> bool:
        for ro in self.child_rsp_dict.values():
            if not ro.test(rsp):
                return False
        return True

    def evaluate_cmd(self) -> Commands:
        if self.cmd.new_command:
            self.cur_state = States.NEW_COMMAND
            self.rsp.set(Responses.EXECUTING, self.cmd.serial)
        return self.cmd.get()

    def get_response(self) -> ResponseObject:
        return (self.rsp)

    def step(self):
        current = self.ddict.get_entry("elapsed-time").data
        self.dclock = current - self.clock
        self.clock = current
        self.elapsed += self.dclock
        # print("dclock = {:.2f}, clock = {:.2f}".format(self.dclock, self.clock))
        self.pre_process()
        self.decision_process()
        self.post_process()

    def pre_process(self):
        pass

    def decision_process(self):
        command = self.evaluate_cmd()
        if command == Commands.INIT:
            self.init_task()
        elif command == Commands.RUN:
            self.run_task()
        elif command == Commands.TERMINATE:
            self.terminate_task()

    def post_process(self):
        pass

    def init_task(self):
        if self.cur_state == States.NEW_COMMAND:
            print("{} is initializing".format(self.name))
            self.set_all_child_cmd(Commands.INIT)
            self.cur_state = States.S0
            self.rsp.set(Responses.EXECUTING, self.cmd.serial)
        elif self.cur_state == States.S0 and self.test_all_child_rsp(Responses.DONE):
            print("{} is initialized".format(self.name))
            self.cur_state = States.NOP
            self.rsp.set(Responses.DONE)

    def run_task(self):
        print("{} run_task(): elapsed = {:.2f}".format(self.name, self.elapsed))
        if self.cur_state == States.NEW_COMMAND:
            print("{} is running".format(self.name))
            self.set_all_child_cmd(Commands.RUN)
            self.cur_state = States.S0
            self.elapsed = 0
            self.rsp.set(Responses.EXECUTING, self.cmd.serial)
        elif self.cur_state == States.S0 and self.elapsed >= 1 and self.test_all_child_rsp(Responses.DONE):
            print("{} has finished running".format(self.name))
            self.cur_state = States.NOP
            self.rsp.set(Responses.DONE)

    def terminate_task(self):
        if self.cur_state == States.NEW_COMMAND:
            print("{} is terminating".format(self.name))
            self.set_all_child_cmd(Commands.TERMINATE)
            self.cur_state = States.S0
            self.rsp.set(Responses.EXECUTING, self.cmd.serial)
        elif self.cur_state == States.S0 and self.test_all_child_rsp(Responses.DONE):
            print("{} is terminated".format(self.name))
            self.cur_state = States.NOP
            self.rsp.set(Responses.DONE)

    def to_string(self):
        to_return = "Module {}:\n\t{}\n\t{}\n\tcur_state = {}". \
            format(self.name, self.cmd.to_string(), self.rsp.to_string(), self.cur_state)
        return to_return

    @staticmethod
    def create_cmd_rsp(parent: "BaseController", child: "BaseController", ddict: DataDictionary):
        p2c_cmd = CommandObject(parent.name, child.name)
        p2c_rsp = ResponseObject(parent.name, child.name)
        child.set_cmd_obj(p2c_cmd)
        child.set_rsp_obj(p2c_rsp)
        parent.add_child_cmd(p2c_cmd)
        parent.add_child_rsp(p2c_rsp)
        de = DictionaryEntry(p2c_cmd.name, DictionaryTypes.COMMAND, p2c_cmd)
        ddict.add_entry(de)
        de = DictionaryEntry(p2c_rsp.name, DictionaryTypes.RESPONSE, p2c_rsp)
        ddict.add_entry(de)


if __name__ == "__main__":
    ddict = DataDictionary()
    elapsed_time_entry = DictionaryEntry("elapsed-time", DictionaryTypes.FLOAT, 0)
    ddict.add_entry(elapsed_time_entry)

    t2p_cmd = CommandObject("board-monitor", "parent-controller")
    de = DictionaryEntry(t2p_cmd.name, DictionaryTypes.COMMAND, t2p_cmd)
    ddict.add_entry(de)

    t2p_rsp = ResponseObject("board-monitor", "parent-controller")
    de = DictionaryEntry(t2p_rsp.name, DictionaryTypes.RESPONSE, t2p_rsp)
    ddict.add_entry(de)

    parent_ctrl = BaseController("parent-controller", ddict)
    parent_ctrl.set_cmd_obj(t2p_cmd)
    parent_ctrl.set_rsp_obj(t2p_rsp)
    # child_ctrl = BaseController("child_controller", ddict)
    # parent_ctrl.add_child(child_ctrl)

    t2p_cmd.set(Commands.INIT, 1)
    done = False
    i = 0
    while not done:
        print("\nstep[{}]---------------".format(i))
        elapsed_time_entry.data += 0.1
        ddict.store(1)
        parent_ctrl.step()
        print(parent_ctrl.to_string())

        if t2p_cmd.test(Commands.INIT) and parent_ctrl.rsp.test(Responses.DONE):
            t2p_cmd.set(Commands.RUN, 2)
        elif t2p_cmd.test(Commands.RUN) and parent_ctrl.rsp.test(Responses.DONE):
            t2p_cmd.set(Commands.TERMINATE, 3)
        elif t2p_cmd.test(Commands.TERMINATE) and parent_ctrl.rsp.test(Responses.DONE):
            done = True

        i += 1
    print("\nDataDictionary:\n{}".format(ddict.to_string()))
    ddict.to_excel("../../data/", "base-controller.xlsx")
