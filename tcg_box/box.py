"""box.py

    Creates the basic box with a sliding lid

"""

import FreeCAD
from FreeCAD import Placement, Rotation, Vector
import Draft

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

# Create objects
# Create a prisum of any shape and size
def prism(name, polygons, radius, height):
    prism = DOC.addObject("Part::Prism", name)
    prism.Polygon = polygons
    prism.Circumradius = radius
    prism.Height = height
    prism.Placement = Placement(VEC0, ROT0)    
    return prism

# Create a box
def box(name, len, wid, hei):
    box = DOC.addObject("Part::Box", name)
    box.Length = len
    box.Width = wid
    box.Height = hei
    box.Placement = Placement(VEC0, ROT0)
    return box

# Create a cylinder
def cylinder(name, radius, height):
    cylinder = DOC.addObject("Part::Cylinder", name)
    cylinder.Radius = radius
    cylinder.Height = height
    cylinder.Placement = Placement(VEC0, ROT0)
    return cylinder

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

# Chamfer the obj
def chamfer(name, base, edges):
    obj = DOC.addObject("Part::Chamfer", name)
    obj.Base = base
    obj.Edges = edges
    base.ViewObject.Visibility = False
    return obj

# Fillet the obj
def fillet(name, base, edges):
    obj = DOC.addObject("Part::Fillet", name)
    obj.Base = base
    obj.Edges = edges
    base.ViewObject.Visibility = False
    return obj

# Create a new orotho array from the object provided
def create_orotho_array(obj, x_interval, y_interval, z_interval, x, y):
    obj.Placement = Placement(Vector(0, 0, 0), Rotation(VEC0, 0))
    array = Draft.make_ortho_array(obj, Vector(x, 0, 0), Vector(0, y, 0), VEC0, x_interval, y_interval, z_interval)
    return array


def create_lid(name, box_base_len, box_base_wid, box_lid_hei, tolerance, chamferEdges, filletEdges, notch_rad):
    obj =  box(name, box_base_len - (box_base_wall_wid * 2) - tolerance, box_base_wid - box_base_wall_wid - tolerance, box_lid_hei - tolerance)
    if filletEdges:
        obj = fillet(name, obj, filletEdges)
    if chamferEdges:
        obj = chamfer(name, obj, chamferEdges)
    #notch = cylinder("notch", notch_rad - tolerance, box_lid_hei - tolerance)
    #notch = create_orotho_array(notch, 2, 1, 1, 82 - tolerance, 70 - tolerance)
    #notch.Placement = Placement(Vector(2, 18, 0), Rotation(VEC0, 0))
    #obj = fuse(name, (obj,  notch))    
    return obj

def create_hex_pattern(rad, hei):
    hex_one = prism("hex_one", 6, rad, hei)
    hex_one.Placement = Placement(Vector(0, 0, 0), Rotation(VEC0, 0))
    hex_two = prism("hex_two", 6, rad, hei)
    hex_two.Placement = Placement(Vector(rad * 2, rad, 0), Rotation(VEC0, 0))
    hex_pattern = fuse("hex_pattern", (hex_one, hex_two))
    hex_pattern.addProperty("App::PropertyFloat", "Radius", "Subsection", "The radius of the whole object")
    hex_pattern.Radius = rad * 2
    return hex_pattern

# General settings
box_base_len = 90
box_base_wid = 70
box_base_hei = 22

box_base_floor_hei = 1.2 # How much extra space to leave at the bottom
box_base_wall_wid = 1 # How much space to leave on the sides for the lid lip
base_box_fillet_outer_edge = 3 # How much to curve the outer edges of the box

box_lid_hei = 2.2 # The thickness of the lid
box_lid_lip_wid = 1 # How much of a lip should we give the lid when hollowing out the center of the box
box_lid_notch_rad = 2 # How big the notches on the side of the lid are
tolerance = 0.1 # How much give there is between the size of the lid and the hole that's made of it


# Create the box base
box_base = box("box_base", box_base_len, box_base_wid, box_base_hei)


# Fillet the 4 corners of the box
edges = [
    (1, base_box_fillet_outer_edge, base_box_fillet_outer_edge),
    (3, base_box_fillet_outer_edge, base_box_fillet_outer_edge),
    (5, base_box_fillet_outer_edge, base_box_fillet_outer_edge),
    (7, base_box_fillet_outer_edge, base_box_fillet_outer_edge),
    ]
