import tkinter as tk
import tkinter.messagebox as tkm
import json
from tkinter import filedialog
from rcsnn.tkUtils.TextField import TextField
from rcsnn.tkUtils.DataField import DataField
from rcsnn.ui.HierarchyGenerator import HierarchyGenerator
from typing import Union, Any

from rcsnn.ui.AppBase import AppBase

class HierarchyApp(AppBase):
    hierarchy_json:Union[Any, None]
    json_text_field:TextField
    output_dir_field:DataField
    hg:HierarchyGenerator

    def setup_app(self):
        self.app_name = "HierarchyBuilder"
        self.app_version = "3.21.2022"
        self.geom = (600, 500)
        self.hierarchy_json = None

    def build_app_view(self, row:int, text_width:int, label_width:int) -> int:
        print("build_app_view")
        self.output_dir_field = DataField(self, row, "Target Dir", width=50)
        row = self.output_dir_field.get_next_row()
        self.json_text_field = TextField(self, row, "JSON:", height=20, label_width=10)
        row = self.json_text_field.get_next_row()
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
        menu_file.add_command(label='Generate Code', command=self.generate_code_callback)
        menu_file.add_command(label='Exit', command=self.terminate)

    def load_callback(self):
        result = filedialog.askopenfile(filetypes=(("JSON files", "*.json"),("All Files", "*.*")), title="Load json ID file")
        if result:
            filename = result.name
            print("loading{}".format(filename))
            with open(filename) as f:
                self.hierarchy_json = json.load(f)
                s = json.dumps(self.hierarchy_json, indent=4, sort_keys=False)
                self.json_text_field.set_text(s)


    def save_json_callback(self):
        if len(self.json_text_field.get_text()) < 3:
            tkm.showwarning("Warning!", "There is no text to save!\nPleas load or enter a JSON hierarchy description.")
            return

        result = filedialog.asksaveasfile(filetypes=(("JSON files", "*.json"),("All Files", "*.*")), title="Load json ID file")
        if result:
            filename = result.name
            print("saving {}".format(filename))

    def generate_code_callback(self):
        if self.hierarchy_json != None:
            print(json.dumps(self.hierarchy_json, indent=2, sort_keys=False))
            self.hg = HierarchyGenerator()
            d = json.loads(self.json_text_field.get_text())
            self.hg.config_from_dict(d)
            self.hg.generate_code()

def main():
    app = HierarchyApp()
    app.mainloop()

if __name__ == "__main__":
    # print(Path.home())
    main()