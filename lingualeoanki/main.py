# import the main window object (mw) from aqt
from aqt import mw
from aqt.qt import QAction
from aqt.utils import showInfo

from . import gui
from . import utils
from ._name import ADDON_NAME


def activate():
    # Not to run multiple copies of a plugin window,
    # we create an attribute in the mw object
    if hasattr(mw, ADDON_NAME):
        addon_window = getattr(mw, ADDON_NAME, None)
        addon_window.activateWindow()
        addon_window.raise_()
    else:
        config = utils.get_config()
        if config:
            window = gui.PluginWindow()
            setattr(mw, ADDON_NAME, window)
            window.exec_()
        else:
            showInfo("Unable to load config. Make sure that config.json "
                     "is present and not in use by other applications")


# create a new menu item
action = QAction("Import from LinguaLeo", mw)
# set it to call a function when it's clicked
action.triggered.connect(activate)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
