from rcsnn.tkUtils.MoveableNode import MovableNode
from rcsnn.tkUtils.CanvasData import CanvasData
from rcsnn.tkUtils.ConsoleDprint import ConsoleDprint

class RCSMoveableNode(MovableNode):
    cmd_str:str
    state_str:str
    rsp_str:str
    cmd_id:int
    state_id:int
    rsp_id:int

    def __init__(self, name:str, canvas:CanvasData, dprint:ConsoleDprint, color:str, size:float,
                 x:float, y:float, dx:float=0, dy:float=0):
         super().__init__(name, canvas, dprint, color, size, x, y, dx, dy)
         self.cmd_str = "CMD"
         self.state_str = "STATE"
         self.rsp_str = "RSP"
         x_offset = 60
         y_offset = 40
         self.cmd_id = self.cd.canvas.create_text(self.x - x_offset, self.y+y_offset, text=self.cmd_str, font=self.font)
         self.state_id = self.cd.canvas.create_text(self.x, self.y+y_offset, text=self.state_str, font=self.font)
         self.rsp_id = self.cd.canvas.create_text(self.x + x_offset, self.y+y_offset, text=self.rsp_str, font=self.font)

    def set_module_text(self, cmd_str:str, state_str:str, rsp_str:str):
        self.cmd_str = cmd_str
        self.state_str = state_str
        self.rsp_str = rsp_str

        self.cd.canvas.itemconfig(self.cmd_id, text=self.cmd_str)
        self.cd.canvas.itemconfig(self.state_id, text=self.state_str)
        self.cd.canvas.itemconfig(self.rsp_id, text=self.rsp_str)

    def move(self, dx:float, dy:float):
        self.cd.canvas.move(self.cmd_id, dx, dy)
        self.cd.canvas.move(self.state_id, dx, dy)
        self.cd.canvas.move(self.rsp_id, dx, dy)
        super().move(dx, dy)