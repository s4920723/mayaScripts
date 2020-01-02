import os
import json
from maya import cmds
from PySide2 import QtCore, QtWidgets


class networkBuilder(QtWidgets.QDialog):
    """
    Creates texture and shading networks
    """

    # A dictionary containing information about the name of the nodes and attributes used
    # by different renderer engines. This includes the name of the master shader node, the
    # diffuse, spec, roughness and bump attributes of that shader, the normal map conversion
    # node with its input/output attributes and the the displacement node used by
    shaderAttr = {
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

    def __init__(self):
        # Dialog Settings
        super(networkBuilder, self).__init__()
        self.setWindowTitle('QuickShade')
        self.resize(300, 250)
        self.buildUI()

        # Get JSON with the texture file naming convention
        self.jsonpath = os.path.join(cmds.internalVar(userScriptDir=True), 'quickShader_extensions.json')
        if not os.path.exists(self.jsonpath):
            self.generateExtensionsJSON()

    def buildUI(self):

        mainLayout = QtWidgets.QVBoxLayout(self)

        tabsWidget = QtWidgets.QTabWidget()
        mainLayout.addWidget(tabsWidget, alignmnet=QtCore.Qt.AlignLeft)

        settingsWidget = QtWidgets.QWidget()
        settingsLayout = QtWidgets.QVBoxLayout(settingsWidget)
        tabsWidget.addTab(settingsWidget, 'General')

        engineLabel = QtWidgets.QLabel('Renderer:')
        engineLabel.setAlignment(QtCore.Qt.AlignLeft)
        settingsLayout.addWidget(engineLabel)

        self.engineCB = QtWidgets.QComboBox()
        for item in self.shaderAttr:
            self.engineCB.addItem(item)
        settingsLayout.addWidget(self.engineCB)

        settingsLayout.addSpacing(10)

        shaderNameLabel = QtWidgets.QLabel('Texture Set Name:')
        shaderNameLabel.setAlignment(QtCore.Qt.AlignLeft)
        settingsLayout.addWidget(shaderNameLabel)

        self.shaderNameField = QtWidgets.QLineEdit()
        settingsLayout.addWidget(self.shaderNameField)

        settingsLayout.addSpacing(10)
        textureDirLabel = QtWidgets.QLabel('Texture Folder')
        textureDirLabel.setAlignment(QtCore.Qt.AlignLeft)
        settingsLayout.addWidget(textureDirLabel)

        self.textureDirField = QtWidgets.QLineEdit()
        self.textureDirField.setText('sourceimages/')
        settingsLayout.addWidget(self.textureDirField)

        textureDirBtn = QtWidgets.QPushButton('...')
        textureDirBtn.setMaximumWidth(20)
        textureDirBtn.setMaximumHeight(20)
        textureDirBtn.clicked.connect(self.setDirectory)
        settingsLayout.addWidget(textureDirBtn, 2, 3)

        settingsLayout.addStretch()
        generateBtn = QtWidgets.QPushButton('Generate')
        generateBtn.setMaximumWidth(100)
        # generateBtn.clicked.connect(self.buildShaderNetwork)
        settingsLayout.addWidget(generateBtn, 4, 1)

        # Extensions Menu
        extensionsTab = QtWidgets.QWidget()
        extensionsTab.setMaximumHeight(200)
        extensionsTab.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        extensionsLayout = QtWidgets.QGridLayout(extensionsTab)
        tabsWidget.addTab(extensionsTab, 'Extensions')

        # Maps
        textureTypes = ['Diffuse', 'Specular', 'Roughness', 'Normal']

        for i in range(0, len(textureTypes)):
            textureExtensionLabel = QtWidgets.QLabel('{0}:'.format(textureTypes[i]))
            extensionsLayout.addWidget(textureExtensionLabel, i, 0, alignment=QtCore.Qt.AlignRight)
            textureExtensionField = QtWidgets.QLineEdit()
            textureExtensionField.setMinimumWidth(100)
            extensionsLayout.addWidget(textureExtensionField, i, 1)

        saveExtensionsBtn = QtWidgets.QPushButton('Set Extensions')
        saveExtensionsBtn.setMaximumWidth(100)
        extensionsLayout.addWidget(saveExtensionsBtn, len(textureTypes) + 1, 1)

        closeBtn = QtWidgets.QPushButton('Close')
        closeBtn.clicked.connect(self.close)
        mainLayout.addWidget(closeBtn)

    def setDirectory(self):
        fileDir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose Texture Directory')
        self.textureDirField.setText(fileDir)

    def buildShaderNetwork(self):
        """
        Builds the shader network
        Returns:

        """
        engineInfo = self.shaderAttr[self.engineCB.currentText()]
        shaderNode = cmds.shadingNode(engineInfo.get('shaderNode'), name=self.shaderNameField.text(), asShader=True)

        placeNode = cmds.shadingNode('place2dTexture', asUtility=True)

        # Create and connect diffuse texture
        diffuseTexture = self.buildTextureNetwork(placeNode, self.textureFiles.get('diffuse'))
        diffuseAttr = engineInfo.get('diffuseAttr')
        cmds.connectAttr('{0}.outColor'.format(diffuseTexture), '{0}.{1}'.format(shaderNode, diffuseAttr))

        # Create and connect specular texture
        specularTexture = self.buildTextureNetwork(placeNode, self.textureFiles.get('specular'))
        specularAttr = engineInfo.get('specularAttr')
        cmds.connectAttr('{0}.outColor'.format(specularTexture), '{0}.{1}'.format(shaderNode, specularAttr))

        # Create and connect roughness map
        roughTexture = self.buildTextureNetwork(placeNode, self.textureFiles.get('roughness'))
        roughAttr = engineInfo.get('roughnessAttr')
        if engineInfo.get('inverseRough'):
            reverseRough = cmds.shadingNode('reverse', asUtility=True)
            cmds.connet('{0}.outColor'.format(roughTexture), '{0}.input'.format(reverseRough))
            cmds.connet('{0}.output'.format(reverseRough), '{0}.{1}'.format(shaderNode, roughAttr))
        else:
            cmds.connet('{0}.outColor'.format(roughTexture), '{0}.{1}'.format(shaderNode, roughAttr))

        # Create normal map
        normalTexture = self.buildTextureNetwork(placeNode, self.textureFiles.get('normal'))

        # Create normal utility node
        normalNode = cmds.shadingNode(engineInfo.get('normalNode'), )
        normalIn = engineInfo.get('normalIn')
        normalOut = engineInfo.get('normalOut')
        cmds.connetAttr('{0}.outColor'.format(normalTexture), '{0}.{1}'.format(normalNode, normalIn))

        # Connect normal utility map
        normalAttr = engineInfo.get('normalAttr')
        cmds.connetAttr('{0}.{1}'.format(normalNode, normalOut), '{0}.{1}'.format(shaderNode, normalAttr))

    def buildTextureNetwork(self, placeNode, texturePath):
        """
        Creates a file node and connects it to a place2dTexture node.
        Similar to using Create Pane->File in the node editor.
        Args:
            placeNode: The place2dTexture node that the file node will be connected to
            texturePath: The path of the image that will be used as a texture

        Returns:
            The file node
        """
        fileNode = cmds.shadingNode('file', name='File', isColorManaged=True, asTexture=True)
        cmds.setAttr('{0}.fileTextureName'.format(texturePath))

        # Shortcut for keying most attributes.
        for attr in cmds.listAttr(placeNode, keyable=True):
            if attr in cmds.listAttr(fileNode):
                cmds.connectAttr('{0}.{1}'.format(placeNode, attr), '{0}.{1}'.format(fileNode, attr))

        # Connect all triangle related attributes.
        for attr in cmds.listAttr(placeNode, string='vertex*'):
            if attr in cmds.listAttr(fileNode):
                cmds.connectAttr('{0}.{1}'.format(placeNode, attr), '{0}.{1}'.format(fileNode, attr))

        # Connect UV filter and coordinates
        cmds.connectAttr('{0}.outUvFilterSize'.format(placeNode), '{0}.uvFilterSize'.format(fileNode))
        cmds.connectAttr('{0}.outUV'.format(placeNode), '{0}.uvCoord'.format(fileNode))

        ## Hardcoded connect commands if something breaks
        # cmds.connectAttr('%s.coverage' % placeNode, '%s.coverage' % fileNode)
        # cmds.connectAttr('%s.translateFrame' % placeNode, '%s.translateFrame' % fileNode)
        # cmds.connectAttr('%s.rotateFrame' % placeNode, '%s.rotateFrame' % fileNode)
        # cmds.connectAttr('%s.mirrorU' % placeNode, '%s.mirrorU' % fileNode)
        # cmds.connectAttr('%s.mirrorV' % placeNode, '%s.mirrorV' % fileNode)
        # cmds.connectAttr('%s.stagger' % placeNode, '%s.stagger' % fileNode)
        # cmds.connectAttr('%s.wrapU' % placeNode, '%s.wrapU' % fileNode)
        # cmds.connectAttr('%s.wrapV' % placeNode, '%s.wrapV' % fileNode)
        # cmds.connectAttr('%s.repeatUV' % placeNode, '%s.repeatUV' % fileNode)
        # cmds.connectAttr('%s.rotateUV' % placeNode, '%s.rotateUV' % fileNode)
        # cmds.connectAttr('%s.offset' % placeNode, '%s.offset' % fileNode)
        # cmds.connectAttr('%s.noiseUV' % placeNode, '%s.noiseUV' % fileNode)
        # cmds.connectAttr('%s.vertextUvOne' % placeNode, '%s.vertextUvOne' % fileNode)
        # cmds.connectAttr('%s.vertextUvTwo' % placeNode, '%s.vertextUvTwo' % fileNode)
        # cmds.connectAttr('%s.vertextUvThree' % placeNode, '%s.vertextUvThree' % fileNode)
        # cmds.connectAttr('%s.vertextCameraOne' % placeNode, '%s.vertextCameraOne' % fileNode)
        # cmds.connectAttr('%s.outUvFilterSize' % placeNode, '%s.uvFilterSize' % fileNode)
        # cmds.connectAttr('%s.outUV' % placeNode, '%s.uvCoord' % fileNode)

        return fileNode

    def generateExtensionsJSON(self):
        textureExtensions = {}
        if self.diffuseExtField.text() != '':
            textureExtensions['diffuse'] = self.diffuseExtField
        else:
            textureExtensions['diffuse'] = 'baseColor'

        if self.specExtField.text() != '':
            textureExtensions['specular'] = self.specExtField
        else:
            textureExtensions['specular'] = 'specular'

        if self.roughExtField.text() != '':
            textureExtensions['roughness'] = self.roughExtField
        else:
            textureExtensions['roughness'] = 'roughness'

        if self.normalExtField.text() != '':
            textureExtensions['normal'] = self.normalExtField
        else:
            textureExtensions['normal'] = 'normal'

        with open(self.jsonpath, 'w') as f:
            json.dump(textureExtensions, f, indent=4)

    def getTextureFiles(self, textureType):

        with open(self.jsonpath, 'r') as f:
            textureExt = json.load(f)

        textureFiles = []

        for f in os.listdir(self.textureDir):
            if f.startswith(self.textureName):
                textureFiles.append(f)

        for f in textureFiles:
            if f.endswith(textureExt[textureType]):
                return os.path.abspath(f)

    def setRaw(self):
        pass


ui = networkBuilder()
ui.show()
