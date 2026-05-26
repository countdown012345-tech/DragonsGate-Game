"""
Worldbuilder command to launch the EvMenu-based world building interface.
"""
from evennia import Command
from evennia.utils.evmenu import EvMenu

class CmdWorldbuilder(Command):
    """
    Launch the Worldbuilder menu.

    Usage:
        worldbuilder
    """
    key = "worldbuilder"
    locks = "cmd:perm(Builders)"
    help_category = "Building"

    def func(self):
        EvMenu(self.caller, "commands.worldbuilder_menu", startnode="node_main_menu")
