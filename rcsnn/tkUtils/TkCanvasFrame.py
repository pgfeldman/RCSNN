import random
import tkinter.font as tkf
from tkinter import *
from tkinter import font
from tkinter import ttk
from typing import List, Dict, Callable, Union

import networkx as nx


class TkCanvasFrame:
    root: ttk.Frame
    datafields: Dict
    canvas: Union[Canvas, None]
    canvas_width: int
    canvas_height: int
    callback_fn: Union[Callable, None]
    gml_model: Union[nx.Graph, None]
    node_list: List
    node_color = "lightblue"
    hover_color = "pink"
    select_color = "red"
    edge_color = "lightgrey"
    font: font
    default_font: font.Font

    def __init__(self, root: ttk.Frame):
        self.reset()
        self.root = root

        self.build_main()

        self.set_resize()

    def reset(self):
        print("TkCanvasFrame.reset()")
        self.default_font = font.Font(family='courier', size=9)
        self.font = font.Font(family='Helvetica', size=12)
        self.canvas = None
        self.canvas_width = 600
        self.canvas_height = 500
        self.current_dir = None
        self.datafields = {}
        self.gml_model = None
        self.node_list = []
        for i in range(10):
            self.node_list.append("node_{:02}".format(i))

    def build_main(self):
        self.canvas = Canvas(self.root, bg="white", height=self.canvas_height, width=self.canvas_width)
        self.canvas.bind("<Button-1>", self.canvas_event_callback)
        self.canvas.pack(fill="both", expand=True)

        for n in self.node_list:
            size = random.randint(10, 50)
            x0 = random.randint(20, 500)
            y0 = random.randint(20, 500)
            x1 = x0 + size
            y1 = y0 + size
            self.canvas.create_oval(x0, y0, x1, y1, fill=self.node_color, activefill=self.hover_color, tags=n)
            self.canvas.create_text(x0, y0, text=n, font=self.font)

        self.gml_model = nx.Graph(name="default")
        for n in self.node_list:
            self.gml_model.add_node(n, graphics={"fill": "lightblue"})

        num_edges = 2
        for n1 in self.node_list:
            for i in range(num_edges):
                n2 = random.choice(self.node_list)
                if n1 != n2:
                    self.gml_model.add_edge(n1, n2)
                    sx, sy, tx, ty = self.get_line_coords(n1, n2)
                    id = self.canvas.create_line(sx, sy, tx, ty, fill=self.edge_color)
                    self.canvas.lower(id)

    def canvas_event_callback(self, event: Event):
        print("clicked at ({}, {})".format(event.x, event.y))
        if self.callback_fn != None:
            self.callback_fn(event)

    def get_center(self, n: str) -> [int, int]:
        c = self.canvas.coords(n)
        bb = self.canvas.bbox(n)
        x = c[0] + (bb[2] - bb[0]) / 2
        y = c[1] + (bb[3] - bb[1]) / 2
        return (int(x), int(y))

    def get_line_coords(self, n1: str, n2: str) -> [int, int, int, int]:
        sx, sy = self.get_center(n1)
        tx, ty = self.get_center(n2)
        return (sx, sy, tx, ty)

    def set_resize(self):
        print("adding resizing")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=0)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)


def main():
    root = Tk()
    print(tkf.families())
    root.title("TkCanvasFrame 5.2.2022")
    mainframe = ttk.Frame(root, borderwidth=2, relief="groove")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    tcb = TkCanvasFrame(mainframe)
    root.mainloop()


if __name__ == "__main__":
    main()