box_base = fillet("box_base", box_base, edges)


# Hollow out the box
punch = box("punch", box_base_len - (box_base_wall_wid * 2) - (box_lid_lip_wid * 2), box_base_wid - (box_base_wall_wid * 2) - (box_lid_lip_wid * 2), box_base_hei - box_base_floor_hei - box_lid_hei)
punch.Placement = Placement(Vector(box_base_wall_wid + box_lid_lip_wid, box_base_wall_wid + box_lid_lip_wid, box_base_floor_hei), Rotation(VEC0, 0))
box_base = cut("box_base", box_base, punch)


# Create the lid punch (only fillet and chamfer 3 of the 4 sides so that the 4th side carves out the space properly for the lip)
filletEdges = [
            (3, base_box_fillet_outer_edge, base_box_fillet_outer_edge),
            (7, base_box_fillet_outer_edge, base_box_fillet_outer_edge),
    ]
chamferEdges = [
        (1, box_lid_hei * 0.75, box_lid_hei * 0.75),
        (6, box_lid_hei * 0.75, box_lid_hei * 0.75),
        (8, box_lid_hei * 0.75, box_lid_hei * 0.75)
    ]
punch = create_lid("punch", box_base_len, box_base_wid, box_lid_hei, 0, chamferEdges, filletEdges, box_lid_notch_rad)
punch.Placement = Placement(Vector(box_base_wall_wid, 0, box_base_hei - box_lid_hei), Rotation(VEC0, 0))
box_base = cut("box_base", box_base, punch)


# Create lid
filletEdges = [
        (1, base_box_fillet_outer_edge, base_box_fillet_outer_edge),
        (3, base_box_fillet_outer_edge, base_box_fillet_outer_edge),
        (5, base_box_fillet_outer_edge, base_box_fillet_outer_edge),
        (7, base_box_fillet_outer_edge, base_box_fillet_outer_edge),
    ]
chamferEdges = [
        (1, box_lid_hei * 0.75, box_lid_hei * 0.75),
        (6, box_lid_hei * 0.75, box_lid_hei * 0.75),
        (8, box_lid_hei * 0.75, box_lid_hei * 0.75),
        (10, box_lid_hei * 0.75, box_lid_hei * 0.75)
    ]
lid_base = create_lid("lid_base", box_base_len, box_base_wid, box_lid_hei, tolerance, chamferEdges, filletEdges, box_lid_notch_rad)



# Apply the hex pattern
r = 6
hex_pattern = create_hex_pattern(r, box_lid_hei)

# Punch the hex in the lid
punch = create_orotho_array(hex_pattern, 3, 4, 1, (r * 2) * 2, r * 2)
punch.Placement = Placement(Vector(12.5, 13, 0), Rotation(VEC0, 0))
lid_base = cut("lid_hex", lid_base, punch)

# Punch the hex in the bottom of the box
r = 6
hex_pattern = create_hex_pattern(r, box_base_floor_hei)
punch = create_orotho_array(hex_pattern, 3, 4, 1, (r * 2) * 2, r * 2)
punch.Placement = Placement(Vector(14.5, 13, 0), Rotation(VEC0, 0))
box_base = cut("box_base", box_base, punch)

# Punch the hex in the wid of the box
r = 3
hex_pattern = create_hex_pattern(r, box_base_wid)
punch = create_orotho_array(hex_pattern, 7, 2, 1, (r * 2) * 2, r * 2)
punch.Placement = Placement(Vector(6, box_base_wid, 6), Rotation(Vector(90, 0, 0), 90))
box_base = cut("box_base", box_base, punch)

# Punch the hex in the len of the box
r = 3
hex_pattern = create_hex_pattern(r, box_base_len)
punch = create_orotho_array(hex_pattern, 5, 2, 1, (r * 2) * 2, r * 2)
punch.Placement = Placement(Vector(-62, box_base_len, 6), Rotation(Vector(90, 0, 0), 90))
box_base.Placement = Placement(Vector(0, 0, 0), Rotation(Vector(0, 0, 90), 90))
box_base = cut("box", box_base, punch)

box_base.Placement = Placement(Vector(0, 0, 0), Rotation(Vector(0, 0, 90), -90))

# show the shape
DOC.recompute()
setview()
