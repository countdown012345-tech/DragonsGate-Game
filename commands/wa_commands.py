"""
Welcome Area account/character menu commands.
"""

from evennia import Command
from evennia.utils.evmenu import EvMenu


class CmdWAMenu(Command):
    """
    Open the WA account menu.

    Usage:
        @menu
    """

    key = "@menu"
    locks = "cmd:perm(WAaccount)"
    help_category = "General"

    def func(self):
        EvMenu(self.caller, "commands.wa_menu", startnode="node_wa_main")


class CmdSleep(Command):
    """
    Return from an active character to your WA account persona.

    Usage:
        sleep
    """

    key = "sleep"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        character = self.caller
        account = character.account
        if not account:
            character.msg("No controlling account found.")
            return

        character.db.last_known_location = character.location

        sessions = account.sessions.get()
        if not sessions:
            character.msg("No active session found.")
            return

        account.unpuppet_object(sessions[0])
        account.msg("You return to your WA account persona. Use @menu to manage characters.")
