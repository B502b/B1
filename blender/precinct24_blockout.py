"""
Precinct 24 Police Headquarters -- FiveM MLO blockout
======================================================
Original concept, drafted from scratch. Not a copy of any existing
server's MLO and not affiliated with Rockstar Games / FiveM.

What this script does
----------------------
Builds a 3D blockout of the four-level building shown in the companion
"Precinct 24 Blueprints" sheet set: matching room footprints, wall
shells with door gaps, floor slabs, a stair core connecting all levels,
and one placeholder Empty per suggested prop so you can see where
dressing goes before you swap it for real assets.

How to run
----------
1. Open Blender -> Scripting tab -> Open this file -> Run Script (Alt+P).
   Or headless:  blender --background --python precinct24_blockout.py
2. Everything is organized into collections per floor
   (B1 / L1 / L2 / L3) so you can hide levels while you work.
3. Every Empty named PROP_* is a placeholder. Install Sollumz, load your
   own GTA V asset archive, and replace each Empty with the real prop it
   names (you must own a legal copy of GTA V -- no game assets ship
   with this script, only the blockout geometry and naming).
4. Once dressed, export per Sollumz's own workflow (ydr/ytyp/ymap) and
   wire doors + job restrictions in FiveM (see the blueprint sheet's
   "Finishing in FiveM" notes).

Units: 1 Blender unit = 1 meter, matching the blueprint sheet's scale.
"""

import bpy
import math

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FLOOR_HEIGHT = 4.0          # m, floor-to-floor
SLAB_THICKNESS = 0.3        # m
WALL_HEIGHT = FLOOR_HEIGHT - SLAB_THICKNESS
WALL_THICKNESS = 0.2        # m
DOOR_WIDTH = 1.2            # m

CORE = {"x": 16.0, "y": 0.0, "w": 4.0, "d": 22.0}
CORRIDORS = [
    {"x": 0.0, "y": 9.0, "w": 16.0, "d": 4.0},
    {"x": 20.0, "y": 9.0, "w": 16.0, "d": 4.0},
]

# ---------------------------------------------------------------------------
# Room data -- mirrors the blueprint sheet exactly (x, y, w, d in meters)
# ---------------------------------------------------------------------------

