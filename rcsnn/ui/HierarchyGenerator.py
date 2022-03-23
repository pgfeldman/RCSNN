import json
import os
import glob
from typing import List, Dict

class CodeSlugs:
    imports = '''from rcsnn.nn_ext.CruiserController import CruiserController
from rcsnn.nn_ext.MissileController import MissileController
from rcsnn.nn_ext.NavigateController import NavigateController
from rcsnn.base.DataDictionary import DataDictionary, DictionaryTypes, DictionaryEntry
from rcsnn.base.CommandObject import CommandObject
from rcsnn.base.Commands import Commands
from rcsnn.base.ResponseObject import ResponseObject
from rcsnn.base.Responses import Responses
from rcsnn.base.BaseController import BaseController'''

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

class HierarchyModule:
    quantity: int
    index: int
    name: str
    classname: str
    parent: str
    children:List
    commands:List

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
                s = "\n\n    def {}_task(self):\n        pass".format(cmd.lower())
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

    def generate_code(self):
        cwd = os.getcwd()
        os.chdir(self.code_dir)

        # remove previous files
        files = glob.glob('./*')
        f:str
        for f in files:
            if f.endswith(".py"):
                os.remove(f)
        # gen bdmon
        with open('bd_mon.py', 'w') as f:
            f.write(CodeSlugs.imports)
            f.write(CodeSlugs.bdmon_head)

        # gen modules
        hm:HierarchyModule
        for hm in self.hmodule_list:
            hm.generate_code()
        os.chdir(cwd)


def main():
    print(os.getcwd())
    hg = HierarchyGenerator();
    hg.read_config_file("../nn_ext/hierarchy.json")
    hg.generate_code()

if __name__ == "__main__":
    main()