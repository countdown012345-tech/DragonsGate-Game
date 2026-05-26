"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    def _get_exit_sentence(self):
        """Build a grammatical exit sentence using destination short descriptions."""
        exits = [obj for obj in self.contents if getattr(obj, "destination", None)]
        if not exits:
            return ""

        current_key = (self.key or "").strip().lower()
        parts = []
        for exi in exits:
            dest = exi.destination
            shortdesc = (dest.key or "somewhere").strip()
            direction = (exi.key or "unknown").strip().lower()
            door = getattr(exi.db, "door", None)
            door_key = (door.key or "").strip() if door else ""

            color = "|g" if (shortdesc.lower() == current_key) else "|b"
            reset = "|n"

            if door_key:
                parts.append(
                    f"{color}{door_key}{reset} to {color}{shortdesc}{reset} to the {color}{direction}{reset}"
                )
            else:
                parts.append(f"{color}{shortdesc}{reset} to the {color}{direction}{reset}")

        if len(parts) == 1:
            return f"You see {parts[0]}."
        if len(parts) == 2:
            return f"You see {parts[0]} and {parts[1]}."
        return f"You see {', '.join(parts[:-1])}, and {parts[-1]}."

    def get_display_exits(self, looker, **kwargs):
        """
        Show exits as a readable sentence using destination short descriptions.

        Examples:
            - You see The Market to the east.
            - You see The Market to the east and A Dusty Road to the west.
            - You see The Market to the east, A Dusty Road to the west, and ...
        """
        return self._get_exit_sentence()

    def return_appearance(self, looker, **kwargs):
        """
        Brief arrival text on movement; indented detailed text on explicit look.
        """
        arrive_room_id = getattr(looker.ndb, "arrive_brief_room_id", None)
        is_arrival = arrive_room_id == self.id

        if is_arrival:
            looker.ndb.arrive_brief_room_id = None
            exit_sentence = self._get_exit_sentence()
            if exit_sentence:
                return f"You arrive at {self.key}. {exit_sentence}"
            return f"You arrive at {self.key}."

        desc = (self.db.desc or "").strip()
        exit_sentence = self._get_exit_sentence()

        lines = []
        if desc:
            lines.append(f"   {desc}")
        if exit_sentence:
            lines.append(f"   {exit_sentence}")
        return "\n".join(lines) if lines else "   Nothing of note."
