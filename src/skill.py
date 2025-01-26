from game_enums import Stats
from game_errors import IllegalMoveException
from confirmwindow import ConfirmSkill
from game_enums import CharacterClass, SkillType

'''
An assistant class which stores all skills there are in the game.
'''


class Skill:
    
    '''
    Lists of different types of skills.
    (Not generally necessary, but makes other methods in the game cleaner)
    If other methods would like to check if a character can pass an enemy player, for example, tehy compare
    the skillset of the character and list can_pass_enemies: if they have at least one common skill, character can pass
    '''
    
    # Skills with which characters can pass enemy players
    can_pass_enemies = [SkillType.GHOST, SkillType.SNEAK]

    # Skills that affect movement in some way
    movement_skills  = [SkillType.LEVITATE, SkillType.GHOST]
    
    # Skills which can be activated the same way as attacks
    active_skills = [SkillType.HEAL, SkillType.RAISEDEF, SkillType.RAISERNG, SkillType.WISH]
    
    # Passive skills which affect in combat
    passive_combat = [SkillType.CAMOUFLAGE, SkillType.BODYGUARD, SkillType.MIRACLE, SkillType.SNIPER]
    
    # Passive skills which activates at the beginning of each turn
    passive_beginning = [SkillType.REST]

    positive_statuses = []
    negative_statuses = []
    
    
    def __init__(self,char):
        self.name = ""
        self.flavor = ""
        self.type = 0
        self.affect_all = False     # Determines if skill affects all characters in range (True) or only one (False)
        self.target = True          # False if doesn't need a target, True if it does
        self.target_enemy = False   # True if targets only enemies, False if allies
        self.positive = True        # True if positive for the user/holder, False if harmful
        self.char = char
        self.range = None
        self.max_uses = 0           # Zero: No limits. Over zero: How many turns does this skill (status) carry over. Under zero: How many individual uses does this skill (status) have.  
        self.use_count = 0
        self.has_ended = False

    def get_name(self):
        return self.name
    
    def get_flavor(self):
        return self.flavor
    
    def get_type(self):
        return self.type
    
    def get_action_type(self):
        return "s"
    
    def get_value(self):
        return 0
    
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
    
    def use(self,**kwargs):
        return
    
    def increase_use_count(self,delta):
        if self.max_uses == 0:
            return
        self.use_count += delta
        if self.use_count >= abs(self.max_uses):
            self.has_ended = True
    
    def new_turn(self):
        return
    
    def get_stats(self, stats):
        return
    
    def define_accuracy(self,accuracy,attacking,defending):
        return accuracy
    
    def define_damage(self,damage,attacking,defending):
        return damage
        
        
#from action import ConfirmSkill        

class Ghost(Skill):
    '''
    Skill makes it possible to pass through enemy players and solid objects.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Ghost"
        self.flavor = "Character can pass through enemies and solid objects"
        self.type = SkillType.GHOST
        

class Sneak(Skill):
    '''
    Skill makes it possible to pass enemy players.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Sneak"
        self.flavor = "Character can pass enemy players."
        self.type = SkillType.SNEAK
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
        self.type = SkillType.LEVITATE


class Heal(Skill):
    '''
    Heals another character.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Heal"
        self.flavor = "Heals another character. Pwr: Mag/2"
        self.type = SkillType.HEAL
        self.range = 3
        self.affect_all = False
        self.target = True
        self.target_enemy = False
        
    def use(self,coordinates, verbose=True):
        stats = self.char.get_stats()
        mag = stats[Stats.MAGIC]
        heal = round(mag/2)
        squares = self.char.define_attack_targets(self.char.get_square(), self.range, False)

        if coordinates not in squares and not self.char.get_owner().is_ai():
            raise IllegalMoveException("Cannot use skill on chosen tile!")
        
        elif coordinates not in squares: # Because character defined it would be a good idea before moving :P
            target = self.char
            
        else:
            target = self.char.get_game().get_board().get_piece(coordinates)
            
        hp = target.get_hp()
        maxhp = target.get_maxhp()
        if hp + heal > maxhp:
            heal = maxhp - hp
        if not self.char.get_owner().is_ai():
            string = "Heal amount: " + str(heal)
            wnd = ConfirmSkill(self.char,self,string)
            if not wnd.exec_():
                return
        
        if verbose:
            print("{} kaytti kykya Heal hahmoon {}!".format(self.char.get_name(),target.get_name()))    
        target.add_hp(heal, verbose=verbose)
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
        self.flavor = "Gives Fortify to nearby allies."
        self.type = SkillType.RAISEDEF
        self.range = 3
        self.affect_all = True
        self.target = True
        self.target_enemy = False
        
    def use(self,coordinates, verbose=True):
        stats = {Stats.ATTACK: 0, Stats.DEFENSE: 4, Stats.MAGIC: 0,\
                       Stats.RESISTANCE: 3, Stats.SPEED: 0, Stats.EVASION: 0}
        all_squares = self.char.get_game().get_board().get_tiles_in_range(self.char.get_square(),self.range)

        if coordinates not in all_squares:
            raise IllegalMoveException("Trying to use skill in no range!")
        
        if not self.char.get_owner().is_ai():
            string = "Raise stats for nearby allies?"
            wnd = ConfirmSkill(self.char,self,string)
            if not wnd.exec_():
                return
        
        for square in all_squares:
            char = self.char.get_game().get_board().get_piece(square)
            if char != None:
                owner = char.get_owner()
                if owner == self.char.get_owner():
                    char.add_skill(Fortify(char))
                    
        self.char.set_ready()
        if verbose:
            print("{} kaytti kykya Raise Defense! Lahella olevien puolulaisten puolustukset nousivat!".format(self.char.get_name()))
    
    
class RaiseRng(Skill):
    '''
    Raises range for nearby allies by 1.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Raise range"
        self.flavor = "Gives Swift to nearby allies."
        self.type = SkillType.RAISERNG
        #self.char = char
        self.range = 3
        self.affect_all = True
        self.target = True
        self.target_enemy = False
        
    def use(self,coordinates, verbose=True):
        all_squares = self.char.get_game().get_board().get_tiles_in_range(self.char.get_square(),self.range)

        if coordinates not in all_squares:
            raise IllegalMoveException("Trying to use skill in no range!")
        
        if not self.char.get_owner().is_ai():
            string = "Raise range for nearby allies?"
            wnd = ConfirmSkill(self.char,self,string)
            if not wnd.exec_():
                return
        
        for square in all_squares:
            char = self.char.get_game().get_board().get_piece(square)
            if char != None:
                owner = char.get_owner()
                if owner == self.char.get_owner():
                    char.add_skill(Swift(char))
                    
        self.char.set_ready()
        if verbose:
            print("{} kaytti kykya Raise Range! Lahella olevien puolulaisten askeleet kasvoivat yhdella!".format(self.char.get_name()))

                    
