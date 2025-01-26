import random
from game_enums import AttackType, Stats
from skill import Skill

class Attack:
    '''
    An assistant class used by characters to store info of their attacks and to determine their damage output.
    '''
    
    def __init__(self,user):
        '''
        @param data: Basic data of the attack in format (user, range, power, accuracy, name, flavor).
        '''
        # Most of these are placeholders and actually defined in subclasses.
        self.user           = user          # User of the attack
        self.min_range      = None          # Minumum range of the attack
        self.max_range      = None          # Maximum range of the attack
        self.power          = None          # Basic power of the attack
        self.accuracy       = None          # Accuracy in percents
        self.name           = ''            # Name of the attack
        self.flavor         = ''            # String that tells basic info of attack
        self.type           = None          # Tells the type of attack
        self.target_enemy   = True          # True if targets enemies, False if allies (Always True for attacks)
        self.attack_type    = None
        self.defense_type   = None
        self.action_type    = "a"           # 'a' for attack
        

    def calculate_damage(self, target, verbose=True):
        '''
        Method calculates the damage character would deal to 'target' with this attack. No actual damage will be done.
        Method assumes that target is in range of attack (can be determined with method define_attack_targets)
        @param target: The character which is taking the attack
        @param attack: The attack with which damage is dealt
        @return: Damage that would be done in hp
        '''
                
        damage = self.calculate_max_damage(target)        
        miss = random.randint(1,100)
        if miss > self.calculate_accuracy(target):
            damage = 0
            if verbose:
                print("Hyokkays meni ohi...")
            
        return damage
    
    
    def calculate_accuracy(self,target):
        '''
        Calculates accuracy when using attack on target.
        '''       
        accuracy = self.accuracy - target.get_stats()[Stats.EVASION]    # Basic accuracy: Attack's own accuracy - target's evasion
        factor = self.user.get_stats()[Stats.SPEED] / target.get_stats()[Stats.SPEED]   # Both attacker's and defender's speed affects accuracy
        if factor < 1 / 3:  # Maximum amount by which speed can reduce accuracy
            factor = 1/3
        accuracy = accuracy * factor
        
        '''
        combat_skills = Skill.passive_combat
        relevant_skills = []
        
        for skill in self.user.get_full_skills():
            if skill.get_type() in combat_skills:
                relevant_skills.append(skill)
                
        for skill in target.get_full_skills():
            if skill.get_type() in combat_skills:
                relevant_skills.append(skill)
        '''
        
        for skill in self.user.get_full_skills():
            accuracy = skill.define_accuracy(accuracy,self.user,target)
        for skill in target.get_full_skills():
            accuracy = skill.define_accuracy(accuracy,self.user,target)
        
        accuracy = round(accuracy)
        if accuracy > 100:
            accuracy = 100
        if accuracy < 0:
            accuracy = 0
        return accuracy
    
    
    def calculate_max_damage(self, target):
        '''
        Calculates the damage assuming that the attack will land.
        '''
        attack = self.user.get_stats()[self.attack_type]
        defense = target.get_stats()[self.defense_type]
        damage = (attack - defense) * self.power
        if damage <= 0:
            damage = 0
            
        combat_skills = Skill.passive_combat
        relevant_skills = []
        
        '''
        for skill in self.user.get_full_skills():
            if skill.get_type() in combat_skills:
                relevant_skills.append(skill)
                
        for skill in target.get_full_skills():
            if skill.get_type() in combat_skills:
                relevant_skills.append(skill)
        '''
        
        for skill in self.user.get_full_skills():
            damage = skill.define_accuracy(damage,self.user,target)
        for skill in target.get_full_skills():
            damage = skill.define_accuracy(damage,self.user,target)
        
        damage = round(damage)
        return damage
    
    
    def calculate_probable_damage(self, target):
        '''
        Calculates the excpected damage output. Considers both accuracy and damage, if it will hit.
        Usable by ai to define who to attack.
        '''
        max_damage = self.calculate_max_damage(target)
        accuracy = self.calculate_accuracy(target)
        expected_damage = max_damage * (accuracy / 100)
        return expected_damage

    def get_range(self):
        return (self.min_range,self.max_range)
    
    def get_flavor(self):
        return self.flavor
    
    def get_type(self):
        return self.type
    
    def get_accuracy(self):
        return self.accuracy
    
    def get_power(self):
        return self.power
    
    def get_name(self):
        return self.name
    
    def get_action_type(self):
        return self.action_type
    
    def targets_enemy(self):
        return self.target_enemy



class Melee(Attack):
    '''
    An attack whose damage depends on user's attack and defender's defense stats.
    '''
    def __init__(self,data):
        Attack.__init__(self, data)
        self.attack_type = Stats.ATTACK
        self.defense_type = Stats.DEFENSE
        

class Magic(Attack):
    '''
    An attack whose damage depends on user's magic and defender's resistance stats.
    '''
    def __init__(self,data):
        Attack.__init__(self, data)
        self.attack_type = Stats.MAGIC
        self.defense_type = Stats.RESISTANCE


