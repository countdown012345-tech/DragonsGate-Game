from evennia import DefaultCharacter
import random

from commands.default_cmdsets import GameMasterCmdSet

class Character(DefaultCharacter):
    """
    The main character template for DragonsGate.
    Tracks background, physical metrics, statistics, skills, vitality pools, 
    and processes the combat action queue.
    """
    def at_object_creation(self):
        super().at_object_creation()

    def at_cmdset_get(self, **kwargs):
        super().at_cmdset_get(**kwargs)
        # Add GameMasterCmdSet if the character has the Gamemaster permission
        if self.locks.check_lockstring(self, "perm(Gamemaster)"):
            self.cmdset.add(GameMasterCmdSet, permanent=True)
        # Add other command sets here as needed for Storyteller, WelcomeArea, PlayerCharacter, etc.
        
        # 1. Character Background
        self.db.full_name = self.key
        self.db.homeland = "Iridine"
        self.db.marital_status = "Single"
        self.db.citizenship = "Iridine"
        self.db.social_standing = "Head Count"
        self.db.popularity = 0
        self.db.age = 18

        # 2. Physical Characteristics
        self.db.height = "6' 6\""
        self.db.weight = 197
        self.db.handed = "Right"
        self.db.eyes = "steel"
        self.db.hair = "coal-black"
        self.db.complexion = "tan"

        # 3. Attributes
        for attr in ["strength", "agility", "constitution", "charisma", "empathy", 
                     "judgement", "perception", "speed", "willpower", "appearance", 
                     "dexterity", "endurance", "memory", "reasoning"]:
            setattr(self.db, attr, 100)
        
        # 4. Vitality & Status
        self.db.hp = 197
        self.db.hp_max = 197
        self.db.stamina = 50
        self.db.stamina_max = 50
        self.db.fatigue_pct = 19
        self.db.state = "conscious"
        self.db.position = "standing"
        self.db.load_lbs = 112
        self.db.encumbrance = "You are bearing a moderate load."

        # 5. Skill Mastery Tracking
        self.db.skills = {
            "Unarmed": {"level": 1, "xp": 0, "xp_needed": 100},
            "Knives": {"level": 1, "xp": 0, "xp_needed": 100},
            "One Handed Crushing": {"level": 1, "xp": 0, "xp_needed": 100}
        }

    def at_cmdset_get(self, **kwargs):
        super().at_cmdset_get(**kwargs)
        # Add GameMasterCmdSet if the character has the Gamemaster permission
        if self.locks.check_lockstring(self, "perm(Gamemaster)"):
            self.cmdset.add(GameMasterCmdSet, permanent=True)
        # Add other command sets here as needed for Storyteller, WelcomeArea, PlayerCharacter, etc.
        # 6. Combat Variables
        self.db.combat_speed = 3        
        self.db.combat_cooldown = 0    
        self.db.action_sequence = []
        self.db.action_loop = False
        self.db.current_target = None
        self.db.slots = {"main_hand": None}

    def get_combat_stats(self):
        p, e, d, s, sp, a = (self.db.perception or 100), (self.db.empathy or 100), \
                            (self.db.dexterity or 100), (self.db.strength or 100), \
                            (self.db.speed or 100), (self.db.agility or 100)
        aim = min(((p / 4) + (e / 4) + (d / 2)), 200) + (s / 10)
        dodge = (sp / 4) + (a / 2)
        return aim, dodge

    def train_skill(self, skill_name, amount):
        skills = self.db.skills or {}
        if skill_name not in skills: return
        skill = skills[skill_name]
        skill["xp"] += amount
        if skill["xp"] >= skill["xp_needed"]:
            skill["xp"] -= skill["xp_needed"]
            skill["level"] += 1
            skill["xp_needed"] = int(skill["xp_needed"] * 1.2)
            self.msg(f"\n|G* Your proficiency grows! Mastery in [{skill_name}] has increased to Level {skill['level']}! *|n\n")
        else:
            self.msg(f"|g[Skill Gain: +{amount} {skill_name} XP ({skill['xp']}/{skill['xp_needed']})]|n")
        self.db.skills = skills

    def queue_action(self, action_string, target):
        actions = [a.strip().lower() for a in action_string.split(",")]
        loop = "*" in actions
        if loop: actions.remove("*")
        self.db.original_sequence = list(actions)
        self.db.action_sequence = list(actions)
        self.db.action_loop = loop
        self.db.current_target = target
        self.msg(f"|gQueued sequence: {', '.join(actions)}{' (Looping)' if loop else ''}|n")
        self.process_next_action()

    def process_next_action(self):
        if not self.db.action_sequence:
            if self.db.action_loop and self.db.original_sequence:
                self.db.action_sequence = list(self.db.original_sequence)
            else:
                self.db.current_target = None
                return
        if (self.db.combat_cooldown or 0) > 0: return

        action_type = self.db.action_sequence.pop(0)
        target = self.db.current_target
        if target and target.location == self.location:
            self.execute_action(action_type, target)
        else:
            self.msg("Target lost. Ending sequence.")
            self.db.action_sequence = []
            self.db.action_loop = False

    def combat_tick(self):
        cooldown = self.attributes.get("combat_cooldown") or 0
        if cooldown > 0:
            cooldown -= 1
            self.attributes.add("combat_cooldown", int(cooldown))
            if cooldown == 0:
                self.msg("|gYou are no longer busy.|n")
                self.process_next_action()

    def execute_action(self, action_type, target):
        aim, _ = self.get_combat_stats()
        _, target_dodge = target.get_combat_stats() if hasattr(target, "get_combat_stats") else (0, 75)
        target_difficulty = max(5, min(95, 50 - (aim - target_dodge)))
        roll = random.randint(1, 100)
        self.msg(f"|c[Success: {target_difficulty:.1f}, Roll: {roll}]|n")
        
        if roll <= target_difficulty:
            self.msg(f"|yYou try to {action_type} {target.key}, but you miss!|n")
            target.msg(f"|y{self.key} tries to {action_type} you, but misses!|n")
        else:
            damage = self.db.strength // 2
            weapon = self.db.slots.get("main_hand")
            weapon_type = "Unarmed"
            if weapon and hasattr(weapon, "db"):
                if weapon.db.damage: damage += weapon.db.damage
                if weapon.db.weapon_type: weapon_type = weapon.db.weapon_type
            
            skill_level = (self.db.skills or {}).get(weapon_type, {}).get("level", 1)
            damage = int(damage * (1.0 + ((skill_level - 1) * 0.05)))

            if action_type == "stab": damage = int(damage * 0.9)
            elif action_type in ["slash", "smash", "bash"]: damage = int(damage * 1.2)
            
            self.msg(f"|wYou perform {action_type} on {target.key}!|n")
            if hasattr(target, "at_damage"): target.at_damage(damage, self)
            elif hasattr(target, "db"): 
                target.db.hp -= damage
            self.train_skill(weapon_type, 15)

        weapon = self.db.slots.get("main_hand")
        speed_cost = weapon.db.speed_cost if (weapon and hasattr(weapon, "db") and weapon.db.speed_cost) else self.db.combat_speed
        self.attributes.add("combat_cooldown", int(speed_cost))
        if speed_cost > 0:
            self.msg(f"|yYou will be busy for {speed_cost} more second(s).|n")

    def at_damage(self, amount, attacker):
        self.db.hp -= amount
        self.msg(f"|rYou take {amount} damage! (HP: {self.db.hp}/{self.db.hp_max})|n")
        if self.db.hp <= 0:
            self.msg("|RYou have died!|n")
            self.db.hp = 10
            self.move_to(self.home)