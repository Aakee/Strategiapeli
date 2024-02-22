'''
Contains data of all character types in the game.
All of the functional methods are defined in Character class.
'''

import pathlib
from character import Character
from stats import Stats
import attack
from skill import *

class TestChar(Character):
    '''
    Basic character type used for testing.
    '''
    def __init__(self, game, owner):
        Character.__init__(self,game, owner)
        self.name = "TestChar"
        self.type = Character.TESTCHAR        
        self.maxhp = 25
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 15
        self.stats[Stats.DEFENSE] = 5
        self.stats[Stats.MAGIC] = 10
        self.stats[Stats.RESISTANCE] = 15
        self.stats[Stats.SPEED] = 15
        self.stats[Stats.EVASION] = 10
        self.init_stats = dict(self.stats)
        self.range = 6
        self.init_range = self.range
        self.skills = [Ghost(self), RaiseDef(self)]
            
        self.attacks.append(attack.Melee((self, (1,1),1, 100,'Swordstrike', 'Attack with your sword. Physical attack.')))
        self.attacks.append(attack.Melee((self, (1,2),0.5, 100,'Javelin', 'Throw your javelin from afar. Physical attack.')))
        # (user, range, power, accuracy, name, flavor)
    def new(self,owner):
        return TestChar(self.game,owner)
        
        
class Knight(Character):
    '''
    An all-around decent physical class.
    '''
    def __init__(self, game, owner):
        Character.__init__(self,game, owner)
        self.name = "Knight"
        self.type = Character.KNIGHT        
        self.maxhp = 25
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 17
        self.stats[Stats.DEFENSE] = 12
        self.stats[Stats.MAGIC] = 5
        self.stats[Stats.RESISTANCE] = 4
        self.stats[Stats.SPEED] = 17
        self.stats[Stats.EVASION] = 0
        self.range = 3
        self.init_stats = dict(self.stats)
        self.init_range = self.range
        self.skills = [RaiseDef(self),Bodyguard(self)]
            
        self.attacks.append(attack.Melee((self, (1,1),1, 100,'Swordstrike', 'Attack with your sword.')))
        self.attacks.append(attack.Melee((self, (1,1),1.5, 75,'Axe', 'Attack with your axe')))
        
        def new(self,owner):
            return TestChar(self.game,owner)
        
        
class Archer(Character):
    '''
    A class which can shoot arrows far away.
    '''
    def __init__(self, game, owner):
        Character.__init__(self,game, owner)
        self.name = "Archer"
        self.type = Character.ARCHER       
        self.maxhp = 20
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 13
        self.stats[Stats.DEFENSE] = 7
        self.stats[Stats.MAGIC] = 5
        self.stats[Stats.RESISTANCE] = 7
        self.stats[Stats.SPEED] = 20
        self.stats[Stats.EVASION] = 5
        self.range = 4
        self.init_stats = dict(self.stats)
        self.init_range = self.range
        self.skills = [Sniper(self)]

        self.attacks.append(attack.Melee((self, (1,2),1.5, 100,'Bow', 'Shoot with your bow. Range: 2.')))
        self.attacks.append(attack.Melee((self, (1,3),1, 80,'Longbow', 'Weaker and worse accuracy than the bow, but better range. Range: 3.')))
        self.attacks.append(attack.Melee((self, (1,4),1, 50,'Snipe', 'Snipe from afar with low accuracy. Range: 4.')))
        
class Mage(Character):
    '''
    A class which attacks with magic.
    '''
    def __init__(self, game, owner):
        Character.__init__(self,game, owner)
        self.name = "Mage"
        self.type = Character.MAGE      
        self.maxhp = 20
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 5
        self.stats[Stats.DEFENSE] = 5
        self.stats[Stats.MAGIC] = 15
        self.stats[Stats.RESISTANCE] = 7
        self.stats[Stats.SPEED] = 20
        self.stats[Stats.EVASION] = 5
        self.range = 3
        self.init_stats = dict(self.stats)
        self.init_range = self.range
        self.skills = [Camouflage(self)]
            
        self.attacks.append(attack.Magic((self, (1,2),1.5, 95,'Fire', 'Cast a somewhat powerful fire. Range: 2.')))
        self.attacks.append(attack.Magic((self, (1,4),0.5, 90,'Thunder', 'Cast a weak thunder. Range: 4.')))


class Cleric(Character):
    '''
    A support class with many useful skills but low defensive stats.
    '''
    def __init__(self, game, owner):
        Character.__init__(self,game, owner)
        self.name = "Cleric"
        self.type = Character.CLERIC      
        self.maxhp = 20
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 5
        self.stats[Stats.DEFENSE] = 2
        self.stats[Stats.MAGIC] = 20
        self.stats[Stats.RESISTANCE] = 3
        self.stats[Stats.SPEED] = 15
        self.stats[Stats.EVASION] = 5
        self.range = 3
        self.init_stats = dict(self.stats)
        self.init_range = self.range
        self.skills = [Heal(self),Camouflage(self),Rest(self),RaiseRng(self)]
            
        self.attacks.append(attack.Magic((self, (1,2),0.4, 100,'Wind', 'Cast a somewhat weak wind to attack. Range: 2.')))
        self.attacks.append(attack.Melee((self, (1,1), 1, 100, 'Knife', 'Attack an enemy with a quick slash from your knife.')))
        
        
class Assassin(Character):
    '''
    An agile class with high evasion and speed.
    '''
    def __init__(self, game, owner):
        Character.__init__(self,game, owner)
        self.name = "Assassin"
        self.type = Character.ASSASSIN      
        self.maxhp = 17
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 15
        self.stats[Stats.DEFENSE] = 10
        self.stats[Stats.MAGIC] = 10
        self.stats[Stats.RESISTANCE] = 7
        self.stats[Stats.SPEED] = 30
        self.stats[Stats.EVASION] = 15
        self.range = 4
        self.init_stats = dict(self.stats)
        self.init_range = self.range
        self.skills = [Camouflage(self), Sneak(self)]
            
        self.attacks.append(attack.Melee((self, (1,1), 1.3, 100, 'Dagger', 'Attack an enemy with your dagger.')))
        self.attacks.append(attack.Melee((self, (1,2), 0.8, 95, 'Throwing knife', 'Throw an enemy with your dagger.')))
        

class Valkyrie(Character):
    '''
    A flying class with high range but with a weakness to arrows.
    '''
    def __init__(self, game, owner):
        Character.__init__(self,game, owner)
        self.name = "Valkyrie"
        self.type = Character.VALKYRIE      
        self.maxhp = 18
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 12
        self.stats[Stats.DEFENSE] = 10
        self.stats[Stats.MAGIC] = 12
        self.stats[Stats.RESISTANCE] = 10
        self.stats[Stats.SPEED] = 15
        self.stats[Stats.EVASION] = 5
        self.range = 5
        self.init_stats = dict(self.stats)
        self.init_range = self.range
        self.skills = [Levitate(self),Rest(self),Wish(self)]
            
        self.attacks.append(attack.Melee((self, (1,1), 1.2, 100, 'Lance', 'Hit an enemy with your lance.')))
        self.attacks.append(attack.Magic((self, (1,2), 1.3, 90, 'Stormwind', 'Cast a somewhat powerful wind magic. Range: 2')))
        
    def get_path(self):
        if self.owner == self.game.get_ai() and self.is_ready():
            return str( pathlib.Path(__file__).parent / 'images' / 'valkyrie_enemy_moven.png' )
        return Character.get_path(self)