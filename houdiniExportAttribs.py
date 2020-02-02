import json
import os

filepath = 'C:\Users\chris\Documents\getAttribTest2.json'

node = hou.pwd()
geo = node.geometry()

attribDict = {}
for pt in geo.iterPoints():
    attribDict[pt.number()] = {'P': pt.floatListAttribValue('P'), 'oreint': pt.floatListAttribValue('orient')}
    
with open(filepath, 'w') as f:
    json.dump(attribDict, f, indent = 4)