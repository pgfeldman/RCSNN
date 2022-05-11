import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkm
import json
import os
import re
from tkinter import filedialog
from rcsnn.tkUtils.TextField import TextField
from rcsnn.tkUtils.DataField import DataField
from rcsnn.tkUtils.Buttons import Buttons
from rcsnn.tkUtils.CanvasFrame import CanvasFrame
from rcsnn.tkUtils.MoveableNode import MovableNode
from rcsnn.ui.HierarchyGenerator import HierarchyGenerator, HierarchyModule
from rcsnn.base.BaseBoardMonitor import BaseBoardMonitor
import importlib
from types import ModuleType
from typing import Dict, List, Union, Any

from rcsnn.ui.AppBase import AppBase

class ModuleNode:
    module:HierarchyModule
    node:MovableNode
    name:str

    def __init__(self, name:str, module:HierarchyModule, node:MovableNode):
        self.name = name
        self.module = module
        self.node = node

class HierarchyApp(AppBase):
    hierarchy_json:Union[Any, None]
    json_text_field:TextField
    rcs_text_field:TextField
    canvas_frame:CanvasFrame
    output_dir_field:DataField
    h_generator:HierarchyGenerator
    bdmon_module: Union[ModuleType, None]
    bdmon_class: Union[BaseBoardMonitor, None]
    module_node_dict:Dict

    def setup_app(self):
        self.app_name = "RCSNN Hierarchy App"
        self.app_version = "4.20.2022"
        self.geom = (600, 550)
        self.hierarchy_json = None
        self.bdmon_module = None
        self.module_node_dict = {}

    def build_app_view(self, row:int, text_width:int, label_width:int) -> int:
        print("build_app_view")
        s = ttk.Style()
        s.configure('TNotebook.Tab', font=self.default_font)

        self.output_dir_field = DataField(self, row, "Target Dir:", width=50)
        row = self.output_dir_field.get_next_row()

        # Add the tabs
        tab_control = ttk.Notebook(self)
        tab_control.grid(column=0, row=row, columnspan=2, sticky="nsew")
        json_tab = ttk.Frame(tab_control)
        tab_control.add(json_tab, text='JSON')
        self.json_text_field = TextField(json_tab, 0, "JSON:", height=20, label_width=10)
        rcs_tab = ttk.Frame(tab_control)
        tab_control.add(rcs_tab, text='RCS')
        self.rcs_text_field = TextField(rcs_tab, 0, "RCS:", height=20, label_width=10)
        canvas_tab = ttk.Frame(tab_control)
        tab_control.add(canvas_tab, text='Canvas')
        self.canvas_frame = CanvasFrame(canvas_tab, 0, "Graph", self.dp, width=550, height=250)
        row += 1

        buttons = Buttons(self, row, "Code Execution:")
        buttons.add_button("Run", self.run_code_callback)
        buttons.add_button("Step", self.step_code_callback)
        buttons.add_button("Stop", self.stop_code_callback)
        row = buttons.get_next_row()

        return row

    def build_menus(self):
        print("building menus")
        self.option_add('*tearOff', tk.FALSE)
        menubar = tk.Menu(self)
        self['menu'] = menubar
        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='Load Hierarchy', command=self.load_callback)
        menu_file.add_command(label='Save Hierarchy', command=self.save_json_callback)
        menu_file.add_command(label='Set Code Directory', command=self.set_code_dir_callback)
        menu_file.add_command(label='Generate Code', command=self.generate_code_callback)
        menu_file.add_command(label='Exit', command=self.terminate)

    def run_code_callback(self):
        self.dp.dprint("Run code")
        if self.bdmon_module != None:
            self.bdmon_module.main()


    def step_code_callback(self):
        self.dp.dprint("Step code")
        if self.bdmon_class != None:
            self.bdmon_class.step()
            s = self.bdmon_class.ddict.to_short_string()
            self.rcs_text_field.set_text(s)

    def stop_code_callback(self):
        self.dp.dprint("Stop code")
        if self.bdmon_class != None:
            self.bdmon_class.terminate()

    def redraw_canvas(self):
        self.module_node_dict = {}
        # Now load the hierarchy into the graph
        self.canvas_frame.clear_Nodes()
        self.h_generator = HierarchyGenerator()
        d = json.loads(self.json_text_field.get_text())
        self.h_generator.config_from_dict(d)
        hm:HierarchyModule
        xpos = 1
        ypos = 1
        for hm in self.h_generator.hmodule_list:
            xpos = hm.layer * 150 + 20
            ypos = hm.child_id * 50 + 10
            move_node = self.canvas_frame.create_MoveableNode(hm.name, x=xpos, y=ypos)
            mod_node = ModuleNode(hm.name, module=hm, node=move_node)
            self.module_node_dict[mod_node.name] = mod_node

        mn:ModuleNode
        pmn:ModuleNode
        for name, mn in self.module_node_dict.items():
            parent_name = mn.module.parent
            if parent_name in self.module_node_dict:
                pmn = self.module_node_dict[parent_name]
                self.canvas_frame.connect_nodes(mn.node, pmn.node)


    def load_callback(self):
        result = filedialog.askopenfile(filetypes=(("JSON files", "*.json"),("All Files", "*.*")), title="Load json ID file")
        if result:
            filename = result.name
            print("loading{}".format(filename))
            with open(filename) as f:
                self.hierarchy_json = json.load(f)
                s = json.dumps(self.hierarchy_json, indent=4, sort_keys=False)
                self.json_text_field.set_text(s)
                if 'code_dir' in self.hierarchy_json:
                    abspath = os.path.abspath(self.hierarchy_json['code_dir'])
                    self.output_dir_field.set_text(abspath)
                if 'code_prefix' in self.hierarchy_json:
                    try:
                        # approach taken from https://stackoverflow.com/questions/4821104/dynamic-instantiation-from-string-name-of-a-class-in-dynamically-imported-module
                        self.bdmon_module = importlib.import_module("{}BoardMonitorChild".format(self.hierarchy_json['code_prefix']))
                        class_ = getattr(self.bdmon_module, "BoardMonitorChild")
                        self.bdmon_class = class_()
                        print("Setting up: {}".format(self.bdmon_class.name))
                        self.bdmon_class.setup()
                        print("Sending first command up: {}".format(self.bdmon_class.name))
                        self.bdmon_class.start()
                        s = self.bdmon_class.ddict.to_short_string()
                        self.rcs_text_field.set_text(s)
                    except ModuleNotFoundError as err:
                        print(err.msg)

                self.redraw_canvas()

    def save_json_callback(self):
        if len(self.json_text_field.get_text()) < 3:
            tkm.showwarning("Warning!", "There is no text to save!\nPleas load or enter a JSON hierarchy description.")
            return

        result = filedialog.asksaveasfile(filetypes=(("JSON files", "*.json"),("All Files", "*.*")), title="Load json ID file")
        if result:
            filename = result.name
            print("saving {}".format(filename))

    def set_code_dir_callback(self):
        cwd = os.getcwd()
        print("Current working dir = {}".format(cwd))
        filename = filedialog.askdirectory(initialdir=cwd, title="Set code generation directory")
        if filename:
            print("Set generation dir to {}".format(filename))
            self.output_dir_field.set_text(filename)

    def set_code_package(self):
        if self.hierarchy_json != None:
            split_regex = re.compile(r"\\|\/")
            self.hierarchy_json['code_dir'] = self.output_dir_field.get_text()
            root_dir:str = os.path.abspath(self.hierarchy_json['root_dir'])
            code_dir:str = self.output_dir_field.get_text()
            root_list = split_regex.split(root_dir)
            code_list = split_regex.split(code_dir)
            root = root_list[-1]
            if root in code_list:
                root_index = code_list.index(root)
                for i in range(root_index+1, len(code_list)):
                    root += "."+code_list[i]
                root += "."
                self.hierarchy_json['code_prefix'] = root
                print("root = {}".format(root))

    def generate_code_callback(self):
        self.set_code_package()
        if self.hierarchy_json != None:
            print(json.dumps(self.hierarchy_json, indent=2, sort_keys=False))
            self.h_generator = HierarchyGenerator()
            d = json.loads(self.json_text_field.get_text())
            self.h_generator.config_from_dict(d)
            self.h_generator.generate_code()

def main():
    app = HierarchyApp()
    app.canvas_frame.setup(debug=False)
    app.mainloop()

if __name__ == "__main__":
    # print(Path.home())
    main()