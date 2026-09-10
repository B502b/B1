"""
Precinct 24 Police Headquarters -- FiveM MLO (professional blockout)
===================================================================
Original concept, drafted from scratch. Not a copy of any existing
server's MLO and not affiliated with Rockstar Games / FiveM.

What this build produces
------------------------
A furnished, materialed 3D blockout of the four-level building shown in
the companion "Precinct 24 Blueprints" sheet set:

  * Wall shells with REAL openings -- framed doors (with leaves) and
    window bands (with glass panes), not just gaps.
  * Floor slabs, ceilings and a perimeter roof parapet.
  * A proper straight-run staircase with landings and railings in the
    central core, plus per-floor elevator doors, connecting every level.
  * Sized proxy furniture in every room (desks, lockers, shelving,
    server/gun racks, dispatch consoles, seating, conference tables,
    holding-cell bars, a rooftop helipad) so the interior reads as a
    designed space, each anchored by a PROP_* empty for easy swapping.
  * A named material set and a camera + sun rig so a test render looks
    presentable straight away.

How to run
----------
1. Blender -> Scripting tab -> open this file -> Run Script (Alt+P).
   Or headless:  blender --background --python precinct24_blockout.py
2. Output is grouped in a 'Precinct24_HQ' collection, one sub-collection
   per level (B1 / L1 / L2 / L3) plus 'Roof' and 'Rig'.
3. Every PROP_* empty marks where a real prop belongs. Install Sollumz,
   load your own legally-owned GTA V asset archive, and swap each proxy
   for the real prop (no game assets ship here -- only blockout geometry
   and naming). Then export ydr/ytyp/ymap and wire doors + job locks in
   FiveM as described in the blueprint sheet.

Units: 1 Blender unit = 1 meter.
"""

import bpy
import math

# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------

FLOOR_HEIGHT = 4.0
SLAB = 0.30
WALL_H = FLOOR_HEIGHT - SLAB
WALL_T = 0.20

DOOR_W, DOOR_H = 1.2, 2.1
WIN_W, WIN_SILL, WIN_HEAD = 1.4, 1.1, 2.6
WIN_PITCH = 3.2                       # target spacing between window centers
PANE_T = 0.06

CORE = {"x": 16.0, "y": 0.0, "w": 4.0, "d": 22.0}
CORRIDORS = [
    {"x": 0.0, "y": 9.0, "w": 16.0, "d": 4.0},
    {"x": 20.0, "y": 9.0, "w": 16.0, "d": 4.0},
]
BUILDING = {"w": 36.0, "d": 22.0}

# ---------------------------------------------------------------------------
# Room data -- mirrors the blueprint sheet exactly (x, y, w, d in meters)
# ---------------------------------------------------------------------------

