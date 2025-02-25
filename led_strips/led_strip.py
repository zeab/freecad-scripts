"""

    Led Strip

"""

import FreeCAD
from FreeCAD import Placement, Rotation, Vector
import Draft
import math

# -- Stuff that should be libed out --

DOC = FreeCAD.activeDocument()
DOC_NAME = "led_strip"

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
amount_of_sections = 3

led_strip_width = 8
led_strip_wall_width = 1
led_strip_width_tolerance = 0.1
led_strip_length = 51 * amount_of_sections
led_strip_height = 3

wedge_length = 20
wedge_width = 8
wedge_height = led_strip_height

# --------------------------------------

#Do the led strip
led_strip = box("led_strip", led_strip_length, led_strip_width + (led_strip_wall_width * 2), led_strip_height)

#Round the 4 edges
led_strip = fillet(
    "led_strip", 
    led_strip, 
    [
        (1, 4, 4),
        (3, 4, 4),
        (5, 4, 4),
        (7, 4, 4),
    ]
)

# Flatten the edges out to half the height of the total
led_strip = chamfer(
    "led_strip", 
    led_strip, 
    [
        (8, led_strip_height / 2, led_strip_height / 2),
    ]
)

# Create the wedge punch
wedge_punch_1 = wedge("wedge_punch", 0, 0, 0, 0, 0, wedge_length, wedge_height, wedge_width + (led_strip_width_tolerance * 2), 0, wedge_width + (led_strip_width_tolerance * 2), Placement(Vector(0, wedge_width + led_strip_wall_width + led_strip_width_tolerance, 0), Rotation(Vector(1, 0, 0), 90)))
wedge_punch_2 = Draft.rotate(wedge_punch_1, 180, Vector(wedge_width + led_strip_wall_width, wedge_length / 4,0), copy=True)
wedge_punch_2.Placement = Placement(Vector(led_strip_length, led_strip_wall_width - led_strip_width_tolerance, 0), Rotation(Vector(0, 0.71, 0.71), 180))

# Carve out a little more from the box
box_punch = box("led_punch", led_strip_length, led_strip_width + (led_strip_width_tolerance * 2), led_strip_height, Placement(Vector(0, led_strip_wall_width - led_strip_width_tolerance, -(led_strip_height / 2)), ROT0))

# Fuse and Cut the box and wedge punches out
wedge_punch = fuse("wedge_punch", (wedge_punch_1, wedge_punch_2, box_punch))
led_strip = cut("led_strip", led_strip, wedge_punch)


# --------------------------------------

# Make a box for the end cover
led_cover = box("led_cover", 18, led_strip_width + (led_strip_width_tolerance * 2) + (led_strip_wall_width * 2) + 3, led_strip_height + 0.6, Placement(Vector(0, -1, -0.6), ROT0))

#Do the led punch
led_punch = box("led_punch", led_strip_length, led_strip_width + (led_strip_wall_width * 2) + (led_strip_width_tolerance * 6), led_strip_height, Placement(Vector(1,0,0), ROT0))

#Round the 4 edges
led_punch = fillet(
    "led_strip", 
    led_punch, 
    [
        (1, 4, 4),
        (3, 4, 4),
        (5, 4, 4),
        (7, 4, 4),
    ]
)

# Flatten the edges out to half the height of the total
led_punch = chamfer(
    "led_strip", 
    led_punch, 
    [
        (8, led_strip_height / 2, led_strip_height / 2),
    ]
)

led_inner_punch = box("led_inner_punch", led_strip_width, 18, led_strip_height, Placement(Vector(1, 1, 0), ROT0))
led_cover = cut("led_cover", led_cover, fuse("led_punch", (led_punch, led_inner_punch)))

# Need to make the other one for the other side
mirror("other_one", led_cover)


# show the shape
DOC.recompute()
setview()