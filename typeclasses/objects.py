from evennia import DefaultObject

class ObjectParent:
    """
    This is a required Evennia mixin class. Do not remove it!
    It injects custom methods across all items, characters, and rooms.
    """
    pass

class Object(ObjectParent, DefaultObject):
    """
    The default template for normal items in the world.
    """
    pass

# =====================================================================
# CUSTOM DRAGONSGATE WEAPON AND MERCHANT CLASSES
# =====================================================================

class Weapon(ObjectParent, DefaultObject):
    """
    Custom Weapon typeclass tracking combat parameters.
    Speed cost dictates how many global ticks a swing consumes.
    """
    def at_object_creation(self):
        """Called once when a weapon object is first created."""
        super().at_object_creation()
        self.db.damage = 5
        self.db.speed_cost = 3  # Default speed value (3 ticks)

class Shopkeeper(ObjectParent, DefaultObject):
    """
    Placeholder template for shop economic entities.
    """
    def at_object_creation(self):
        super().at_object_creation()
        self.db.gold_reserves = 500


class Door(DefaultObject):
    def at_object_creation(self):
        self.db.is_open = False
        self.db.partner = None
        self.db.exit = None  # The exit this door controls

    def open(self, opener=None):
        """Open this door and its partner."""
        if self.db.is_open:
            if opener:
                opener.msg(f"{self.key.capitalize()} is already open.")
            return False
        self.db.is_open = True
        if opener:
            opener.msg(f"You open {self.key}.")
        if self.db.partner and not self.db.partner.db.is_open:
            self.db.partner.db.is_open = True
            if opener:
                opener.msg(f"{self.db.partner.key.capitalize()} opens as well.")
        return True

    def close(self, closer=None):
        """Close this door and its partner."""
        if not self.db.is_open:
            if closer:
                closer.msg(f"{self.key.capitalize()} is already closed.")
            return False
        self.db.is_open = False
        if closer:
            closer.msg(f"You close {self.key}.")
        if self.db.partner and self.db.partner.db.is_open:
            self.db.partner.db.is_open = False
            if closer:
                closer.msg(f"{self.db.partner.key.capitalize()} closes as well.")
        return True

    def get_look_result(self, looker):
        # Enforce location constraint
        if looker.location != self.location:
            return "You must be in the same room as the door to look at it."
        if self.db.is_open and self.db.partner:
            # Look through to the partner's location
            target_room = self.db.partner.location
            looker.msg(f"You look through {self.key} and see:")
            return target_room.return_appearance(looker)
        else:
            return f"{self.key.capitalize()} is closed."