FLOORS = {
    "B1": {
        "z": 0.0, "title": "Basement - Holding & Evidence Level",
        "rooms": [
            dict(code="B-01", name="Sally Port / Prisoner Intake", x=0, y=0, w=10, d=9, type="garage",
                 exterior="w", props=["ROLLERDOOR", "VAN_MARKER", "TIRE_SPIKES"]),
            dict(code="B-02", name="Booking & Processing", x=10, y=0, w=6, d=9, type="room",
                 props=["DESK_BOOKING", "MUGSHOT_WALL", "FINGERPRINT"]),
            dict(code="B-03", name="Interrogation A", x=20, y=0, w=4, d=4.5, type="restricted",
                 props=["TABLE_INTERROGATION", "MIRROR_ONEWAY"]),
            dict(code="B-04", name="Interrogation B", x=20, y=4.5, w=4, d=4.5, type="restricted",
                 props=["TABLE_INTERROGATION", "CAMERA_WALL"]),
            dict(code="B-05", name="Holding Cell Block", x=24, y=0, w=12, d=9, type="restricted",
                 cells=6, props=["CELLBARS"]),
            dict(code="B-06", name="Evidence Storage", x=0, y=13, w=10, d=9, type="restricted",
                 props=["SHELVING_EVIDENCE", "LOCKER_EVIDENCE", "DESK_SIGNOUT"]),
            dict(code="B-07", name="Armory / Weapons Vault", x=10, y=13, w=6, d=9, type="restricted",
                 props=["GUNRACK", "AMMO_CRATE", "VAULT_DOOR"]),
            dict(code="B-08", name="Server Room", x=20, y=13, w=4, d=4.5, type="room",
                 props=["SERVER_RACK", "UPS_UNIT"]),
            dict(code="B-09", name="Records Archive", x=20, y=17.5, w=4, d=4.5, type="room",
                 props=["FILING_CABINET", "ARCHIVE_BOX"]),
            dict(code="B-10", name="Staff Break Room", x=24, y=13, w=6, d=9, type="room",
                 props=["TABLE_BREAK", "VENDING", "LOCKER_STAFF"]),
            dict(code="B-11", name="Electrical / Utility", x=30, y=13, w=6, d=9, type="room",
                 props=["BREAKER_PANEL", "WATER_HEATER", "SHELVING_UTILITY"]),
        ],
    },
    "L1": {
        "z": FLOOR_HEIGHT, "title": "Ground Floor - Public & Operations Level",
        "rooms": [
            dict(code="G-01", name="Main Entrance & Lobby", x=0, y=0, w=10, d=9, type="public",
                 exterior="w", entry=True, props=["SEATING_LOBBY", "SEAL_PLAQUE"]),
            dict(code="G-02", name="Reception / Front Desk", x=10, y=0, w=6, d=9, type="public",
                 props=["RECEPTION_DESK", "KIOSK_SIGNIN"]),
            dict(code="G-03", name="Briefing Room", x=20, y=0, w=4, d=9, type="room",
                 props=["PODIUM", "CHAIR_ROW", "WHITEBOARD"]),
            dict(code="G-04", name="Patrol Officer Bullpen", x=24, y=0, w=12, d=9, type="room",
                 props=["DESK_PATROL", "DESK_PATROL", "FILING_CABINET", "WATER_COOLER"]),
            dict(code="G-05", name="Vehicle Garage Bay", x=0, y=13, w=16, d=9, type="garage",
                 exterior="s", props=["ROLLERDOOR", "CRUISER_MARK", "FUEL_PUMP", "TOOL_BENCH"]),
            dict(code="G-06", name="Patrol Locker Room", x=20, y=13, w=4, d=9, type="room",
                 props=["LOCKER_STAFF", "BENCH_LOCKER"]),
            dict(code="G-07", name="Public Waiting Area", x=24, y=13, w=6, d=9, type="public",
                 props=["CHAIR_WAITING", "TV_WALL", "NOTICE_BOARD"]),
            dict(code="G-08", name="Restroom - Men", x=30, y=13, w=3, d=9, type="room",
                 props=["SINK", "STALL"]),
            dict(code="G-09", name="Restroom - Women", x=33, y=13, w=3, d=9, type="room",
                 props=["SINK", "STALL"]),
        ],
    },
    "L2": {
        "z": FLOOR_HEIGHT * 2, "title": "2nd Floor - Detective & Forensics Level",
        "rooms": [
            dict(code="D-01", name="Detective Bullpen", x=0, y=0, w=16, d=9, type="room",
                 props=["DESK_DETECTIVE", "DESK_DETECTIVE", "CORKBOARD_CASE"]),
            dict(code="D-02", name="Captain's Office", x=20, y=0, w=4, d=9, type="room",
                 props=["DESK_EXEC", "BOOKSHELF"]),
            dict(code="D-03", name="Forensics Lab", x=24, y=0, w=6, d=9, type="restricted",
                 props=["LAB_BENCH", "MICROSCOPE", "EVIDENCE_BAG"]),
            dict(code="D-04", name="Conference Room", x=30, y=0, w=6, d=9, type="room",
                 props=["TABLE_CONFERENCE", "PROJECTOR_SCREEN"]),
            dict(code="D-05", name="Records / File Room", x=0, y=13, w=10, d=9, type="room",
                 props=["FILING_CABINET", "SHELVING_ARCHIVE"]),
            dict(code="D-06", name="Detective Break Room", x=10, y=13, w=6, d=9, type="room",
                 props=["TABLE_BREAK", "KITCHENETTE"]),
            dict(code="D-07", name="IT / Storage Closet", x=20, y=13, w=4, d=9, type="room",
                 props=["SHELVING_UTILITY", "NETWORK_RACK"]),
            dict(code="D-08", name="Locker Room - Men", x=24, y=13, w=3, d=9, type="room",
                 props=["LOCKER_STAFF", "BENCH_LOCKER"]),
            dict(code="D-09", name="Locker Room - Women", x=27, y=13, w=3, d=9, type="room",
                 props=["LOCKER_STAFF", "BENCH_LOCKER"]),
            dict(code="D-10", name="Tactical Armory", x=30, y=13, w=6, d=9, type="restricted",
                 props=["GEARRACK_TACTICAL", "VEST_RACK", "HELMET_RACK"]),
        ],
    },
    "L3": {
        "z": FLOOR_HEIGHT * 3, "title": "3rd Floor - Command Level",
        "rooms": [
            dict(code="C-01", name="Chief of Police Suite", x=0, y=0, w=16, d=9, type="room",
                 props=["DESK_EXEC", "SEATING_LOUNGE", "TROPHY_CASE"]),
            dict(code="C-02", name="IT / Server Closet", x=20, y=0, w=4, d=9, type="room",
                 props=["SERVER_RACK", "PATCH_PANEL"]),
            dict(code="C-03", name="Command Center / Dispatch", x=24, y=0, w=12, d=9, type="restricted",
                 props=["CONSOLE_DISPATCH", "CONSOLE_DISPATCH", "MONITOR_WALL", "CITY_MAP"]),
            dict(code="C-04", name="Executive Conference", x=0, y=13, w=16, d=9, type="room",
                 props=["TABLE_CONFERENCE", "AV_SCREEN"]),
            dict(code="C-05", name="Storage", x=20, y=13, w=4, d=9, type="room",
                 props=["SHELVING_UTILITY"]),
            dict(code="C-06", name="Rooftop Terrace / Helipad", x=24, y=13, w=12, d=9, type="outdoor",
                 props=["HELIPAD", "RAILING", "HVAC_UNIT"]),
        ],
    },
}
FLOOR_ORDER = ["B1", "L1", "L2", "L3"]


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

