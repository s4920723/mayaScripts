from maya import cmds
from PySide2 import QtCore, QtWidgets


class shaderConverter(QtWidgets.QDialog):
    shaderAttr = {
        'Phong':
            {
                'shaderNode': 'phong',
                'diffuseAttr': 'color',
                'specularAttr': 'specularColor',
                'roughnessAttr': 'reflectivity',
                'invertRough': True,
                'normalAttr': 'normalCamera',
                'normalNode': 'bump2d',
                'normalNodeIn': 'bumpValue',
                'normalNodeOut' : 'outNormal'

            },
        'Renderman 22':
            {
                'shaderNode': 'PxrSurface',
                'diffuseAttr': 'diffuseColor',
                'specularAttr': 'specularColor',
                'roughnessAttr': 'specularRoughness',
                'invertRough': False,
                'normalAttr': 'bumpNormal',
                'normalNode': 'PxrNormalMap',
                'normalNodeIn': 'inputRGB',
                'normalNodeOut': 'resultN'
            },

        'Arnold 5':
            {
                'shaderNode': 'aiStandardSurface',
                'diffuseAttr': 'baseColor',
                'specularAttr': 'specularColor',
                'roughnessAttr': 'specularRoughness',
                'invertRough': False,
                'normalAttr': 'normalCamera',
                'normalNode': 'aiNormalMap',
                'normalNodeIn': 'input',
                'normalNodeOut': 'outValue'
            }
    }
    shaderTypes = ('anisotropic', 'blinn', 'lambert', 'phong', 'PxrSurface', 'aiStandardSurface', 'VRayMtl')

    def __init__(self):
        super(shaderConverter, self).__init__()
        self.setWindowTitle('Convert Shader')
        self.buildUI()

    def buildUI(self):
        mainLayout = QtWidgets.QGridLayout(self)

        # Old Shader dropdown
        oldShaderLabel = QtWidgets.QLabel("Convert from:")
        oldShaderLabel.setAlignment(QtCore.Qt.AlignRight)
        mainLayout.addWidget(oldShaderLabel, 0, 0)

        self.oldShaderCB = QtWidgets.QComboBox()
        for i in self.shaderTypes:
            self.oldShaderCB.addItem(i)
        mainLayout.addWidget(self.oldShaderCB, 0, 1)

        # New Shader dropdown
        newShaderLabel = QtWidgets.QLabel("Convert to:")
        newShaderLabel.setAlignment(QtCore.Qt.AlignRight)
        mainLayout.addWidget(newShaderLabel, 1, 0)

        self.newShaderCB = QtWidgets.QComboBox()
        for i in self.shaderTypes:
            self.newShaderCB.addItem(i)
        mainLayout.addWidget(self.newShaderCB, 1, 1)

        # Delete checkbox
        self.deleteShader = QtWidgets.QCheckBox("Delete old shaders")
        mainLayout.addWidget(self.deleteShader, 2, 1)

        # Convert button
        convertBtn = QtWidgets.QPushButton("Convert")
        convertBtn.clicked.connect(self.convert)
        mainLayout.addWidget(convertBtn, 3, 1)

    def convert(self):
        oldShaders = cmds.ls(type=self.oldShaderCB.currentText())

        for oldShader in oldShaders:
            textures = cmds.listConnections(oldShader, type='file')
            print textures

            # Connect textures to new shader
            newShader = cmds.shadingNode(self.newShaderCB.currentText(), name='{0}_converted'.format(oldShader), asShader=True)
            for texture in textures:
                cmds.connectAttr('{0}.outColor'.format(texture), '{0}.baseColor'.format(newShader))

            # Connect new shader to shading group
            shadingGroup = cmds.listConnections(oldShader, type='shadingEngine')
            cmds.connectAttr('{0}.outColor'.format(newShader), '{0}.surfaceShader'.format(shadingGroup[0]), force=True)
            if self.deleteShader.isChecked():
                cmds.delete(oldShader)