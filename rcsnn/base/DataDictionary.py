import os
import sys
from enum import Enum
import time
import numpy as np
import pandas as pd
from typing import Any, List, Dict


class DictionaryTypes(Enum):
    UNSET = "unset"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    LIST = "list"
    COMMAND = "cmd"
    RESPONSE = "rsp"


class DictionaryEntry:
    type:DictionaryTypes = None
    name:str = "unset"
    master:bool = True  # or slave if from another dictionary
    data:Any = None
    data_list:List = []

    def __init__(self, name: str, type: DictionaryTypes, data=None, master: bool = True):
        print("DataDictionary: adding name='{}' type = '{}'".format(name, type))
        self.reset()
        self.type = type
        self.name = name
        self.data = data

    def reset(self):
        self.type = None
        self.name = "unset"
        self.data = None
        self.data_list = []

    def set_data(self, data):
        self.data = data

    def get_data(self):
        if self.type == DictionaryTypes.COMMAND:
            return self.data.cmd.name
        elif self.type == DictionaryTypes.RESPONSE:
            return self.data.rsp.name
        elif self.type == DictionaryTypes.FLOAT:
            #return "{:.3f}".format(self.data)
            return self.data
        else:
            return self.data

    def get_type(self) -> str:
        return self.type

    def store(self):
        if self.type == DictionaryTypes.COMMAND:
            n = self.data.cmd.name
            self.data_list.append(n)
        elif self.type == DictionaryTypes.RESPONSE:
            n = self.data.rsp.name
            self.data_list.append(n)
        else:
            self.data_list.append(self.data)

    def to_string(self) -> str:
        return "{} (type = {}): current = {}, history{}".format(self.name, self.get_type(), self.get_data(),
                                                                self.data_list)

    def to_dict(self) -> Dict:
        return {"name":self.name, "type":self.get_type().name, "current":self.get_data()}



