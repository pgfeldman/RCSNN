import io
import json
import os
import glob
from typing import List, Dict, Union, TextIO

class CodeSlugs:
    imports = '''from rcsnn.nn_ext.CruiserController import CruiserController
from rcsnn.nn_ext.MissileController import MissileController
from rcsnn.nn_ext.NavigateController import NavigateController
from rcsnn.base.DataDictionary import DataDictionary, DictionaryTypes, DictionaryEntry
from rcsnn.base.CommandObject import CommandObject
from rcsnn.base.Commands import Commands
from rcsnn.base.ResponseObject import ResponseObject
from rcsnn.base.Responses import Responses
from rcsnn.base.States import States
from rcsnn.base.BaseController import BaseController\n\n'''

    module_head = '''

class {}(BaseController):
    heading:DictionaryEntry

    def __init__(self, name: str, ddict: DataDictionary):
        super().__init__(name, ddict)'''

    decision = '''\n\n    def decision_process(self):
        command = self.evaluate_cmd()'''

    bdmon_head = '''
def main():
    """
    Exercise the class in a toy hierarchy that initializes, runs, and terminates. The hierarchy is controlled from the
    main loop and has two controllers, a "parent" and a "child"
    """
    # create the data dictionary and add "elapsed-time" as a float
    ddict = DataDictionary()
    elapsed_time_entry = DictionaryEntry("elapsed-time", DictionaryTypes.FLOAT, 0)
    ddict.add_entry(elapsed_time_entry)
    
'''
    bdmon_loop = '''
    {}.set(Commands.{}, 1)
    done = False
    current_step = 0
    while not done:
        print("\\nstep[",current_step,"]---------------")
        elapsed_time_entry.data += 0.1
        ddict.store(skip = {})
        ddict.log_to_csv("testlog.csv", {})
    '''
    bdmon_tail = '''            done = True
        current_step += 1

        # for debugging
        if current_step == 100:
            done = True

    ddict.to_excel("../../data/", "{}.xlsx")

if __name__ == "__main__":
    main()'''

class HierarchyModule:
    quantity: int
    index: int
    name: str
    classname: str
    parent: str
    children:List
    commands:List
    cmd_obj_name:str
    rsp_obj_name:str

    def __init__(self, d:Dict):
        self.quantity = 1 #default
        self.index = 0 #default
        self.children = []
        self.__dict__.update(d)

    def find_children(self, hm_list:List):
        hm:HierarchyModule
        for hm in hm_list:
            if hm != self:
                if self.name == hm.parent:
                    self.children.append(hm)

    def has_child(self, name:str):
        hm:HierarchyModule
        for hm in self.children:
            if hm.name == name:
                return hm
        return None

    def generate_code(self):
        filename = "{}.py".format(self.classname)
        with open(filename, 'w') as f:
            f.write(CodeSlugs.imports)
            f.write(CodeSlugs.module_head.format(self.classname))

            f.write(CodeSlugs.decision)
            cmd:str = self.commands[0]
            s = '''\n        if command == Commands.{}:
            self.{}_task()'''.format(cmd, cmd.lower())
            f.write(s)
            for i in range(1, len(self.commands)):
                cmd = self.commands[i]
                s = '''\n        elif command == Commands.{}:\n            self.{}_task()'''.format(cmd, cmd.lower())
                f.write(s)

            for cmd in self.commands:
                self.generate_task(cmd, f)


    def generate_task(self, cmd_str, f:TextIO):
        s = "\n\n    def {}_task(self):\n".format(cmd_str.lower())
        f.write(s)
        no_child_tasks = True
        child_hm:HierarchyModule
        state_num = 0
        for child_hm in self.children:
            s = "        {} = self.ddict.get_entry('{}').data\n".format(child_hm.cmd_obj_name, child_hm.cmd_obj_name)
            f.write(s)
            s = "        {} = self.ddict.get_entry('{}').data\n".format(child_hm.rsp_obj_name, child_hm.rsp_obj_name)
            f.write(s)

        s = '''        if self.cur_state == States.NEW_COMMAND:
            print("{}:{} NEW_COMMAND ")
            self.cur_state = States.S{}
            self.rsp.set(Responses.EXECUTING, self.cmd.serial)\n'''.format(self.name, cmd_str, state_num)
        f.write(s)
        cur_child:HierarchyModule
        next_child:HierarchyModule
        for i in range(len(self.children)):
            cur_child = self.children[i]
            if cmd_str in cur_child.commands:
                s = "            {}.set(Commands.{}, {}.next_serial()+1)\n".format(cur_child.cmd_obj_name, cmd_str, cur_child.cmd_obj_name)
                f.write(s)
                s = "        elif self.cur_state == States.S{} and {}.test(Responses.DONE):\n".format(state_num, cur_child.rsp_obj_name)
                f.write(s)
                state_num += 1
                s = "            self.cur_state = States.S{}\n".format(state_num)
                f.write(s)
        s = "        elif self.cur_state == States.S{}:\n".format(state_num)
        f.write(s)
        state_num += 1
        s = '''            print("{}:DONE")\n            self.cur_state = States.S{}\n            self.rsp.set(Responses.DONE)\n'''.format(self.name, state_num)
        f.write(s)

    def to_string(self) -> str:
        s = "name = {}\n\tquantity = {} of {}\n\tparent = {}\n\tcommands = {}".format(self.name, self.index+1, self.quantity, self.parent, self.commands)
        if len(self.children) > 0:
            s += "\n\tchildren:"
            hm:HierarchyModule
            for hm in self.children:
                s += "\n\t\t{}".format(hm.name)
        return s



