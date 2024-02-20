from stats import Stats
from game_errors import IllegalMoveException
from confirmwindow import ConfirmSkill
import character

'''
An assistant class which stores all skills there are in the game.
'''


class Skill:
    
    '''
    Skills which affect moving.
    '''
    
    LEVITATE = 1    # Character can levitate for instance over gaps
    GHOST = 2       # Character can pass walls and enemy players (but not land on them)
    SNEAK = 3       # Character can pass enemy players
    
    
    
    '''
    Skills which affect in combat.
    '''
    
    CAMOUFLAGE = 11
    BODYGUARD = 12
    MIRACLE = 13
    SNIPER = 14
    
    
    '''
    Passive skills which affect outside of combat
    '''
    
    REST = 21       # Character gains HP at the start of each turn.
    
    
    
    '''
    Active skills which affect outside of combat (must be activated)
    '''
    
    HEAL = 31       # Character can heal other characters (and themselves).
    RAISEDEF = 33   # Character raises defensive stats for nearby allies until start of next turn
    RAISERNG = 34   # Character raises range for nearby allies until start of next turn
    WISH = 39       # Another character can move second time
    
    
    
    '''
    Lists of different types of skills.
    (Not generally necessary, but makes other methods in the game cleaner)
    If other methods would like to check if a character can pass an enemy player, for example, tehy compare
    the skillset of the character and list can_pass_enemies: if they have at least one common skill, character can pass
    '''
    
    # Skills with which characters can pass enemy players
    can_pass_enemies = [GHOST, SNEAK]
    
    # Skills which can be activated the same way as attacks
    active_skills = [HEAL, RAISEDEF, RAISERNG, FREE, CAPTURE, TRANSFER, EXECUTE, WISH]
    
    # Passive skills which affect in combat
    passive_combat = [CAMOUFLAGE, BODYGUARD, MIRACLE, SNIPER]
    
    # Passive skills which activates at the beginning of each turn
    passive_beginning = [REST]
    
    
    def __init__(self,char):
        self.name = ""
        self.flavor = ""
        self.type = 0
        self.affect_all = False # Determines if skill affects all characters in range (True) or only one (False)
        self.target = True # False if doesn't need a target, True if it does
        self.target_enemy = False # True if targets only enemies, False if allies
        self.char = char
        self.range = None
        
    def get_name(self):
        return self.name
    
    def get_flavor(self):
        return self.flavor
    
    def get_type(self):
        return self.type
    
    def get_action_type(self):
        return "s"
    
    def get_range(self):
        return self.range
    
    def affects_all(self):
        return self.affect_all
    
    def targets(self):
        return self.target
    
    def targets_enemy(self):
        return self.target_enemy
    
    def get_value(self):    # For ai to determine how clever it is to use skill
        return 0
        
        
#from action import ConfirmSkill        

class Ghost(Skill):
    '''
    Skill makes it possible to pass through enemy players and solid objects.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Ghost"
        self.flavor = "Character can pass through enemies and solid objects"
        self.type = Skill.GHOST
        

class Sneak(Skill):
    '''
    Skill makes it possible to pass enemy players.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Sneak"
        self.flavor = "Character can pass enemy players."
        self.type = Skill.SNEAK
        self.affect_all = False
        self.target = True
        self.range = None


class Levitate(Skill):
    '''
    Skill makes it possible to go over gaps. Also is unaffected by certain tiles.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Levitate"
        self.flavor = "Character can fly over gaps and certain terrains unaffected."
        self.type = Skill.LEVITATE


class Heal(Skill):
    '''
    Heals another character.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Heal"
        self.flavor = "Heals another character. Pwr: Mag/2"
        self.type = Skill.HEAL
        self.range = 3
        self.affect_all = False
        self.target = True
        self.target_enemy = False
        
    def use(self,coordinates):
        stats = self.char.get_stats()
        mag = stats[Stats.MAGIC]
        heal = round(mag/2)
        squares = self.char.define_attack_targets(self.char.get_square(), self.range, False)

        if coordinates not in squares and self.char.get_owner() == self.char.get_game().get_human():
            raise IllegalMoveException("Cannot use skill on chosen tile!")
        
        elif coordinates not in squares: # Because character defined it would be a good idea before moving :P
            target = self.char
            
        else:
            target = self.char.get_game().get_board().get_piece(coordinates)
            
        hp = target.get_hp()
        maxhp = target.get_maxhp()
        if hp + heal > maxhp:
            heal = maxhp - hp
        if self.char.get_owner() == self.char.get_game().get_human():
            string = "Heal amount: " + str(heal)
            wnd = ConfirmSkill(self.char,self,string)
            if not wnd.exec_():
                return
        
        
        print("{} kaytti kykya Heal hahmoon {}!".format(self.char.get_name(),target.get_name()))    
        target.add_hp(heal)
        self.char.set_ready()
        
        
    
    def get_value(self,coordinates):
        target = self.char.get_game().get_board().get_piece(coordinates)
        stats = self.char.get_stats()
        mag = stats[Stats.MAGIC]        
        hp = target.get_hp()
        maxhp = target.get_maxhp()
        heal = round(mag/2)
        
        value = round((1-hp/maxhp) * heal * 20)
        return value
    
    