class DataDictionary:
    ddict:Dict
    count:int
    store_count:int
    log_line:int

    def __init__(self):
        self.reset()

    def reset(self):
        self.ddict = {}
        self.count = 0
        self.store_count = 0
        self.log_line = 0

    def add_entry(self, de: DictionaryEntry) -> bool:
        if de.name in self.ddict:
            print("-------- ERROR -------- DataDictionary.add_entry() Duplicate definition of {}".format(de.name))
            sys.exit(-1)
            #return False
        self.ddict[de.name] = de
        return True

    def set_entries_from_dict(self, dict_list:List):
        entry:Dict
        for entry in dict_list:
            self.set_entry_from_dict(entry)

    def set_entry_from_dict(self, d:Dict) -> bool:
        name:str
        type_name:str
        current:str
        try:
            name = d['name']
            type_name = d['type']
            current = d['current']
        except KeyError:
            print("DataDictionary.set_entry_from_dict(): KeyError with {}".format(d))
            return False

        if name in self.ddict:
            e = self.get_entry(name)
            e.set_data(current)
        else:
            dt:Enum
            for dt in DictionaryTypes:
                if type_name == dt.name:
                    type = dt
                    de = DictionaryEntry(name, type, current)
                    for i in range(self.store_count):
                        de.store()
                    self.ddict[name] = de
                    return True
        return False

    def remove_entry(self, name: str) -> bool:
        if name in self.ddict:
            del self.ddict[name]
            return True
        return False

    def get_entry(self, name: str) -> DictionaryEntry:
        if name in self.ddict:
            return self.ddict[name]
        else:
            print("DataDictionary.get_entry(): No entry named '{}'".format(name))
        return None

    def has_entry(self, name:str):
        if name in self.ddict:
            return True
        return False

    def safe_get_entry_val(self, name:str, default:Any) -> Any:
        if self.has_entry(name):
            val = self.get_entry(name).data
            return val
        return default

    def store(self, skip: int = 10):
        self.count += 1
        if (self.count % skip) == 0:
            self.store_count += 1
            for entry in self.ddict.values():
                entry.store()

    def setup_influx(self, url:str=None, token:str=None, org:str=None, bucket:str=None):
        self.influx_writer.setup_client(url, token, org, bucket)

    def tear_down_influx(self):
        self.influx_writer.tear_down_client()

    def stream(self, t:float= None):
        if t == None:
            t = time.time()
        key:str
        val:DictionaryEntry
        for key, val in self.ddict.items():
            # write_point(self, t:float, name:str, val:Any, tags: Dict = {}):
            self.influx_writer.write_point(t, key, val.get_data())
            #print ("({}:{})  ".format(key, val.get_data()))

    def log_to_csv(self, filename, skip:int = 1):
        key:str
        val:DictionaryEntry
        with open(filename, mode="a") as f:
            if self.log_line == 0: # write headers
                f.truncate(0) # clear the file
                f.write("log_line, ")
                for key, val in self.ddict.items():
                    t = val.get_type()
                    if t == DictionaryTypes.LIST:
                        l:List
                        l = val.get_data()
                        for i in range(len(l)):
                            f.write("{}_{}, ".format(key, i))
                    else:
                        f.write("{}, ".format(key))
                f.write("\n")
            if (self.log_line % skip) == 0:
                f.write("{}, ".format(self.log_line))
                for key, val in self.ddict.items():
                    t = val.get_type()
                    if t == DictionaryTypes.LIST:
                        l = val.get_data()
                        for v in l:
                            f.write("{}, ".format(v))
                    else:
                        f.write("{}, ".format(val.get_data()))
                f.write("\n")
            self.log_line += 1

    def to_excel(self, pathname: str, filename: str):
        index_list = []
        rows = []
        num_rows = len(self.ddict)
        max_cols = 0
        for key, val in self.ddict.items():
            index_list.append(key)
            rows.append(val.data_list)
            max_cols = max(max_cols, len(val.data_list))
        empty = np.zeros((num_rows, max_cols))
        df = pd.DataFrame(rows, index_list)
        cur_dir = os.getcwd()
        os.chdir(pathname)
        writer = pd.ExcelWriter(filename)
        df.to_excel(writer)
        writer.save()
        os.chdir(cur_dir)

    def to_string(self) -> str:
        to_return = ""
        for key, val in self.ddict.items():
            to_return += "{}\n".format(val.to_string())
        return to_return

    def to_short_string(self) -> str:
        to_return = ""
        for key, val in self.ddict.items():
            to_return += "({}:{})  ".format(key, val.get_data())
        return to_return

    def to_dict_array(self) -> List:
        to_return = []
        val:DictionaryEntry
        for key, val in self.ddict.items():
            to_return.append(val.to_dict())
        return to_return


if __name__ == "__main__":
    ddict = DataDictionary()

    ddict.add_entry(DictionaryEntry("test_int", DictionaryTypes.INT, 1))
    ddict.add_entry(DictionaryEntry("test_float", DictionaryTypes.FLOAT, 3.141592))
    ddict.add_entry(DictionaryEntry("test_string", DictionaryTypes.STRING, "Hello, world"))
    ddict.add_entry(DictionaryEntry("test_list", DictionaryTypes.LIST, [1, 2, 3, 4, 5]))

    for i in range(1, 10):
        print("adding data i = {}".format(i))
        ddict.get_entry("test_int").data = i
        ddict.get_entry("test_float").data = i+i/10
        ddict.get_entry("test_string").data = "str_{}".format(i)
        l = []
        l.extend(range(i, i+10))
        ddict.get_entry("test_list").data = l

        ddict.store(1)
        ddict.log_to_csv("testlog.csv", 2)
        # ddict.stream()
        time.sleep(1)

    print(ddict.to_string())
    # ddict.tear_down_influx()

    print ("Adding another 'test_string' to force an exit")
    ddict.add_entry(DictionaryEntry("test_string", DictionaryTypes.STRING, "Hello, world"))