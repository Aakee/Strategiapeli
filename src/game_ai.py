'''
Module has functions for the AI to run.
'''

import random
import skill
from game_enums import CharacterClass, PlayerColor
from move import Move

import copy
import math
import datetime
import itertools



def get_ai_move_1(game, player_color: PlayerColor):

    player = game.get_player(player_color)

    not_ready = []
    for char in player.characters:
        if not char.is_ready():
            not_ready.append(char)
            
    size = len(not_ready)
    next = random.randint(0,size-1)
    char = not_ready[next]
    line = calculate_best_move(char)

    source_square = char.get_square()
    destination_square, action, target_square, value = line
    action_id = action.type if action is not None else None
    action_type = action.get_action_type() if action is not None else None

    mov = Move(source_square, destination_square, target_square, action_type, action_id)

    return mov

  

def calculate_best_move(char):
    '''
    Character calculates the best move it thinks it can do.
    @return: list in format [square, action, target_square, value]
    '''
    possibilities = []
    priority = [CharacterClass.CLERIC, CharacterClass.VIP] # Main priority classes for ai (healers, etc)
    legal_squares = char.board.legal_squares(char)
    init_value = 0.5

    for square in legal_squares:
        
        possible_actions = False               
        multip = calculate_enemy_threat(char,square)

        for attack in char.attacks:
            
            ranges = attack.get_range()
            squares = char.define_attack_targets(square, ranges[1], True)
                
            for attack_square in squares:
                value = init_value
                target = char.board.get_piece(attack_square)
                if target != None:
                    
                    prob_dmg = attack.calculate_probable_damage(target)
                    target_hp = target.get_hp()
                        
                    type = target.get_type()
                    tile = char.board.get_tile(char.get_square())
                    tile_type = tile.get_terrain()

                    if prob_dmg >= target_hp and type in priority:
                        value = value * 100
                    elif prob_dmg >= target_hp:      # More value if attack would kill target
                        value = value * 50
                    elif type in priority:    # More value if target is a priority (duh)
                        value = value * 50
                        
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
                        

        
        if len(char.skills) > 0:
            
            for sk in char.skills:
                
                if sk.get_type() in skill.Skill.active_skills:
                    range = sk.get_range()

                    squares = char.define_attack_targets(square, range, sk.targets_enemy()) 
                    for skill_square in squares:
                        
                        value = init_value
                        multip2 = sk.get_value(skill_square)                    
                        value = value * multip * multip2
                        value = round(value)
                            
                        line = [square,sk,skill_square,value]
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

def calculate_enemy_threat(char,square):
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
    enemy = char.game.get_blue_player() if char.owner == char.game.get_red_player() else char.game.get_red_player()
    for char in enemy.get_characters():
        possible_squares = char.board.legal_squares(char)
        enemy_attacks = char.get_attacks()
        for enemy_attack in enemy_attacks:

            range = enemy_attack.get_range()
            max_range = range[1]
                        
            for enemy_square in possible_squares:
                danger_squares = char.board.legal_attack_targets(enemy_square,max_range,enemy)
                            
                if square in danger_squares:
                    dmg = enemy_attack.calculate_probable_damage(char)
                    possible_damage += dmg
                    if dmg >= char.hp:
                        value = value / 3
                        
                                            
    if possible_damage == 0:
        value = value * 5
        if char.type == CharacterClass.CLERIC:
            value = value * 4
            
    if 0 < possible_damage < (char.hp / 2):
        value = value * 1
    if (char.hp / 2) <= possible_damage < char.hp:
        value = value * 0.7
    if possible_damage >= char.hp:
        value = value * 0.4
        if char.type == CharacterClass.CLERIC:
            value = value * 0.2
        
    if possible_damage == 0 and char.get_type() != CharacterClass.CLERIC:
        enemy_squares = []
        subvalue = 1
        for char in enemy.get_characters():
            enemy_squares.append(char.get_square())
        for tile in enemy_squares:
            distance = char.game.get_board().distance_to(square,tile)
            if distance > 0: # Just to be sure :P
                subvalue += 30 * (1 / distance)

        value = value * subvalue
        
    return value

# Approximate values how well each character class fares against each other character class.
# Scale: from -10 (very bad) to 10 (very good). 0 is neutral.
BASE_VALUES = {
    CharacterClass.ARCHER   : 10,
    CharacterClass.ASSASSIN : 10,
    CharacterClass.CLERIC   : 40,
    CharacterClass.KNIGHT   : 10,
    CharacterClass.MAGE     : 10,
    CharacterClass.VALKYRIE : 20,
    CharacterClass.TESTCHAR : 10,
}


