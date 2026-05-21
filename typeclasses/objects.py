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
