'''
Instance of this class is an independent character
'''
from enum import Enum
import configload
from game_enums import Stats
from game_errors import IllegalMoveException
from confirmwindow import ConfirmAttack
import random
import skill
import attack
from game_enums import CharacterClass, PlayerColor

class Character:
    '''
    Basic class for all characters.
    '''
    def __init__(self, game, color):
        self.game = game
        self.board = game.get_board()
        self.color = color
        self.name = "Name"
        self.alive = True
        self.type = None
        self.square = None
        self.status = None
        self.carried = False # Char is being carried by another char
        self.carrying = None # Char is carrying another char
        self.ready = False
        self.maxhp = 0
        self.hp = 0
        self.stats = {Stats.ATTACK: 0, Stats.DEFENSE: 0, Stats.MAGIC: 0,\
                       Stats.RESISTANCE: 0, Stats.SPEED: 0, Stats.EVASION: 0, Stats.RANGE: 0}
        self.attacks = []
        self.skills = []
        self.legal_squares = None
        self.init_square = None
        self.game.get_player(self.color).add_character(self)
        
    def get_initial_stats(self):
        return self.stats
    
    def reset_stats(self):
        '''
        Method resets character's stats to their initial state, for example
        at the beginning of turn.
        '''
        self.stats = dict(self.init_stats)
        #self.stats[Stats.RANGE] = self.init_range
        #self.range = self.init_range
    
    def get_stats(self):
        '''
        Calculates the terrain's effect in the stats.
        '''
        stats = dict(self.stats)
        stat_enhanc = self.board.get_tile(self.get_square()).get_combat_bonuses()
        stats[Stats.ATTACK]     += stat_enhanc[Stats.ATTACK]
        stats[Stats.DEFENSE]    += stat_enhanc[Stats.DEFENSE]
        stats[Stats.MAGIC]      += stat_enhanc[Stats.MAGIC]
        stats[Stats.RESISTANCE] += stat_enhanc[Stats.RESISTANCE]
        stats[Stats.SPEED]      += stat_enhanc[Stats.SPEED]
        stats[Stats.EVASION]    += stat_enhanc[Stats.EVASION]
        for skill in self.skills:
            skill.get_stats(stats)
        return stats
    
    def modify_stats(self,stat_enhanc,range_enhac):
        '''
        Modifies character's stats.
        '''
        self.stats[Stats.ATTACK] += stat_enhanc[Stats.ATTACK]
        self.stats[Stats.DEFENSE] += stat_enhanc[Stats.DEFENSE]
        self.stats[Stats.MAGIC] += stat_enhanc[Stats.MAGIC]
        self.stats[Stats.RESISTANCE] += stat_enhanc[Stats.RESISTANCE]
        self.stats[Stats.SPEED] += stat_enhanc[Stats.SPEED]
        self.stats[Stats.EVASION] += stat_enhanc[Stats.EVASION]
        self.stats[Stats.RANGE] += range_enhac
        #self.range += range_enhac
          
    def get_range(self):
        return self.stats[Stats.RANGE]
    
    def add_skill(self, new_skill):
        # Possible old status with the same id
        old_skills = [old for old in self.skills if old.type == new_skill.type]
        if len(old_skills) > 0:
            old_skill = old_skills[0]
            if old_skill.max_uses - old_skill.use_count > new_skill.max_uses:
                return 
            self.delete_skill(new_skill.type)
        self.skills.append(new_skill)

    def delete_skill(self, skill_type):
        self.skills = [sk for sk in self.skills if sk.type != skill_type]
        
    def has_skill(self, skill_type):
        return len([sk for sk in self.skills if sk.type == skill_type]) > 0
    
    def get_legal_squares(self):
        '''
        Returns list of squares character can move to this turn.
        Initilized to None at the beginning of each turn.
        '''
        if self.init_square == None:
            self.legal_squares = self.board.legal_squares(self)
            self.init_square = self.get_square()
        else:
            self.legal_squares = self.board.legal_squares_from_tile(self,self.init_square)
        return self.legal_squares
    
    def get_type(self):
        return self.type
    
    def get_square(self):
        self.square = self.board.get_square(self)
        return self.square
    
    def get_attacks(self):
        return self.attacks
    
    def get_skills(self):
        '''
        Returns list of types character has.
        '''
        skills = []
        for skill in self.skills:
            skills.append(skill.get_type())
        return skills
    
    def get_full_skills(self):
        '''
        In comparison to above, returns whole self.skills list
        '''
        return self.skills
    
    def get_name(self):
        return self.name
    
    def get_hp(self):
        return self.hp

    def get_maxhp(self):
        return self.maxhp
    
    def add_hp(self, amount, verbose=True):
        amount = max(amount, 0)
        amount = min(amount, self.maxhp-self.hp)
        self.hp += amount
        if verbose:
            print("{} paransi {} hp vahinkoa.".format(self.get_name(),amount))
        if self.hp > self.maxhp:
            self.hp = self.maxhp
            
    def remove_hp(self,amount, verbose=True):
        amount = max(amount, 0)
        amount = min(amount, self.maxhp)
        self.hp -= amount
        if verbose:
            print("{} otti {} hp vahinkoa.".format(self.get_name(),amount))
        if self.hp <= 0:
            self.die(verbose=verbose)
            
    def set_hp(self,hp, verbose=True):
        self.hp = hp
        if self.hp > self.maxhp:
            self.hp = self.maxhp
        if self.hp <= 0:
            self.die(verbose=verbose)
            
    def get_owner(self):
        return self.game.get_player(self.color)
            
    def is_enemy(self,other):
        return self.color != other.color
    
    def is_ready(self):
        return self.ready
    
    def set_ready(self):
        self.ready = True
        
    def set_not_ready(self):
        self.init_square = None
        self.ready = False
        
    def get_game(self):
        return self.game
    
    def set_status(self, status):
        self.status = status
        
    def set_carrying(self,char):
        self.carrying = char
        char.set_carried()
        
    def remove_carrying(self,square):
        if square:
            self.board.set_object(square,self.carrying)
            self.carrying.get_owner().add_character(self.carrying)
        self.carrying.set_not_carried()
        self.carrying = None
        
    def get_carrying(self):
        return self.carrying
    
    def set_carried(self):
        if self.get_square() != None:
            self.board.remove_object(self.get_square())
            try:
                self.get_owner().remove_character(self)
            except ValueError:
                pass
        self.carried = True
        
    def set_not_carried(self):
        self.carried = False
        
    def add_vip(self):
        '''
        Method adds skill Free and possibly Capture to character.
        '''
        self.skills.append(skill.Free(self))
        if self.game.get_capture():
            self.skills.append(skill.Capture(self))
            if self.get_owner() == self.game.get_ai():
                self.skills.append(skill.Execute(self))
        
    def set_transfer(self):
        '''
        Depending on  if the character has already skill Transfer, method either gives or takes it away.
        '''
        has_transfer = False
        trasfer = None
        for skill1 in self.skills:
            if skill1.get_type() == skill.Skill.TRANSFER:
                has_transfer = True
                transfer = skill1
        if has_transfer:
            self.skills.remove(transfer)
        else:
            self.skills.append(skill.Transfer(self))
        
        
    def get_path(self):
        '''
        Method returns path to character's image.
        '''
        filename = self.name.lower()
        if self.carried:
            filename += '_carry_'
        if self.ready:
            filename += '_grey.png'
        elif self.get_owner() == self.game.get_blue_player():
            filename += '_blue.png'
        elif self.get_owner() == self.game.get_red_player():
            filename += '_red.png'
        else:
            raise KeyError("Error with player's controller!")
        return configload.get_image(filename)
    
    def get_default_path(self):
        '''
        Same as get_path, but always returns path to coloured version of the picture (not the grey variant).
        '''
        filename = self.name.lower()
        if self.get_owner() == self.game.get_blue_player():
            filename += '_blue.png'
        elif self.get_owner() == self.game.get_red_player():
            filename += '_red.png'
        else:
            raise KeyError("Error with player's controller!")
        return configload.get_image(filename)
    
    def get_attack_by_id(self, attack_id):
        ret = None
        for att in self.attacks:
            if att.type == attack_id:
                ret = att
                break
        if ret is None:
            raise ValueError
        return ret
    
    def get_skill_by_id(self, skill_id):
        ret = None
        for sk in self.skills:
            if sk.type == skill_id:
                ret = sk
                break
        if ret is None:
            raise ValueError
        return ret
        
    def attack(self,attack,coordinates, verbose=True):
        '''
        Character attacks to another square with attack.
        @param attack: attack that character is using
        @param coordinates: Coordinates character is trying to attack to
        '''
        if attack.get_action_type() == "s": # Skill
            attack.use(coordinates, verbose=verbose)
            return
        
        range = attack.get_range()
        min_range = range[0]
        max_range = range[1]
        squares = self.define_attack_targets(self.get_square(), max_range, True)     
        if coordinates not in squares:
            raise IllegalMoveException("Cannot attack to chosen tile!")
        
        target = self.board.get_piece(coordinates)
        
        #print(self.game.get_board().get_tile(self.game.get_board().get_square(self)))
        #print(self.tile.get_gui_tile())
        if not self.get_owner().is_ai() and self.game.get_board().get_tile(self.game.get_board().get_square(self)) != None: # If player controls char and gui is active
            wnd = ConfirmAttack(self,attack,target)     
            if not wnd.exec_():
                return
        
        if verbose:
            print("{} hyokkasi hahmoon {} hyokkayksella {}!".format(self.get_name(),target.get_name(),attack.get_name()))
        
        damage = int(attack.calculate_damage(target, verbose=verbose))
        
        #print("{} otti {} hp vahinkoa.".format(target.get_name(),damage))
        
        self.deal_damage(target, damage, verbose=verbose) 
        self.set_ready()
   
    
    def define_legal_squares(self):
        squares = self.board.legal_squares(self)
        return squares  
    
    def die(self, verbose=True):
        if not self.carried:
            square = self.get_square()
            self.board.remove_object(square)
            self.get_owner().remove_character(self)
        self.hp = 0
        self.alive = False
        if self.get_carrying() != None:
            carrying = self.get_carrying()
            self.remove_carrying(square)
            carrying.get_stuck(square)
        if verbose:
            print("{} kuoli!".format(self.get_name()))
        
    def deal_damage(self,other,amount, verbose=True):
        '''
        Character deals damage to other character.
        Method doesn't check if character should be able to do so. It is checked
        in other methods.
        '''
        other.remove_hp(amount, verbose=verbose)
        
    def define_attack_targets(self, tile, range, enemy):
        '''
        Method defines all possible squares character can attack to from given tile.
        @param tile: Coordinates for the tile attacking from OR the actual character attacking (in which case coordinates will be where char is currently)
        @param range: Attack range in squares
        @param enemy: True if attacking an enemy; False if targeting an ally
        @return: List of all possible target tiles' coordinates in format (x,y)
        '''
        try:
            square = tile.get_square()
        except AttributeError:
            square = tile
        if not enemy:
            target = self.get_owner()
        else:
            if self.get_owner() == self.game.get_blue_player():
                target = self.game.get_red_player()
            else:
                target = self.game.get_blue_player()
        return self.board.legal_attack_targets(square,range,target)
    
    def define_attack_squares(self,tile):
        squares = []
        for attack in self.attacks:
            ranges = attack.get_range()
            for range in range(ranges[0],ranges[1]):
                list = self.define_attack_targets(tile, range, True)
                for thing in list:
                    squares.append(thing)
        return squares
        
        
            
    def new_turn(self):
        '''
        Resets character's stats every turn (self.ready, etc)
        '''
        self.ready = False
        self.init_square = None
        self.reset_stats()

        for sk in self.skills:
            sk.new_turn()
            if sk.has_ended:
                self.delete_skill(sk.type)

    def __str__(self):
        '''
        Returns the character's state as a string.
        Used for testing purposes.
        @return: Character's state as a string
        '''
        
        name = self.get_name()
        
        char = "\n"
        char += name + "\n"
        
        if self.get_owner() == self.game.get_blue_player():
            char += "Controller: Blue\n"
        else:
            char += "Controller: Red\n"
            
        tile = self.get_square()
        char += "In tile " + str(tile) + "\n"
        char += "HP: " + str(self.hp) + " / " + str(self.maxhp) + "\n"
        char += "Carrying: "
        if self.carrying:
            char += self.carrying.get_name()
        else:
            char += "None"
        char += "\n"
        
        return char
    
    def to_dict(self):
        '''
        Returns the character's data as a dictionary
        '''
        data                = {}
        data['name']        = self.name
        data['color']       = self.color
        data['class']       = self.type
        data['square']      = self.get_square()
        data['status']      = self.status
        data['carried']     = self.carried
        data['ready']       = self.ready
        data['init_square'] = self.init_square
        data['hp']          = self.hp
        return data


