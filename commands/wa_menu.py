"""
EvMenu nodes for Welcome Area account management (@menu).
"""

from evennia import search_object, create_object


def _get_account(caller):
    """Allow menu to be opened from either Account or puppeted Character."""
    return caller if hasattr(caller, "create_character") else getattr(caller, "account", None)


def _wa_chars(account):
    return list(account.db.wa_characters or [])


def _save_wa_chars(account, chars):
    account.db.wa_characters = chars


def _first(result):
    """Handle Evennia search return styles (single obj vs iterable)."""
    if not result:
        return None
    if isinstance(result, (list, tuple)):
        return result[0] if result else None
    if hasattr(result, "__iter__") and not isinstance(result, (str, bytes)):
        try:
            return next(iter(result), None)
        except TypeError:
            pass
    return result


def node_wa_main(caller, raw_string, **kwargs):
    account = _get_account(caller)
    if not account:
        return "No account context found.", None
    text = "|cWelcome Area Menu|n\n\nChoose an option:"
    options = [
        {"desc": "Create a new character", "goto": "node_wa_create_name"},
        {"desc": "Delete a character", "goto": "node_wa_delete_prompt"},
        {"desc": "Select a character to play", "goto": "node_wa_select"},
        {"desc": "Quit", "goto": "node_wa_quit"},
    ]
    return text, options


def node_wa_quit(caller, raw_string, **kwargs):
    account = _get_account(caller)
    account.msg("Exiting menu.")
    return None


def node_wa_create_name(caller, raw_string, **kwargs):
    text = "Enter a character name:"
    options = ({"key": "_default", "goto": "node_wa_create_do"},)
    return text, options


def node_wa_create_do(caller, raw_string, **kwargs):
    account = _get_account(caller)
    if not account:
        return "No account context found.", [{"desc": "Back", "goto": "node_wa_main"}]

    name = (raw_string or "").strip()
    if not name:
        return "Name cannot be empty.", [{"desc": "Try again", "goto": "node_wa_create_name"}]

    if search_object(name):
        return "That name is already in use.", [{"desc": "Try another", "goto": "node_wa_create_name"}]

    home = _first(search_object("#10"))
    if not home:
        return "Home room #10 was not found.", [{"desc": "Back", "goto": "node_wa_main"}]

    try:
        char = create_object(
            "typeclasses.characters.Character",
            key=name,
            home=home,
            location=home,
        )
        char.locks.add(f"puppet:id({account.id}) or perm(Developer)")
        account.characters.add(char)
    except Exception as err:
        return f"Character creation failed: {err}", [{"desc": "Back", "goto": "node_wa_main"}]

    chars = _wa_chars(account)
    if char not in chars:
        chars.append(char)
        _save_wa_chars(account, chars)

    return f"Created character '{char.key}'.", [{"desc": "Back", "goto": "node_wa_main"}]


def node_wa_delete_prompt(caller, raw_string, **kwargs):
    account = _get_account(caller)
    chars = _wa_chars(account)
    if not chars:
        return "No characters to delete.", [{"desc": "Back", "goto": "node_wa_main"}]
    listing = "\n".join(f"- {char.key}" for char in chars if char)
    text = (
        "Type exactly: CONFIRM <character name>\n\n"
        f"Your characters:\n{listing}"
    )
    options = ({"key": "_default", "goto": "node_wa_delete_do"},)
    return text, options


def node_wa_delete_do(caller, raw_string, **kwargs):
    account = _get_account(caller)
    data = (raw_string or "").strip()
    if not data.lower().startswith("confirm "):
        return "Deletion aborted (must use CONFIRM <character name>).", [{"desc": "Back", "goto": "node_wa_main"}]

    target_name = data[8:].strip().lower()
    chars = _wa_chars(account)
    target = next((char for char in chars if char and char.key.lower() == target_name), None)
    if not target:
        return "No matching character in your WA list.", [{"desc": "Back", "goto": "node_wa_main"}]

    chars = [char for char in chars if char and char.id != target.id]
    _save_wa_chars(account, chars)
    target.delete()
    return f"Deleted '{target_name}'.", [{"desc": "Back", "goto": "node_wa_main"}]


def node_wa_select(caller, raw_string, **kwargs):
    account = _get_account(caller)
    chars = [char for char in _wa_chars(account) if char]
    _save_wa_chars(account, chars)
    if not chars:
        return "No characters available.", [{"desc": "Back", "goto": "node_wa_main"}]

    text = "Select a character to play:"
    options = []
    for idx, char in enumerate(chars, start=1):
        options.append(
            {
                "desc": f"{idx}. {char.key}",
                "goto": ("node_wa_select_do", {"char_index": idx - 1}),
            }
        )
    options.append({"desc": "Back", "goto": "node_wa_main"})
    return text, options


def node_wa_select_do(caller, raw_string, char_index=None, **kwargs):
    account = _get_account(caller)
    chars = [char for char in _wa_chars(account) if char]
    if char_index is None or char_index >= len(chars):
        return "Invalid selection.", [{"desc": "Back", "goto": "node_wa_select"}]

    char = chars[char_index]
    if char.db.last_known_location:
        char.location = char.db.last_known_location
    elif char.home:
        char.location = char.home

    sessions = account.sessions.get()
    if not sessions:
        return "No active session found.", [{"desc": "Back", "goto": "node_wa_main"}]

    account.puppet_object(sessions[0], char)
    return None
