from maya import cmds
from PySide2 import QtWidgets, QtCore


class SubdivUI(QtWidgets.QDialog):
    # A dictionary of the usable render engines.
    # Every key holds a dictionary of commands for setting the subdiv type and interations.
    # Should probably just rewrite into a class
    renderers = {
        'Arnold': {
            'Type Command': '.aiSubdivType',
            'Iter Command': '.aiSubdivIterations'
        },

        'Renderman': {
            'Type Command': '.rman_subdivScheme'
        }
    }

    def __init__(self):

        super(SubdivUI, self).__init__()
        self.setWindowTitle("Batch change subdivs")
        self.setFixedSize(200, 100)
        self.buildUI()

    def buildUI(self):

        mainLayout = QtWidgets.QGridLayout(self)

        rendererLabel = QtWidgets.QLabel("Renderer:")
        rendererLabel.setAlignment(QtCore.Qt.AlignRight)
        mainLayout.addWidget(rendererLabel, 0, 0)

        self.rendererCB = QtWidgets.QComboBox()
        for i in self.renderers:
            self.rendererCB.addItem(i)
        mainLayout.addWidget(self.rendererCB, 0, 1)

        amountLabel = QtWidgets.QLabel("Subdiv Level:")
        amountLabel.setAlignment(QtCore.Qt.AlignRight)
        mainLayout.addWidget(amountLabel, 1, 0)

        self.subdivAmount = QtWidgets.QSpinBox()
        self.subdivAmount.setValue(1)
        mainLayout.addWidget(self.subdivAmount, 1, 1)

        setBtn = QtWidgets.QPushButton("Set")
        setBtn.clicked.connect(self.setSubdivAttr)
        mainLayout.addWidget(setBtn, 2, 1)

    def setSubdivAttr(self):
        currentSelection = cmds.ls(selection=True)
        meshList = []
        for item in currentSelection:
            if cmds.objectType(item) == "mesh":
                meshList.append(item)
            if cmds.listRelatives(item) != []:
                for child in cmds.listRelatives(item, allDescendents=True, path=True):
                    if cmds.objectType(child) == "mesh":
                        meshList.append(child)
        for mesh in meshList:
            renderer = self.renderers.get(self.rendererCB.currentText())
            typeCmnd = renderer.get("Type Command")
            iterCmnd = renderer.get("Iter Command")

            cmds.setAttr('{0}{1}'.format(mesh, typeCmnd), 1)
            if iterCmnd:
                iterAmount = self.subdivAmount.value()
                cmds.setAttr('{0}{1}'.format(mesh, iterCmnd), iterAmount)


ui = SubdivUI()
ui.show()