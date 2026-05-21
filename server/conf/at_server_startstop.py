from evennia import DefaultScript

class GlobalHeartbeatScript(DefaultScript):
    """
    A single global script running engine-wide every 2 seconds.
    Synchronizes vital regenerations and processes combat action queues.
    """
    def at_script_creation(self):
        self.key = "global_heartbeat"
        self.desc = "Synchronized global combat queue processor and regeneration heartbeat."
        self.interval = 2  # Universal game tick length = 2 seconds
        self.persistent = True

    def at_repeat(self):
        """Fires every 2 seconds across all active characters."""
        # FIX: Explicit database model import to bypass shortcut restrictions
        from evennia.accounts.models import AccountDB

        # Loop ONLY over accounts that are actively connected online
        for account in AccountDB.objects.get_connected_accounts():
            obj = account.character
            if not obj or not hasattr(obj, "db"):
                continue

            try:
                # Direct database lookup to completely bypass caching issues
                cooldown = obj.attributes.get("combat_cooldown")
                
                if cooldown is not None and cooldown > 0:
                    # Let the character execute its decrement & action steps
                    obj.combat_tick()

                # Passive Pool Regeneration
                hp = obj.attributes.get("hp") or 0
                hp_max = obj.attributes.get("hp_max") or 100
                if hp < hp_max:
                    con = obj.attributes.get("constitution") or 10
                    regen_bonus = max(1, con // 5)
                    obj.attributes.add("hp", min(hp_max, hp + regen_bonus))
                    
                stamina = obj.attributes.get("stamina") or 0
                stamina_max = obj.attributes.get("stamina_max") or 50
                if stamina < stamina_max:
                    obj.attributes.add("stamina", min(stamina_max, stamina + 2))
                    
            except Exception as e:
                obj.msg(f"|r[ERROR] Heartbeat loop encountered: {e}|n")


def at_server_init():
    pass

def at_server_start():
    from evennia.utils.create import create_script
    from evennia import ScriptDB
    
    if not ScriptDB.objects.filter(db_key="global_heartbeat"):
        create_script(GlobalHeartbeatScript)

def at_server_stop():
    pass