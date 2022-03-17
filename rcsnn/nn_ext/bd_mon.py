from rcsnn.nn_ext.CruiserController import CruiserController
from rcsnn.nn_ext.MissileController import MissileController
from rcsnn.nn_ext.NavigateController import NavigateController
from rcsnn.base.DataDictionary import DataDictionary, DictionaryTypes, DictionaryEntry
from rcsnn.base.CommandObject import CommandObject
from rcsnn.base.Commands import Commands
from rcsnn.base.ResponseObject import ResponseObject
from rcsnn.base.Responses import Responses
from rcsnn.base.BaseController import BaseController

def main():
    """
    Exercise the class in a toy hierarchy that initializes, runs, and terminates. The hierarchy is controlled from the
    main loop and has two controllers, a "parent" and a "child"
    """
    # create the data dictionary and add "elapsed-time" as a float
    ddict = DataDictionary()
    elapsed_time_entry = DictionaryEntry("elapsed-time", DictionaryTypes.FLOAT, 0)
    ddict.add_entry(elapsed_time_entry)

    # Create the command object that will send commands from the main loop to the only module in this hierarchy
    top_to_ship_cmd_obj = CommandObject("board-monitor", "ship-controller")
    de = DictionaryEntry(top_to_ship_cmd_obj.name, DictionaryTypes.COMMAND, top_to_ship_cmd_obj)
    ddict.add_entry(de)

    # Create the response object that will send responses from the module to the main loop
    top_to_ship_rsp_obj = ResponseObject("board-monitor", "ship-controller")
    de = DictionaryEntry(top_to_ship_rsp_obj.name, DictionaryTypes.RESPONSE, top_to_ship_rsp_obj)
    ddict.add_entry(de)

    # Create an instance of a controller. An actual controller would inherit from this class rather than instancing the
    # default
    ship_ctrl = CruiserController("ship-controller", ddict)
    ship_ctrl.set_cmd_obj(top_to_ship_cmd_obj)
    ship_ctrl.set_rsp_obj(top_to_ship_rsp_obj)

    # Add the child controller under the ship controller
    navigation_ctrl = NavigateController("navigate_controller", ddict)
    BaseController.link_parent_child(ship_ctrl, navigation_ctrl, ddict)

    missile_ctrl = MissileController("missile_controller", ddict)
    BaseController.link_parent_child(ship_ctrl, missile_ctrl, ddict)

    # Set the INIT command that will start the hierarchy, then iterate until the INIT->RUN->TERMINATE sequence completes
    top_to_ship_cmd_obj.set(Commands.INIT, 1)
    done = False
    current_step = 0
    while not done:
        print("\nstep[{}]---------------".format(current_step))
        elapsed_time_entry.data += 0.1
        ddict.store(skip = 1)

        # ---------- step all the controllers
        ship_ctrl.step()
        print(ship_ctrl.to_string())

        navigation_ctrl.step()
        print(navigation_ctrl.to_string())

        missile_ctrl.step()
        print(missile_ctrl.to_string())


        if top_to_ship_cmd_obj.test(Commands.INIT) and ship_ctrl.rsp.test(Responses.DONE):
            top_to_ship_cmd_obj.set(Commands.RUN, 2)
        elif top_to_ship_cmd_obj.test(Commands.RUN) and ship_ctrl.rsp.test(Responses.DONE):
            top_to_ship_cmd_obj.set(Commands.TERMINATE, 3)
        elif top_to_ship_cmd_obj.test(Commands.TERMINATE) and ship_ctrl.rsp.test(Responses.DONE):
            done = True

        current_step += 1
    print("\nDataDictionary:\n{}".format(ddict.to_string()))
    ddict.to_excel("../../data/", "ship-controller.xlsx")

if __name__ == "__main__":
    main()