'''
The following classes depict one class of characters each.
'''

class TestChar(Character):
    '''
    Basic character type used for testing.
    '''
    def __init__(self, game, color):
        Character.__init__(self,game, color)
        self.name = "TestChar"
        self.type = CharacterClass.TESTCHAR      
        self.maxhp = 25
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 15
        self.stats[Stats.DEFENSE] = 5
        self.stats[Stats.MAGIC] = 10
        self.stats[Stats.RESISTANCE] = 15
        self.stats[Stats.SPEED] = 15
        self.stats[Stats.EVASION] = 10
        self.stats[Stats.RANGE] = 6
        self.init_stats = dict(self.stats)
        self.skills = [skill.Ghost(self), skill.RaiseDef(self)]
            
        self.attacks.append(attack.Swordstrike(self))
        self.attacks.append(attack.Javelin(self))
        # (user, range, power, accuracy, name, flavor)
        
        
class Knight(Character):
    '''
    An all-around decent physical class.
    '''
    def __init__(self, game, color):
        Character.__init__(self,game, color)
        self.name = "Knight"
        self.type = CharacterClass.KNIGHT        
        self.maxhp = 25
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 17
        self.stats[Stats.DEFENSE] = 12
        self.stats[Stats.MAGIC] = 5
        self.stats[Stats.RESISTANCE] = 4
        self.stats[Stats.SPEED] = 17
        self.stats[Stats.EVASION] = 0
        self.stats[Stats.RANGE] = 3
        self.init_stats = dict(self.stats)
        self.skills = [skill.RaiseDef(self), skill.Bodyguard(self)]
            
        self.attacks.append(attack.Swordstrike(self))
        self.attacks.append(attack.Axe(self))

        
