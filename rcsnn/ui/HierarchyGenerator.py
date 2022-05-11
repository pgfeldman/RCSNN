import io
import json
import os
import glob
from pathlib import Path
from typing import List, Dict, Union, TextIO

class CodeSlugs:
    imports = '''from rcsnn.base.DataDictionary import DataDictionary, DictionaryTypes, DictionaryEntry
from rcsnn.base.BaseBoardMonitor import BaseBoardMonitor
from rcsnn.base.CommandObject import CommandObject
from rcsnn.base.Commands import Commands
from rcsnn.base.ResponseObject import ResponseObject
from rcsnn.base.Responses import Responses
from rcsnn.base.States import States
from rcsnn.base.BaseController import BaseController\n\n'''

    module_head = '''

class {}({}):

    def __init__(self, name: str, ddict: DataDictionary):
        super().__init__(name, ddict)'''

    decision = '''\n\n    def decision_process(self):
        command = self.evaluate_cmd()'''


    bdmon_main = '''
def main():
    """
    Exercise the class in a toy hierarchy that initializes, runs, and terminates. The hierarchy is controlled from the
    main loop and has two controllers, a "parent" and a "child"
    """
    bdmon = {}()
    bdmon.setup()
    bdmon.start()
    done = False
    while not done:
        done = bdmon.step()
        
    bdmon.terminate()
    
if __name__ == "__main__":
    main()
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
    layer:int
    child_id:int
    name: str
    classname: str
    parent: str
    children:List["HierarchyModule"]
    commands:List
    cmd_obj_name:str
    rsp_obj_name:str
    code_prefix:str

    def __init__(self, d:Dict):
        self.quantity = 1 #default
        self.index = 0 #default
        self.children = []
        child_id = -1
        layer = -1
        self.__dict__.update(d)

    def find_children(self, hm_list:List):
        hm:HierarchyModule
        for hm in hm_list:
            if hm != self:
                if self.name == hm.parent:
                    self.children.append(hm)

    def set_layer_info(self, layer:int, child_id):
        self.layer = layer
        self.child_id = child_id

    def get_max_child_id(self) -> int:
        if len(self.children) == 0:
            return self.child_id
        hm:HierarchyModule

        val = self.child_id
        for hm in self.children:
            val = max(val, hm.get_max_child_id())
        return val

    def get_min_child_id(self) -> int:
        if len(self.children) == 0:
            return 0
        hm:HierarchyModule

        val = self.children[0].child_id
        for i in range(1, len(self.children)):
            hm = self.children[i]
            val = min(val, hm.child_id)
        return val

    def has_child(self, name:str):
        hm:HierarchyModule
        for hm in self.children:
            if hm.name == name:
                return hm
        return None

    def get_child_class(self) -> str:
        childclass = "{}Child".format(self.classname)
        return childclass

    def generate_code(self):
        filename = "./generated/{}.py".format(self.classname)
        if Path(filename).is_file():
            os.remove(filename)
        with open(filename, 'w') as f:
            f.write(CodeSlugs.imports)
            f.write(CodeSlugs.module_head.format(self.classname, 'BaseController'))

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

        filename = "{}.py".format(self.get_child_class())
        if not Path(filename).is_file():
            with open(filename, 'w') as f:
                f.write(CodeSlugs.imports)
                f.write("from {}generated.{} import {}\n".format(self.code_prefix, self.classname, self.classname))
                f.write(CodeSlugs.module_head.format(self.get_child_class(), self.classname))


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
        s = "name = {}\n\tquantity = {} of {}\n\tparent = {}\n\tcommands = {}\n\tlayer = {}, child id = {}".format(
            self.name, self.index+1, self.quantity, self.parent, self.commands, self.layer, self.child_id)
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
        self.reset()

    def reset(self):
        self.hmodule_list = []
        self.hierarchy_dict = {}

    def config_from_dict(self, d:Dict):
        self.hierarchy_dict = d
        print(json.dumps(self.hierarchy_dict, indent=4, sort_keys=True))
        self.__dict__.update(self.hierarchy_dict)
        #load the modules
        hm:HierarchyModule
        d:Dict
        for d in self.module_list:
            hm = HierarchyModule(d)
            hm.code_prefix = self.code_prefix
            self.hmodule_list.append(hm)
            # TODO: Also check to see if the parent has a quantity over 1. We need to do combinatorials
            if hm.quantity > 1:
                for i in range(1, hm.quantity):
                    d2 = d.copy()
                    d2['name'] = "{}_{}".format(d['name'], i)
                    d2['classname'] = "{}_{}".format(d['classname'], i)
                    d2['index'] = i
                    hm2 = HierarchyModule(d2)
                    hm2.code_prefix = self.code_prefix
                    self.hmodule_list.append(hm2)

        for hm in self.hmodule_list:
            hm.find_children(self.hmodule_list)

        # Get the tree relationships
        parent_list = ['board_monitor']
        self.recurse_layer_index(parent_list)

    def recurse_layer_index(self, parent_list:List, layer:int = 0):
        hm:HierarchyModule
        child_list = []

        child_index = 0
        for parent_name in parent_list:
            for hm in self.hmodule_list:
                if hm.parent == parent_name:
                    child_list.append(hm.name)
                    hm.set_layer_info(layer, child_index)
                    child_index += 1

        layer += 1
        if len(child_list) > 0:
            self.recurse_layer_index(child_list, layer)


    def read_config_file(self, filename:str):
        print("loading{}".format(filename))
        with open(filename) as f:
            d = json.load(f)
            self.config_from_dict(d)

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

    def gen_bdmon_class_code(self, f:TextIO):
        # write the class version of this
        f.write("\nclass BoardMonitor(BaseBoardMonitor):\n")
        # f.write("    current_step : int\n")
        # f.write("    name = 'BoardMonitor'\n")
        # f.write("    ddict : DataDictionary\n")
        # f.write("    elapsed_time_entry : DictionaryEntry\n")

        hm_child:HierarchyModule
        for hm_child in self.hmodule_list:
            parent_name = hm_child.parent
            child_name = hm_child.name
            hm_child.cmd_obj_name = 'CMD_{}_to_{}'.format(parent_name, child_name)
            s = '    {} : CommandObject\n'.format(hm_child.cmd_obj_name)
            f.write(s)

            hm_child.rsp_obj_name = 'RSP_{}_to_{}'.format(child_name, parent_name)
            s = '    {} : ResponseObject\n'.format(hm_child.rsp_obj_name)
            f.write(s)

            s = '    {} : {}\n'.format(hm_child.name, hm_child.get_child_class())
            f.write(s)

        f.write("\n    def setup(self):\n")
        f.write("        super().setup()\n")
        f.write("        self.name = 'BoardMonitor'\n")
        # f.write('        self.elapsed_time_entry = DictionaryEntry("elapsed-time", DictionaryTypes.FLOAT, 0)\n')
        # f.write('        self.ddict.add_entry(self.elapsed_time_entry)\n')

        top_command_dict = {}
        for hm_child in self.hmodule_list:
            parent_name = hm_child.parent
            child_name = hm_child.name
            hm_child.cmd_obj_name = 'CMD_{}_to_{}'.format(parent_name, child_name)
            s = '        self.{} = CommandObject("{}", "{}")\n'.format(hm_child.cmd_obj_name, parent_name, hm_child.name)
            f.write(s)

            hm_child.rsp_obj_name = 'RSP_{}_to_{}'.format(child_name, parent_name)
            s = '        self.{} = ResponseObject("{}", "{}")\n'.format(hm_child.rsp_obj_name, parent_name, hm_child.name)
            f.write(s)

            s = '        self.{} = {}("{}", self.ddict)\n'.format(hm_child.name, hm_child.get_child_class(), hm_child.name)
            s += '        self.{}.set_cmd_obj(self.{})\n'.format(hm_child.name, hm_child.cmd_obj_name)
            s += '        self.{}.set_rsp_obj(self.{})\n\n'.format(hm_child.name, hm_child.rsp_obj_name)
            f.write(s)

            if parent_name == 'board_monitor':
                top_command_dict = {'name': hm_child.cmd_obj_name, 'child_name':child_name,
                                    'cmd': hm_child.commands[0], 'hmodule':hm_child,
                                    'cmd_obj_name':hm_child.cmd_obj_name, 'rsp_obj_name':hm_child.rsp_obj_name}

        f.write("\n        # Link the modules\n")
        for hm_child in self.hmodule_list:
            if hm_child.parent != 'board_monitor':
                s = "        BaseController.link_parent_child(self.{}, self.{}, self.ddict)\n".format(hm_child.parent, hm_child.name)
                f.write(s)

        f.write("\n    def start(self):\n")
        f.write("        super().start()\n")
        s = "        self.{}.set(Commands.{}, 1)\n".format(top_command_dict['name'], top_command_dict['cmd'])
        f.write(s)


        f.write("\n    def step(self) -> bool:\n")
        f.write("        super().step()\n")
        f.write('        self.ddict.log_to_csv("testlog.csv", 1)\n')
        hm:HierarchyModule
        f.write("\n")
        for hm in self.hmodule_list:
            f.write("        self.{}.step()\n".format(hm.name))

        f.write("        done = self.decision_process()\n")

        f.write('        self.current_step += 1\n')
        end_slug = '''        # for debugging
        if self.current_step == 100:
            done = True
        return done
            '''
        f.write(end_slug)

        f.write("\n    def decision_process(self) -> bool:\n")
        f.write("        done = False\n")
        hm = top_command_dict['hmodule']
        # gp through all the commands that the top controller takes
        for i in range(len(hm.commands)-1):
            cur_cmd =  hm.commands[i]
            next_cmd = hm.commands[i+1]
            conditional = "if"
            if i > 0:
                conditional = "elif"
            s = "        {} self.{}.test(Commands.{}) and self.{}.test(Responses.DONE):\n".format(conditional, top_command_dict['cmd_obj_name'], cur_cmd, top_command_dict['rsp_obj_name'])
            f.write(s)
            s = "            self.{}.set(Commands.{}, {})\n".format(top_command_dict['cmd_obj_name'], next_cmd, i+2)
            f.write(s)
        f.write('            done = True\n')
        f.write('        return(done)\n')

        f.write("\n    def terminate(self):\n")
        s = '        self.ddict.to_excel("../../data/", "{}.xlsx")\n'.format(top_command_dict['child_name'])
        f.write(s)


    def generate_code(self):
        cwd = os.getcwd()
        os.chdir(self.code_dir)
        if not Path('./generated').is_dir():
            os.mkdir('./generated')

        # gen bdmon
        if Path('./generated/BoardMonitor.py').is_file():
            os.remove('./generated/BoardMonitor.py')
        hm_child:HierarchyModule
        f:TextIO
        with open('./generated/BoardMonitor.py', 'w') as f:
            f.write(CodeSlugs.imports)
            for hm_child in self.hmodule_list:
                # f.write("from {}{} import {}\n".format(self.code_prefix, hm_child.classname, hm_child.classname))
                f.write("from {}{} import {}\n".format(self.code_prefix, hm_child.get_child_class(), hm_child.get_child_class()))
            self.gen_bdmon_class_code(f)
            f.write(CodeSlugs.bdmon_main.format("BoardMonitor"))

        # gen bdmon child
        s = '''\nclass BoardMonitorChild(BoardMonitor):

    def __init__(self):
        super().__init__()
        self.name = "BoardMonitorChild"\n'''
        if Path('BoardMonitorChild.py').is_file():
            os.remove('BoardMonitorChild.py')
        hm_child:HierarchyModule
        f:TextIO
        with open('BoardMonitorChild.py', 'w') as f:
            f.write(CodeSlugs.imports)
            for hm_child in self.hmodule_list:
                # f.write("from {}{} import {}\n".format(self.code_prefix, hm_child.classname, hm_child.classname))
                f.write("from {}{} import {}\n".format(self.code_prefix, hm_child.get_child_class(), hm_child.get_child_class()))
            f.write("from {}generated.BoardMonitor import BoardMonitor\n".format(self.code_prefix))
            f.write(s)
            f.write(CodeSlugs.bdmon_main.format("BoardMonitorChild"))

        # gen modules
        for hm_child in self.hmodule_list:
            hm_child.generate_code()
        os.chdir(cwd)

    def to_string(self):
        hm:HierarchyModule
        for hm in self.hmodule_list:
            print(hm.to_string())


def main():
    print(os.getcwd())
    hg = HierarchyGenerator()
    hg.read_config_file("../nn_ext/hierarchy.json")

    #hg.generate_code()
    hg.to_string()

if __name__ == "__main__":
    main()