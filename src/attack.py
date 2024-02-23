import random
from game_enums import Stats
from skill import Skill

class Attack:
    '''
    An assistant class used by characters to store info of their attacks and to determine their damage output.
    '''
    
    def __init__(self,data):
        '''
        @param data: Basic data of the attack in format (user, range, power, accuracy, name, flavor).
        '''
        self.user = data[0]         # User of the attack
        self.min_range = data[1][0] # Minumum range of the attack
        self.max_range = data[1][1] # Maximum range of the attack
        self.power = data[2]        # Basic power of the attack
        self.accuracy = data[3]     # Accuracy in percents
        self.name = data[4]         # Name of the attack
        self.flavor = data[5]       # String that tells basic info of attack
        self.type = None            # Tells the type of attack
        self.target_enemy = True    # True if targets enemies, False if allies (Always True for attacks)
        self.attack_type = None
        self.defense_type = None
        self.action_type = "a"      # For attack
        
    def calculate_damage(self, target):
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
        
        combat_skills = Skill.passive_combat
        relevant_skills = []
        
        for skill in self.user.get_full_skills():
            if skill.get_type() in combat_skills:
                relevant_skills.append(skill)
                
        for skill in target.get_full_skills():
            if skill.get_type() in combat_skills:
                relevant_skills.append(skill)
                
        
        for skill in relevant_skills:
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
        
        for skill in self.user.get_full_skills():
            if skill.get_type() in combat_skills:
                relevant_skills.append(skill)
                
        for skill in target.get_full_skills():
            if skill.get_type() in combat_skills:
                relevant_skills.append(skill)
                
        
        for skill in relevant_skills:
            damage = skill.define_damage(damage,self.user,target)
        
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
        

class Heal(Attack):
    '''
    Action heals character etc
    '''
    pass