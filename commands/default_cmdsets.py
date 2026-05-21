"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
from evennia import Command
from evennia import CmdSet
from commands.command import CmdStats


# =====================================================================
# DRAGONSGATE COMBAT QUEUE COMMAND ENGINE
# =====================================================================

class CmdCombatAction(Command):
    """
    Queue an attack profile against a specific target.

    Usage:
      stab <target>
      slash <target>
    """
    key = "stab"
    aliases = ["slash"]
    help_category = "Combat"

    def func(self):
        caller = self.caller
        action_type = self.cmdstring  # Dynamically parses if user typed 'stab' or 'slash'
        
        if not self.args:
            caller.msg(f"Who do you want to {action_type}?")
            return
            
        target = caller.search(self.args.strip())
        if not target:
            return

        caller.queue_action(action_type, target)


class CmdEquip(Command):
    """
    Wield a structural weapon from your local inventory bag.

    Usage:
      equip <weapon>
    """
    key = "equip"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Equip what?")
            return
            
        obj = caller.search(self.args.strip(), location=caller)
        if not obj:
            return
            
        if not hasattr(obj, "db") or obj.db.speed_cost is None:
            caller.msg("You cannot equip that asset as a functional weapon.")
            return

        caller.db.slots["main_hand"] = obj
        caller.msg(f"You equip {obj.key} as your main weapon. (Speed Cost: {obj.db.speed_cost} ticks)")


# =====================================================================
# CORE EVENNIA CMDSETS (OVERLOADED FOR DRAGONSGATE)
# =====================================================================

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        
        # Add DragonsGate combat system triggers
        self.add(CmdCombatAction())
        self.add(CmdEquip())
        
        # Add the classic text-adjective sheet command
        self.add(CmdStats())


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        # Any commands you add below will overload the default ones.


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        # Any commands you add below will overload the default ones.


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.
        """
        super().at_cmdset_creation()
        # Any commands you add below will overload the default ones.