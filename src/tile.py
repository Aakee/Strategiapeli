'''
Classes represent the environment where characters ale moving. Each of them has
different properties.
'''

from game_errors import IllegalMoveException
from skill import Skill
from game_enums import Stats
from PyQt5.QtGui import QColor
from game_enums import Terrain, SkillType


class Tile:
    '''
    Basic class for all tiles.
    '''
    
    def __init__(self,game):
        self.game = game
        self.object = None      # Initially holds no object
        self.passable = True    # List of skills char has to have to pass; True if always passable, False if never passable
        self.endable = True     # List of skills char has to have to end on this tile; True if endable regardless of skills, False if never endable
        self.steps_taken = 1    # Basic amount steps needed to pass; can be altered by char skills
        self.terrain = None
        self.combat = {Stats.ATTACK: 0, Stats.DEFENSE: 0, Stats.MAGIC: 0, Stats.RESISTANCE: 0, Stats.SPEED: 0, Stats.EVASION: 0}
        self.set_combat()
        self.color = QColor(255,255,255) # Color for this type of tile; used by GUI
        self.color2 = QColor(170,170,255)
        self.color_attack = QColor(254,72,52) # Color to indicate that a character can attack to this tile
        self.color_skill = QColor(135,241,95)
        self.gui_tile = None    # Makes a connection between this tile and its counterpart in gui
     
    def get_object(self):
        return self.object
    
    def get_terrain(self):
        return self.terrain
    
    def get_color(self):
        return self.color
    
    def get_color2(self):
        return self.color2
    
    def get_color_attack(self):
        return self.color_attack
    
    def get_color_skill(self):
        return self.color_skill
    
    def set_object(self, object):
        if self.object != None:
            raise IllegalMoveException("Tile is already occupied!")
        self.object = object
        
    def remove_object(self):
        self.object = None
        
    def set_combat(self):
        '''
        Tells how much terrain affects when in combat.
        Implemented in subclasses.
        '''
        pass
    
    def get_combat_bonuses(self):
        return self.combat
    
    def is_endable(self,char):
        '''
        Defines if char can land on this tile.
        @param char: Character object trying to land on tile
        @return: True if can land, False if can't
        '''
        if self.endable == True:    # If anyone can end on tile
            return True
        if self.endable == False:   # If no one can land on tile
            return False
        skills = char.get_skills()
        for skill in skills:
            if skill in self.endable: # If atleast one skill allows user to land
                return True
        return False                # If no skills allow char to end on tile
    
    def get_endable(self):
        return self.endable
    
    def pass_by(self,char,steps):
        '''
        Defines if a character can pass through this tile and/or end on this tile.
        Assistant method of Board.pass_by_square().
        @param char: Which character we are moving
        @param steps: How many steps char can still take. Used to define return value steps_left
        @return: Tuple result: (add, steps_left). Add tells if the character can actually end on this tile, 
        steps_left tells how many steps the character can take after this tile.
        If character can't actually get on this tile (Wall, for example), return value is always (False, 0).
        If character can pass by this tile but can not end on it, return value is (False, steps_left).
        '''
        add = False
        steps_left = 0
        skills = char.get_skills()
        
        
        # Defines if the character can actually be on this tile
        if self.passable != True:
            if self.passable == False:
                return(add, steps_left)
            can_pass = False
            skills_passable = self.passable
            for skill in skills:
                if skill in skills_passable:
                    can_pass = True
            if not can_pass:
                return (add, steps_left)
        
        
        # Tile is empty
        if self.object == None:
            if self.endable == True:
                add = True
            elif self.endable == False:
                add = False
            else:
                for skill in skills:
                    if skill in self.endable:
                        add = True
            steps_left = self.define_steps_left(char, steps)
            return (add, steps_left)
        
        # Tile has an ally on it
        elif not self.object.is_enemy(char) and steps - self.steps_taken > 0:
            steps_left = self.define_steps_left(char, steps)
            return (add, steps_left)
        
        # Tile has an enemy on it
        elif steps - self.steps_taken > 0:
            for skill in skills:
                if skill in Skill.can_pass_enemies:
                    steps_left = self.define_steps_left(char, steps)
                    return (add, steps_left)
                
        return (add, steps_left)
        
    def define_steps_left(self,char,steps):
        '''
        Defines how many steps a character has to take to pass this tile.
        Implemented in subclasses.
        Method assumes that character can actually pass through this tile
        - if not, method pass_by will correct this.
        '''
        pass
 
 
 
    
    
class Plain(Tile):
    
    '''
    The most basic type of a tile.
    Every character can pass this tile with one step.
    Every character can end on this tile.
    '''
            
    def __init__(self,game):
        Tile.__init__(self,game)
        self.object = None
        self.passable = True
        self.endable = True
        self.steps_taken = 1
        self.terrain = Terrain.PLAIN
        self.color = QColor(243,243,215)
    
    def define_steps_left(self,char,steps):
        return steps - self.steps_taken     # 1 for every character class; always passable
    
    def set_combat(self):
        return    # Doesn't affect combat
    
    
