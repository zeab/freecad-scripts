"""

    SOME DESCRIPTION

"""

import FreeCAD
from FreeCAD import Placement, Rotation, Vector
import Draft
import math

# -- Stuff that should be libed out --

DOC = FreeCAD.activeDocument()
DOC_NAME = "NAME"

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

# Create objects
# Create an ellipsoide
def ellipsoid(name, r1, r2, r3, a1 = -90, a2 = 90, a3 = 360, placement = Placement(VEC0, ROT0)):
    ellipsoid = DOC.addObject("Part::Ellipsoid", name)
    ellipsoid.Radius1 = r1
    ellipsoid.Radius2 = r2
    ellipsoid.Radius3 = r3
    ellipsoid.Angle1 = a1
    ellipsoid.Angle2 = a2
    ellipsoid.Angle3 = a3
    ellipsoid.Placement = placement
    return ellipsoid

# Create a prisum of any shape and size
def prism(name, polygons, intraradius, height, placement = Placement(VEC0, ROT0)):
    prism = DOC.addObject("Part::Prism", name)
    prism.Polygon = polygons
    prism.Circumradius = intraradius / math.cos(math.radians(180 / polygons))
    prism.addProperty("App::PropertyFloat", "Intraradius", "Prism")
    prism.Intraradius = intraradius
    prism.Height = height
    prism.Placement = placement    
    return prism

# Create a box
def box(name, length, width, height, placement = Placement(VEC0, ROT0)):
    box = DOC.addObject("Part::Box", name)
    box.Length = length
    box.Width = width
    box.Height = height
    box.Placement = placement
    return box

# Create a cylinder
def cylinder(name, radius, height, placement = Placement(VEC0, ROT0)):
    cylinder = DOC.addObject("Part::Cylinder", name)
    cylinder.Radius = radius
    cylinder.Height = height
    cylinder.Placement = placement
    return cylinder

# Create a wedge shape
def wedge(name, xMin = 0, yMin = 0, zMin = 0, X2min = 0, Z2min = 0, Xmax = 10, Ymax = 10, Zmax = 10, X2Max = 0, Z2Max = 8, placement = Placement(VEC0, ROT0)):
    wedge = DOC.addObject("Part::Wedge", name)
    wedge.Xmin = xMin
    wedge.Ymin = yMin
    wedge.Zmin = zMin
    wedge.X2min = X2min
    wedge.Z2min = Z2min
    wedge.Xmax = Xmax
    wedge.Ymax = Ymax
    wedge.Zmax = Zmax
    wedge.X2max = X2Max
    wedge.Z2max = Z2Max
    wedge.Placement = placement
    return wedge

# Manipulation
# Fuse object together
def fuse(name, objs):
    obj = DOC.addObject("Part::MultiFuse", name)
    obj.Shapes = objs
    obj.Refine = True
    return obj

# Cut the object from the other
def cut(name, base, tool):
    obj = DOC.addObject("Part::Cut", name)
    obj.Base = base
    obj.Tool = tool
    return obj

# Chamfer the obj (flatten)
# obj = chamfer(
#     "some_item", 
#     obj, 
#     [
#         (1, 4, 4),
#         (3, 4, 4),
#     ]
# )
def chamfer(name, base, edges):
    obj = DOC.addObject("Part::Chamfer", name)
    obj.Base = base
    obj.Edges = edges
    base.ViewObject.Visibility = False
    return obj

# Fillet the obj (round)
# obj = fillet(
#     "some_item", 
#     obj, 
#     [
#         (1, 4, 4),
#         (3, 4, 4),
#     ]
# )
def fillet(name, base, edges):
    obj = DOC.addObject("Part::Fillet", name)
    obj.Base = base
    obj.Edges = edges
    base.ViewObject.Visibility = False
    return obj

# Create a new orotho array from the object provided
def orotho_array(obj, x_interval, y_interval, z_interval, x, y, placement=Placement(VEC0, ROT0)):
    obj.Placement = placement
    array = Draft.make_ortho_array(obj, Vector(x, 0, 0), Vector(0, y, 0), VEC0, x_interval, y_interval, z_interval)
    return array

# Miror an object
def mirror(name, objs):
    obj = DOC.addObject("Part::Mirroring", name)
    obj.Source = objs
    return obj

# --------------------------------------




## PUT CODE HERE


# show the shape
DOC.recompute()
setview()
