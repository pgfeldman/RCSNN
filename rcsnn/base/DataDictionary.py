import os
import sys
from enum import Enum
import time
import numpy as np
import pandas as pd
from typing import Any, List, Dict, Union


class DictionaryTypes(Enum):
    UNSET = "unset"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    LIST = "list"
    COMMAND = "cmd"
    RESPONSE = "rsp"


class DictionaryEntry:
    '''
    The DictionaryEntry class creates a data entry that all controllers use to communicate and current and historical
    data.

    Attributes
    ----------
    type:DictionaryTypes
        The type of data this is. Can be a simple type like and INT or a FLOAT, or something more complex like COMMAND or RESPONSE
    name:str
        The name of this value
    master:bool
        A flag that indicates if this value comes from another dictionary. If it does, we sync to the master whenever possible
    data:Any
        The data stored in this entry
    data_list:List
        A list of historical values. May be a sampling of the values to save space

    Methods
    -------
    reset(self):
        Resets all the global values for this Base class
    set_data(self, data):
        Sets the current data value
    get_data(self) -> Any:
        Returns the current value. If it's a COMMAND or RESPONSE, return the string value
    get_type(self) -> DictionaryTypes:
        Returns the type of this entry
    store(self):
        Saves the current value. If it's a COMMAND or RESPONSE, return the string value
    to_string(self, num_history:int=10) -> str:
        Returns a string with the name, type, value, and last n values from the history
    to_dict(self) -> Dict:
        Returns a Dict with the name, type, and current value
    '''
    type:DictionaryTypes
    name:str
    master:bool  # or slave if from another dictionary
    data:Any
    data_list:List

    def __init__(self, name:str, type:DictionaryTypes, data:Any=None, master: bool = True):
        """Constructor: Sets up the basic components of the class

        Parameters
        ----------
        name: str
            The name of the class
        type: DictionaryType
            The type of data this is. Can be a simple type like and INT or a FLOAT, or something more complex like COMMAND or RESPONSE
        data:Any
            The data stored in this entry
        master:bool
            A flag that indicates if this value comes from another dictionary. If it does, we sync to the master whenever possible
        """
        print("DataDictionary: adding name='{}' type = '{}'".format(name, type))
        self.reset()
        self.type = type
        self.name = name
        self.data = data
        self.master = master
        self.data_list = []
        if data != None:
            self.store() # store the first entry

    def reset(self):
        """ Resets all the global values for this class

        Parameters
        ----------
        :return:
        """
        self.type = None
        self.name = "unset"
        self.data = None
        self.data_list = []

    def set_data(self, data:Any):
        """ Sets the current data value

        Parameters
        ----------
        data: The current value for this entry
        :return:
        """
        self.data = data

    def get_data(self) -> Any:
        """ Gets the current data value

        Parameters
        ----------

        :return: The current value for this entry
        """
        if self.type == DictionaryTypes.COMMAND:
            return self.data.cmd#.name
        elif self.type == DictionaryTypes.RESPONSE:
            return self.data.rsp#.name
        else:
            return self.data

    def get_type(self) -> DictionaryTypes:
        """ Gets the type for this entry

        Parameters
        ----------

        :return: The DictionaryTypes value for this entry
        """
        return self.type

    def store(self):
        """ Stores the current data value

        Parameters
        ----------
        :return:
        """
        if self.type == DictionaryTypes.COMMAND:
            n = self.data.cmd#.name
            self.data_list.append(n)
        elif self.type == DictionaryTypes.RESPONSE:
            n = self.data.rsp#.name
            self.data_list.append(n)
        else:
            self.data_list.append(self.data)

    def to_string(self, num_history:int=10) -> str:
        """ Returns a string with the name, type, value, and last n values from the history

        Parameters
        ----------
        num_history:int=10
            How many values of history to show
        :return: The string describing this this entry
        """
        return "{} (type = {}): current = {}, history{}".format(self.name, self.get_type(), self.get_data(),
                                                                self.data_list[num_history:])

    def to_dict(self) -> Dict:
        """ Returns a Dict with the name, type, and current value

        Parameters
        ----------

        :return: The Dict for this entry
        """
        return {"name":self.name, "type":self.get_type().name, "current":self.get_data()}



