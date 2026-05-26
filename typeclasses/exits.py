"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia.objects.objects import DefaultExit

from .objects import ObjectParent


DIRECTION_ALIASES = {
    "north": ("n",),
    "south": ("s",),
    "east": ("e",),
    "west": ("w",),
    "northeast": ("ne",),
    "northwest": ("nw",),
    "southeast": ("se",),
    "southwest": ("sw",),
    "up": ("u",),
    "down": ("d",),
}


def _sync_direction_aliases(exit_obj):
    """Ensure short direction aliases exist for directional exits."""
    key = (exit_obj.key or "").strip().lower()
    aliases = DIRECTION_ALIASES.get(key)
    if aliases:
        for alias in aliases:
            exit_obj.aliases.add(alias)


class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property and overrides some hooks
    and methods to represent the exits.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects child classes like this.

    """

    def at_object_creation(self):
        super().at_object_creation()
        _sync_direction_aliases(self)

    def at_cmdset_get(self, **kwargs):
        """Ensure legacy exits also gain short aliases when commandset is built."""
        _sync_direction_aliases(self)
        return super().at_cmdset_get(**kwargs)

    def at_traverse(self, traverser, target_loc):
        traverser.ndb.arrive_brief_room_id = getattr(target_loc, "id", None)
        return super().at_traverse(traverser, target_loc)


class DoorAwareExit(ObjectParent, DefaultExit):
    """
    An exit that is aware of a specific door object.
    The exit should have self.db.door set to the door object (and the door should have db.exit set to this exit).
    """
    def at_traverse(self, traverser, target_loc):
        door = self.db.door
        if door and not door.db.is_open:
            traverser.msg(f"The {door.key} is closed.")
            return False # Stops the movement
        traverser.ndb.arrive_brief_room_id = getattr(target_loc, "id", None)
        return super().at_traverse(traverser, target_loc)

    def at_object_creation(self):
        super().at_object_creation()
        _sync_direction_aliases(self)

    def at_cmdset_get(self, **kwargs):
        """Ensure legacy exits also gain short aliases when commandset is built."""
        _sync_direction_aliases(self)
        return super().at_cmdset_get(**kwargs)
