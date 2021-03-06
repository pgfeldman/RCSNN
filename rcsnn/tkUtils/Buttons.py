import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from typing import List, Callable, Any

class Buttons():
    tk_label:tk.Label
    tk_combo:ttk.Combobox
    tk_button:ttk.Button
    wrapper:tk.Frame
    default_font:Font
    row = 0
    col:int = 0
    parent:'tk.Frame'

    def __init__(self, parent:'tk.Frame', row:int, label:str, label_width:int=20, sticky="nsew"):
        self.default_font = Font(family='courier', size = 9)
        self.parent = parent
        self.row = row
        self.tk_label = tk.Label(parent, text=label, width=label_width, anchor="w")
        self.tk_label.configure(font=self.default_font)

        self.wrapper = tk.Frame(parent)
        self.tk_label.grid(column=0, row=row, sticky="w", padx=5)
        self.wrapper.grid(column=1, row=row, sticky=sticky)

        self.col = 0

    def add_button(self, name:str, command:Callable, sticky:Any = (tk.N, tk.W)) -> ttk.Button:
        s = ttk.Style()
        s.configure('my.TButton', font=self.default_font)
        b = ttk.Button(self.wrapper, text=name, command=command, style = 'my.TButton')


        b.grid(column=self.col, row=0, sticky=sticky, pady=2, padx=5)
        self.col += 1
        return b

    def get_next_row(self):
        return self.row + 1

