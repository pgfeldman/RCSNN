import json
import os
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
    name: str
    classname: str
    parent: str
    commands:List

    def __init__(self, d:Dict):
        self.quantity = 1 #default
        self.__dict__.update(d)

    def get_classnames(self) -> List:
        l = [self.classname]
        for i in range(1, self.quantity):
            l.append("{}_{}".format(self.classname, i))
        return l

    def to_string(self) -> str:
        return "name = {}\n\tquantity = {}\n\tparent = {}\n\tcommands = {}".format(self.name, self.quantity, self.parent, self.commands)


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
            d:Dict
            for d in self.module_list:
                hm = HierarchyModule(d)
                print(hm.to_string())
                self.hmodule_list.append(hm)

    def generate_code(self):
        cwd = os.getcwd()
        os.chdir(self.code_dir)
        # gen bdmon
        with open('bd_mon.py', 'w') as f:
            f.write(CodeSlugs.imports)
            f.write(CodeSlugs.bdmon_head)

        # gen modules
        hm:HierarchyModule
        for hm in self.hmodule_list:
            for classname in hm.get_classnames():
                filename = "{}.py".format(classname)
                with open(filename, 'w') as f:
                    f.write(CodeSlugs.imports)
                    f.write(CodeSlugs.module_head.format(classname))
        os.chdir(cwd)


def main():
    print(os.getcwd())
    hg = HierarchyGenerator();
    hg.read_config_file("../nn_ext/hierarchy.json")
    hg.generate_code()

if __name__ == "__main__":
    main()