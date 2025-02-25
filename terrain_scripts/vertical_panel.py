"""vertical_panel.py

    Create a bunch of vertial panels for modular terrain

"""

import FreeCAD
from FreeCAD import Placement, Rotation, Vector
import Draft

DOC = FreeCAD.activeDocument()
DOC_NAME = "support"

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

# Specifics

def create_t_notch(name, shaft_len, shaft_wid, shaft_hei, head_len, head_wid, head_hei):
    shaft = box("shaft", shaft_len, shaft_wid, shaft_hei)
    head = box("head", head_len, head_wid, head_hei)
    head.Placement = Placement(Vector(shaft_len / 2 - (head_len / 2), shaft_wid, 0), ROT0, VEC0)
    obj = fuse(name, (head, shaft))
    return obj



# Settings
scale = 1.0

support_rad = 10 * scale
support_hei = 40 * scale
support_chamfer_outer_edge = 2

notch_shaft_len = 2 * scale # How wide the shaft is
notch_shaft_wid = 4 * scale # How long the shaft is
notch_shaft_hei = support_hei
notch_head_len = 4 * scale # How wide the T bar of the T is
notch_head_wid = 2 * scale # How tall the T bar of the T is
notch_head_hei = support_hei
notch_scale = 0.1

vertical_panel_len = 40 * scale
vertical_panel_wid = 20 * scale
vertical_panel_hei = 5 * scale

vertical_panel = box("vertical_panel_base", vertical_panel_len, vertical_panel_wid, vertical_panel_hei)




# Create the hex mesh that gets taken out of the lid
hex_rad = 3
x_interval = 3
y_interval = 2
z_interval = 1

hex_one = prism("hex_one", 6, hex_rad, vertical_panel_hei)
hex_one.Placement = Placement(Vector(0, 0, 0), Rotation(VEC0, 0))

hex_two = prism("hex_two", 6, hex_rad, vertical_panel_hei)
hex_two.Placement = Placement(Vector(hex_rad * 2, hex_rad, 0), Rotation(VEC0, 0))

hex_pattern = fuse("hex_pattern", (hex_one, hex_two))

punch = Draft.make_ortho_array(hex_pattern, Vector(hex_rad * 4, 0, 0), Vector(0, hex_rad * 2, 0), VEC0, x_interval, y_interval, z_interval)
vertical_panel.Placement = Placement(Vector(-5, -5, 0), Rotation(VEC0, 0))

vertical_panel = cut("vertical_panel_base", vertical_panel, punch) 



notch = create_t_notch("notch", notch_shaft_len - notch_scale, notch_shaft_wid, notch_shaft_hei, notch_head_len - (notch_scale * 2), notch_head_wid - notch_scale, notch_head_hei)
notch.Placement = Placement(Vector(0, vertical_panel_wid * notch_scale, 0), Rotation(VEC0, 90))
#vertical_panel = fuse("vertical_panel_base", (vertical_panel, notch))

#notch = create_t_notch("notch", notch_shaft_len - notch_scale, notch_shaft_wid, notch_shaft_hei, notch_head_len - (notch_scale * 2), notch_head_wid - notch_scale, notch_head_hei)
#notch.Placement = Placement(Vector(vertical_panel_len, (notch_shaft_len - notch_scale) + (vertical_panel_wid - notch_scale) ,0), Rotation(VEC0, 270))
#vertical_panel = fuse("vertical_panel_base", (vertical_panel, notch))



# show the shape
DOC.recompute()
setview()
