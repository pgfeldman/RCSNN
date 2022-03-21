import tkinter as tk
import json
from tkinter import filedialog
from typing import Union, Any

from rcsnn.ui.AppBase import AppBase

class HierarchyBuilder(AppBase):
    hierarchy_json:Union[Any, None]

    def setup_app(self):
        self.app_name = "HierarchyBuilder"
        self.app_version = "3.21.2022"
        self.geom = (600, 150)
        self.hierarchy_json = None

    def build_menus(self):
        print("building menus")
        self.option_add('*tearOff', tk.FALSE)
        menubar = tk.Menu(self)
        self['menu'] = menubar
        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='Load Hierarchy', command=self.load_callback)
        menu_file.add_command(label='Generate Code', command=self.generate_code_callback)
        menu_file.add_command(label='Exit', command=self.terminate)

    def load_callback(self):
        result = filedialog.askopenfile(filetypes=(("JSON files", "*.json"),("All Files", "*.*")), title="Load json ID file")
        if result:
            filename = result.name
            print("loading{}".format(filename))
            with open(filename) as f:
                self.hierarchy_json = json.load(f)
                print(json.dumps(self.hierarchy_json, indent=4, sort_keys=True))

    def generate_code_callback(self):
        if self.hierarchy_json != None:
            print(json.dumps(self.hierarchy_json, indent=2, sort_keys=False))

def main():
    app = HierarchyBuilder()
    app.mainloop()

if __name__ == "__main__":
    # print(Path.home())
    main()