class DataDictionary:
    '''
    The DictionaryEntry class creates a data entry that all controllers use to communicate and current and historical
    data.

    Attributes
    ----------
    ddict:Dict
        The Dict that contains all the entries
    count:int
        The times that self.store() has been called, which should be once per main loop
    store_count:int
        The number of items that have been stored which can be up to count
    log_line:int
        The line in the log output. If it is zero, then write headers

    Methods
    -------
    reset(self):
        Resets all the global values for this Base class
    add_entry(self, de: DictionaryEntry):
        Adds a DictionaryEntry to the dictionary using the DictionaryEntry's name as the key. If the key already exists
        in the ddict, throw a ValueError
    set_entries_from_dict(self, dict_list:List):
        Set a batch of entrise from a List of Dicts. Useful for loading from a file
    set_entry_from_dict(self, d:Dict) -> bool:
        Set a single entry from a Dict
    remove_entry(self, name: str) -> bool:
        Delete the entry from the ddict. If successful return True, otherwise False
    get_entry(self, name: str) -> DictionaryEntry:
        Get a DictionaryEntry based on the key. If no entry return None
    has_entry(self, name:str) -> bool:
        Check to see if the key exists in the ddict. Return True if so, otherwise False
    safe_get_entry_val(self, name:str, default:Any) -> Any:
        Returns a value associated with the key. If none, then the default value is returned
    store(self, skip: int = 10):
        If the count % skip, then store values in item's histories.
    log_to_csv(self, filename, skip:int = 1):
        Generate a file with all the stored data in csv format
    to_excel(self, pathname: str, filename: str):
        Generate a file with all the stored data in excel format
    to_string(self) -> str:
        Generate a (big!) string using the default to_string() behavior for DictionaryEntrys
    to_short_string(self) -> str:
        Generate a smaller string with just the current values of the items in the ddict
    to_dict_array(self) -> List:
        Create a list of Dicts that can be saved out as a file and loaded in using set_entries_from_dict()
    '''
    ddict:Dict
    count:int
    store_count:int
    log_line:int

    def __init__(self):
        """Constructor: Sets up the basic components of the class

        Parameters
        ----------

        """
        self.reset()

    def reset(self):
        """ Resets all the global values for this  class

        Parameters
        ----------
        :return:
        """
        self.ddict = {}
        self.count = 0
        self.store_count = 0
        self.log_line = 0

    def add_entry(self, de: DictionaryEntry):
        """ Adds a DictionaryEntry to the dictionary using the DictionaryEntry's name as the key.
        If the key already exists, throw a ValueError

        Parameters
        ----------
        de: DictionaryEntry
            The entry to add
        :return:
        """
        if de.name in self.ddict:
            raise ValueError("-------- ERROR -------- DataDictionary.add_entry() Duplicate definition of {}".format(de.name))
        self.ddict[de.name] = de

    def set_entries_from_dict(self, dict_list:List):
        """ set a batch of entrise from a List of Dicts. Useful for loading from a file. Entries are in the form of:
        [{'name': 'test_int', 'type': 'INT', 'current': 20}, {'name': 'test_float', 'type': 'FLOAT', 'current': 22.0}]

        Parameters
        ----------
        dict_list:List
            An array of Dicts
        :return:
        """
        entry:Dict
        for entry in dict_list:
            self.set_entry_from_dict(entry)

    def set_entry_from_dict(self, d:Dict) -> bool:
        """ set an entry from a Dict. Useful for loading from a file. Entries are in the form of:
        {'name': 'test_int', 'type': 'INT', 'current': 20}

        Parameters
        ----------
        dict_list:List
            An array of Dicts
        :return: True if successful
        """
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
            type:DictionaryTypes
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
        """ Delete the entry from the ddict. If successful return True, otherwise False

        Parameters
        ----------
        name: str
            The key value to search the ddict for
        :return: True if successful
        """
        if name in self.ddict:
            del self.ddict[name]
            return True
        return False

    def get_entry(self, name: str) -> DictionaryEntry:
        """ Get a DictionaryEntry based on the key. If no entry return None

        Parameters
        ----------
        name: str
            The key value to search the ddict for
        :return: DictionaryEntry based on the key. If no entry return None
        """
        if name in self.ddict:
            return self.ddict[name]
        else:
            print("DataDictionary.get_entry(): No entry named '{}'".format(name))
        return None

    def has_entry(self, name:str) -> bool:
        """ Check to see if the key exists in the ddict. Return True if so, otherwise False

        Parameters
        ----------
        name: str
            The key value to search the ddict for
        :return: Return True if entry exists, otherwise False
        """
        if name in self.ddict:
            return True
        return False

    def safe_get_entry_val(self, name:str, default:Any) -> Any:
        """ Returns a value associated with the key. If none, then the default value is returned

        Parameters
        ----------
        name: str
            The key value to search the ddict for
        default:Any
            The default value
        :return: The data value for the entry if it exists, otherwise the default value
        """
        if self.has_entry(name):
            val = self.get_entry(name).data
            return val
        return default

    def store(self, skip: int = 10):
        """ If the count % skip, then store values in all the item's histories.

        Parameters
        ----------
        skip: int = 10
            The number of frames to skip. The default is 10. Set to 1 to store everything
        :return:
        """
        self.count += 1
        if (self.count % skip) == 0:
            self.store_count += 1
            for entry in self.ddict.values():
                entry.store()

    def log_to_csv(self, filename, skip:int = 1):
        """ Generate a file with all the stored data in csv format

        Parameters
        ----------
        filename:str
            The name of the logfile
        skip: int = 1
            The number of frames to skip. The default is 1, which writes out everything
        :return:
        """
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
        """ Generate a file with all the stored data in Excel format

        Parameters
        ----------
        pathname: str
            The path to the file
        filename:str
            The name of the logfile
        :return:
        """
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
        """ Generate a (big!) string using the default to_string() behavior for DictionaryEntrys

        Parameters
        ----------

        :return: The string representation of the entire ddict
        """
        to_return = ""
        for key, val in self.ddict.items():
            to_return += "{}\n".format(val.to_string())
        return to_return

    def to_short_string(self) -> str:
        """ Generate a smaller string with just the current values of the items in the ddict

        Parameters
        ----------

        :return: A minimal string representation of the entire ddict
        """
        to_return = ""
        for key, val in self.ddict.items():
            to_return += "({}:{})  ".format(key, val.get_data())
        return to_return

    def to_dict_array(self) -> List:
        """ Create a list of Dicts that can be saved out as a file and loaded in using set_entries_from_dict()

        Parameters
        ----------

        :return: A list of Dicts that contains the ddict data
        """
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

    for i in range(1, 21):
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
        time.sleep(0.25)

    print(ddict.to_string())
    dl = ddict.to_dict_array()
    for d in dl:
        print(d)

    print ("\nAdding another 'test_string' to force an exception")
    try:
        ddict.add_entry(DictionaryEntry("test_string", DictionaryTypes.STRING, "Hello, world"))
    except ValueError as ve:
        print(ve)