class Archer(Character):
    '''
    A class which can shoot arrows far away.
    '''
    def __init__(self, game, color):
        Character.__init__(self,game, color)
        self.name = "Archer"
        self.type = CharacterClass.ARCHER     
        self.maxhp = 20
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 13
        self.stats[Stats.DEFENSE] = 7
        self.stats[Stats.MAGIC] = 5
        self.stats[Stats.RESISTANCE] = 7
        self.stats[Stats.SPEED] = 20
        self.stats[Stats.EVASION] = 5
        self.stats[Stats.RANGE] = 4
        self.init_stats = dict(self.stats)
        self.skills = [skill.Sniper(self)]

        self.attacks.append(attack.Bow(self))
        self.attacks.append(attack.Longbow(self))
        self.attacks.append(attack.Snipe(self))
        

class Mage(Character):
    '''
    A class which attacks with magic.
    '''
    def __init__(self, game, color):
        Character.__init__(self,game, color)
        self.name = "Mage"
        self.type = CharacterClass.MAGE  
        self.maxhp = 20
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 5
        self.stats[Stats.DEFENSE] = 5
        self.stats[Stats.MAGIC] = 15
        self.stats[Stats.RESISTANCE] = 7
        self.stats[Stats.SPEED] = 20
        self.stats[Stats.EVASION] = 5
        self.stats[Stats.RANGE] = 3
        self.init_stats = dict(self.stats)
        self.skills = [skill.Camouflage(self)]
            
        self.attacks.append(attack.Fire(self))
        self.attacks.append(attack.Thunder(self))


