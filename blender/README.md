# Precinct 24 Police Headquarters — FiveM MLO Concept

Original, from-scratch architectural concept for a FiveM police station
MLO: basement + 3 floors, ~36 x 22 m footprint. Not a copy of any
existing server's map and not affiliated with Rockstar Games / FiveM.

## Contents

- `precinct24_blockout.py` — a Blender Python script that builds a
  furnished, materialed 4-level interior at the same coordinates as the
  blueprint sheet:
  - Wall shells with **real openings** — framed doors (with leaves) and
    window bands with glass panes, not just gaps.
  - Floor slabs, ceilings and a perimeter **roof parapet**.
  - A proper **straight-run staircase** with landings and railings in the
    central core, plus per-floor elevator doors, linking every level.
  - **Sized proxy furniture** in every room (desks, lockers, shelving,
    server/gun racks, dispatch consoles, seating, conference tables,
    holding-cell bars, a rooftop helipad), each anchored by a `PROP_*`
    empty so you can snap the real asset to it and delete the proxy.
  - A named **material set** and a **camera + sun rig** so a test render
    looks presentable straight away.

## Levels

| Level | Title | Notable rooms |
|---|---|---|
| B1 | Holding & Evidence | sally port, booking, interrogation A/B, 6-cell holding block, evidence storage, armory, server room |
| L1 | Public & Operations | lobby/reception, briefing room, patrol bullpen, vehicle garage bay, restrooms |
| L2 | Detective & Forensics | detective bullpen, captain's office, forensics lab, tactical armory |
| L3 | Command | chief's suite, command center/dispatch, executive conference, rooftop/helipad terrace |

## Running the script

1. Open Blender → **Scripting** tab → open `precinct24_blockout.py` → **Run Script** (Alt+P).
   Or headless: `blender --background --python precinct24_blockout.py`
2. Output is organized into a `Precinct24_HQ` collection with one sub-collection
   per level (`B1`, `L1`, `L2`, `L3`) plus `Roof` and `Rig`, so you can hide
   levels while you work. Press F12 to render the pre-framed camera view.

## Finishing it as a working MLO

1. Install the **Sollumz** Blender add-on and load your own legally-owned
   GTA V asset archive (no game assets ship with this script — only the
   blockout geometry and `PROP_*` naming).
2. Replace every `PROP_*` empty with the real prop it names, then delete
   the grey proxy mesh next to it (desks, cell bars, gun racks, dispatch
   consoles, etc.).
3. Export the dressed interior as `.ydr`/`.ytyp`, then place it with a
   `.ymap` using Sollumz's map-export tools.
4. Define interior rooms + portals in the ytyp so the game culls floors
   correctly between levels.
5. Add an MLO entrance point at the Main Entrance marker on the ground
   floor (`G-01`).
6. Wire doors with a lock/interaction resource (e.g. `ox_doorlock`) at
   every door gap, and restrict the armory, evidence room and holding
   cells to the Police job.
7. Add the finished `.ymap`/`.ytyp` to your resource manifest and test
   all four levels in-game before shipping.