class RaiseDef(Skill):
    '''
    Raises defense by 4 and resistance by 3 for nearby allies.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Raise defense"
        self.flavor = "Raises defense by 4 and resistance by 3 for all allies in range 3 until end of turn."
        self.type = Skill.RAISEDEF
        self.range = 3
        self.affect_all = True
        self.target = True
        self.target_enemy = False
        
    def use(self,coordinates):
        stats = {Stats.ATTACK: 0, Stats.DEFENSE: 4, Stats.MAGIC: 0,\
                       Stats.RESISTANCE: 3, Stats.SPEED: 0, Stats.EVASION: 0}
        all_squares = self.char.get_game().get_board().get_tiles_in_range(self.char.get_square(),self.range)

        if coordinates not in all_squares:
            raise IllegalMoveException("Trying to use skill in no range!")
        
        if self.char.get_owner() == self.char.get_game().get_human():
            string = "Raise stats for nearby allies?"
            wnd = ConfirmSkill(self.char,self,string)
            if not wnd.exec_():
                return
        
        for square in all_squares:
            char = self.char.get_game().get_board().get_piece(square)
            if char != None:
                owner = char.get_owner()
                if owner == self.char.get_owner():
                    char.modify_stats(stats,0)
                    
        self.char.set_ready()
        
        print("{} kaytti kykya Raise Defense! Lahella olevien puolulaisten puolustukset nousivat!".format(self.char.get_name()))

                    
    def get_value(self,coordinates):
        all_squares = self.char.get_game().get_board().get_tiles_in_range(self.char.get_square(),self.range)
        chars = []
        
        for square in all_squares:
            char = self.char.get_game().get_board().get_piece(square)
            if char != None:
                owner = char.get_owner()
                if owner == self.char.get_owner:
                    chars.append(char)
        
        value = 0
        for char in chars:
            value += char.calculate_enemy_threat(char.get_square())
            
        value = value * 5
        
        return value
    
    
    
class RaiseRng(Skill):
    '''
    Raises range for nearby allies by 1.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Raise range"
        self.flavor = "Raises range by 1 for allies in range 3 until end of turn."
        self.type = Skill.HEAL
        #self.char = char
        self.range = 3
        self.affect_all = True
        self.target = True
        self.target_enemy = False
        
    def use(self,coordinates):
        stats = {Stats.ATTACK: 0, Stats.DEFENSE: 0, Stats.MAGIC: 0,\
                       Stats.RESISTANCE: 0, Stats.SPEED: 0, Stats.EVASION: 0}
        all_squares = self.char.get_game().get_board().get_tiles_in_range(self.char.get_square(),self.range)

        if coordinates not in all_squares:
            raise IllegalMoveException("Trying to use skill in no range!")
        
        if self.char.get_owner() == self.char.get_game().get_human():
            string = "Raise range for nearby allies?"
            wnd = ConfirmSkill(self.char,self,string)
            if not wnd.exec_():
                return
        
        for square in all_squares:
            char = self.char.get_game().get_board().get_piece(square)
            if char != None:
                owner = char.get_owner()
                if owner == self.char.get_owner():
                    char.modify_stats(stats,1)
                    
        self.char.set_ready()
        
        print("{} kaytti kykya Raise Range! Lahella olevien puolulaisten askeleet kasvoivat yhdella!".format(self.char.get_name()))

                    
    def get_value(self,coordinates):
        
        all_squares = self.char.get_game().get_board().get_tiles_in_range(self.char.get_square(),self.range)
        chars = []

        for square in all_squares:
            char = self.char.get_game().get_board().get_piece(square)
            if char != None:
                owner = char.get_owner()
                if owner == self.char.get_owner():
                    chars.append(char)
                    
        value = -5
        for char in chars:
            if not char.is_ready():
                value += 5
            
        value = value * 2

        return value
    
    
