"""
Commands

Commands describe the input the account can do to the game.

"""

from evennia.commands.command import Command as BaseCommand

# from evennia import default_cmds


class Command(BaseCommand):
    """
    Base command (you may see this if a child command had no help text defined)

    Note that the class's `__doc__` string is used by Evennia to create the
    automatic help entry for the command, so make sure to document consistently
    here. Without setting one, the parent's docstring will show (like now).

    """

    # Each Command class implements the following methods, called in this order
    # (only func() is actually required):
    #
    #     - at_pre_cmd(): If this returns anything truthy, execution is aborted.
    #     - parse(): Should perform any extra parsing needed on self.args
    #         and store the result on self.
    #     - func(): Performs the actual work.
    #     - at_post_cmd(): Extra actions, often things done after
    #         every command, like prompts.
    #
    pass

def get_stat_description(value):
    """Translates a raw number (1-20) into your game's text adjectives."""
    if value is None: return "unknown"
    if value <= 4:  return "terrible"
    if value <= 6:  return "poor"
    if value <= 8:  return "slightly below average"
    if value == 9:  return "average"
    if value == 11: return "slightly above average"
    if value == 12: return "good"
    if value <= 14: return "very good"
    if value <= 15: return "great"
    if value <= 16: return "remarkable"
    return "outstanding"

class CmdStats(Command):
    """
    View your character's background, physical attributes, and stats.

    Usage:
      stats
    """
    key = "stats"
    aliases = ["sheet", "score"]
    lock = "cmd:all()"

    def func(self):
        caller = self.caller
        
        # Pull values safely with fallbacks if an attribute isn't set yet
        name = caller.db.full_name or caller.key
        homeland = caller.db.homeland or "Unknown"
        marital = caller.db.marital_status or "Single"
        citizenship = caller.db.citizenship or "None"
        social = caller.db.social_standing or "Citizen"
        popularity = caller.db.popularity or 0
        age = caller.db.age or 18

        height = caller.db.height or "5'10\""
        weight = caller.db.weight or 150
        handed = caller.db.handed or "Right"
        eyes = caller.db.eyes or "brown"
        hair = caller.db.hair or "brown"
        complexion = caller.db.complexion or "fair"

        hp = caller.db.hp or 100
        hp_max = caller.db.hp_max or 100
        fatigue = caller.db.fatigue_pct or 0
        state = caller.db.state or "conscious"
        load = caller.db.load_lbs or 0
        encumbrance = caller.db.encumbrance or "You are unencumbered."
        position = caller.db.position or "standing"

        # Build the descriptive text mappings from numbers
        agility_desc = get_stat_description(caller.db.agility)
        appearance_desc = get_stat_description(caller.db.appearance)
        charisma_desc = get_stat_description(caller.db.charisma)
        dexterity_desc = get_stat_description(caller.db.dexterity)
        empathy_desc = get_stat_description(caller.db.empathy)
        endurance_desc = get_stat_description(caller.db.endurance)
        judgement_desc = get_stat_description(caller.db.judgement)
        memory_desc = get_stat_description(caller.db.memory)
        perception_desc = get_stat_description(caller.db.perception)
        reasoning_desc = get_stat_description(caller.db.reasoning)
        speed_desc = get_stat_description(caller.db.speed)
        strength_desc = get_stat_description(caller.db.strength)
        willpower_desc = get_stat_description(caller.db.willpower)

        # Format the block exactly to match your visual spacing rules
        sheet = f"""Character Sheet for {caller.key}
_____________________________________________________

Character Background

Name: {name:<30} Homeland: {homeland}
Marital Status: {marital:<22}
Citizenship Status: {citizenship:<20} Social Standing: {social}
Popularity:  {popularity}

Age: {age}

Physical Characteristics

Height: {height:<10} Weight: {weight} lbs.    Handed: {handed}
Eyes: {eyes:<12} Hair: {hair:<12} Complexion: {complexion}

Health Points: {hp}/{hp_max:<10} Fatigue: {fatigue}%        State: {state}

Load: {load} lbs.
Encumbrance: {encumbrance}

Position: {position}

Attributes:
Agility:    {agility_desc:<22} Appearance: {appearance_desc}
Charisma:   {charisma_desc:<22} Dexterity:  {dexterity_desc}
Empathy:    {empathy_desc:<22} Endurance:  {endurance_desc}
Judgement:  {judgement_desc:<22} Memory:     {memory_desc}
Perception: {perception_desc:<22} Reasoning:  {reasoning_desc}
Speed:      {speed_desc:<22} Strength:   {strength_desc}
Willpower:  {willpower_desc}

To see a list of skills and actions your character knows, type: skills

_____________________________________________________

"""

        caller.msg(sheet)
# -------------------------------------------------------------
#
# The default commands inherit from
#
#   evennia.commands.default.muxcommand.MuxCommand.
#
# If you want to make sweeping changes to default commands you can
# uncomment this copy of the MuxCommand parent and add
#
#   COMMAND_DEFAULT_CLASS = "commands.command.MuxCommand"
#
# to your settings file. Be warned that the default commands expect
# the functionality implemented in the parse() method, so be
# careful with what you change.
#
# -------------------------------------------------------------

