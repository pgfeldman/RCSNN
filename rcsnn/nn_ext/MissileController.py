from rcsnn.base.BaseController import BaseController
from rcsnn.base.DataDictionary import DataDictionary

class MissileController(BaseController):

    def __init__(self, name: str, ddict: DataDictionary):
        super().__init__(name, ddict)