FLOORS = {
    "B1": {
        "z": 0.0,
        "title": "Basement - Holding & Evidence Level",
        "rooms": [
            dict(code="B-01", name="Sally Port / Prisoner Intake Garage", x=0, y=0, w=10, d=9, type="garage",
                 props=["ROLLERDOOR", "VAN_MARKER", "TIRE_SPIKES"]),
            dict(code="B-02", name="Booking & Processing", x=10, y=0, w=6, d=9, type="room",
                 props=["DESK_BOOKING", "MUGSHOT_WALL", "FINGERPRINT_SCANNER"]),
            dict(code="B-03", name="Interrogation A", x=20, y=0, w=4, d=4.5, type="restricted",
                 props=["TABLE_INTERROGATION", "MIRROR_ONEWAY"]),
            dict(code="B-04", name="Interrogation B", x=20, y=4.5, w=4, d=4.5, type="restricted",
                 props=["TABLE_INTERROGATION", "CAMERA_WALL"]),
            dict(code="B-05", name="Holding Cell Block", x=24, y=0, w=12, d=9, type="restricted",
                 cells=6, props=["CELLBARS", "CELL_BENCH", "CELL_DOOR"]),
            dict(code="B-06", name="Evidence Storage & Lockers", x=0, y=13, w=10, d=9, type="restricted",
                 props=["SHELVING_EVIDENCE", "LOCKER_EVIDENCE", "DESK_SIGNOUT"]),
            dict(code="B-07", name="Armory / Weapons Vault", x=10, y=13, w=6, d=9, type="restricted",
                 props=["GUNRACK", "AMMO_CRATE", "VAULT_DOOR"]),
            dict(code="B-08", name="Server Room", x=20, y=13, w=4, d=4.5, type="room",
                 props=["SERVER_RACK", "UPS_UNIT"]),
            dict(code="B-09", name="Records Archive", x=20, y=17.5, w=4, d=4.5, type="room",
                 props=["FILING_CABINET", "ARCHIVE_BOX"]),
            dict(code="B-10", name="Staff Break Room", x=24, y=13, w=6, d=9, type="room",
                 props=["TABLE_BREAK", "VENDING_MACHINE", "LOCKER_STAFF"]),
            dict(code="B-11", name="Electrical / Utility", x=30, y=13, w=6, d=9, type="room",
                 props=["BREAKER_PANEL", "WATER_HEATER", "SHELVING_UTILITY"]),
        ],
    },
    "L1": {
        "z": FLOOR_HEIGHT,
        "title": "Ground Floor - Public & Operations Level",
        "rooms": [
            dict(code="G-01", name="Main Entrance & Lobby", x=0, y=0, w=10, d=9, type="public",
                 props=["DOOR_ENTRY", "SEATING_LOBBY", "SEAL_PLAQUE"]),
            dict(code="G-02", name="Reception / Front Desk", x=10, y=0, w=6, d=9, type="public",
                 props=["DESK_FRONT", "GLASS_PARTITION", "KIOSK_SIGNIN"]),
            dict(code="G-03", name="Briefing Room", x=20, y=0, w=4, d=9, type="room",
                 props=["PODIUM", "CHAIR_ROW", "WHITEBOARD"]),
            dict(code="G-04", name="Patrol Officer Bullpen", x=24, y=0, w=12, d=9, type="room",
                 props=["DESK_PATROL", "FILING_CABINET", "WATER_COOLER"]),
            dict(code="G-05", name="Vehicle Garage Bay", x=0, y=13, w=16, d=9, type="garage",
                 props=["ROLLERDOOR", "CRUISER_MARK", "FUEL_PUMP", "TOOL_BENCH"]),
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
        "z": FLOOR_HEIGHT * 2,
        "title": "2nd Floor - Detective & Forensics Level",
        "rooms": [
            dict(code="D-01", name="Detective Bullpen", x=0, y=0, w=16, d=9, type="room",
                 props=["DESK_DETECTIVE", "CORKBOARD_CASE"]),
            dict(code="D-02", name="Captain's Office", x=20, y=0, w=4, d=9, type="room",
                 props=["DESK_EXEC", "BOOKSHELF", "FLAG_STAND"]),
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
            dict(code="D-10", name="Tactical Armory (secondary)", x=30, y=13, w=6, d=9, type="restricted",
                 props=["GEARRACK_TACTICAL", "VEST_RACK", "HELMET_RACK"]),
        ],
    },
    "L3": {
        "z": FLOOR_HEIGHT * 3,
        "title": "3rd Floor - Command Level",
        "rooms": [
            dict(code="C-01", name="Chief of Police Suite", x=0, y=0, w=16, d=9, type="room",
                 props=["DESK_EXEC", "SEATING_LOUNGE", "TROPHY_CASE"]),
            dict(code="C-02", name="IT / Server Closet", x=20, y=0, w=4, d=9, type="room",
                 props=["SERVER_RACK", "PATCH_PANEL"]),
            dict(code="C-03", name="Command Center / Dispatch", x=24, y=0, w=12, d=9, type="restricted",
                 props=["CONSOLE_DISPATCH", "MONITOR_WALL", "CITY_MAP"]),
            dict(code="C-04", name="Executive Conference & Training", x=0, y=13, w=16, d=9, type="room",
                 props=["TABLE_CONFERENCE", "AV_SCREEN"]),
            dict(code="C-05", name="Storage", x=20, y=13, w=4, d=9, type="room",
                 props=["SHELVING_UTILITY"]),
            dict(code="C-06", name="Rooftop Terrace / Helipad", x=24, y=13, w=12, d=9, type="outdoor",
                 props=["HELIPAD_MARKING", "RAILING", "HVAC_UNIT"]),
        ],
    },
}
FLOOR_ORDER = ["B1", "L1", "L2", "L3"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_or_create_collection(name, parent=None):
    if name in bpy.data.collections:
        coll = bpy.data.collections[name]
    else:
        coll = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(coll)
    return coll


def add_box(name, cx, cy, cz, sx, sy, sz, collection):
    """Axis-aligned box centered at (cx, cy, cz) with full dimensions sx, sy, sz."""
    if sx <= 0 or sy <= 0 or sz <= 0:
        return None
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)

    hx, hy, hz = sx / 2, sy / 2, sz / 2
    verts = [
        (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
        (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz),
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5),
        (0, 4, 5, 1), (1, 5, 6, 2),
        (2, 6, 7, 3), (3, 7, 4, 0),
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj.location = (cx, cy, cz)
    return obj


def add_empty(name, x, y, z, collection, size=0.25):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = size
    empty.location = (x, y, z)
    collection.objects.link(empty)
    return empty


def add_label(text, x, y, z, collection, size=0.35):
    curve = bpy.data.curves.new(name="label", type="FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    obj = bpy.data.objects.new(text[:30], curve)
    obj.location = (x, y, z)
    obj.rotation_euler = (0, 0, 0)
    collection.objects.link(obj)
    return obj


def wall_x(name, x1, x2, y, z, height, thickness, collection):
    if x2 - x1 <= 0:
        return None
    return add_box(name, (x1 + x2) / 2, y, z + height / 2, x2 - x1, thickness, height, collection)


def wall_y(name, y1, y2, x, z, height, thickness, collection):
    if y2 - y1 <= 0:
        return None
    return add_box(name, x, (y1 + y2) / 2, z + height / 2, thickness, y2 - y1, height, collection)


def build_room_shell(room, z, collection):
    """West/east walls always closed; north/south wall gets a door gap on
    whichever edge touches the corridor, matching the blueprint sheet."""
    x, y, w, d, code = room["x"], room["y"], room["w"], room["d"], room["code"]

    wall_y(f"{code}_wall_W", y, y + d, x, z, WALL_HEIGHT, WALL_THICKNESS, collection)
    wall_y(f"{code}_wall_E", y, y + d, x + w, z, WALL_HEIGHT, WALL_THICKNESS, collection)

    door_on_north = abs(y - 13.0) < 1e-6   # south-zone room: door faces corridor above it
    door_on_south = abs((y + d) - 9.0) < 1e-6  # north-zone room: door faces corridor below it
    gx = x + w / 2

    if door_on_north:
        wall_x(f"{code}_wall_N1", x, gx - DOOR_WIDTH / 2, y, z, WALL_HEIGHT, WALL_THICKNESS, collection)
        wall_x(f"{code}_wall_N2", gx + DOOR_WIDTH / 2, x + w, y, z, WALL_HEIGHT, WALL_THICKNESS, collection)
    else:
        wall_x(f"{code}_wall_N", x, x + w, y, z, WALL_HEIGHT, WALL_THICKNESS, collection)

    if door_on_south:
        wall_x(f"{code}_wall_S1", x, gx - DOOR_WIDTH / 2, y + d, z, WALL_HEIGHT, WALL_THICKNESS, collection)
        wall_x(f"{code}_wall_S2", gx + DOOR_WIDTH / 2, x + w, y + d, z, WALL_HEIGHT, WALL_THICKNESS, collection)
    else:
        wall_x(f"{code}_wall_S", x, x + w, y + d, z, WALL_HEIGHT, WALL_THICKNESS, collection)


def build_cell_partitions(room, z, collection):
    """Subdivides the Holding Cell Block into a 3x2 grid, matching the sheet."""
    x, y, w, d, code = room["x"], room["y"], room["w"], room["d"], room["code"]
    cols, rows = 3, 2
    cw, ch = w / cols, d / rows
    n = 1
    for r in range(rows):
        for c in range(cols):
            cx0 = x + c * cw
            cy0 = y + r * ch
            if c > 0:
                wall_y(f"{code}_cell{n}_div_x", cy0, cy0 + ch, cx0, z, WALL_HEIGHT, 0.08, collection)
            if r > 0:
                wall_x(f"{code}_cell{n}_div_y", cx0, cx0 + cw, cy0, z, WALL_HEIGHT, 0.08, collection)
            add_empty(f"PROP_CELLBARS_{code}_{n}", cx0 + cw / 2, cy0 + ch - 0.1, z + 1.0, collection)
            add_empty(f"PROP_CELL_BENCH_{code}_{n}", cx0 + cw / 2, cy0 + 0.6, z + 0.25, collection)
            add_label(f"CELL {n}", cx0 + cw / 2, cy0 + ch / 2, z + 0.02, collection, size=0.3)
            n += 1


def build_room(room, z, collection):
    x, y, w, d, code, name = room["x"], room["y"], room["w"], room["d"], room["code"], room["name"]

    add_box(f"{code}_floor", x + w / 2, y + d / 2, z - SLAB_THICKNESS / 2, w, d, SLAB_THICKNESS, collection)

    if room["type"] != "outdoor":
        build_room_shell(room, z, collection)

    if room.get("cells"):
        build_cell_partitions(room, z, collection)
    else:
        add_label(f"{code}  {name}", x + w / 2, y + d / 2, z + 0.02, collection, size=0.4)
        # spread placeholder prop markers evenly along the room's centerline
        props = room.get("props", [])
        margin = 0.9
        usable_w = max(w - 2 * margin, 0.1)
        for i, prop in enumerate(props):
            px = x + margin + (usable_w * (i + 0.5) / max(len(props), 1))
            py = y + d / 2
            add_empty(f"PROP_{prop}_{code}_{i+1}", px, py, z + 0.05, collection)

    if room.get("exterior"):
        side = room["exterior"]
        ex = x if side == "w" else x + w / 2
        ey = y + d / 2 if side == "w" else y + d
        add_empty(f"PROP_EXTERIOR_ACCESS_{code}", ex, ey, z + 1.0, collection, size=0.4)


def build_core_and_stairs(z_base, collection, is_top=False):
    x, y, w, d = CORE["x"], CORE["y"], CORE["w"], CORE["d"]
    add_box("CORE_floor", x + w / 2, y + d / 2, z_base - SLAB_THICKNESS / 2, w, d, SLAB_THICKNESS, collection)
    add_empty(f"PROP_ELEVATOR_DOOR_{int(z_base)}", x + w / 2, y + 9.0, z_base + 1.0, collection)
    add_empty(f"PROP_ELEVATOR_DOOR_{int(z_base)}_b", x + w / 2, y + 13.0, z_base + 1.0, collection)

    if is_top:
        return

    # staircase run: steps climb from this floor to the one above, inside the core
    riser, tread = 0.19, 0.28
    steps = max(int(round(WALL_HEIGHT / riser)) + 1, 1)  # + slab handled by z offset below
    stair_width = 1.5
    run_start_y = y + 1.0
    stair_x = x + w / 2
    for i in range(steps):
        step_z = z_base + i * riser + riser / 2
        step_y = run_start_y + i * tread + tread / 2
        add_box(f"CORE_step_{int(z_base)}_{i}", stair_x, step_y, step_z, stair_width, tread, riser, collection)


def build_corridors(z, collection):
    for i, c in enumerate(CORRIDORS):
        add_box(f"CORRIDOR_{i}_floor", c["x"] + c["w"] / 2, c["y"] + c["d"] / 2,
                z - SLAB_THICKNESS / 2, c["w"], c["d"], SLAB_THICKNESS, collection)


def build_roof(collection):
    z = FLOORS["L3"]["z"] + FLOOR_HEIGHT
    for room in FLOORS["L3"]["rooms"]:
        if room["type"] == "outdoor":
            continue
        x, y, w, d = room["x"], room["y"], room["w"], room["d"]
        add_box(f"ROOF_{room['code']}", x + w / 2, y + d / 2, z + SLAB_THICKNESS / 2, w, d, SLAB_THICKNESS, collection)
    add_box("ROOF_core", CORE["x"] + CORE["w"] / 2, CORE["y"] + CORE["d"] / 2,
            z + SLAB_THICKNESS / 2, CORE["w"], CORE["d"], SLAB_THICKNESS, collection)


def main():
    root = get_or_create_collection("Precinct24_HQ")

    for idx, key in enumerate(FLOOR_ORDER):
        floor = FLOORS[key]
        z = floor["z"]
        coll = get_or_create_collection(f"{key} - {floor['title']}", parent=root)

        for room in floor["rooms"]:
            build_room(room, z, coll)

        build_corridors(z, coll)
        build_core_and_stairs(z, coll, is_top=(key == "L3"))

    roof_coll = get_or_create_collection("Roof", parent=root)
    build_roof(roof_coll)

    print(f"Precinct 24 blockout complete: {len(FLOOR_ORDER)} levels built under 'Precinct24_HQ'.")
    print("Every PROP_* empty is a placeholder -- replace with real props via Sollumz before export.")


if __name__ == "__main__":
    main()
