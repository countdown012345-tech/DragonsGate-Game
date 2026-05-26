# mygame/world/riverside_map.py

# This defines what symbols represent which room types and sizes
LEGEND = {
    "C": {"typeclass": "typeclasses.rooms.XYZRoom", "key": "Outside Stone Toga Inn", "size": 4},
    "t": {"typeclass": "typeclasses.rooms.XYZRoom", "size": 1},
    "s": {"typeclass": "typeclasses.rooms.XYZRoom", "size": 2},
    "l": {"typeclass": "typeclasses.rooms.XYZRoom", "size": 4},
    "h": {"typeclass": "typeclasses.rooms.XYZRoom", "size": 8},
    ".": None, # Represents 'empty' spaces occupied by larger rooms
}

# This is your visual grid. 
# Note: Since C is size 4, it effectively takes up a 4x4 area.
# In a coordinate grid, the 'anchor' is the top-left (0,0).
MAP_DATA = """
C . . . l . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
s . . . . . . .
"""