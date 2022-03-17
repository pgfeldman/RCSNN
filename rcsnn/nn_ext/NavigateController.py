import math
from rcsnn.base.BaseController import BaseController
from rcsnn.base.DataDictionary import DataDictionary, DictionaryEntry, DictionaryTypes

class NavigateController(BaseController):
    heading:DictionaryEntry

    def __init__(self, name: str, ddict: DataDictionary):
        super().__init__(name, ddict)

        self.heading = DictionaryEntry("nav-heading", DictionaryTypes.FLOAT, 0)
        self.ddict.add_entry(self.heading)

    def pre_process(self):
        self.heading.data = math.sin(self.elapsed)
        print("NavigateController heading = {}".format(self.heading.data))
        
    def run_task(self):
        super().run_task()

    def query_nn(self):
        # results = my_nn.predict()
        pass

    def load_nn(self):
        pass