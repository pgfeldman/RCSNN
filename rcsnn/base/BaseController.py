from rcsnn.base.Commands import Commands
from rcsnn.base.CommandObject import CommandObject
from rcsnn.base.DataDictionary import DataDictionary, DictionaryEntry, DictionaryTypes
from rcsnn.base.Responses import Responses
from rcsnn.base.ResponseObject import ResponseObject
from rcsnn.base.States import States

from typing import Union, Dict

class BaseController():
    '''
    The BaseController object is the base class for all modules. It has basic functionality to
    connect to a data dictionary process and respond to commands from its parent and issue
    commands and handle responses from its child modules

    Attributes
    ----------
    cmd: CommandObject
        The commands from the parent to this instance
    rsp: ResponseObject
        The response from this instance to the parent
    cur_state:States
        The current state of the command that is currently being executed
    ddict:DataDictionary
        The pointer to the DataDictionary instance that mediates all communication in the system
    name:str
        The name of this instance
    clock:float
        The current time. Taken from the DataDictionary "elapsed-time"
    dclock:float
        The time since this instance was called
    elapsed:float
        A resettable clock that increments by dclock
    child_cmd_dict:Dict
        A Dict containing names and pointers to all the commands to child controllers
    child_rsp_dict:Dict
        A Dict containing names and pointers to all the responses from child controllers

    Methods
    -------
    reset(self):
        Resets all the global values for this Base class
    add_init(self):
        An empty method for subclasses to initialize. Called from self.__init__()
    add_reset(self):
        An empty method for subclasses to reset. Called from self.reset()
    set_cmd_obj(self, co: CommandObject):
        Sets the pointer to an externally created CommandObject
    set_rsp_obj(self, ro: ResponseObject):
        Sets the pointer to an externally created ResponseObject
    add_child_cmd(self, cmd: CommandObject):
        Adds a CommandObject to this instance's child_cmd_dict
    add_child_rsp(self, rsp: ResponseObject):
        Adds a ResponseObject to this instance's child_rsp_dict
    set_all_child_cmd(self, cmd: Commands):
        Set the same Commands enum for all the entries in the child_cmd_dict
    test_all_child_rsp(self, rsp: Responses) -> bool:
        Test to see that all the entries are equal to the passed-in Responses enum. Returns True if they all match
    evaluate_cmd(self) -> Commands:
        Handle the current command. It it's a new command, then set the cur_state to NEW_COMMAND and the response to
        EXECUTING. Returns the current command enum
    get_response(self) -> ResponseObject:
        Get the this controller's ResponseObject that it uses to reply to its parent
    step(self):
        Update the clocks, and call the pre_process(), decision_process() and post_process() methods
    pre_process(self):
        An empty method for subclasses to use to perform any calculations that need to be performed before the
        decision_process(). This could be reading in sensor values or processing information in the data dictionary
        in ways that are only used by this class
    decision_process(self):
        The method that decides what code to run, based on the current command. The default modes are INIT, RUN,
        and TERMINATE
    post_process(self):
        An empty method for subclasses to use to perform any actions that need to be performed after the
        decision_process(). This could be writing out information to the data dictionary in ways that are
        needed by other classes or displays
    init_task(self):
        Initialization code is wrapped in state tables so that each command has a specific lifecycle. In
        the default case, when a new INIT has been issued, cur_state will be NEW_COMMAND. This is relayed to the
        child controllers, the cur_state is set to S0, and the response is set to EXECUTING. After the INIT has
        rippled through the child classes and they have all returned DONE, this this class returns DONE to its parent
    run_task(self):
        Often, the normal state for a module is RUN. The RUN code is wrapped in state tables so that the command has
        a specific lifecycle. In the default case, when a new RUN has been issued, cur_state will be NEW_COMMAND.
        This is relayed to the child controllers, the cur_state is set to S0, and the response is set to EXECUTING.
        This state can sustain for as long as the context doesn't change. In the default (example) class, execution
        continues until elapsed exceeds run_time_limit, at which point the bottommost class would return a DONE. The
        DONE ripples up through the parent classes until it hits a level in the hierarchy where a new command is issued
    terminate_task(self):
        Termination code is wrapped in state tables so that each command has a specific lifecycle. In
        the default case, when a new TERMINATE has been issued, cur_state will be NEW_COMMAND. This is relayed to the
        child controllers, the cur_state is set to S0, and the response is set to EXECUTING. After the TERMINATE has
        rippled through the child classes and they have all returned DONE, this this class returns DONE to its parent
    to_string(self):
        returns a string that shows the name, command, response, and current state
    create_cmd_rsp(parent: "BaseController", child: "BaseController", ddict: DataDictionary): Static method
        Convenience class that creates a CommandObject and ResponseObject between a child and parent and adds these
        objects to the data dictionary


    '''
    cmd: Union[CommandObject, None]
    rsp: Union[ResponseObject, None]
    cur_state: str
    ddict: Union[DataDictionary, None]
    name:str
    clock:float
    dclock:float
    elapsed:float
    child_cmd_dict:Dict
    child_rsp_dict:Dict

    def __init__(self, name: str, ddict: DataDictionary):
        """Constructor: Sets up the basic components of the class

        Parameters
        ----------
        name: str
            The name of the class
        ddict: DataDictionary
            The data dictionary used for all data in the system
        """
        self.reset()
        self.name = name
        self.ddict = ddict
        self.add_init()

    def reset(self):
        """ Resets all the global values for this Base class

        Parameters
        ----------
        :return:
        """
        self.name = "unset"
        self.clock = 0
        self.dclock = 0
        self.elapsed = 0
        self.cmd = None
        self.rsp = None
        self.cur_state = States.NOP
        self.child_cmd_dict = {}
        self.child_rsp_dict = {}
        self.add_reset()

    def add_init(self):
        """ An empty method for subclasses to initialize. Called from self.__init__()

        Parameters
        ----------
        :return:
        """
        pass

    def add_reset(self):
        """ An empty method for subclasses to reset. Called from self.reset()

        Parameters
        ----------
        :return:
        """
        pass

    def set_cmd_obj(self, co: CommandObject):
        """ Sets the pointer to an externally created CommandObject

        Parameters
        ----------
        co: CommandObject
            The CommandObject that this class uses to get commands from its parent
        :return:
        """
        self.cmd = co

    def set_rsp_obj(self, ro: ResponseObject):
        """ Sets the pointer to an externally created ResponseObject

        Parameters
        ----------
        ro: ResponseObject
            The ResponseObject that this class uses to send responses to its parent
        :return:
        """
        self.rsp = ro

    def add_child_cmd(self, cmd: CommandObject):
        """ Adds a CommandObject to this instance's child_cmd_dict

        Parameters
        ----------
        co: CommandObject
            The CommandObject that the child class uses to get commands from this class, its parent
        :return:
        """
        self.child_cmd_dict[cmd.name] = cmd

    def add_child_rsp(self, rsp: ResponseObject):
        """ Adds a ResponseObject to this instance's child_rsp_dict

        Parameters
        ----------
        rsp: ResponseObject
            The ResponseObject that the child class uses to send responses to this class, its parent
        :return:
        """
        self.child_rsp_dict[rsp.name] = rsp

    def set_all_child_cmd(self, cmd: Commands):
        """ Set the same Commands enum for all the entries in the child_cmd_dict

        Parameters
        ----------
         cmd: Commands
            The Commands enum that will be sent to all child controllers
        :return:
        """
        for co in self.child_cmd_dict.values():
            co.set(cmd, co.next_serial())

    def test_all_child_rsp(self, rsp: Responses) -> bool:
        """ Test to see that all the entries are equal to the passed-in Responses enum. Returns True if they all match

        Parameters
        ----------
         rsp: Responses
            The Responses enum that will be evaluated against all child controllers
        :return: True if all responses match, False otherwise
        """
        for ro in self.child_rsp_dict.values():
            if not ro.test(rsp):
                return False
        return True

    def evaluate_cmd(self) -> Commands:
        """ Handle the current command. It it's a new command, then set the cur_state to NEW_COMMAND and the response to
        EXECUTING. Returns the current command enum

        Parameters
        ----------

        :return: The current command enum for this controller
        """
        if self.cmd.new_command:
            self.cur_state = States.NEW_COMMAND
            self.rsp.set(Responses.EXECUTING, self.cmd.serial)
        return self.cmd.get()

    def get_response(self) -> ResponseObject:
        """ Get the this controller's ResponseObject that it uses to reply to its parent

        Parameters
        ----------

        :return: This controller's ResponseObject that it uses to reply to its parent
        """
        return (self.rsp)

    def step(self):
        """ Update the clocks, and call the pre_process(), decision_process() and post_process() methods

        Parameters
        ----------

        :return:
        """
        current = self.ddict.get_entry("elapsed-time").data
        self.dclock = current - self.clock
        self.clock = current
        self.elapsed += self.dclock
        # print("dclock = {:.2f}, clock = {:.2f}".format(self.dclock, self.clock))
        self.pre_process()
        self.decision_process()
        self.post_process()

    def pre_process(self):
        """ An empty method for subclasses to use to perform any calculations that need to be performed before the
        decision_process(). This could be reading in sensor values or processing information in the data dictionary
        in ways that are only used by this class

        Parameters
        ----------

        :return:
        """
        pass

    def decision_process(self):
        """ The method that decides what code to run, based on the current command. The default modes are INIT, RUN,
        and TERMINATE

        Parameters
        ----------

        :return:
        """
        command = self.evaluate_cmd()
        if command == Commands.INIT:
            self.init_task()
        elif command == Commands.RUN:
            self.run_task()
        elif command == Commands.TERMINATE:
            self.terminate_task()

    def post_process(self):
        """ An empty method for subclasses to use to perform any actions that need to be performed after the
        decision_process(). This could be writing out information to the data dictionary in ways that are
        needed by other classes or displays

        Parameters
        ----------

        :return:
        """
        pass

    def init_task(self):
        """ Initialization code is wrapped in state tables so that each command has a specific lifecycle. In
        the default case, when a new INIT has been issued, cur_state will be NEW_COMMAND. This is relayed to the
        child controllers, the cur_state is set to S0, and the response is set to EXECUTING. After the INIT has
        rippled through the child classes and they have all returned DONE, this this class returns DONE to its parent

        Parameters
        ----------

        :return:
        """
        if self.cur_state == States.NEW_COMMAND:
            print("{} is initializing".format(self.name))
            self.set_all_child_cmd(Commands.INIT)
            self.cur_state = States.S0
            self.rsp.set(Responses.EXECUTING, self.cmd.serial)
        elif self.cur_state == States.S0 and self.test_all_child_rsp(Responses.DONE):
            print("{} is initialized".format(self.name))
            self.cur_state = States.NOP
            self.rsp.set(Responses.DONE)

    def run_task(self):
        """ Often, the normal state for a module is RUN. The RUN code is wrapped in state tables so that the command has
        a specific lifecycle. In the default case, when a new RUN has been issued, cur_state will be NEW_COMMAND.
        This is relayed to the child controllers, the cur_state is set to S0, and the response is set to EXECUTING.
        This state can sustain for as long as the context doesn't change. In the default (example) class, execution
        continues until elapsed exceeds run_time_limit, at which point the bottommost class would return a DONE. The
        DONE ripples up through the parent classes until it hits a level in the hierarchy where a new command is issued

        Parameters
        ----------

        :return:
        """
        run_time_limit = 0.3
        print("{} run_task(): elapsed = {:.2f} of {} ({:.2f} remaining)".format(self.name, self.elapsed, run_time_limit, (run_time_limit-self.elapsed)))
        if self.cur_state == States.NEW_COMMAND:
            print("{} is running".format(self.name))
            self.set_all_child_cmd(Commands.RUN)
            self.cur_state = States.S0
            self.elapsed = 0
            self.rsp.set(Responses.EXECUTING, self.cmd.serial)
        elif self.cur_state == States.S0 and self.elapsed >= run_time_limit and self.test_all_child_rsp(Responses.DONE):
            print("{} has finished running".format(self.name))
            self.cur_state = States.NOP
            self.rsp.set(Responses.DONE)

    def terminate_task(self):
        """ Termination code is wrapped in state tables so that each command has a specific lifecycle. In
        the default case, when a new TERMINATE has been issued, cur_state will be NEW_COMMAND. This is relayed to the
        child controllers, the cur_state is set to S0, and the response is set to EXECUTING. After the TERMINATE has
        rippled through the child classes and they have all returned DONE, this this class returns DONE to its parent

        Parameters
        ----------

        :return:
        """
        if self.cur_state == States.NEW_COMMAND:
            print("{} is terminating".format(self.name))
            self.set_all_child_cmd(Commands.TERMINATE)
            self.cur_state = States.S0
            self.rsp.set(Responses.EXECUTING, self.cmd.serial)
        elif self.cur_state == States.S0 and self.test_all_child_rsp(Responses.DONE):
            print("{} is terminated".format(self.name))
            self.cur_state = States.NOP
            self.rsp.set(Responses.DONE)

    def to_string(self) -> str:
        """ returns a string that shows the name, command, response, and current state

        Parameters
        ----------

        :return: A string that shows the name, command, response, and current state
        """
        to_return = "Module {}:\n\t{}\n\t{}\n\tcur_state = {}". \
            format(self.name, self.cmd.to_string(), self.rsp.to_string(), self.cur_state)
        return to_return

    @staticmethod
    def link_parent_child(parent: "BaseController", child: "BaseController", ddict: DataDictionary):
        """ Convenience class that creates a CommandObject and ResponseObject between a child and parent and adds these
        objects to the data dictionary

        Parameters
        ----------
        parent: BaseController
            The parent controller that will send commands and get responses from the child controller
        child: BaseController
            The child controller that will get commands and send responses to the parent controller
        ddict: DataDictionary
            The data dictionary that will contain the entries for the CommandObject and responseObject that are
            created for communication

        :return:
        """
        p2c_cmd = CommandObject(parent.name, child.name)
        p2c_rsp = ResponseObject(parent.name, child.name)
        child.set_cmd_obj(p2c_cmd)
        child.set_rsp_obj(p2c_rsp)
        parent.add_child_cmd(p2c_cmd)
        parent.add_child_rsp(p2c_rsp)
        de = DictionaryEntry(p2c_cmd.name, DictionaryTypes.COMMAND, p2c_cmd)
        ddict.add_entry(de)
        de = DictionaryEntry(p2c_rsp.name, DictionaryTypes.RESPONSE, p2c_rsp)
        ddict.add_entry(de)


