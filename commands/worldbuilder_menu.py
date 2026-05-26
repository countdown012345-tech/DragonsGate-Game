"""
EvMenu nodes for the Worldbuilder menu, starting with Room Builder as the only option.
"""
from evennia.utils.evmenu import EvMenu


REVERSE_DIRECTIONS = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
    "up": "down",
    "down": "up",
    "northeast": "southwest",
    "northwest": "southeast",
    "southeast": "northwest",
    "southwest": "northeast",
}


def _state(caller):
    if not caller.ndb._evmenu_room_builder:
        caller.ndb._evmenu_room_builder = {}
    return caller.ndb._evmenu_room_builder


def _search_rooms(query):
    from evennia import search_object
    from typeclasses.rooms import Room

    query = (query or "").strip()
    if not query:
        return []
    return [obj for obj in search_object(query) if isinstance(obj, Room)]


def _cleanup_exit_and_door(exit_obj):
    if not exit_obj:
        return
    door = getattr(exit_obj.db, "door", None)
    if door:
        partner = getattr(door.db, "partner", None)
        if partner:
            partner.db.partner = None
            partner.delete()
        door.delete()
    exit_obj.delete()


def _aggressive_delete_room(room):
    if not room:
        return
    for obj in list(room.contents):
        if obj.destination:
            _cleanup_exit_and_door(obj)
        else:
            obj.delete()
    room.delete()

def node_main_menu(caller, raw_string, **kwargs):
    text = """
    |cWorldbuilder Menu|n

    Please select an option:
    """
    options = [
        {"desc": "Room Builder", "goto": "node_room_builder"},
        # Future options: Objects, Characters, etc.
        {"desc": "Quit", "goto": "node_quit"},
    ]
    return text, options

def node_quit(caller, raw_string, **kwargs):
    caller.msg("Exiting Worldbuilder menu.")
    return None

def node_room_builder(caller, raw_string, **kwargs):

    # --- Room Builder Menu State and Flow ---
    text = """
    |cRoom Builder|n

    What would you like to do?
    """
    options = [
        {"desc": "Create Room", "goto": "node_create_room_shortdesc"},
        {"desc": "Delete Room", "goto": "node_delete_room_direction"},
        {"desc": "Add Exit to Another Room", "goto": "node_add_exit_search"},
        {"desc": "Back to Main Menu", "goto": "node_main_menu"},
    ]
    return text, options

def node_create_room_shortdesc(caller, raw_string, **kwargs):
    caller.ndb._evmenu_room_builder = {}  # Reset state
    text = "Enter a short description for the new room:"
    options = ({"key": "_default", "goto": "node_create_room_longdesc"},)
    return text, options

def node_create_room_longdesc(caller, raw_string, **kwargs):
    state = caller.ndb._evmenu_room_builder
    state["shortdesc"] = raw_string.strip()
    text = "Enter a long description for the new room:"
    options = ({"key": "_default", "goto": "node_create_room_direction"},)
    return text, options

def node_create_room_direction(caller, raw_string, **kwargs):
    state = caller.ndb._evmenu_room_builder
    state["longdesc"] = raw_string.strip()
    text = "Which direction from here should the new room be created? (e.g., north, east, up)"
    options = ({"key": "_default", "goto": "node_create_room_door"},)
    return text, options

def node_create_room_door(caller, raw_string, **kwargs):
    state = caller.ndb._evmenu_room_builder
    state["direction"] = raw_string.strip().lower()
    state.setdefault("door", False)
    state.setdefault("linkback", True)
    text = f"Add a door to the exit? (yes/no) [Current: {'yes' if state['door'] else 'no'}]"
    options = [
        {"key": "yes", "desc": "Yes", "goto": ("node_create_room_linkback", {"door": True})},
        {"key": "no", "desc": "No", "goto": ("node_create_room_linkback", {"door": False})},
    ]
    return text, options

def node_create_room_linkback(caller, raw_string, door=None, **kwargs):
    state = caller.ndb._evmenu_room_builder
    if door is not None:
        state["door"] = door
    text = f"Create a linkback exit from the new room? (yes/no) [Current: {'yes' if state['linkback'] else 'no'}]"
    options = [
        {"key": "yes", "desc": "Yes", "goto": ("node_create_room_confirm", {"linkback": True})},
        {"key": "no", "desc": "No", "goto": ("node_create_room_confirm", {"linkback": False})},
    ]
    return text, options