class Camouflage(Skill):
    '''
    Raises evasion against archers.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Camouflage"
        self.flavor = "Raises evasion against archers by 15."
        self.type = Skill.CAMOUFLAGE
        #self.char = char
        self.affect_all = False
        self.target = False
        
    def define_accuracy(self,accuracy,attacking,defending):
        if self.char != defending:
            return accuracy
        
        type = attacking.get_type()
        if type == character.Character.ARCHER:
            accuracy -= 15
            
        return accuracy
    
    def define_damage(self,damage,attacking,defending):
        return damage
        

class Rest(Skill):
    '''
    Heals user at the beginning of each turn.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Rest"
        self.flavor = "Heals the user at the beginning of each turn."
        self.type = Skill.REST
        self.affect_all = False
        self.target = False
        self.gain = 2   # How much is regained each turn
        
    def use(self):
        if self.char.get_hp() < self.char.get_maxhp(): # If hp is not already full
            print("{} kaytti kykya Rest!".format(self.char.get_name()))
            if self.char.get_hp() + self.gain <= self.char.get_maxhp(): # If character can heal whole amount
                self.char.add_hp(self.gain)
            else:   # If character can heal only a part of the self.gain
                self.char.add_hp(self.char.get_maxhp() - self.char.get_hp())
        
        
class Bodyguard(Skill):
    '''
    Makes character stronger against assassins.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Bodyguard"
        self.flavor = "Character has 2x accuracy and 1.5x damage against assassins."
        self.type = Skill.BODYGUARD
        self.affect_all = False
        self.target = False
        
    def define_accuracy(self,accuracy,attacking,defending):
        if self.char != attacking:
            return accuracy
        
        type = defending.get_type()
        if type == character.Character.ASSASSIN:
            accuracy = accuracy * 2
            
        return accuracy
    
    def define_damage(self,damage,attacking,defending):
        if self.char != attacking:
            return damage
        
        type = defending.get_type()
        if type == character.Character.ASSASSIN:
            damage = damage * 1.5
            
        return damage       
        
        
class Miracle(Skill):
    '''
    Character cannot die in a single hit
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Miracle"
        self.flavor = "If character would die in one hit when on full HP, it survives it instead with 1 hp left."
        self.type = Skill.MIRACLE
        self.affect_all = False
        self.target = False
        
    def define_accuracy(self,accuracy,attacking,defending):
        return accuracy
    
    def define_damage(self,damage,attacking,defending):
       
        if self.char != defending:
            return damage
        
        if self.char.get_hp() == self.char.get_maxhp():
            if damage >= self.char.get_hp():
                return self.char.get_hp() - 1
            
        return damage
    

class Sniper(Skill):
    '''
    Character makes double damage to Valkyries.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Sniper"
        self.flavor = "Character deals 2.5 times damage against Valkyries."
        self.type = Skill.SNIPER
        #self.char = char
        self.affect_all = False
        self.target = False
        
    def define_accuracy(self,accuracy,attacking,defending):
        return accuracy
    
    def define_damage(self,damage,attacking,defending):
        if defending.get_type() == character.Character.VALKYRIE:
            return damage * 2.5
        return damage
    

class Wish(Skill):
    '''
    Character makes it able to another character to move second time during the turn.
    Also raises little its stats.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Wish"
        self.flavor = "Character enables another character to move second time with enhanced stats.\n  Cannot be used on another characters with Wish."
        self.type = Skill.WISH
        self.affect_all = False
        self.target = True
        self.range = 2
        
    def use(self,coordinates):
        stats = {Stats.ATTACK: 1, Stats.DEFENSE: 1, Stats.MAGIC: 1,\
                       Stats.RESISTANCE: 1, Stats.SPEED: 0, Stats.EVASION: 0}
        range = 0
        
        target = self.char.get_game().get_board().get_piece(coordinates)
        squares = self.char.define_attack_targets(self.char.get_square(), self.range, self.target_enemy)
        
        if target == None:
            raise IllegalMoveException("Cannot use skill on empty tile!")
        if coordinates not in squares:
            raise IllegalMoveException("Cannot use skill on chosen tile!")
        if target.get_owner() != self.char.get_owner():
            raise IllegalMoveException("Cannot use skill on chosen character!")
        if not target.is_ready():
            raise IllegalMoveException("Cannot use skill on chosen character!")
        skills = target.get_skills()
        if Skill.WISH in skills:
            raise IllegalMoveException("Cannot use skill on chosen character!")       
        
        if self.char.get_owner() == self.char.get_game().get_human():
            string = "Use Wish?"
            wnd = ConfirmSkill(self.char,self,string)
            if not wnd.exec_():
                return 
        
        target.set_not_ready()
        target.modify_stats(stats,range)
        self.char.set_ready()
        
        print("{} used Wish on {}!".format(self.char.get_name(), target.get_name()))
        
    def get_value(self,coordinates):
        target = self.char.get_game().get_board().get_piece(coordinates)
        if target == None:
            return 0
        if target.get_owner() != self.char.get_owner():
            return 0
        if not target.is_ready():
            return 0
        skills = target.get_skills()
        if Skill.WISH in skills:
            return 0
        '''
        line = target.calculate_best_move()
        value = line[3]
        return value
        '''
        return 1000