"""
Commands to open and close doors (or other linked objects).
"""
from evennia import Command
from commands.builder_helpers import set_linked_object_state

class CmdOpen(Command):
    """
    Open a door or similar object.
    Usage:
        open <door>
    """
    key = "open"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if not self.args:
            self.caller.msg("Open what?")
            return
        obj = self.caller.search(self.args.strip(), location=self.caller.location)
        if not obj:
            return
        if not hasattr(obj, "open"):
            self.caller.msg(f"You can't open {obj.key}.")
            return
        set_linked_object_state(obj, "open", actor=self.caller)

class CmdClose(Command):
    """
    Close a door or similar object.
    Usage:
        close <door>
    """
    key = "close"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if not self.args:
            self.caller.msg("Close what?")
            return
        obj = self.caller.search(self.args.strip(), location=self.caller.location)
        if not obj:
            return
        if not hasattr(obj, "close"):
            self.caller.msg(f"You can't close {obj.key}.")
            return
        set_linked_object_state(obj, "close", actor=self.caller)