def node_create_room_confirm(caller, raw_string, linkback=None, **kwargs):
    state = caller.ndb._evmenu_room_builder
    if linkback is not None:
        state["linkback"] = linkback
    text = (
        f"|cConfirm Room Creation|n\n"
        f"Short Desc: {state['shortdesc']}\n"
        f"Long Desc: {state['longdesc']}\n"
        f"Direction: {state['direction']}\n"
        f"Door: {'yes' if state['door'] else 'no'}\n"
        f"Linkback: {'yes' if state['linkback'] else 'no'}\n\n"
        "Proceed?"
    )
    options = [
        {"desc": "Create Room", "goto": "node_create_room_do_create"},
        {"desc": "Cancel", "goto": "node_room_builder"},
    ]
    return text, options

def node_create_room_do_create(caller, raw_string, **kwargs):
    from evennia import create_object
    from typeclasses.rooms import Room
    from typeclasses.exits import DoorAwareExit
    from commands.builder_helpers import create_linked_door_pair
    state = caller.ndb._evmenu_room_builder
    # Create the new room
    new_room = create_object(Room, key=state["shortdesc"], location=None)
    new_room.db.desc = state["longdesc"]
    # Create the exit from current room to new room
    exit_to = create_object(DoorAwareExit, key=state["direction"], location=caller.location, destination=new_room)
    # Optionally create a linkback exit
    if state["linkback"]:
        reverse_dir = REVERSE_DIRECTIONS.get(state["direction"], "back")
        exit_back = create_object(DoorAwareExit, key=reverse_dir, location=new_room, destination=caller.location)
    else:
        exit_back = None
    # Optionally create doors and link them
    if state["door"]:
        create_linked_door_pair(caller.location, new_room, exit1=exit_to, exit2=exit_back)
    caller.msg("Room created!")
    return "Room created!", [
        {"desc": "Back to Room Builder", "goto": "node_room_builder"},
        {"desc": "Back to Main Menu", "goto": "node_main_menu"},
    ]


def node_delete_room_direction(caller, raw_string, **kwargs):
    text = "Which exit direction from this room do you want to delete?"
    options = ({"key": "_default", "goto": "node_delete_room_confirm_room"},)
    return text, options


def node_delete_room_confirm_room(caller, raw_string, **kwargs):
    st = _state(caller)
    st["delete_direction"] = raw_string.strip().lower()
    direction = st["delete_direction"]
    exit_obj = caller.search(direction, location=caller.location, quiet=True)
    exit_obj = exit_obj[0] if exit_obj else None
    if not exit_obj or not exit_obj.destination:
        return "No exit found in that direction.", [{"desc": "Back", "goto": "node_room_builder"}]

    st["delete_exit"] = exit_obj
    st["delete_target_room"] = exit_obj.destination
    text = (
        f"Delete exit '{direction}' to '{exit_obj.destination.key}'.\n"
        "Also delete the target room and all its exits/contents?"
    )
    options = [
        {"key": "yes", "desc": "Yes, delete target room too", "goto": ("node_delete_room_do_delete", {"delete_target": True})},
        {"key": "no", "desc": "No, delete exit only", "goto": ("node_delete_room_do_delete", {"delete_target": False})},
        {"desc": "Cancel", "goto": "node_room_builder"},
    ]
    return text, options


def node_delete_room_do_delete(caller, raw_string, delete_target=False, **kwargs):
    st = _state(caller)
    exit_obj = st.get("delete_exit")
    target_room = st.get("delete_target_room")

    if not exit_obj:
        return "Exit no longer exists.", [{"desc": "Back", "goto": "node_room_builder"}]

    _cleanup_exit_and_door(exit_obj)

    if delete_target and target_room:
        _aggressive_delete_room(target_room)
        msg = "Exit and target room deleted."
    else:
        msg = "Exit deleted."

    return msg, [{"desc": "Back to Room Builder", "goto": "node_room_builder"}]


def node_add_exit_search(caller, raw_string, **kwargs):
    st = _state(caller)
    st["add_exit"] = {}
    text = "Search for a target room by name/string:"
    options = ({"key": "_default", "goto": "node_add_exit_pick_result"},)
    return text, options