ADVANTAGES = {
    CharacterClass.TESTCHAR: {
        CharacterClass.ARCHER   : 0,
        CharacterClass.ASSASSIN : 0,
        CharacterClass.CLERIC   : 0,
        CharacterClass.KNIGHT   : 0,
        CharacterClass.MAGE     : 0,
        CharacterClass.VALKYRIE : 0,
        CharacterClass.TESTCHAR : 0,
    },
    CharacterClass.ARCHER: {
        CharacterClass.ARCHER   : 0,
        CharacterClass.ASSASSIN :-3,
        CharacterClass.CLERIC   : 9,
        CharacterClass.KNIGHT   :-5,
        CharacterClass.MAGE     : 7,
        CharacterClass.VALKYRIE : 10,
        CharacterClass.TESTCHAR : 0,
    },
    CharacterClass.ASSASSIN: {
        CharacterClass.ARCHER   : 2,
        CharacterClass.ASSASSIN : 0,
        CharacterClass.CLERIC   : 10,
        CharacterClass.KNIGHT   :-6,
        CharacterClass.MAGE     : 4,
        CharacterClass.VALKYRIE : 2,
        CharacterClass.TESTCHAR : 0,
    },
    CharacterClass.CLERIC: {
        CharacterClass.ARCHER   : 0,
        CharacterClass.ASSASSIN :-9,
        CharacterClass.CLERIC   : 0,
        CharacterClass.KNIGHT   : 1,
        CharacterClass.MAGE     : 0,
        CharacterClass.VALKYRIE :-5,
        CharacterClass.TESTCHAR : 0,
    },
    CharacterClass.KNIGHT: {
        CharacterClass.ARCHER   : 0,
        CharacterClass.ASSASSIN : 8,
        CharacterClass.CLERIC   : 9,
        CharacterClass.KNIGHT   :-3,
        CharacterClass.MAGE     : 5,
        CharacterClass.VALKYRIE : 0,
        CharacterClass.TESTCHAR : 0,
    },
    CharacterClass.MAGE: {
        CharacterClass.ARCHER   : 0,
        CharacterClass.ASSASSIN : 3,
        CharacterClass.CLERIC   : 5,
        CharacterClass.KNIGHT   : 7,
        CharacterClass.MAGE     : 0,
        CharacterClass.VALKYRIE : 0,
        CharacterClass.TESTCHAR : 0,
    },
    CharacterClass.VALKYRIE: {
        CharacterClass.ARCHER   : 0,
        CharacterClass.ASSASSIN :-3,
        CharacterClass.CLERIC   : 3,
        CharacterClass.KNIGHT   : 3,
        CharacterClass.MAGE     : 4,
        CharacterClass.VALKYRIE : 0,
        CharacterClass.TESTCHAR : 0,
    },
}


def get_heuristic_board_value(game, player_color):
    '''
    Returns a heuristically determined value of how good a given board situation is to a player.
    '''
    # Game has been determined
    if game.get_winner() is not None:
        # Current player won
        if game.get_winner() == player_color:
            return  math.inf
        # Current player lost
        else:
            return -math.inf

    player = game.get_player(player_color)
    enemy = game.get_blue_player() if player_color == PlayerColor.RED else game.get_red_player()
    value = 0

    enemy_threat_board = construct_enemy_threat_board(game, enemy)

    # Base value for each character which is alive
    value += sum([BASE_VALUES[char.type] for char in player.get_characters()])
    value -= sum([BASE_VALUES[char.type] for char in enemy.get_characters()])

    # Points based on the current hp of the characters
    value += sum([0.5*BASE_VALUES[char.type] * char.get_hp() / char.get_maxhp() for char in player.get_characters()])
    value -= sum([0.5*BASE_VALUES[char.type] * char.get_hp() / char.get_maxhp() for char in enemy.get_characters()])

    # For each character, -10 to +10 points based on how well it fares against remaining enemy characters
    for player_char, enemy_char in itertools.product(player.get_characters(), enemy.get_characters()):
        value += ADVANTAGES[player_char.type][enemy_char.type] / len(enemy.get_characters())
        value -= ADVANTAGES[enemy_char.type][player_char.type] / len(player.get_characters())

    # For each char, drop the value if enemy can deal damage to this square
    for char in player.get_characters():
        prob_dmg = get_probable_enemy_damage(enemy_threat_board, char, char.get_square())
        max_dmg  = get_max_enemy_damage(enemy_threat_board, char, char.get_square())
        value -= 0.3 * BASE_VALUES[char.type] * ( 1 - max(0, (char.get_hp() - prob_dmg) / char.get_maxhp()) )
        if prob_dmg > char.get_hp():
            value -= 0.2 * BASE_VALUES[char.type]
        elif max_dmg > char.get_hp():
            value -= 0.1 * BASE_VALUES[char.type]

    # Prefer positions where characters are close to each other
    median_distance_from_teammates = 0
    if len(player.get_characters()) > 1:
        for char in player.get_characters():
            for other_char in [ch for ch in player.get_characters() if ch != char]:
                median_distance_from_teammates += ( abs(char.get_square()[0] - other_char.get_square()[0] ) + abs(char.get_square()[1] - other_char.get_square()[1] ) ) / (len(player.get_characters()) - 1)
        median_distance_from_teammates = median_distance_from_teammates / len(player.get_characters())
        value -= 0.2 * median_distance_from_teammates

    # To avoid games where no player does anything, slightly favor positions where characters are closer to enemies
    mean_distance_from_closest_enemy = 0
    for char in player.get_characters():
        closest_distance = math.inf
        for enemy_char in enemy.get_characters():
            closest_distance = min( closest_distance, abs(char.get_square()[0]-enemy_char.get_square()[0]) + abs(char.get_square()[1]-enemy_char.get_square()[1]) )
        mean_distance_from_closest_enemy += closest_distance / len(player.get_characters())
    value += 0.1 * mean_distance_from_closest_enemy

    return value


