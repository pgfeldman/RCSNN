from rcsnn.base.Commands import Commands

class CommandObject():
    '''
    The CommandObject class creates object that contains command relatinoships between parent and child

    Attributes
    ----------
    serial:int
        The serial number of the command. Incremented each time a new Commands is set
    cmd:Commands
        The enumeration of all possible commands. Add to the Commands object to extend
    parentname:str
        The name of the parent that sets the command
    childname:str
        The name of the child that gets the command
    new_command:bool
        A flag that indicates that this command has ben set but not acted on
    name:str
        The name of this command


    Methods
    -------
    reset(self):
        Resets all the global values for this Base class
    next_serial(self):
        returns what the next serial will be
    set(self, cmd: str, serial: int):
        set the command and serial number
    get(self) -> Commands:
        get the Commands enum
    test(self, to_test: Commands) -> bool:
        Test to see if the self.cmd == the passed-in value
    to_string(self) -> str:
    '''

    serial:int
    cmd:str
    parentname:str
    childname:str
    new_command:bool
    name:str

    def __init__(self, parentname: str, childname: str):
        """ Constructor. Sets up this instance

        Parameters
        parentname: str
            The name of the parent controller
        childname: str
            The name of the child controller
        ----------
        :return:
        """
        self.reset()
        self.parentname = parentname
        self.childname = childname
        self.name = "CMD_{}_to_{}".format(parentname, childname)

    def reset(self):
        """ Resets all the global values for this class

        Parameters
        ----------
        :return:
        """
        self.serial = 0
        self.cmd = Commands.NOP
        self.parentname = "unset"
        self.childname = "unset"
        self.new_command = False
        self.name = "unset"

    def next_serial(self):
        """ returns what the next serial will be

        Parameters
        ----------
        :return:
        """
        return self.serial + 1

    def set(self, cmd: Commands, serial: int):
        """ Set the command and serial number

        Parameters
        ----------
        cmd: Commands
            The new Commands
        serial: int
            The new sertial number
        :return:
        """
        if serial != self.serial:
            self.new_command = True
            self.cmd = cmd
            self.serial = serial

    def get(self) -> Commands:
        """ Get the current Commands enum

        Parameters
        ----------

        :return: the current Commands enum
        """
        self.new_command = False
        return self.cmd

    def test(self, to_test: Commands) -> bool:
        """ Test to see if the self.cmd == the passed-in value

        Parameters
        ----------
        to_test: Commands
            The enum we are comparing to

        :return: True if match
        """
        return self.cmd == to_test

    def to_string(self) -> str:
        """ returns a string that shows the name and serial number

        Parameters
        ----------

        :return: A string that shows the name and serial number of this object
        """
        return "cmd = {}, serial = {}".format(self.cmd, self.serial)