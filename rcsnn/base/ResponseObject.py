from rcsnn.base.Responses import Responses

class ResponseObject():
    '''
    The CommandObject class creates object that contains command relatinoships between parent and child

    Attributes
    ----------
    serial:int
        The serial number of the command. Incremented each time a new Commands is set
    rsp:Responses
        The enumeration of all possible responses. Add to the Responses object to extend
    parentname:str
        The name of the parent that sets the command
    childname:str
        The name of the child that gets the command
    name:str
        The name of this command


    Methods
    -------
    reset(self):
        Resets all the global values for this Base class
    set(self, cmd: str, serial: int):
        set the command and serial number
    get(self) -> Commands:
        get the Commands enum
    test(self, to_test: Commands) -> bool:
        Test to see if the self.cmd == the passed-in value
    to_string(self) -> str:
    '''
    serial:int
    rsp:str
    parentname:str
    childname:str
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
        self.name = "RSP_{}_to_{}".format(childname, parentname)

    def reset(self):
        """ Resets all the global values for this class

        Parameters
        ----------
        :return:
        """
        self.serial = 0
        self.rsp = Responses.NOP
        self.parentname = "unset"
        self.childname = "unset"
        self.name = "unset"

    def set(self, rsp: Responses, serial: int = -1):
        """ Set the command and serial number

        Parameters
        ----------
        rsp: Responses
            The new Responses
        serial: int
            The new sertial number
        :return:
        """
        self.rsp = rsp
        if serial > 0:
            self.serial = serial

    def get(self) -> Responses:
        """ Get the current Responses enum

        Parameters
        ----------

        :return: the current Responses enum
        """
        return self.rsp

    def test(self, to_test: Responses) -> bool:
        """ Test to see if the self.rsp == the passed-in value

        Parameters
        ----------
        to_test: Responses
            The enum we are comparing to

        :return: True if match
        """
        return self.rsp == to_test

    def to_string(self) -> str:
        """ returns a string that shows the name and serial number

        Parameters
        ----------

        :return: A string that shows the name and serial number of this object
        """
        return "rsp = {}, serial = {}".format(self.rsp, self.serial)