class Cleric(Character):
    '''
    A support class with many useful skills but low defensive stats.
    '''
    def __init__(self, game, color):
        Character.__init__(self,game, color)
        self.name = "Cleric"
        self.type = CharacterClass.CLERIC   
        self.maxhp = 20
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 5
        self.stats[Stats.DEFENSE] = 2
        self.stats[Stats.MAGIC] = 20
        self.stats[Stats.RESISTANCE] = 3
        self.stats[Stats.SPEED] = 15
        self.stats[Stats.EVASION] = 5
        self.stats[Stats.RANGE] = 3
        self.init_stats = dict(self.stats)
        self.skills = [skill.Heal(self), skill.Camouflage(self), skill.Rest(self), skill.RaiseRng(self)]
            
        self.attacks.append(attack.Wind(self))
        self.attacks.append(attack.Knife(self))
        
        
class Assassin(Character):
    '''
    An agile class with high evasion and speed.
    '''
    def __init__(self, game, color):
        Character.__init__(self,game, color)
        self.name = "Assassin"
        self.type = CharacterClass.ASSASSIN  
        self.maxhp = 17
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 15
        self.stats[Stats.DEFENSE] = 10
        self.stats[Stats.MAGIC] = 10
        self.stats[Stats.RESISTANCE] = 7
        self.stats[Stats.SPEED] = 30
        self.stats[Stats.EVASION] = 15
        self.stats[Stats.RANGE] = 4
        self.init_stats = dict(self.stats)
        self.skills = [skill.Camouflage(self), skill.Sneak(self)]
            
        self.attacks.append(attack.Dagger(self))
        self.attacks.append(attack.ThrowingKnife(self))
        

