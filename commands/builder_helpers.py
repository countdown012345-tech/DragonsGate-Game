def set_linked_object_state(obj, action, actor=None):
    """
    Open or close a linked object (door, window, etc.) and its partner.
    Args:
        obj: The object to act on (should have .open/.close methods and .db.partner).
        action: 'open' or 'close'.
        actor: The character performing the action (optional, for messaging).
    Returns:
        True if action succeeded, False otherwise.
    """
    if not obj:
        if actor:
            actor.msg("No such object to act on.")
        return False
    if action == "open":
        return obj.open(opener=actor)
    elif action == "close":
        return obj.close(closer=actor)
    else:
        if actor:
            actor.msg("Unknown action. Use 'open' or 'close'.")
        return False
"""
Helper functions for world building, such as creating linked doors or windows between rooms.
"""
from evennia import create_object

def create_linked_door_pair(room1, room2, exit1=None, exit2=None, door1_key="door", door2_key="door", door_typeclass="typeclasses.objects.Door"):
    """
    Create a pair of linked doors between two rooms, optionally linking to exits.
    Args:
        room1, room2: The two rooms to link.
        exit1, exit2: The exits (DoorAwareExit) in each room to associate with the doors (optional).
        door1_key, door2_key: The keys/names for the doors in each room.
        door_typeclass: The typeclass path for the door objects.
    Returns:
        (door1, door2): The created door objects.
    """
    door1 = create_object(door_typeclass, key=door1_key, location=room1)
    door2 = create_object(door_typeclass, key=door2_key, location=room2)
    door1.db.partner = door2
    door2.db.partner = door1
    if exit1:
        exit1.db.door = door1
        door1.db.exit = exit1
    if exit2:
        exit2.db.door = door2
        door2.db.exit = exit2
    return door1, door2