if __name__ == "__main__":
    """
    Exercise the class in a toy hierarchy that initializes, runs, and terminates. The hierarchy is controlled from the
    main loop and has two controllers, a "parent" and a "child"
    """
    # create the data dictionary and add "elapsed-time" as a float
    ddict = DataDictionary()
    elapsed_time_entry = DictionaryEntry("elapsed-time", DictionaryTypes.FLOAT, 0)
    ddict.add_entry(elapsed_time_entry)

    # Create the command object that will send commands from the main loop to the only module in this hierarchy
    top_to_parent_cmd_obj = CommandObject("board-monitor", "parent-controller")
    de = DictionaryEntry(top_to_parent_cmd_obj.name, DictionaryTypes.COMMAND, top_to_parent_cmd_obj)
    ddict.add_entry(de)

    # Create the response object that will send responses from the module to the main loop
    top_to_parent_rsp_obj = ResponseObject("board-monitor", "parent-controller")
    de = DictionaryEntry(top_to_parent_rsp_obj.name, DictionaryTypes.RESPONSE, top_to_parent_rsp_obj)
    ddict.add_entry(de)

    # Create an instance of a controller. An actual controller would inherit from this class rather than instancing the
    # default
    parent_ctrl = BaseController("parent-controller", ddict)
    parent_ctrl.set_cmd_obj(top_to_parent_cmd_obj)
    parent_ctrl.set_rsp_obj(top_to_parent_rsp_obj)

    # Add a child controller under the parent controller
    child_ctrl = BaseController("child_controller", ddict)
    BaseController.link_parent_child(parent_ctrl, child_ctrl, ddict)

    # Set the INIT command that will start the hierarchy, then iterate until the INIT->RUN->TERMINATE sequence completes
    top_to_parent_cmd_obj.set(Commands.INIT, 1)
    done = False
    current_step = 0
    while not done:
        print("\nstep[{}]---------------".format(current_step))
        elapsed_time_entry.data += 0.1
        ddict.store(skip = 1)
        parent_ctrl.step()
        print(parent_ctrl.to_string())

        child_ctrl.step()
        print(child_ctrl.to_string())

        if top_to_parent_cmd_obj.test(Commands.INIT) and parent_ctrl.rsp.test(Responses.DONE):
            top_to_parent_cmd_obj.set(Commands.RUN, 2)
        elif top_to_parent_cmd_obj.test(Commands.RUN) and parent_ctrl.rsp.test(Responses.DONE):
            top_to_parent_cmd_obj.set(Commands.TERMINATE, 3)
        elif top_to_parent_cmd_obj.test(Commands.TERMINATE) and parent_ctrl.rsp.test(Responses.DONE):
            done = True

        current_step += 1
    print("\nDataDictionary:\n{}".format(ddict.to_string()))
    ddict.to_excel("../../data/", "base-controller.xlsx")
