"""
Command sets for DragonsGate.
Includes structural validation mechanics for specialized asymmetrical weapon combat commands.
"""

from evennia import default_cmds
from evennia import Command
from evennia import CmdSet
from commands.command import CmdStats, CmdQueue, CmdStop  # Ensure CmdQueue is imported from your command.py
from commands.worldbuilder import CmdWorldbuilder
from commands.cmd_door import CmdOpen, CmdClose
from commands.wa_commands import CmdWAMenu, CmdSleep
class GameMasterCmdSet(CmdSet):
    """Command set for GameMasters."""
    key = "GameMasterCmdSet"
    priority = 110
    mergetype = "Union"

    def at_cmdset_creation(self):
        self.add(CmdWorldbuilder)
        self.add(CmdOpen)
        self.add(CmdClose)

# Placeholder for future command sets
class StorytellerCmdSet(CmdSet):
    key = "StorytellerCmdSet"
    priority = 100
    mergetype = "Union"
    def at_cmdset_creation(self):
        pass

class WelcomeAreaCmdSet(CmdSet):
    key = "WelcomeAreaCmdSet"
    priority = 90
    mergetype = "Union"
    def at_cmdset_creation(self):
        pass

class PlayerCharacterCmdSet(CmdSet):
    key = "PlayerCharacterCmdSet"
    priority = 80
    mergetype = "Union"
    def at_cmdset_creation(self):
        pass
from evennia.contrib.grid.xyzgrid.commands import XYZGridCmdSet

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(XYZGridCmdSet)
        self.add(CmdWorldbuilder)
        self.add(CmdOpen)
        self.add(CmdClose)

# =====================================================================
# DRAGONSGATE COMBAT QUEUE COMMAND ENGINE WITH VALIDATION
# =====================================================================

class CmdCombatAction(Command):
    """
    Queue a specialized weapon combat attack against a specific target.
    
    Valid weapon groupings required:
      Knives              -> stab, slash
      One Handed Crushing -> bash, smash
      Unarmed             -> (None yet)

    Usage:
      stab <target>
      slash <target>
      bash <target>
      smash <target>
    """
    # Registered attack trigger keywords
    key = "stab"
    aliases = ["slash", "bash", "smash"]
    help_category = "Combat"

    def func(self):
        caller = self.caller
        
        # 1. Roundtime/Busy Check
        cooldown = caller.attributes.get("combat_cooldown") or 0
        if cooldown > 0:
            caller.msg(f"|rYou are still recovering (busy for {cooldown} more second(s)).|n")
            return

        action_type = self.cmdstring.lower()
        
        # 2. Look up equipped status parameters
        weapon = caller.db.slots.get("main_hand")
        weapon_type = "Unarmed"
        
        if weapon and hasattr(weapon, "db") and weapon.db.weapon_type:
            weapon_type = weapon.db.weapon_type

        # 3. Strict Weapon Validation Matrices
        if weapon_type == "Unarmed":
            caller.msg(f"You cannot '{action_type}' while completely barehanded.")
            return

        if weapon_type == "Knives":
            if action_type not in ["stab", "slash"]:
                caller.msg(f"You cannot '{action_type}' with a knife! Try: stab, slash.")
                return

        elif weapon_type == "One Handed Crushing":
            if action_type not in ["bash", "smash"]:
                caller.msg(f"You cannot '{action_type}' with a blunt crushing weapon! Try: bash, smash.")
                return
        
        else:
            # Catch-all failsafe for unmapped future weapon types
            caller.msg("Your current weapon does not support that specialized attack move.")
            return

        # 4. Standard parsing loop for finding your local target combatant
        if not self.args:
            caller.msg(f"Who do you want to {action_type}?")
            return
            
        target = caller.search(self.args.strip())
        if not target:
            return

        # Success! Enqueue valid combat attack
        caller.queue_action(action_type, target)


class CmdEquip(Command):
    """
    Wield an item from your inventory bag as your main functional weapon asset.

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

        # Set main hand tracking pointer
        caller.db.slots["main_hand"] = obj
        
        # Pull category name safely for user feedback text formatting
        w_type = obj.db.weapon_type or "Unknown"
        caller.msg(f"You equip {obj.key} as your main weapon. ({w_type} - Speed: {obj.db.speed_cost} ticks)")


# =====================================================================
# CORE EVENNIA CMDSETS
# =====================================================================

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The CharacterCmdSet contains general in-game commands like look, get, etc.
    """
    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        
        # Add validated multi-move fighting actions
        self.add(CmdCombatAction())
        self.add(CmdEquip())
        
        # Add the classic sheet overview command
        self.add(CmdStats())
        
        # Add the new sequence queuing command
        self.add(CmdQueue())
        self.add(CmdStop())
        self.add(CmdSleep())


class AccountCmdSet(default_cmds.AccountCmdSet):
    key = "DefaultAccount"
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdWAMenu())


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    key = "DefaultUnloggedin"
    def at_cmdset_creation(self):
        super().at_cmdset_creation()


class SessionCmdSet(default_cmds.SessionCmdSet):
    key = "DefaultSession"
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