# Melee attacks

class Swordstrike(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 1
        self.power          = 1
        self.accuracy       = 100
        self.name           = 'Swordstrike'
        self.flavor         = 'Attack with your sword. Physical attack.'
        self.type           = AttackType.SWORDSTRIKE
        self.attack_type    = Stats.ATTACK
        self.defense_type   = Stats.DEFENSE

class Axe(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 1
        self.power          = 1.5
        self.accuracy       = 75
        self.name           = 'Axe'
        self.flavor         = 'Attack with your axe. Strong but can miss.'
        self.type           = AttackType.AXE
        self.attack_type    = Stats.ATTACK
        self.defense_type   = Stats.DEFENSE

class Knife(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 1
        self.power          = 1
        self.accuracy       = 100
        self.name           = 'Knife'
        self.flavor         = 'Attack an enemy with a quick slash from your knife.'
        self.type           = AttackType.KNIFE
        self.attack_type    = Stats.ATTACK
        self.defense_type   = Stats.DEFENSE

class Dagger(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 1
        self.power          = 1.3
        self.accuracy       = 100
        self.name           = 'Dagger'
        self.flavor         = 'Attack an enemy with your dagger.'
        self.type           = AttackType.DAGGER
        self.attack_type    = Stats.ATTACK
        self.defense_type   = Stats.DEFENSE

class Lance(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 1
        self.power          = 1.2
        self.accuracy       = 100
        self.name           = 'Lance'
        self.flavor         = 'Hit an enemy with your lance.'
        self.type           = AttackType.LANCE
        self.attack_type    = Stats.ATTACK
        self.defense_type   = Stats.DEFENSE


# Ranged attacks
        
class Bow(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 2
        self.power          = 1.5
        self.accuracy       = 100
        self.name           = 'Bow'
        self.flavor         = 'Shoot with your bow. Range: 2.'
        self.type           = AttackType.BOW
        self.attack_type    = Stats.ATTACK
        self.defense_type   = Stats.DEFENSE

class Longbow(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 3
        self.power          = 1
        self.accuracy       = 80
        self.name           = 'Longbow'
        self.flavor         = 'Weaker and worse accuracy than the bow, but better range. Range: 3.'
        self.type           = AttackType.LONGBOW
        self.attack_type    = Stats.ATTACK
        self.defense_type   = Stats.DEFENSE

class Snipe(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 4
        self.power          = 1
        self.accuracy       = 50
        self.name           = 'Snipe'
        self.flavor         = 'Snipe from afar with low accuracy. Range: 4.'
        self.type           = AttackType.SNIPE
        self.attack_type    = Stats.ATTACK
        self.defense_type   = Stats.DEFENSE

class Javelin(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 2
        self.power          = 0.5
        self.accuracy       = 100
        self.name           = 'Javelin'
        self.flavor         = 'Throw your javelin from afar. Physical attack.'
        self.type           = AttackType.JAVELIN
        self.attack_type    = Stats.ATTACK
        self.defense_type   = Stats.DEFENSE

class ThrowingKnife(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 2
        self.power          = 0.8
        self.accuracy       = 95
        self.name           = 'Throwing knife'
        self.flavor         = 'Throw an enemy with your dagger.'
        self.type           = AttackType.THROWINGKNF
        self.attack_type    = Stats.ATTACK
        self.defense_type   = Stats.DEFENSE


# Magic attacks
        
class Fire(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 2
        self.power          = 1.5
        self.accuracy       = 95
        self.name           = 'Fire'
        self.flavor         = 'Cast a somewhat powerful fire. Range: 2.'
        self.type           = AttackType.FIRE
        self.attack_type    = Stats.MAGIC
        self.defense_type   = Stats.RESISTANCE

class Thunder(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 4
        self.power          = 0.5
        self.accuracy       = 90
        self.name           = 'Thunder'
        self.flavor         = 'Cast a weak thunder. Range: 4.'
        self.type           = AttackType.THUNDER
        self.attack_type    = Stats.MAGIC
        self.defense_type   = Stats.RESISTANCE

class Wind(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 2
        self.power          = 0.4
        self.accuracy       = 100
        self.name           = 'Wind'
        self.flavor         = 'Cast a somewhat weak wind to attack. Range: 2.'
        self.type           = AttackType.WIND
        self.attack_type    = Stats.MAGIC
        self.defense_type   = Stats.RESISTANCE

class Stormwind(Attack):
    def __init__(self,user):
        Attack.__init__(self, user)
        self.min_range      = 1
        self.max_range      = 2
        self.power          = 1.3
        self.accuracy       = 90
        self.name           = 'Stormwind'
        self.flavor         = 'Cast a somewhat powerful wind magic. Range: 2'
        self.type           = AttackType.STORMWIND
        self.attack_type    = Stats.MAGIC
        self.defense_type   = Stats.RESISTANCE
