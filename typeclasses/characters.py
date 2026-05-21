from evennia import DefaultCharacter

class Character(DefaultCharacter):
    """
    The main character template for DragonsGate.
    Tracks background, physical metrics, statistics, skills, vitality pools, 
    and processes the combat action queue.
    """
    def at_object_creation(self):
        """Called once when a character is first created in the database."""
        super().at_object_creation()
        
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
        self.db.weight = 197  # Numeric so we can calculate encumbrance or health modifications
        self.db.handed = "Right"
        self.db.eyes = "steel"
        self.db.hair = "coal-black"
        self.db.complexion = "tan"

        # 3. Attributes (Expanded List)
        # Using numeric values internally (1-20+ baseline) so calculations work.
        # The stats command will translate these into descriptive text!
        self.db.strength = 14       # great
        self.db.agility = 13        # very good
        self.db.constitution = 10   # impacts maximum HP scaling
        self.db.charisma = 8        # slightly below average
        self.db.empathy = 8         # slightly below average
        self.db.judgement = 13      # very good
        self.db.perception = 11     # slightly above average
        self.db.speed = 16          # outstanding
        self.db.willpower = 10      # good
        self.db.appearance = 9      # average
        self.db.dexterity = 15      # remarkable
        self.db.endurance = 16      # outstanding
        self.db.memory = 10         # good
        self.db.reasoning = 14      # great
        
        # 4. Vitality & Status
        self.db.hp = 197
        self.db.hp_max = 197
        self.db.stamina = 50
        self.db.stamina_max = 50
        self.db.fatigue_pct = 19    # Saved as % depleted or % remaining. We'll map to your layout!
        self.db.state = "conscious"
        self.db.position = "standing"
        self.db.load_lbs = 112
        self.db.encumbrance = "You are bearing a moderate load."

        # 5. Skill Mastery Tracking
        self.db.skills = {
            "Unarmed": {"level": 1, "xp": 0, "xp_needed": 100},
            "Dagger": {"level": 1, "xp": 0, "xp_needed": 100},
            "Sword": {"level": 1, "xp": 0, "xp_needed": 100},
            "Axe": {"level": 1, "xp": 0, "xp_needed": 100}
        }

        # 6. Combat Variables
        self.db.combat_speed = 3       
        self.db.combat_cooldown = 0     
        self.db.queued_action = None    
        self.db.slots = {"main_hand": None}

    def train_skill(self, skill_name, amount):
        """ Adds experience to a specified weapon mastery category and checks for level ups. """
        skills = self.db.skills
        if not skills or skill_name not in skills:
            return

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

    def queue_action(self, action_type, target):
        """ Main player combat queue entry point. """
        if not target or target.location != self.location:
            self.msg("Your target is no longer here.")
            self.db.queued_action = None
            return

        speed_cost = self.db.combat_speed
        weapon = self.db.slots.get("main_hand")
        if weapon and hasattr(weapon, "db") and weapon.db.speed_cost:
            speed_cost = weapon.db.speed_cost

        current_cooldown = self.attributes.get("combat_cooldown") or 0

        if current_cooldown == 0:
            self.execute_action(action_type, target)
            self.attributes.add("combat_cooldown", int(speed_cost))
            return

        old_action = self.db.queued_action
        self.db.queued_action = (action_type, target)

        if old_action:
            old_type, _ = old_action
            self.msg(f"|yChanged your mind. Switched from {old_type} to {action_type} on {target.key}.|n")
        else:
            self.msg(f"|gQueued up a {action_type} on {target.key}. ({current_cooldown} ticks remaining)|n")

    def combat_tick(self):
        """ Processed by the global server heartbeat script. """
        cooldown = self.attributes.get("combat_cooldown") or 0
        if cooldown > 0:
            cooldown -= 1
            self.attributes.add("combat_cooldown", int(cooldown))
            
            if cooldown == 0:
                if self.db.queued_action:
                    action_type, target = self.db.queued_action
                    
                    if target and target.location == self.location:
                        self.execute_action(action_type, target)
                        
                        weapon = self.db.slots.get("main_hand")
                        speed_cost = weapon.db.speed_cost if (weapon and weapon.db.speed_cost) else self.db.combat_speed
                        self.attributes.add("combat_cooldown", int(speed_cost))
                    else:
                        self.msg("Your target is gone. Action canceled.")
                        
                    self.db.queued_action = None
                else:
                    self.msg("|gYou are ready for your next move!|n")

    def execute_action(self, action_type, target):
        """Calculate damage and directly reward weapon proficiency skill XP."""
        damage = self.db.strength // 2
        weapon = self.db.slots.get("main_hand")
        weapon_type = "Unarmed"
        
        if weapon and hasattr(weapon, "db"):
            if weapon.db.damage:
                damage += weapon.db.damage
            if weapon.db.weapon_type:
                weapon_type = weapon.db.weapon_type

        skill_level = 1
        if self.db.skills and weapon_type in self.db.skills:
            skill_level = self.db.skills[weapon_type]["level"]
        
        mastery_modifier = 1.0 + ((skill_level - 1) * 0.05)
        damage = int(damage * mastery_modifier)

        if action_type == "stab":
            damage = int(damage * 0.9)
            self.msg(f"|wYou lunge forward and STAB {target.key}!|n")
            target.msg(f"|r{self.key} lunges forward and stabs you!|n")
        elif action_type == "slash":
            damage = int(damage * 1.3)
            self.msg(f"|wYou swing wide and SLASH {target.key}!|n")
            target.msg(f"|r{self.key} swings wide and slashes you!|n")

        if hasattr(target, "at_damage"):
            target.at_damage(damage, self)
        elif hasattr(target, "db") and "hp" in target.db.all():
            target.db.hp -= damage
            if target.db.hp <= 0:
                self.msg(f"You have defeated {target.key}!")

        self.train_skill(weapon_type, 15)

    def at_damage(self, amount, attacker):
        """Called when this character takes damage."""
        self.db.hp -= amount
        self.msg(f"|rYou take {amount} damage! (HP: {self.db.hp}/{self.db.hp_max})|n")
        if self.db.hp <= 0:
            self.msg("|RYou have died!|n")
            self.db.hp = 10
            self.move_to(self.home)