class Valkyrie(Character):
    '''
    A flying class with high range but with a weakness to arrows.
    '''
    def __init__(self, game, color):
        Character.__init__(self,game, color)
        self.name = "Valkyrie"
        self.type = CharacterClass.VALKYRIE
        self.maxhp = 18
        self.hp = self.maxhp
        self.stats[Stats.ATTACK] = 12
        self.stats[Stats.DEFENSE] = 10
        self.stats[Stats.MAGIC] = 12
        self.stats[Stats.RESISTANCE] = 10
        self.stats[Stats.SPEED] = 15
        self.stats[Stats.EVASION] = 5
        self.stats[Stats.RANGE] = 5
        self.init_stats = dict(self.stats)
        self.skills = [skill.Levitate(self), skill.Rest(self), skill.Wish(self)]
            
        self.attacks.append(attack.Lance(self))
        self.attacks.append(attack.Stormwind(self))
        
    def get_path(self):
        if self.color == PlayerColor.RED and self.is_ready():
            return configload.get_image('valkyrie_red_moven.png')
        return Character.get_path(self)



CHARACTER_CLASS_TO_CHARACTER = {
    CharacterClass.TESTCHAR:    TestChar,
    CharacterClass.KNIGHT:      Knight,
    CharacterClass.ARCHER:      Archer,
    CharacterClass.MAGE:        Mage,
    CharacterClass.CLERIC:      Cleric,
    CharacterClass.ASSASSIN:    Assassin,
    CharacterClass.VALKYRIE:    Valkyrie,
}

def from_dict(data, game):
    '''
    Function creates a Character based on the data in the given dictionary.
    @param data:    Dictionary, in the format given by Character.to_dict(),
                    i.e. from_dict(char.to_dict()) should return a character identical to char
    @param game:    Game object this character will be inserted into
    '''
    character_class     = data['class'].lower()
    color               = data['color'].lower()
    
    # Create the character object based on the character class name given, and the color of the character
    char                = CHARACTER_CLASS_TO_CHARACTER[character_class](game, color)
    
    # Loop through the values and add them to the character
    for key, value in data.items():
        if key in ('class','color'):
            continue
        if key == 'loc':
            x,y = data[key].split(',')
            x,y = int(x), int(y)
            game.get_board().set_object((x,y), char)
            continue
        if key == 'square':
            game.get_board().set_object(data[key], char)
            continue
        if not hasattr(char, key):
            raise ValueError(key)
        char.key = value
        setattr(char, key, value)
        
    return char
