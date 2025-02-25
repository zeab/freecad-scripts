"""box.py

    Creates the basic box with a sliding lid

"""

import FreeCAD
from FreeCAD import Placement, Rotation, Vector
import Draft
import importSVG

DOC = FreeCAD.activeDocument()
DOC_NAME = "tcg_box"

# DOC methods

def clear_doc():
    """Clear activeDocument deleting all the objects."""
    for obj in DOC.Objects:
        DOC.removeObject(obj.Name)

def setview():
    """Rearrange View."""
    FreeCAD.Gui.SendMsgToActiveView("ViewFit")
    FreeCAD.Gui.activeDocument().activeView().viewAxometric()

if DOC is None:
    FreeCAD.newDocument(DOC_NAME)
    FreeCAD.setActiveDocument(DOC_NAME)
    DOC = FreeCAD.activeDocument()
else:
    clear_doc()

# Constants
ROT0 = Rotation(0, 0, 0)
VEC0 = Vector(0, 0, 0)


def extrude_object(name):
    DOC.addObject('Part::Extrusion','Extrude')
    obj = DOC.getObject('Extrude')
    obj.Base = DOC.getObject(name)
    obj.DirMode = "Normal"
    obj.DirLink = None
    obj.LengthFwd = 10.000000000000000
    obj.LengthRev = 0.000000000000000
    obj.Solid = True
    obj.Reversed = False
    obj.Symmetric = False
    obj.TaperAngle = 0.000000000000000
    obj.TaperAngleRev = 0.000000000000000
    DOC.getObject(name).Visibility = False
    obj.Placement = Placement(Vector(0, 0, 0), Rotation(VEC0, 0))
    return obj

importSVG.open("C:/Mine/tcg_box/christmas-tree-template-blank-outline-rounded.svg")
# Move it to the token box doc
#FreeCAD.getDocument('token_box').moveObject(FreeCAD.getDocument('smaller_svg').getObject('path1'), True)
# Close the other doc
#FreeCAD.closeDocument("smaller_svg")

# Extrue the object
extrude_object("path1")

# mickey_two = DOC.copyObject(f, True)
# mickey_two.Placement = Placement(Vector(hex_rad * 2, hex_rad, 0), Rotation(VEC0, 0))

# mickey_punch = fuse( "mickey_punch", (f, mickey_two))

# punch2 = Draft.make_ortho_array(mickey_punch, Vector(hex_rad * 4, 0, 0), Vector(0, hex_rad * 2, 0), VEC0, x_interval, y_interval, z_interval)
# punch2.Placement = Placement(Vector(9, 14, 56), Rotation(VEC0, 0))

# token_box_lid2 = cut(token_box_lid2, punch2, "lid_mickey") 

# show the shape
DOC.recompute()
setview()