class HierarchyGenerator:
    hierarchy_dict:Dict

    module_list:List
    system_name:str
    bdmon:str
    data_dir:str
    code_dir:str
    code_prefix:str
    logfile:str
    spreadsheet:str
    log_step:int
    module_list:List
    hmodule_list:List

    def __init__(self):
        print("HierarchyGenerator")
        self.hmodule_list = []
        self.hierarchy_dict = {}

    def read_config_file(self, filename:str):
        print("loading{}".format(filename))
        with open(filename) as f:
            self.hierarchy_dict = json.load(f)
            print(json.dumps(self.hierarchy_dict, indent=4, sort_keys=True))
            self.__dict__.update(self.hierarchy_dict)
            #load the modules
            hm:HierarchyModule
            d:Dict
            for d in self.module_list:
                hm = HierarchyModule(d)
                self.hmodule_list.append(hm)
                # TODO: Also check to see if the parent has a quantity over 1. We need to do combinatorials
                if hm.quantity > 1:
                    for i in range(1, hm.quantity):
                        d2 = d.copy()
                        d2['name'] = "{}_{}".format(d['name'], i)
                        d2['classname'] = "{}_{}".format(d['classname'], i)
                        d2['index'] = i
                        hm2 = HierarchyModule(d2)
                        self.hmodule_list.append(hm2)

            for hm in self.hmodule_list:
                hm.find_children(self.hmodule_list)
                print(hm.to_string())

    def find_modules_by_parent_name(self, name:str) -> List[HierarchyModule]:
        l = []
        hm:HierarchyModule
        for hm in self.hmodule_list:
            if hm.parent == name:
                l.append(hm)
        return l

    def find_module_by_child_name(self, name:str) -> Union[None, HierarchyModule]:
        hm:HierarchyModule
        for hm in self.hmodule_list:
            if hm.has_child(name):
                return hm
        return None


    def generate_code(self):
        cwd = os.getcwd()
        os.chdir(self.code_dir)

        # remove previous files
        files = glob.glob('./*')
        fname:str
        for fname in files:
            if fname.endswith(".py"):
                os.remove(fname)

        # gen bdmon
        hm_child:HierarchyModule
        f:TextIO
        top_command_dict = {}
        with open('bd_mon.py', 'w') as f:
            f.write(CodeSlugs.imports)
            for hm_child in self.hmodule_list:
                f.write("from {}{} import {}\n".format(self.code_prefix, hm_child.classname, hm_child.classname))

            f.write(CodeSlugs.bdmon_head)

            # set up communication between modules TODO - make this a method
            # start with "board-monitor"
            # parent_name = 'board_monitor'
            # hm_child_list = self.find_modules_by_parent_name(parent_name)
            # for hm_child in hm_child_list:
            for hm_child in self.hmodule_list:
                parent_name = hm_child.parent
                child_name = hm_child.name
                hm_child.cmd_obj_name = 'CMD_{}_to_{}'.format(parent_name, child_name)
                s = '    {} = CommandObject("{}", "{}")\n'.format(hm_child.cmd_obj_name, parent_name, hm_child.name)
                f.write(s)

                hm_child.rsp_obj_name = 'RSP_{}_to_{}'.format(child_name, parent_name)
                s = '    {} = ResponseObject("{}", "{}")\n'.format(hm_child.rsp_obj_name, parent_name, hm_child.name)
                f.write(s)

                s = '    {} = {}("{}", ddict)\n'.format(hm_child.name, hm_child.classname, hm_child.name)
                s += '    {}.set_cmd_obj({})\n'.format(hm_child.name, hm_child.cmd_obj_name)
                s += '    {}.set_rsp_obj({})\n\n'.format(hm_child.name, hm_child.rsp_obj_name)
                f.write(s)

                if parent_name == 'board_monitor':
                    top_command_dict = {'name': hm_child.cmd_obj_name, 'child_name':child_name,
                                        'cmd': hm_child.commands[0], 'hmodule':hm_child,
                                        'cmd_obj_name':hm_child.cmd_obj_name, 'rsp_obj_name':hm_child.rsp_obj_name}

            f.write("\n    # Link the modules")
            for hm_child in self.hmodule_list:
                if parent_name != 'board_monitor':
                    s = "    BaseController.link_parent_child({}, {}, ddict)\n".format(hm_child.parent, hm_child.name)
                    f.write(s)

            # set up loop
            hm:HierarchyModule
            s = CodeSlugs.bdmon_loop.format(top_command_dict['name'], top_command_dict['cmd'], self.log_step, self.log_step)
            f.write(s)
            hm:HierarchyModule
            f.write("\n")
            for hm in self.hmodule_list:
                f.write("        {}.step()\n".format(hm.name))

            hm = top_command_dict['hmodule']
            # gp through all the commands that the top controller takes
            for i in range(len(hm.commands)-1):
                cur_cmd =  hm.commands[i]
                next_cmd = hm.commands[i+1]
                conditional = "if"
                if i > 0:
                    conditional = "elif"
                s = "        {} {}.test(Commands.{}) and {}.test(Responses.DONE):\n".format(conditional, top_command_dict['cmd_obj_name'], cur_cmd, top_command_dict['rsp_obj_name'])
                f.write(s)
                s = "            {}.set(Commands.{}, {})\n".format(top_command_dict['cmd_obj_name'], next_cmd, i+2)
                f.write(s)

            f.write(CodeSlugs.bdmon_tail.format(top_command_dict['child_name']))

        # gen modules
        for hm_child in self.hmodule_list:
            hm_child.generate_code()
        os.chdir(cwd)


def main():
    print(os.getcwd())
    hg = HierarchyGenerator();
    hg.read_config_file("../nn_ext/hierarchy.json")
    hg.generate_code()

if __name__ == "__main__":
    main()