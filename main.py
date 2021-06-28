"""
DevLogs Initialization.

Where the DevLogs App is initialized and executed.
"""
from os.path import join
from kivy.logger import Logger
from kivy.resources import resource_add_path
from warnings import filterwarnings
from globaldata import __author__, __version__, __license__


# filterwarnings("ignore")


__author__ = __author__
__version__ = __version__
__license__ = __license__


# Logger.disabled = True


try:
    from sys import _MEIPASS
    has_MEIPASS = True
except ImportError:
    has_MEIPASS = False


if __name__ == "__main__":
    from frontend import DevLogs

    if has_MEIPASS:
        resource_add_path(join(_MEIPASS))

    main_app = DevLogs()
    main_app.run()