# from evennia.utils import utils
#
#
# class MuxCommand(Command):
#     """
#     This sets up the basis for a MUX command. The idea
#     is that most other Mux-related commands should just
#     inherit from this and don't have to implement much
#     parsing of their own unless they do something particularly
#     advanced.
#
#     Note that the class's __doc__ string (this text) is
#     used by Evennia to create the automatic help entry for
#     the command, so make sure to document consistently here.
#     """
#     def has_perm(self, srcobj):
#         """
#         This is called by the cmdhandler to determine
#         if srcobj is allowed to execute this command.
#         We just show it here for completeness - we
#         are satisfied using the default check in Command.
#         """
#         return super().has_perm(srcobj)
#
#     def at_pre_cmd(self):
#         """
#         This hook is called before self.parse() on all commands
#         """
#         pass
#
#     def at_post_cmd(self):
#         """
#         This hook is called after the command has finished executing
#         (after self.func()).
#         """
#         pass
#
#     def parse(self):
#         """
#         This method is called by the cmdhandler once the command name
#         has been identified. It creates a new set of member variables
#         that can be later accessed from self.func() (see below)
#
#         The following variables are available for our use when entering this
#         method (from the command definition, and assigned on the fly by the
#         cmdhandler):
#            self.key - the name of this command ('look')
#            self.aliases - the aliases of this cmd ('l')
#            self.permissions - permission string for this command
#            self.help_category - overall category of command
#
#            self.caller - the object calling this command
#            self.cmdstring - the actual command name used to call this
#                             (this allows you to know which alias was used,
#                              for example)
#            self.args - the raw input; everything following self.cmdstring.
#            self.cmdset - the cmdset from which this command was picked. Not
#                          often used (useful for commands like 'help' or to
#                          list all available commands etc)
#            self.obj - the object on which this command was defined. It is often
#                          the same as self.caller.
#
#         A MUX command has the following possible syntax:
#
#           name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]
#
#         The 'name[ with several words]' part is already dealt with by the
#         cmdhandler at this point, and stored in self.cmdname (we don't use
#         it here). The rest of the command is stored in self.args, which can
#         start with the switch indicator /.
#
#         This parser breaks self.args into its constituents and stores them in the
#         following variables:
#           self.switches = [list of /switches (without the /)]
#           self.raw = This is the raw argument input, including switches
#           self.args = This is re-defined to be everything *except* the switches
#           self.lhs = Everything to the left of = (lhs:'left-hand side'). If
#                      no = is found, this is identical to self.args.
#           self.rhs: Everything to the right of = (rhs:'right-hand side').
#                     If no '=' is found, this is None.
#           self.lhslist - [self.lhs split into a list by comma]
#           self.rhslist - [list of self.rhs split into a list by comma]
#           self.arglist = [list of space-separated args (stripped, including '=' if it exists)]
#
#           All args and list members are stripped of excess whitespace around the
#           strings, but case is preserved.
#         """
#         raw = self.args
#         args = raw.strip()
#
#         # split out switches
#         switches = []
#         if args and len(args) > 1 and args[0] == "/":
#             # we have a switch, or a set of switches. These end with a space.
#             switches = args[1:].split(None, 1)
#             if len(switches) > 1:
#                 switches, args = switches
#                 switches = switches.split('/')
#             else:
#                 args = ""
#                 switches = switches[0].split('/')
#         arglist = [arg.strip() for arg in args.split()]
#
#         # check for arg1, arg2, ... = argA, argB, ... constructs
#         lhs, rhs = args, None
#         lhslist, rhslist = [arg.strip() for arg in args.split(',')], []
#         if args and '=' in args:
#             lhs, rhs = [arg.strip() for arg in args.split('=', 1)]
#             lhslist = [arg.strip() for arg in lhs.split(',')]
#             rhslist = [arg.strip() for arg in rhs.split(',')]
#
#         # save to object properties:
#         self.raw = raw
#         self.switches = switches
#         self.args = args.strip()
#         self.arglist = arglist
#         self.lhs = lhs
#         self.lhslist = lhslist
#         self.rhs = rhs
#         self.rhslist = rhslist
#
#         # if the class has the account_caller property set on itself, we make
#         # sure that self.caller is always the account if possible. We also create
#         # a special property "character" for the puppeted object, if any. This
#         # is convenient for commands defined on the Account only.
#         if hasattr(self, "account_caller") and self.account_caller:
#             if utils.inherits_from(self.caller, "evennia.objects.objects.DefaultObject"):
#                 # caller is an Object/Character
#                 self.character = self.caller
#                 self.caller = self.caller.account
#             elif utils.inherits_from(self.caller, "evennia.accounts.accounts.DefaultAccount"):
#                 # caller was already an Account
#                 self.character = self.caller.get_puppet(self.session)
#             else:
#                 self.character = None