def get_next_move_2(game, player_color):
    player = game.get_player(player_color)
    enemy = game.get_blue_player() if player_color == PlayerColor.RED else game.get_red_player()


class CandidateMove:
    def __init__(self, char) -> None:
        self.char = char

class PositioningStrategy:
    SAFE        = 0     # Far away from enemies but close to allies
    SCOUT       = 1     # Close to enemies but out of their reach
    RISKY       = 2     # Attack without concerns of own safety


def get_ai_move_2(game, player_color):
    player = game.get_player(player_color)
    enemy = game.get_blue_player() if player_color == PlayerColor.RED else game.get_red_player()
    
    chars = [char for char in player.get_characters() if not char.is_ready() ]
    if len(chars) == 0:
        return
    # Tähän joku sorttausalgoritmi

    char = chars[0]
    possible_moves = []
    
    # Just move
    for square in char.get_legal_squares():
        possible_moves.append( Move( char.get_square(), square, None, 'p', None ) )
    
    # Attack
    for square, attack in itertools.product(char.get_legal_squares(), char.get_attacks()):
        for attack_target in char.define_attack_targets(square, attack.get_range()[1], True):
            possible_moves.append( Move( char.get_square(), square, attack_target, 'a', attack.type ) )
    
    # Skill
    for square, sk in itertools.product(char.get_legal_squares(), [sk for sk in char.skills if sk.type in skill.Skill.active_skills]):
        for skill_target in char.define_attack_targets(square, sk.get_range(), sk.targets_enemy()):
            possible_moves.append( Move( char.get_square(), square, skill_target, 's', sk.type ) )

    # Find best
    best_move = None
    best_value = -math.inf
    for move in possible_moves:
        game_copy = copy.deepcopy(game)
        game_copy.apply_move(move)
        value = get_heuristic_board_value(game_copy, player_color)
        move.value = value
        if value > best_value:
            best_move = move
            best_value = value

    return best_move


def construct_enemy_threat_board(game, enemy):
    board = [[[] for col in range(game.board.width)] for row in range(game.board.height) ]
    for char in enemy.get_characters():
        legal_movement_squares = char.get_legal_squares()
        all_attacks = char.get_attacks()
        for square, attack in itertools.product(legal_movement_squares, all_attacks):
            attack_range = attack.get_range()[1]
            attack_squares = game.board.get_tiles_in_range(square, attack_range)
            for attack_square in attack_squares:
                board[attack_square[1]][attack_square[0]].append([char, attack])
    return board

def get_max_enemy_damage(board, char, coordinates):
    all_attacks = board[coordinates[1]][coordinates[0]]
    char_attack = {}
    for enemy_char, attack in all_attacks:
        dmg = attack.calculate_max_damage(char)
        if enemy_char not in char_attack or dmg > char_attack[enemy_char]:
            char_attack[enemy_char] = dmg
    return sum([dmg for key, dmg in char_attack.items()])

def get_probable_enemy_damage(board, char, coordinates):
    all_attacks = board[coordinates[1]][coordinates[0]]
    char_attack = {}
    for enemy_char, attack in all_attacks:
        dmg = attack.calculate_probable_damage(char)
        if enemy_char not in char_attack or dmg > char_attack[enemy_char]:
            char_attack[enemy_char] = dmg
    return sum([dmg for key, dmg in char_attack.items()])