class Camouflage(Skill):
    '''
    Raises evasion against archers.
    '''
    def __init__(self,char):
        super().__init__(char)
        self.name = "Camouflage"
        self.flavor = "Raises evasion against archers by 15."
        self.type = SkillType.CAMOUFLAGE
        #self.char = char
        self.affect_all = False
        self.target = False
        
    def define_accuracy(self,accuracy,attacking,defending):
        if self.char != defending:
            return accuracy
        
        type = attacking.get_type()
        if type == CharacterClass.ARCHER:
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
        self.type = SkillType.REST
        self.affect_all = False
        self.target = False
        self.gain = 2   # How much is regained each turn
        
    def new_turn(self, verbose=True):
        if self.char.get_hp() < self.char.get_maxhp(): # If hp is not already full
            if verbose:
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
        self.type = SkillType.BODYGUARD
        self.affect_all = False
        self.target = False
        
    def define_accuracy(self,accuracy,attacking,defending):
        if self.char != attacking:
            return accuracy
        
        type = defending.get_type()
        if type == CharacterClass.ASSASSIN:
            accuracy = accuracy * 2
            
        return accuracy
    
    def define_damage(self,damage,attacking,defending):
        if self.char != attacking:
            return damage
        
        type = defending.get_type()
        if type == CharacterClass.ASSASSIN:
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
        self.type = SkillType.MIRACLE
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
        self.type = SkillType.SNIPER
        self.affect_all = False
        self.target = False
        
    def define_accuracy(self,accuracy,attacking,defending):
        return accuracy
    
    def define_damage(self,damage,attacking,defending):
        if defending.get_type() == CharacterClass.VALKYRIE:
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
        self.type = SkillType.WISH
        self.affect_all = False
        self.target = True
        self.range = 2
        
    def use(self,coordinates, verbose=True):
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
        if SkillType.WISH in skills:
            raise IllegalMoveException("Cannot use skill on chosen character!")       
        
        if not self.char.get_owner().is_ai():
            string = "Use Wish?"
            wnd = ConfirmSkill(self.char,self,string)
            if not wnd.exec_():
                return 
        
        target.set_not_ready()
        target.modify_stats(stats,range)
        self.char.set_ready()
        if verbose:
            print("{} used Wish on {}!".format(self.char.get_name(), target.get_name()))
        

class Fortify(Skill):
    '''
    Enhances character's defensive stats.
    '''
    def __init__(self, char) -> None:
        super().__init__(char)
        self.name = "Fortify"
        self.flavor = "Enhances defense and resistance."
        self.type = SkillType.FORTIFY
        self.max_uses = 1

    def new_turn(self):
        self.increase_use_count(1)

    def get_stats(self, orig_stats):
        orig_stats[Stats.DEFENSE] += 3
        orig_stats[Stats.RESISTANCE] += 3


class Swift(Skill):
    '''
    Enhances character's movement range.
    '''
    def __init__(self, char) -> None:
        super().__init__(char)
        self.name = "Swift"
        self.flavor = "Enhances movement range."
        self.type = SkillType.SWIFT
        self.max_uses = 1

    def new_turn(self):
        self.increase_use_count(1)

    def get_stats(self, orig_stats):
        orig_stats[Stats.RANGE] += 1
