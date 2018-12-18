from aqt import mw
from aqt.qt import QAction

from lingualeo import gui


def activate():
    window = gui.PluginWindow()
    window.exec_()


# create a new menu item
action = QAction("Import From LinguaLeo", mw)
# set it to call a function when it's clicked
action.triggered.connect(activate)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
