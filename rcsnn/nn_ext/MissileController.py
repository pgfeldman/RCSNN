from rcsnn.base.BaseController import BaseController
from rcsnn.base.DataDictionary import DataDictionary
from rcsnn.base.Commands import Commands

class MissileController(BaseController):

    def __init__(self, name: str, ddict: DataDictionary):
        super().__init__(name, ddict)

    def decision_process(self):
        command = self.evaluate_cmd()
        if command == Commands.INIT:
            self.init_task()
        elif command == Commands.TARGET_SHIPS:
            self.run_task()
        elif command == Commands.TERMINATE:
            self.terminate_task()