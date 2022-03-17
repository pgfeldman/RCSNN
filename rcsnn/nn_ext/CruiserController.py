from rcsnn.base.BaseController import BaseController
from rcsnn.base.DataDictionary import DataDictionary
from rcsnn.base.DataDictionary import DataDictionary, DictionaryEntry, DictionaryTypes

class CruiserController(BaseController):
    target_pos:DictionaryEntry

    def __init__(self, name: str, ddict: DataDictionary):
        super().__init__(name, ddict)
        self.heading = DictionaryEntry("target_pos", DictionaryTypes.LIST, [0, 0])
        self.ddict.add_entry(self.heading)

    def run_task(self):
        super().run_task()
        # S0: ask MissileControler how far away a 90% accuracy shot is
        # S1: Plot a destination and ask the NavigateController for the time to reach
        # S3: Jump forward in time and ask the MissileController to fire a missile and if it hit
        # S4: Evaluate and re-fire as needed
        # S5: Report back success or failure