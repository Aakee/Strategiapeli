'''
Instance of this class is an independent character
'''

from stats import Stats
from game_errors import IllegalMoveException
from confirmwindow import ConfirmAttack
import random
from skill import Skill
import skill
from tile import Tile

class Character:
    
    '''
    Basic class for all characters.
    '''
    
    TESTCHAR = 0
    KNIGHT = 1
    ARCHER = 2
    MAGE = 3
    CLERIC = 4
    ASSASSIN = 5
    VIP = 6
    STUCK_VIP = 7
    VALKYRIE = 8
    

    def __init__(self, game, owner):
        self.game = game
        self.board = game.get_board()
        self.owner = owner
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
                       Stats.RESISTANCE: 0, Stats.SPEED: 0, Stats.EVASION: 0}
        self.attacks = []
        self.skills = []
        self.legal_squares = None
        self.init_square = None
        owner.add_character(self)
        
    def get_initial_stats(self):
        return self.stats
    
    def reset_stats(self):
        '''
        Method resets character's stats to their initial state, for example
        at the beginning of turn.
        '''
        self.stats = dict(self.init_stats)
        self.range = self.init_range
    
    def get_stats(self):
        '''
        Calculates the terrain's effect in the stats.
        '''
        stats = dict(self.stats)
        stat_enhanc = self.board.get_tile(self.get_square()).get_combat_bonuses()
        stats[Stats.ATTACK] += stat_enhanc[Stats.ATTACK]
        stats[Stats.DEFENSE] += stat_enhanc[Stats.DEFENSE]
        stats[Stats.MAGIC] += stat_enhanc[Stats.MAGIC]
        stats[Stats.RESISTANCE] += stat_enhanc[Stats.RESISTANCE]
        stats[Stats.SPEED] += stat_enhanc[Stats.SPEED]
        stats[Stats.EVASION] += stat_enhanc[Stats.EVASION]
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
        self.range += range_enhac
          
    def get_range(self):
        return self.range
    
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
    
    def add_hp(self, amount):
        self.hp += amount
        print("{} paransi {} hp vahinkoa.".format(self.get_name(),amount))
        if self.hp > self.maxhp:
            self.hp = self.maxhp
            
    def remove_hp(self,amount):
        self.hp -= amount
        print("{} otti {} hp vahinkoa.".format(self.get_name(),amount))
        if self.hp <= 0:
            self.die()
            
    def set_hp(self,hp):
        self.hp = hp
        if self.hp > self.maxhp:
            self.hp = self.maxhp
        if self.hp <= 0:
            self.die()
            
    def get_owner(self):
        return self.owner
            
    def is_enemy(self,other):
        return self.owner != other.owner
    
    def is_ready(self):
        return self.ready
    
    def set_ready(self):
        self.ready = True
        if self.game.get_gui():
            self.game.get_gui().set_active(None)
        
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
                self.owner.remove_character(self)
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
            if self.owner == self.game.get_ai():
                self.skills.append(skill.Execute(self))
        
    def set_transfer(self):
        '''
        Depending on  if the character has already skill Transfer, method either gives or takes it away.
        '''
        has_transfer = False
        trasfer = None
        for skill1 in self.skills:
            if skill1.get_type() == Skill.TRANSFER:
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
        path = './images/' + self.name.lower() + '_'
        if self.carried:
            path += 'carry_'
        if self.ready:
            path += 'moven.png'
        elif self.owner == self.game.get_human():
            path += 'player.png'
        elif self.owner == self.game.get_ai():
            path += 'enemy.png'
        else:
            raise KeyError("Error with player's controller!")
        return path
    
    def get_default_path(self):
        '''
        Same as get_path, but always returns path to coloured version of the picture (not the grey variant).
        '''
        path = './images/' + self.name.lower() + '_'
        if self.owner == self.game.get_human():
            path += 'player.png'
        elif self.owner == self.game.get_ai():
            path += 'enemy.png'
        else:
            raise KeyError("Error with player's controller!")
        return path
        
    def attack(self,attack,coordinates):
        '''
        Character attacks to another square with attack.
        @param attack: attack that character is using
        @param coordinates: Coordinates character is trying to attack to
        '''
        if attack.get_action_type() == "s": # Skill
            attack.use(coordinates)
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
        if self.owner == self.game.get_human() and self.game.get_board().get_tile(self.game.get_board().get_square(self)) != None: # If player controls char and gui is active
            wnd = ConfirmAttack(self,attack,target)     
            if not wnd.exec_():
                return
            
        print("{} hyokkasi hahmoon {} hyokkayksella {}!".format(self.get_name(),target.get_name(),attack.get_name()))
        
        damage = int(attack.calculate_damage(target))
        
        #print("{} otti {} hp vahinkoa.".format(target.get_name(),damage))
        
        self.deal_damage(target, damage) 
        self.set_ready()
   
    
    def define_legal_squares(self):
        squares = self.board.legal_squares(self)
        return squares  
    
    def die(self):
        if not self.carried:
            square = self.get_square()
            self.board.remove_object(square)
            self.owner.remove_character(self)
        self.hp = 0
        self.alive = False
        if self.get_carrying() != None:
            carrying = self.get_carrying()
            self.remove_carrying(square)
            carrying.get_stuck(square)
        print("{} kuoli!".format(self.get_name()))
        
    def deal_damage(self,other,amount):
        '''
        Character deals damage to other character.
        Method doesn't check if character should be able to do so. It is checked
        in other methods.
        '''
        other.remove_hp(amount)
        
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
            if self.get_owner() == self.game.get_human():
                target = self.game.get_ai()
            else:
                target = self.game.get_human()
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
        
    
    def ai_make_turn(self):
        '''
        Used by ai to make turn.
        Possible actions will be placed to a two-dimensional 
        list as following: [square, action, target_square, value]
        with the help of self.calculate_best_move.
        Square: the square where this character would move to.
        Action: Attack or skill character would do.
        Target_square: Target square for attack / skill
        Value: A number (>= 0) how clever this action would be.
        '''
        line = self.calculate_best_move()
        
        square = line[0]
        action = line[1]
        target_square = line[2]
         
        if action != None:
            
            if action.get_action_type() == "a": # Attack
                self.board.move_char(self,square)
                self.attack(action, target_square)
                
            elif action.get_action_type() == "s": # Skill
                self.board.move_char(self,square)
                action.use(target_square)
        
        if action == None:
            self.board.move_char(self,square)
                    
        self.set_ready()             
    
    def calculate_best_move(self):
        '''
        Character calculates the best move it thinks it can do.
        @return: list in format [square, action, target_square, value]
        '''
        possibilities = []
        priority = [Character.CLERIC, Character.VIP] # Main priority classes for ai (healers, etc)
        legal_squares = self.board.legal_squares(self)
        init_value = 0.5

        for square in legal_squares:
            
            possible_actions = False               
            multip = self.calculate_enemy_threat(square)

            for attack in self.attacks:
                
                ranges = attack.get_range()
                squares = self.define_attack_targets(square, ranges[1], True)
                    
                for attack_square in squares:
                    value = init_value
                    target = self.board.get_piece(attack_square)
                    if target != None and target.get_type() != Character.STUCK_VIP:
                        
                        prob_dmg = attack.calculate_probable_damage(target)
                        target_hp = target.get_hp()
                            
                        type = target.get_type()
                        tile = self.board.get_tile(self.get_square())
                        tile_type = tile.get_type()

                        if prob_dmg >= target_hp and type in priority:
                            value = value * 100
                        elif prob_dmg >= target_hp:      # More value if attack would kill target
                            value = value * 50
                        elif type in priority:    # More value if target is a priority (duh)
                            value = value * 50
                            
                        if tile_type == Tile.GOAL:
                            value = value * 100
                                
                        if multip >= 5:
                            value = value * 20
                            
                        if prob_dmg <= target_hp:
                            value = value * 10 * (prob_dmg / target_hp)
                            
                        else:
                            value = value * 10
                        
                        if prob_dmg == 0:
                            value = 0
                        
                        value = value * multip
                        value = round(value)
                        
                        if value > 0:
                            line = [square,attack,attack_square,value]
                            possibilities.append(line)
                            possible_actions = True
                            

            
            if len(self.skills) > 0:
                
                for skill in self.skills:
                    
                    if skill.get_type() in Skill.active_skills:
                        range = skill.get_range()

                        squares = self.define_attack_targets(square, range, skill.targets_enemy()) 
                        for skill_square in squares:
                            
                            value = init_value
                            multip2 = skill.get_value(skill_square)                    
                            value = value * multip * multip2
                            value = round(value)
                                
                            line = [square,skill,skill_square,value]
                            possibilities.append(line)
                                
                            if value > 0:
                                possible_actions = True

                                              
            if not possible_actions:
                
                value = round(init_value*multip)
                line = [square,None,None,value]
                possibilities.append(line)

            
        value = 0
        for action in possibilities:
            value += action[3]
            
        i = random.randint(0,value-1)
          
        for action in possibilities:
            i -= action[3]
            if i <= 0:
                line = action
                break
            
        return line
        
        
                        
    def calculate_enemy_threat(self,square):
        '''
        Used with ai_make_turn to define, if char is in danger in a tile.
        Value is low, if character is in threat of dying next turn.
        Damage is the highest, if character cannot be dealt damage to next turn but character is still close
        to enemies (because it is boring if enemies start to camp in corners :P)
        Exception: Cleric characters doesn't want to go close enemies
        @param square: Square in format (x,y) whose dangers we are inspecting
        '''
        value = 1
        possible_damage = 0
        for char in self.game.get_human().get_characters():
            possible_squares = self.board.legal_squares(char)
            enemy_attacks = char.get_attacks()
            for enemy_attack in enemy_attacks:

                range = enemy_attack.get_range()
                max_range = range[1]
                            
                for enemy_square in possible_squares:
                    danger_squares = self.board.legal_attack_targets(enemy_square,max_range,self.game.get_human())
                                
                    if square in danger_squares:
                        dmg = enemy_attack.calculate_probable_damage(self)
                        possible_damage += dmg
                        if dmg >= self.hp:
                            value = value / 3
                            
                                                
        if possible_damage == 0:
            value = value * 5
            if self.type == Character.CLERIC or self.type == Character.VIP:
                value = value * 4
                
        if 0 < possible_damage < (self.hp / 2):
            value = value * 1
        if (self.hp / 2) <= possible_damage < self.hp:
            value = value * 0.7
        if possible_damage >= self.hp:
            value = value * 0.4
            if self.type == Character.CLERIC or self.type == Character.VIP:
                value = value * 0.2
            
        if possible_damage == 0 and self.get_type() != Character.CLERIC and self.get_type() != Character.VIP:
            enemy_squares = []
            subvalue = 1
            for char in self.game.get_human().get_characters():
                enemy_squares.append(char.get_square())
            for tile in enemy_squares:
                distance = self.game.get_board().distance_to(square,tile)
                if distance > 0: # Just to be sure :P
                    subvalue += 30 * (1 / distance)

            value = value * subvalue
            
        return value
    
        
            
    def new_turn(self):
        '''
        Resets character's stats every turn (self.ready, etc)
        '''
        activating_skills = Skill.passive_beginning
        self.ready = False
        self.init_square = None
        self.reset_stats()
        for skill in self.skills:
            if skill.get_type() in activating_skills:
                skill.use()
        
        

        
    def __str__(self):
        '''
        Returns the character's state as a string.
        Used for testing purposes.
        @return: Character's state as a string
        '''
        
        name = self.get_name()
        
        char = "\n"
        char += name + "\n"
        
        if self.get_owner() == self.game.get_human():
            char += "Controller: Human\n"
        else:
            char += "Controller: Computer\n"
            
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
    
        