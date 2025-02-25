"""

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
    #obj.Placement = Placement(Vector(0, 0, 0), Rotation(VEC0, 0))
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

# Specifics 
def create_punch(name, head_rad, notch_len, notch_wid, hei):
    head = cylinder("head", head_rad, hei)
    notch = box("notch", notch_len, notch_wid + head_rad, hei)
    notch.Placement = Placement(Vector(-(notch_len / 2), 0, 0), Rotation(VEC0, 0))
    obj = fuse(name, (notch, head))
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

# Smaller punch settings
dmg_token_punch_rad = 9.2

# Bigger punch settings
lore_token_punch_rad = 18.5

# Center token rad
center_token_punch_rad = 14

# Punch settings
punch_len = 14
punch_wid = 8
punch_hei = box_base_hei - box_base_floor_hei # punch height minus whatever base were supposed to have
punch_hollow_percent = 0.60 # how much to size down when were hollowing out the punc
punch_extra_rad = 2.1 # gives the punch some extra room to work with so when we champher later we have the room

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


# Hollow out the bits of the box
# Side A
dmg_token_punch = create_punch("dmg_token_punch", dmg_token_punch_rad, punch_len, punch_wid, punch_hei)
dmg_token_punch.Placement = Placement(VEC0, Rotation(Vector(0,0,1), 180))
punch = create_orotho_array(dmg_token_punch, 4, 1, 1, (dmg_token_punch_rad * 2) + punch_extra_rad, dmg_token_punch_rad * 2)
punch.Placement = Placement(Vector(dmg_token_punch_rad + box_base_wall_wid + box_lid_lip_wid + punch_extra_rad, dmg_token_punch_rad, box_base_floor_hei), Rotation(VEC0, 0))
box_base = cut ("box_base", box_base, punch)

# Side B
dmg_token_punch = create_punch("dmg_token_punch", dmg_token_punch_rad, punch_len, punch_wid, punch_hei)
dmg_token_punch.Placement = Placement(VEC0, Rotation(Vector(0,0,1), 90))
punch = create_orotho_array(dmg_token_punch, 1, 2, 1, (dmg_token_punch_rad * 2), (dmg_token_punch_rad * 2) + punch_extra_rad)
punch.Placement = Placement(Vector(dmg_token_punch_rad, dmg_token_punch_rad + (dmg_token_punch_rad * 2) + punch_extra_rad, box_base_floor_hei), Rotation(VEC0, 0))
box_base = cut ("box_base", box_base, punch)

# Side C
dmg_token_punch = create_punch("dmg_token_punch", dmg_token_punch_rad, punch_len, punch_wid, punch_hei)
punch = create_orotho_array(dmg_token_punch, 2, 1, 1, (dmg_token_punch_rad * 2) + punch_extra_rad, (dmg_token_punch_rad * 2))
punch.Placement = Placement(Vector(dmg_token_punch_rad + (dmg_token_punch_rad * 2), box_base_wid - dmg_token_punch_rad, box_base_floor_hei), Rotation(VEC0, 0))
box_base = cut ("box_base", box_base, punch)

# Side D
lore_token_punch = create_punch("lore_token_punch", lore_token_punch_rad, punch_len, punch_wid, punch_hei)
lore_token_punch.Placement = Placement(Vector(box_base_wid, lore_token_punch_rad + (dmg_token_punch_rad * 2) + punch_extra_rad, box_base_floor_hei), Rotation(Vector(0,0,1), 270))
box_base = cut ("box_base", box_base, lore_token_punch)

# Chamfer down the sides of each of the punches
chamfer_inner_edge = 1
chamfer_outer_edge = 12
edges = [
    (13, chamfer_inner_edge, chamfer_outer_edge),
    (14, chamfer_inner_edge, chamfer_outer_edge),
    (15, chamfer_inner_edge, chamfer_outer_edge),
    (16, chamfer_inner_edge, chamfer_outer_edge),
    (17, chamfer_inner_edge, chamfer_outer_edge),
    (19, chamfer_inner_edge, chamfer_outer_edge),
    (20, chamfer_inner_edge, chamfer_outer_edge),
    (23, chamfer_inner_edge, chamfer_outer_edge),    
    (24, chamfer_inner_edge, chamfer_outer_edge), 
    (25, chamfer_inner_edge, chamfer_outer_edge),
    (26, chamfer_inner_edge, chamfer_outer_edge),
    (28, chamfer_inner_edge, chamfer_outer_edge),
    (29, chamfer_inner_edge, chamfer_outer_edge),
    (30, chamfer_inner_edge, chamfer_outer_edge), 
    (31, chamfer_inner_edge, chamfer_outer_edge),
    (35, chamfer_inner_edge, chamfer_outer_edge),
    (36, chamfer_inner_edge, chamfer_outer_edge),
    (37, chamfer_inner_edge, chamfer_outer_edge),
    (38, chamfer_inner_edge, chamfer_outer_edge), 
    (42, chamfer_inner_edge, chamfer_outer_edge),
    (43, chamfer_inner_edge, chamfer_outer_edge),
    (44, chamfer_inner_edge, chamfer_outer_edge),
    (45, chamfer_inner_edge, chamfer_outer_edge),
    (47, chamfer_inner_edge, chamfer_outer_edge), 
    (48, chamfer_inner_edge, chamfer_outer_edge),
    (49, chamfer_inner_edge, chamfer_outer_edge),
    (50, chamfer_inner_edge, chamfer_outer_edge), 
    (52, chamfer_inner_edge, chamfer_outer_edge),
    (53, chamfer_inner_edge, chamfer_outer_edge), 
    (54, chamfer_inner_edge, chamfer_outer_edge), 
    (55, chamfer_inner_edge, chamfer_outer_edge),
    (57, chamfer_inner_edge, chamfer_outer_edge),
    (58, chamfer_inner_edge, chamfer_outer_edge),
    (59, chamfer_inner_edge, chamfer_outer_edge),
    (60, chamfer_inner_edge, chamfer_outer_edge),
    ]

box_base = chamfer("box_base", box_base, edges)


# Center Hole
center_token_punch = cylinder("center_token_punch", center_token_punch_rad, punch_hei)
center_token_punch.Placement = Placement(Vector(35, 35, box_base_floor_hei), Rotation(VEC0, 0))
box_base = cut ("box_base", box_base, center_token_punch)
edges = [
    (67, chamfer_inner_edge, chamfer_outer_edge),
    ]

box_base = chamfer("box_base", box_base, edges)

# Side A
dmg_token_punch = create_punch("dmg_token_punch", dmg_token_punch_rad * punch_hollow_percent, punch_len * punch_hollow_percent, punch_wid, punch_hei)
dmg_token_punch.Placement = Placement(VEC0, Rotation(Vector(0,0,1), 180))
punch = create_orotho_array(dmg_token_punch, 4, 1, 1, (dmg_token_punch_rad * 2) + punch_extra_rad, dmg_token_punch_rad * 2)
punch.Placement = Placement(Vector(dmg_token_punch_rad + box_base_wall_wid + box_lid_lip_wid + punch_extra_rad, dmg_token_punch_rad, 0), Rotation(VEC0, 0))
box_base = cut ("box_base", box_base, punch)

# Side B
dmg_token_punch = create_punch("dmg_token_punch", dmg_token_punch_rad * punch_hollow_percent, punch_len * punch_hollow_percent, punch_wid, punch_hei)
dmg_token_punch.Placement = Placement(VEC0, Rotation(Vector(0,0,1), 90))
punch = create_orotho_array(dmg_token_punch, 1, 2, 1, (dmg_token_punch_rad * 2), (dmg_token_punch_rad * 2) + punch_extra_rad)
punch.Placement = Placement(Vector(dmg_token_punch_rad, dmg_token_punch_rad + (dmg_token_punch_rad * 2) + punch_extra_rad, 0), Rotation(VEC0, 0))
box_base = cut ("box_base", box_base, punch)

# Side C
dmg_token_punch = create_punch("dmg_token_punch", dmg_token_punch_rad * punch_hollow_percent, punch_len * punch_hollow_percent, punch_wid, punch_hei)
punch = create_orotho_array(dmg_token_punch, 2, 1, 1, (dmg_token_punch_rad * 2) + punch_extra_rad, (dmg_token_punch_rad * 2))
punch.Placement = Placement(Vector(dmg_token_punch_rad + (dmg_token_punch_rad * 2), box_base_wid - dmg_token_punch_rad, 0), Rotation(VEC0, 0))
box_base = cut ("box_base", box_base, punch)

# Side D
lore_token_punch = create_punch("lore_token_punch", lore_token_punch_rad * punch_hollow_percent, punch_len, punch_wid + 10, punch_hei)
lore_token_punch.Placement = Placement(Vector(box_base_wid, lore_token_punch_rad + (dmg_token_punch_rad * 2) + punch_extra_rad, 0), Rotation(Vector(0,0,1), 270))
box_base = cut ("box_base", box_base, lore_token_punch)

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
box_base = cut("token_box", box_base, punch)

# show the shape
DOC.recompute()
setview()