def new_mat(name, rgb, rough=0.85, metal=0.0, alpha=1.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        mat.blend_method = "BLEND"
    mat.diffuse_color = (rgb[0], rgb[1], rgb[2], alpha)   # viewport solid-shading color
    return mat


def build_materials():
    return {
        "concrete":   new_mat("P24_Concrete",   (0.62, 0.62, 0.60), 0.90),
        "wall_res":   new_mat("P24_WallRestr",  (0.52, 0.32, 0.30), 0.88),
        "floor":      new_mat("P24_Floor",      (0.28, 0.30, 0.34), 0.65),
        "floor_pub":  new_mat("P24_FloorPublic",(0.55, 0.53, 0.47), 0.55),
        "floor_gar":  new_mat("P24_FloorGarage",(0.17, 0.17, 0.19), 0.75),
        "glass":      new_mat("P24_Glass",      (0.35, 0.52, 0.60), 0.08, 0.0, 0.28),
        "metal":      new_mat("P24_Metal",      (0.46, 0.48, 0.51), 0.35, 0.9),
        "metal_dark": new_mat("P24_MetalDark",  (0.20, 0.21, 0.24), 0.45, 0.85),
        "accent":     new_mat("P24_Accent",     (0.82, 0.60, 0.10), 0.55, 0.3),
        "red":        new_mat("P24_Red",        (0.55, 0.16, 0.13), 0.7),
        "wood":       new_mat("P24_Wood",       (0.45, 0.30, 0.18), 0.6),
        "fabric":     new_mat("P24_Fabric",     (0.22, 0.32, 0.48), 0.8),
        "roof":       new_mat("P24_Roof",       (0.33, 0.33, 0.35), 0.9),
        "terrace":    new_mat("P24_Terrace",    (0.26, 0.38, 0.29), 0.85),
        "screen":     new_mat("P24_Screen",     (0.10, 0.14, 0.20), 0.25),
        "trim":       new_mat("P24_Trim",       (0.15, 0.15, 0.16), 0.5),
    }


# ---------------------------------------------------------------------------
# Low-level geometry
# ---------------------------------------------------------------------------

def get_coll(name, parent=None):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    coll = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(coll)
    return coll


def box(name, cx, cy, cz, sx, sy, sz, coll, mat=None):
    """Axis-aligned box centered at (cx,cy,cz) with full size (sx,sy,sz)."""
    if sx <= 0 or sy <= 0 or sz <= 0:
        return None
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    verts = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
             (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj.location = (cx, cy, cz)
    if mat:
        obj.data.materials.append(mat)
    return obj


def cyl(name, cx, cy, cz, radius, height, coll, mat=None, seg=28):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    verts, faces = [], []
    hz = height / 2
    for i in range(seg):
        a = 2 * math.pi * i / seg
        verts.append((radius * math.cos(a), radius * math.sin(a), -hz))
    for i in range(seg):
        a = 2 * math.pi * i / seg
        verts.append((radius * math.cos(a), radius * math.sin(a), hz))
    for i in range(seg):
        j = (i + 1) % seg
        faces.append((i, j, seg + j, seg + i))
    faces.append(tuple(range(seg - 1, -1, -1)))          # bottom cap
    faces.append(tuple(range(seg, 2 * seg)))             # top cap
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj.location = (cx, cy, cz)
    if mat:
        obj.data.materials.append(mat)
    return obj


def anchor(name, x, y, z, coll, size=0.3):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "ARROWS"
    e.empty_display_size = size
    e.location = (x, y, z)
    coll.objects.link(e)
    return e


def label(text, x, y, z, coll, size=0.4):
    cu = bpy.data.curves.new("lbl", type="FONT")
    cu.body, cu.align_x, cu.align_y, cu.size = text, "CENTER", "CENTER", size
    obj = bpy.data.objects.new("TXT_" + text[:24], cu)
    obj.location = (x, y, z)
    coll.objects.link(obj)
    return obj


# ---------------------------------------------------------------------------
# Walls with openings
# ---------------------------------------------------------------------------

def leaf_mat(kind, room_type, M):
    if kind == "window":
        return M["glass"]
    if kind == "entry":
        return M["glass"]
    if kind == "roller":
        return M["accent"]
    return M["metal_dark"] if room_type == "restricted" else M["wood"]


def make_windows(a, b, sill=WIN_SILL, head=WIN_HEAD):
    length = b - a
    if length < WIN_W + 0.8:
        return []
    n = max(1, int(length // WIN_PITCH))
    pitch = length / n
    out = []
    for i in range(n):
        c = a + pitch * (i + 0.5)
        out.append(dict(a=c - WIN_W / 2, b=c + WIN_W / 2, sill=sill, head=head, kind="window"))
    return out


def build_wall(orient, fixed, a, b, z, coll, M, openings, room_type):
    """orient 'H' -> runs along X at Y=fixed; 'V' -> runs along Y at X=fixed."""
    wall_mat = M["wall_res"] if room_type == "restricted" else M["concrete"]

    def solid(s0, s1, zc, h, tag):
        if s1 - s0 <= 1e-4:
            return
        if orient == "H":
            box(tag, (s0 + s1) / 2, fixed, zc, s1 - s0, WALL_T, h, coll, wall_mat)
        else:
            box(tag, fixed, (s0 + s1) / 2, zc, WALL_T, s1 - s0, h, coll, wall_mat)

    def pane(s0, s1, z0, z1, tag, mat):
        if s1 - s0 <= 1e-4 or z1 - z0 <= 1e-4:
            return
        if orient == "H":
            box(tag, (s0 + s1) / 2, fixed, (z0 + z1) / 2, (s1 - s0) - 0.05, PANE_T, z1 - z0, coll, mat)
        else:
            box(tag, fixed, (s0 + s1) / 2, (z0 + z1) / 2, PANE_T, (s1 - s0) - 0.05, z1 - z0, coll, mat)

    ops = sorted(openings, key=lambda o: o["a"])
    cursor = a
    for i, o in enumerate(ops):
        solid(cursor, o["a"], z + WALL_H / 2, WALL_H, f"wall_seg{i}")
        if o["sill"] > 0:                                       # apron below opening
            solid(o["a"], o["b"], z + o["sill"] / 2, o["sill"], f"wall_sill{i}")
        if o["head"] < WALL_H:                                  # lintel above opening
            solid(o["a"], o["b"], z + o["head"] + (WALL_H - o["head"]) / 2, WALL_H - o["head"], f"wall_lint{i}")
        pane(o["a"], o["b"], z + o["sill"], z + o["head"], f"wall_leaf{i}", leaf_mat(o["kind"], room_type, M))
        cursor = o["b"]
    solid(cursor, b, z + WALL_H / 2, WALL_H, "wall_segEnd")


def build_room_shell(room, z, level_key, coll, M):
    x, y, w, d, code = room["x"], room["y"], room["w"], room["d"], room["code"]
    rtype = room["type"]
    x2, y2 = x + w, y + d
    windows_ok = level_key != "B1" and rtype not in ("restricted", "garage")

    def perim_x(v):
        return abs(v) < 1e-6 or abs(v - BUILDING["w"]) < 1e-6

    def perim_y(v):
        return abs(v) < 1e-6 or abs(v - BUILDING["d"]) < 1e-6

    # NORTH (horizontal at y)
    ops = []
    if abs(y - 13.0) < 1e-6:
        ops = [dict(a=(x + x2) / 2 - DOOR_W / 2, b=(x + x2) / 2 + DOOR_W / 2, sill=0, head=DOOR_H, kind="door")]
    elif perim_y(y) and windows_ok:
        ops = make_windows(x + 0.3, x2 - 0.3)
    build_wall("H", y, x, x2, z, coll, M, ops, rtype)

    # SOUTH (horizontal at y2)
    ops = []
    if room.get("exterior") == "s":
        c = (x + x2) / 2
        ops = [dict(a=c - 3.0, b=c + 3.0, sill=0, head=3.2, kind="roller")]
    elif abs(y2 - 9.0) < 1e-6:
        ops = [dict(a=(x + x2) / 2 - DOOR_W / 2, b=(x + x2) / 2 + DOOR_W / 2, sill=0, head=DOOR_H, kind="door")]
    elif perim_y(y2) and windows_ok:
        ops = make_windows(x + 0.3, x2 - 0.3)
    build_wall("H", y2, x, x2, z, coll, M, ops, rtype)

    # WEST (vertical at x)
    ops = []
    if room.get("exterior") == "w":
        c = (y + y2) / 2
        if room.get("entry"):
            ops = [dict(a=c - 1.1, b=c + 1.1, sill=0, head=2.4, kind="entry")]
        else:
            ops = [dict(a=c - 2.0, b=c + 2.0, sill=0, head=3.2, kind="roller")]
    elif perim_x(x) and windows_ok:
        ops = make_windows(y + 0.3, y2 - 0.3)
    build_wall("V", x, y, y2, z, coll, M, ops, rtype)

    # EAST (vertical at x2)
    ops = []
    if perim_x(x2) and windows_ok:
        ops = make_windows(y + 0.3, y2 - 0.3)
    build_wall("V", x2, y, y2, z, coll, M, ops, rtype)


# ---------------------------------------------------------------------------
# Furniture proxies  (all axis-aligned; anchored by a PROP_ empty)
# ---------------------------------------------------------------------------

def f_desk(cx, cy, z, coll, M, code, key, w=1.6, dp=0.8):
    anchor(f"PROP_{code}_{key}", cx, cy, z, coll)
    box(f"{code}_{key}_top", cx, cy, z + 0.74, w, dp, 0.05, coll, M["wood"])
    box(f"{code}_{key}_panel", cx, cy + dp / 2 - 0.03, z + 0.36, w, 0.04, 0.72, coll, M["wood"])
    box(f"{code}_{key}_mon", cx, cy - 0.2, z + 1.0, 0.5, 0.05, 0.32, coll, M["screen"])
    box(f"{code}_{key}_chair", cx, cy - 0.55, z + 0.25, 0.5, 0.5, 0.5, coll, M["fabric"])
    box(f"{code}_{key}_chairbk", cx, cy - 0.78, z + 0.65, 0.5, 0.05, 0.5, coll, M["fabric"])


def f_reception(cx, cy, z, coll, M, code, key, w=3.0, dp=0.9):
    anchor(f"PROP_{code}_{key}", cx, cy, z, coll)
    box(f"{code}_{key}_body", cx, cy, z + 0.55, w, dp, 1.1, coll, M["wood"])
    box(f"{code}_{key}_ledge", cx, cy - dp / 2 - 0.08, z + 1.05, w, 0.25, 0.05, coll, M["metal"])


def f_seating(cx, cy, z, coll, M, code, key, w=2.0):
    anchor(f"PROP_{code}_{key}", cx, cy, z, coll)
    box(f"{code}_{key}_base", cx, cy, z + 0.22, w, 0.7, 0.4, coll, M["fabric"])
    box(f"{code}_{key}_back", cx, cy + 0.32, z + 0.55, w, 0.12, 0.5, coll, M["fabric"])


def f_locker(cx, cy, z, coll, M, code, key, w=1.8):
    anchor(f"PROP_{code}_{key}", cx, cy, z, coll)
    box(f"{code}_{key}_body", cx, cy, z + 0.9, w, 0.45, 1.8, coll, M["metal"])
    n = max(2, int(w / 0.35))
    for i in range(1, n):
        box(f"{code}_{key}_seam{i}", cx - w / 2 + i * w / n, cy - 0.23, z + 0.9, 0.02, 0.02, 1.7, coll, M["trim"])


def f_shelving(cx, cy, z, coll, M, code, key, w=2.0):
    anchor(f"PROP_{code}_{key}", cx, cy, z, coll)
    box(f"{code}_{key}_frame", cx, cy, z + 1.0, w, 0.5, 2.0, coll, M["metal"])
    for i in range(1, 4):
        box(f"{code}_{key}_shelf{i}", cx, cy, z + i * 0.5, w - 0.04, 0.46, 0.03, coll, M["trim"])


def f_rack(cx, cy, z, coll, M, code, key):
    anchor(f"PROP_{code}_{key}", cx, cy, z, coll)
    box(f"{code}_{key}_body", cx, cy, z + 1.0, 0.7, 0.9, 2.0, coll, M["metal_dark"])
    for i in range(6):
        box(f"{code}_{key}_led{i}", cx - 0.3 + (i % 2) * 0.6, cy - 0.46, z + 0.5 + i * 0.22, 0.06, 0.02, 0.06, coll, M["accent"])


def f_table(cx, cy, z, coll, M, code, key, w=2.4, dp=1.1):
    anchor(f"PROP_{code}_{key}", cx, cy, z, coll)
    box(f"{code}_{key}_top", cx, cy, z + 0.74, w, dp, 0.06, coll, M["wood"])
    for sx in (-w / 2 + 0.2, w / 2 - 0.2):
        for sy in (-dp / 2 + 0.2, dp / 2 - 0.2):
            box(f"{code}_{key}_leg", cx + sx, cy + sy, z + 0.36, 0.08, 0.08, 0.72, coll, M["metal_dark"])


def f_console(cx, cy, z, coll, M, code, key, w=2.6):
    anchor(f"PROP_{code}_{key}", cx, cy, z, coll)
    box(f"{code}_{key}_desk", cx, cy, z + 0.5, w, 1.0, 1.0, coll, M["metal_dark"])
    box(f"{code}_{key}_screens", cx, cy + 0.35, z + 1.35, w, 0.08, 0.6, coll, M["screen"])


def f_bench(cx, cy, z, coll, M, code, key, w=1.6):
    anchor(f"PROP_{code}_{key}", cx, cy, z, coll)
    box(f"{code}_{key}_seat", cx, cy, z + 0.22, w, 0.4, 0.08, coll, M["wood"])
    for sx in (-w / 2 + 0.15, w / 2 - 0.15):
        box(f"{code}_{key}_leg", cx + sx, cy, z + 0.11, 0.06, 0.36, 0.22, coll, M["metal_dark"])


def f_appliance(cx, cy, z, coll, M, code, key, w=0.8, dp=0.7, h=1.7):
    anchor(f"PROP_{code}_{key}", cx, cy, z, coll)
    box(f"{code}_{key}_body", cx, cy, z + h / 2, w, dp, h, coll, M["metal"])


def f_mounted(cx, cy_wall, z, coll, M, code, key, w=1.4, h=0.9, face=1):
    """Thin wall-mounted panel (mirror, board, screen, plaque)."""
    anchor(f"PROP_{code}_{key}", cx, cy_wall, z + 1.6, coll)
    box(f"{code}_{key}_panel", cx, cy_wall, z + 1.6, w, 0.08, h, coll, M["screen"])


def f_helipad(cx, cy, z, coll, M, code, key):
    anchor(f"PROP_{code}_{key}", cx, cy, z, coll)
    cyl(f"{code}_{key}_pad", cx, cy, z + 0.04, 3.4, 0.08, coll, M["metal_dark"])
    cyl(f"{code}_{key}_ring", cx, cy, z + 0.09, 3.4, 0.02, coll, M["accent"], seg=40)
    box(f"{code}_{key}_H_l", cx - 0.9, cy, z + 0.1, 0.25, 2.4, 0.03, coll, M["accent"])
    box(f"{code}_{key}_H_r", cx + 0.9, cy, z + 0.1, 0.25, 2.4, 0.03, coll, M["accent"])
    box(f"{code}_{key}_H_c", cx, cy, z + 0.1, 1.8, 0.25, 0.03, coll, M["accent"])


def railing(x1, y1, x2, y2, z, coll, M, tag, height=1.05):
    length = math.hypot(x2 - x1, y2 - y1)
    n = max(2, int(length / 0.9))
    for i in range(n + 1):
        t = i / n
        box(f"{tag}_post{i}", x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, z + height / 2, 0.06, 0.06, height, coll, M["metal"])
    box(f"{tag}_rail", (x1 + x2) / 2, (y1 + y2) / 2, z + height,
        max(abs(x2 - x1), 0.06), max(abs(y2 - y1), 0.06), 0.06, coll, M["metal"])


# ---------------------------------------------------------------------------
# Prop routing + layout
# ---------------------------------------------------------------------------

CENTER_KEYS = ("DESK", "RECEPTION", "TABLE", "CONSOLE", "PODIUM", "LAB_BENCH", "TOOL_BENCH", "KITCHENETTE")
MOUNT_KEYS = ("MIRROR", "CAMERA", "SEAL", "WHITEBOARD", "TV", "NOTICE", "PROJECTOR", "AV", "MAP",
              "CORKBOARD", "MONITOR_WALL", "MUGSHOT", "PATCH", "SCREEN")


def build_prop(key, cx, cy, z, coll, M, code, room, back_y):
    k = key
    if any(s in k for s in ("RECEPTION",)):
        f_reception(cx, cy, z, coll, M, code, k)
    elif any(s in k for s in ("DESK",)):
        f_desk(cx, cy, z, coll, M, code, k)
    elif any(s in k for s in ("CONSOLE", "DISPATCH")):
        f_console(cx, cy, z, coll, M, code, k)
    elif any(s in k for s in ("TABLE", "PODIUM", "LAB_BENCH", "TOOL_BENCH", "KITCHENETTE")):
        f_table(cx, cy, z, coll, M, code, k)
    elif any(s in k for s in ("SEATING", "SOFA", "LOUNGE", "CHAIR", "WAITING")):
        f_seating(cx, cy, z, coll, M, code, k)
    elif any(s in k for s in ("LOCKER",)):
        f_locker(cx, cy, z, coll, M, code, k)
    elif any(s in k for s in ("SHELVING", "ARCHIVE", "FILING", "CABINET", "TROPHY", "BOOKSHELF", "VEST", "HELMET")):
        f_shelving(cx, cy, z, coll, M, code, k)
    elif any(s in k for s in ("RACK", "SERVER", "GUNRACK", "GEARRACK", "NETWORK")):
        f_rack(cx, cy, z, coll, M, code, k)
    elif any(s in k for s in ("BENCH",)):
        f_bench(cx, cy, z, coll, M, code, k)
    elif any(s in k for s in ("HELIPAD",)):
        f_helipad(cx, cy, z, coll, M, code, k)
    elif any(s in k for s in ("HVAC", "VENDING", "WATER", "BREAKER", "HEATER", "FUEL", "UPS",
                              "SINK", "STALL", "FINGERPRINT", "KIOSK", "AMMO", "CRATE", "BOX",
                              "MICROSCOPE", "EVIDENCE", "TIRE", "VAN", "CRUISER")):
        f_appliance(cx, cy, z, coll, M, code, k)
    elif any(s in k for s in MOUNT_KEYS):
        f_mounted(cx, back_y, z, coll, M, code, k)
    else:
        anchor(f"PROP_{code}_{k}", cx, cy, z, coll)


def place_props(room, z, coll, M):
    x, y, w, d, code = room["x"], room["y"], room["w"], room["d"], room["code"]
    props = room.get("props", [])
    south_zone = abs(y - 13.0) < 1e-6
    back_y = (y + 0.55) if not south_zone else (y + d - 0.55)   # wall opposite the door
    inset = 0.85

    center = [p for p in props if any(s in p for s in CENTER_KEYS)]
    mounted = [p for p in props if any(s in p for s in MOUNT_KEYS)]
    wall = [p for p in props if p not in center and p not in mounted]

    def spread(items, yline, tag_default):
        n = len(items)
        if n == 0:
            return
        for i, p in enumerate(items):
            cx = x + inset + (w - 2 * inset) * ((i + 0.5) / n)
            build_prop(p, cx, yline, z, coll, M, code, room, back_y)

    spread(center, y + d / 2, "center")
    spread(wall, back_y + (0.35 if not south_zone else -0.35), "wall")
    for i, p in enumerate(mounted):
        cx = x + inset + (w - 2 * inset) * ((i + 0.5) / max(len(mounted), 1))
        f_mounted(cx, y + 0.12 if not south_zone else y + d - 0.12, z, coll, M, code, p)

    label(f"{code}  {room['name']}", x + w / 2, y + d / 2, z + 0.02, coll, size=0.38)


def build_cells(room, z, coll, M):
    x, y, w, d, code = room["x"], room["y"], room["w"], room["d"], room["code"]
    cols, rows = 3, 2
    cw, ch = w / cols, d / rows
    n = 1
    for r in range(rows):
        for c in range(cols):
            cx0, cy0 = x + c * cw, y + r * ch
            if c > 0:
                box(f"{code}_div_x{n}", cx0, cy0 + ch / 2, z + WALL_H / 2, 0.1, ch, WALL_H, coll, M["wall_res"])
            if r > 0:
                box(f"{code}_div_y{n}", cx0 + cw / 2, cy0, z + WALL_H / 2, cw, 0.1, WALL_H, coll, M["wall_res"])
            # cell bars across the front (interior-facing edge)
            front_y = cy0 + (ch - 0.15 if r == 0 else 0.15)
            nb = int(cw / 0.22)
            for b in range(nb + 1):
                bx = cx0 + 0.1 + (cw - 0.2) * (b / nb)
                box(f"{code}_bar{n}_{b}", bx, front_y, z + 1.1, 0.05, 0.05, 2.2, coll, M["metal"])
            box(f"{code}_bartop{n}", cx0 + cw / 2, front_y, z + 2.2, cw - 0.2, 0.06, 0.06, coll, M["metal"])
            f_bench(cx0 + cw / 2, cy0 + (0.4 if r == 0 else ch - 0.4), z, coll, M, code, f"bunk{n}", w=cw - 0.5)
            anchor(f"PROP_{code}_CELLBARS_{n}", cx0 + cw / 2, front_y, z + 1.1, coll)
            label(f"CELL {n}", cx0 + cw / 2, cy0 + ch / 2, z + 0.02, coll, size=0.3)
            n += 1


# ---------------------------------------------------------------------------
# Core: stairs, landings, railings, elevator
# ---------------------------------------------------------------------------

def build_core(z, coll, M, is_top):
    x, y, w = CORE["x"], CORE["y"], CORE["w"]
    box("CORE_floor", x + w / 2, y + CORE["d"] / 2, z - SLAB / 2, w, CORE["d"], SLAB, coll, M["concrete"])

    # elevator (doors face the two corridors)
    ex, ey = x + w / 2, 9.0
    box(f"CORE_elev_shaft_{int(z)}", ex, y + 10.0, z + WALL_H / 2, 2.2, 2.2, WALL_H, coll, M["metal_dark"])
    box(f"CORE_elev_door_{int(z)}", ex, ey - 0.05, z + 1.05, 1.4, 0.08, 2.1, coll, M["metal"])
    anchor(f"PROP_CORE_ELEVATOR_{int(z)}", ex, ey, z + 1.05, coll)

    if is_top:
        return

    # straight stair run + top landing, in the front part of the core
    riser = 0.185
    tread = 0.28
    n = max(int(round(WALL_H / riser)), 1)
    riser = WALL_H / n
    sw = 1.6
    sx = x + w / 2 - 0.1
    y0 = 0.6
    for i in range(n):
        box(f"CORE_step_{int(z)}_{i}", sx, y0 + i * tread + tread / 2, z + i * riser + riser / 2,
            sw, tread, riser, coll, M["concrete"])
    run_end = y0 + n * tread
    box(f"CORE_landing_{int(z)}", sx, run_end + 0.7, z + WALL_H - SLAB / 2, sw, 1.4, SLAB, coll, M["concrete"])
    railing(sx - sw / 2, y0, sx - sw / 2, run_end, z, coll, M, f"CORE_rail_L_{int(z)}")
    railing(sx + sw / 2, y0, sx + sw / 2, run_end, z, coll, M, f"CORE_rail_R_{int(z)}")


def build_corridors(z, coll, M):
    for i, c in enumerate(CORRIDORS):
        box(f"CORRIDOR{i}_floor", c["x"] + c["w"] / 2, c["y"] + c["d"] / 2,
            z - SLAB / 2, c["w"], c["d"], SLAB, coll, M["floor"])


def build_roof(coll, M):
    z = FLOORS["L3"]["z"] + FLOOR_HEIGHT
    for room in FLOORS["L3"]["rooms"]:
        if room["type"] == "outdoor":
            continue
        x, y, w, d = room["x"], room["y"], room["w"], room["d"]
        box(f"ROOF_{room['code']}", x + w / 2, y + d / 2, z + SLAB / 2, w, d, SLAB, coll, M["roof"])
    box("ROOF_core", CORE["x"] + CORE["w"] / 2, CORE["y"] + CORE["d"] / 2, z + SLAB / 2,
        CORE["w"], CORE["d"], SLAB, coll, M["roof"])
    # perimeter parapet
    W, D, t, h = BUILDING["w"], BUILDING["d"], 0.25, 0.9
    box("PARAPET_N", W / 2, 0, z + h / 2, W, t, h, coll, M["concrete"])
    box("PARAPET_S", W / 2, D, z + h / 2, W, t, h, coll, M["concrete"])
    box("PARAPET_W", 0, D / 2, z + h / 2, t, D, h, coll, M["concrete"])
    box("PARAPET_E", W, D / 2, z + h / 2, t, D, h, coll, M["concrete"])


# ---------------------------------------------------------------------------
# Floor slab material by room type
# ---------------------------------------------------------------------------

def floor_mat(rtype, M):
    if rtype == "garage":
        return M["floor_gar"]
    if rtype == "public":
        return M["floor_pub"]
    if rtype == "outdoor":
        return M["terrace"]
    return M["floor"]


# ---------------------------------------------------------------------------
# Presentation rig
# ---------------------------------------------------------------------------

def build_rig(coll):
    target = bpy.data.objects.new("RIG_target", None)
    target.location = (18, 11, 5)
    coll.objects.link(target)

    cam_data = bpy.data.cameras.new("RIG_camera")
    cam_data.lens = 32
    cam = bpy.data.objects.new("RIG_camera", cam_data)
    cam.location = (62, -42, 40)
    coll.objects.link(cam)
    c = cam.constraints.new("TRACK_TO")
    c.target = target
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    bpy.context.scene.camera = cam

    sun_data = bpy.data.lights.new("RIG_sun", "SUN")
    sun_data.energy = 3.2
    sun = bpy.data.objects.new("RIG_sun", sun_data)
    sun.location = (30, -20, 60)
    sun.rotation_euler = (math.radians(52), math.radians(8), math.radians(35))
    coll.objects.link(sun)

    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.05, 0.06, 0.08, 1.0)
        bg.inputs[1].default_value = 1.0

    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            bpy.context.scene.render.engine = engine
            break
        except TypeError:
            continue


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    M = build_materials()
    root = get_coll("Precinct24_HQ")

    for key in FLOOR_ORDER:
        floor = FLOORS[key]
        z = floor["z"]
        coll = get_coll(f"{key} - {floor['title']}", parent=root)

        for room in floor["rooms"]:
            x, y, w, d = room["x"], room["y"], room["w"], room["d"]
            box(f"{room['code']}_floor", x + w / 2, y + d / 2, z - SLAB / 2, w, d, SLAB,
                coll, floor_mat(room["type"], M))
            if room["type"] != "outdoor":
                build_room_shell(room, z, key, coll, M)
            if room.get("cells"):
                build_cells(room, z, coll, M)
            else:
                place_props(room, z, coll, M)
            if room["type"] == "outdoor":
                railing(x + 0.2, y + 0.2, x + w - 0.2, y + 0.2, z, coll, M, f"{room['code']}_railN")
                railing(x + w - 0.2, y + 0.2, x + w - 0.2, y + d - 0.2, z, coll, M, f"{room['code']}_railE")

        build_corridors(z, coll, M)
        build_core(z, coll, M, is_top=(key == "L3"))

    build_roof(get_coll("Roof", parent=root), M)
    build_rig(get_coll("Rig", parent=root))

    print("Precinct 24 build complete: 4 levels, furnished, materialed, with rig.")
    print("Swap every PROP_* empty for a real asset via Sollumz before export.")


if __name__ == "__main__":
    main()