def node_add_exit_pick_result(caller, raw_string, **kwargs):
    st = _state(caller)
    matches = _search_rooms(raw_string)
    st["add_exit"]["matches"] = matches
    if not matches:
        return "No matching rooms found.", [{"desc": "Search again", "goto": "node_add_exit_search"}, {"desc": "Back", "goto": "node_room_builder"}]

    text = "Select a target room:"
    options = []
    for idx, room in enumerate(matches, start=1):
        options.append({"desc": f"{idx}. {room.key} (#{room.id})", "goto": ("node_add_exit_direction", {"room_index": idx - 1})})
    options.append({"desc": "Cancel", "goto": "node_room_builder"})
    return text, options


def node_add_exit_direction(caller, raw_string, room_index=None, **kwargs):
    st = _state(caller)
    matches = st.get("add_exit", {}).get("matches", [])
    if room_index is None or room_index >= len(matches):
        return "Invalid selection.", [{"desc": "Back", "goto": "node_add_exit_search"}]

    st["add_exit"]["target_room"] = matches[room_index]
    text = "Which direction from here should this new exit use?"
    options = ({"key": "_default", "goto": "node_add_exit_door"},)
    return text, options


def node_add_exit_door(caller, raw_string, **kwargs):
    st = _state(caller)
    st["add_exit"]["direction"] = raw_string.strip().lower()
    st["add_exit"].setdefault("door", False)
    st["add_exit"].setdefault("linkback", True)
    text = f"Add a door to this exit? [Current: {'yes' if st['add_exit']['door'] else 'no'}]"
    options = [
        {"key": "yes", "desc": "Yes", "goto": ("node_add_exit_linkback", {"door": True})},
        {"key": "no", "desc": "No", "goto": ("node_add_exit_linkback", {"door": False})},
    ]
    return text, options


def node_add_exit_linkback(caller, raw_string, door=None, **kwargs):
    st = _state(caller)
    if door is not None:
        st["add_exit"]["door"] = door
    text = f"Create linkback exit from target room? [Current: {'yes' if st['add_exit']['linkback'] else 'no'}]"
    options = [
        {"key": "yes", "desc": "Yes", "goto": ("node_add_exit_confirm", {"linkback": True})},
        {"key": "no", "desc": "No", "goto": ("node_add_exit_confirm", {"linkback": False})},
    ]
    return text, options


def node_add_exit_confirm(caller, raw_string, linkback=None, **kwargs):
    st = _state(caller)
    if linkback is not None:
        st["add_exit"]["linkback"] = linkback
    data = st["add_exit"]
    text = (
        "|cConfirm Add Exit|n\n"
        f"Target Room: {data['target_room'].key} (#{data['target_room'].id})\n"
        f"Direction: {data['direction']}\n"
        f"Door: {'yes' if data['door'] else 'no'}\n"
        f"Linkback: {'yes' if data['linkback'] else 'no'}\n\n"
        "Proceed?"
    )
    options = [
        {"desc": "Create Exit", "goto": "node_add_exit_do_create"},
        {"desc": "Cancel", "goto": "node_room_builder"},
    ]
    return text, options


def node_add_exit_do_create(caller, raw_string, **kwargs):
    from evennia import create_object
    from typeclasses.exits import DoorAwareExit
    from commands.builder_helpers import create_linked_door_pair

    st = _state(caller)
    data = st.get("add_exit", {})
    target_room = data.get("target_room")
    direction = data.get("direction")
    if not target_room or not direction:
        return "Missing exit data.", [{"desc": "Back", "goto": "node_room_builder"}]

    exit_to = create_object(DoorAwareExit, key=direction, location=caller.location, destination=target_room)

    if data.get("linkback", True):
        rev = REVERSE_DIRECTIONS.get(direction, "back")
        exit_back = create_object(DoorAwareExit, key=rev, location=target_room, destination=caller.location)
    else:
        exit_back = None

    if data.get("door", False):
        create_linked_door_pair(caller.location, target_room, exit1=exit_to, exit2=exit_back)

    return "Exit created.", [{"desc": "Back to Room Builder", "goto": "node_room_builder"}]