class Sand(Tile):
    '''
    Tile halts the movement of characters by 1.
    Also reduces speed in combat.
    '''
    
    def __init__(self,game):
        Tile.__init__(self,game)
        self.object = None
        self.passable = True
        self.endable = True
        self.steps_taken = 2
        self.terrain = Terrain.SAND
        self.color = QColor(255,237,135)
        self.color2 = QColor(129,179,254)
        
    def define_steps_left(self,char,steps):
        '''
        While Sand-type tile halts movement, this can be neglected by characters, who have at least one of their
        skills included in list not_affected.
        '''
        steps_taken = self.steps_taken
        not_affected = [SkillType.LEVITATE] # List of skills which give immunity to movement halting
        skills = char.get_skills()
        for skill in skills:
            if skill in not_affected:
                steps_taken = 1
        return steps - steps_taken
    
    def set_combat(self):
        self.combat[Stats.SPEED] -= 5
    


class Wall(Tile):
    '''
    Unpassable for normal characters.
    '''
    
    def __init__(self,game):
        Tile.__init__(self,game)
        self.object = None
        self.passable = [SkillType.GHOST]
        self.endable = False
        self.steps_taken = 1
        self.terrain = Terrain.WALL
        self.color = QColor(0,0,0)
        
    def define_steps_left(self,char,steps):
        '''
        Wall-type tiles are normally impossible to pass and always
        impossible to land on. It only takes one step to go through for
        those who can go past it, though.
        '''
        return steps - self.steps_taken
    
    def set_combat(self):
        pass
    

class Forest(Tile):
    '''
    Tile halts characters by 0.5.
    Additionally reduces speed in combat for those without certain skills.
    '''
    def __init__(self,game):
        Tile.__init__(self,game)
        self.object = None
        self.passable = True
        self.endable = True
        self.steps_taken = 1.5
        self.terrain = Terrain.FOREST
        self.color = QColor(17,197,8)
        self.color2 = QColor(6,198,155)
        
    def define_steps_left(self,char,steps):
        steps_taken = self.steps_taken
        not_affected = [] # List of skills which give immunity to movement halting
        skills = char.get_skills()
        for skill in skills:
            if skill in not_affected:
                steps_taken = 1
        
        return steps - steps_taken
    
    def set_combat(self):
        self.combat[Stats.SPEED] -= 2
    

class Mountain(Tile):
    '''
    Doesn't affect normal characters.
    Halts movement for characters with horses. 
    '''
    
    def __init__(self,game):
        Tile.__init__(self,game)
        self.object = None
        self.passable = True
        self.endable = True
        self.steps_taken = 1
        self.terrain = Terrain.MOUNTAIN
        self.color = QColor(172,172,172)
        self.color2 = QColor(174,155,234)
        
    def define_steps_left(self,char,steps):
        steps_taken = self.steps_taken
        affected = [] # List of skills which give handicap to terrain
        skills = char.get_skills()
        for skill in skills:
            if skill in affected:
                steps_taken = 2
        
        return steps - steps_taken
    
    def set_combat(self):
        pass
    

class Water(Tile):
    '''
    Normally unpassable, but some characters can fly over.
    '''
    def __init__(self,game):
        Tile.__init__(self,game)
        self.object = None
        self.passable = [SkillType.LEVITATE]
        self.endable = [SkillType.LEVITATE]
        self.steps_taken = 1
        self.terrain = Terrain.WATER
        self.color = QColor(0,13,255)
        self.color2 = QColor(152,3,252)
        
    def define_steps_left(self,char,steps):
        '''
        Takes 1 step for those who can pass it.
        '''
        return steps - self.steps_taken
    
    def set_combat(self):
        pass
    
    
class Snow(Tile):
    '''
    Identical to Forest except for the colour.
    '''
    def __init__(self,game):
        Tile.__init__(self,game)
        self.object = None
        self.passable = True
        self.endable = True
        self.steps_taken = 1.5
        self.terrain = Terrain.SNOW
        self.color = QColor(249,249,249)
        self.color2 = QColor(239,209,239)
        
    def define_steps_left(self,char,steps):
        steps_taken = self.steps_taken
        not_affected = [] # List of skills which give immunity to movement halting
        skills = char.get_skills()
        for skill in skills:
            if skill in not_affected:
                steps_taken = 1
        
        return steps - steps_taken
    
    def set_combat(self):
        self.combat[Stats.SPEED] -= 2
        
        

class Wood(Tile):
    
    '''
    Identical to Plain except for the colour.
    '''
            
    def __init__(self,game):
        Tile.__init__(self,game)
        self.object = None
        self.passable = True
        self.endable = True
        self.steps_taken = 1
        self.terrain = Terrain.WOOD
        self.color = QColor(120,74,50)
        self.color2 = QColor(207,105,167)
    
    def define_steps_left(self,char,steps):
        return steps - self.steps_taken     # 1 for every character class; always passable
    
    def set_combat(self):
        return    # Doesn't affect combat
    
    

class Goal(Tile):
    '''
    Objective of the map.
    '''
    def __init__(self,game):
        Tile.__init__(self,game)
        self.object = None
        self.passable = True
        self.endable = True
        self.steps_taken = 1
        self.terrain = Terrain.GOAL
        self.color = QColor(255,210,74)
        self.color2 = QColor(152,3,252)
        
        
    def define_steps_left(self,char,steps):
        '''
        Takes 1 step for everyone.
        '''
        return steps - self.steps_taken
    
    def set_combat(self):
        self.combat[Stats.DEFENSE] -= 3
        self.combat[Stats.RESISTANCE] -= 3
        self.combat[Stats.EVASION] -= 10