import os
import textwrap
import tkinter.font as tkf
from tkinter import *
from tkinter import ttk
from typing import Dict, Union

from rcsnn.tkUtils.DataField import DataField
from rcsnn.tkUtils.ListField import ListField
from rcsnn.tkUtils.TextField import TextField
from rcsnn.tkUtils.TkCanvasFrame import TkCanvasFrame


class TkCanvasBase:
    root: Union[Tk, None]
    datafields: Dict
    mainframe: Union[ttk.Frame, None]
    left_frame: ttk.Frame
    right_frame: ttk.Frame
    bottom_frame: ttk.Frame
    main_console: Union[TextField, None]
    canvasFrame: TkCanvasFrame
    current_dir: Union[str, None]
    dcount: int

    def __init__(self, root: Tk, version: str):
        self.reset()
        self.root = root
        self.root.title("TkCanvasBase {}".format(version))
        self.mainframe = ttk.Frame(self.root, borderwidth=2, relief="groove")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        self.build_menus()
        self.build_left()
        self.build_right()
        self.build_bottom()
        self.set_resize()
        self.current_dir = os.getcwd()
        self.dprint("Current dir = {}".format(self.current_dir))

        self.dprint(version)
        self.canvasFrame.callback_fn = self.canvas_callback_actions

    def reset(self):
        print("TkCanvasBase.reset()")
        self.root: Tk = None
        self.mainframe = None
        self.main_console = None
        self.current_dir = None
        self.datafields = {}
        self.dcount = 0

    def build_menus(self):
        print("building menus")
        self.root.option_add('*tearOff', FALSE)
        menubar = Menu(self.root)
        self.root['menu'] = menubar
        self.add_menus(menubar)

    def add_menus(self, menubar: Menu):
        menu_file = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='Exit', command=self.terminate)

    def build_left(self):
        self.left_frame = ttk.Frame(self.mainframe, borderwidth=5, relief="groove")
        self.left_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        row = 0
        row = self.add_left_components(self.left_frame, row)
        row += 1
        row = self.create_textfield("console", self.left_frame, row, "Console", "", 30, 10)
        self.main_console = self.datafields["console"]

    def add_left_components(self, f: ttk.Frame, row: int) -> int:
        return row

    def build_right(self):
        self.right_frame = ttk.Frame(self.mainframe, borderwidth=5, relief="groove")
        self.right_frame.grid(column=1, row=0, sticky=(N, W, E, S))
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)
        self.canvasFrame = TkCanvasFrame(self.right_frame)

    def build_bottom(self):
        self.bottom_frame = ttk.Frame(self.mainframe, borderwidth=5, relief="groove")
        self.bottom_frame.grid(column=0, row=1, columnspan=2, sticky=(N, W, E, S))
        # self.bottom_frame.columnconfigure(1, weight=1)
        self.bottom_frame.rowconfigure(0, weight=1)
        row = 0
        row = self.create_textfield("path", self.bottom_frame, row, "Path", "", 110, 10)


    def create_datafield(self, name: str, parent: 'ttk.Frame', row: int, label: str, default: str,
                         width: int = 20) -> int:
        df = DataField(parent, row, label, width)
        df.set_text(default)
        self.datafields[name] = df
        return df.get_next_row()

    def create_textfield(self, name: str, parent: 'ttk.Frame', row: int, label: str, default: str, width: int = 20,
                         height: int = 3) -> int:
        tf = TextField(parent, row, label, width=width, height=height)
        tf.add_text(default)
        self.datafields[name] = tf
        return tf.get_next_row()

    def create_listfield(self, name: str, parent: 'ttk.Frame', row: int, label: str, default: str, width: int = 20,
                         height: int = 3, selectmode=MULTIPLE) -> int:
        lf = ListField(parent, row, label, width=width, height=height, selectmode=selectmode)

        lf.set_text(default)
        self.datafields[name] = lf
        return lf.get_next_row()

    def set_resize(self):
        print("adding resizing")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=0)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)

    def canvas_callback_actions(self, event: Event):
        self.dprint("clicked at ({}, {})".format(event.x, event.y))

    def log_path(self, d: Dict, clear: bool = True):
        tf: TextField = self.datafields["path"]
        if clear:
            tf.tk_text.delete('1.0', END)
        tf.tk_text.insert(END, "path = {}".format(d.keys()))
        for key, val in d.items():
            line = "{}: {}\n".format(key, val)
            tf.tk_text.insert(END, line)

    def dprint(self, text: str, max_chars: int = -1):
        if self.main_console:
            if max_chars > -1:
                text = textwrap.shorten(text, width=max_chars)

            self.main_console.tk_text.insert("1.0", "[{}] {}\n".format(self.dcount, text))
            # self.main_console.set_text(text, self.dcount)
            self.dcount += 1
            self.mainframe.update()
        else:
            print(text)

    def terminate(self):
        print("terminating")
        self.root.destroy()

    def impliment_me(self):
        self.dprint("Implement me!")


def main():
    root = Tk()
    print(tkf.families())
    tcb = TkCanvasBase(root, "Version 0.1")
    root.mainloop()


if __name__ == "__main__":
    main()
