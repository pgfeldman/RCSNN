import inspect
import sys
import os
from pathlib import Path

def get_project_root_dir() -> str:
    """
    Returns the name of the project root directory.

    :return: Project root directory name
    """

    # stack trace history related to the call of this function
    frame_stack: [inspect.FrameInfo] = inspect.stack()

    # get info about the module that has invoked this function
    # (index=0 is always this very module, index=1 is fine as long this function is not called by some other
    # function in this module)
    frame_info: inspect.FrameInfo = frame_stack[1]

    # if there are multiple calls in the stacktrace of this very module, we have to skip those and take the first
    # one which comes from another module
    if frame_info.filename == __file__:
        for frame in frame_stack:
            if frame.filename != __file__:
                frame_info = frame
                break

    # path of the module that has invoked this function
    caller_path: str = frame_info.filename

    # absolute path of the of the module that has invoked this function
    caller_absolute_path: str = os.path.abspath(caller_path)

    # get the top most directory path which contains the invoker module
    paths: [str] = [p for p in sys.path if p in caller_absolute_path]
    paths.sort(key=lambda p: len(p))
    caller_root_path: str = paths[0]

    if not os.path.isabs(caller_path):
        # file name of the invoker module (eg: "mymodule.py")
        caller_module_name: str = Path(caller_path).name

        # this piece represents a subpath in the project directory
        # (eg. if the root folder is "myproject" and this function has ben called from myproject/foo/bar/mymodule.py
        # this will be "foo/bar")
        project_related_folders: str = caller_path.replace(os.sep + caller_module_name, '')

        # fix root path by removing the undesired subpath
        caller_root_path = caller_root_path.replace(project_related_folders, '')

    dir_name: str = Path(caller_root_path).name

    return dir_name

def get_package_root_dir():
    return Path(__file__).parent.parent


if __name__ == "__main__":
    print("Project root = {}".format(get_project_root_dir()))
    print("Package root = {}".format(get_package_root_dir()))