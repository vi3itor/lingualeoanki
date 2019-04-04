# import the main window object (mw) from aqt
from aqt import mw
from aqt.qt import QAction

from . import gui
from ._name import ADDON_NAME


def activate():
    # Not to run multiple copies of a plugin window,
    # we create an attribute in the mw object
    if hasattr(mw, ADDON_NAME):
        mw.lingualeoanki.activateWindow()
        mw.lingualeoanki.raise_()
    else:
        window = gui.PluginWindow()
        setattr(mw, ADDON_NAME, window)
        window.exec_()


# create a new menu item
action = QAction("Import From LinguaLeo", mw)
# set it to call a function when it's clicked
action.triggered.connect(activate)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
