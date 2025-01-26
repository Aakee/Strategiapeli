'''
Module has a set of AI functions to run.
'''

import random
import skill
from game_enums import CharacterClass, PlayerColor
from game_errors import IllegalMoveException
from move import Move, Value

import copy
import math
import statistics


# Some base value for each character class, from 1-10
BASE_VALUES = {
    CharacterClass.ARCHER   : 5,
    CharacterClass.ASSASSIN : 5,
    CharacterClass.CLERIC   : 10,
    CharacterClass.KNIGHT   : 5,
    CharacterClass.MAGE     : 5,
    CharacterClass.VALKYRIE : 7,
    CharacterClass.TESTCHAR : 5,
}

# How much the character class tries to move towards allies, from 0 to 10
PREFER_ALLY_COMPANY = {
    CharacterClass.ARCHER   : 4,
    CharacterClass.ASSASSIN : 1,
    CharacterClass.CLERIC   : 10,
    CharacterClass.KNIGHT   : 7,
    CharacterClass.MAGE     : 5,
    CharacterClass.VALKYRIE : 7,
    CharacterClass.TESTCHAR : 5,
}

# How much the character class tries to move towards enemies, from 1 to 10
PREFER_ENEMY_COMPANY = {
    CharacterClass.ARCHER   : 5,
    CharacterClass.ASSASSIN : 9,
    CharacterClass.CLERIC   : 0,
    CharacterClass.KNIGHT   : 4,
    CharacterClass.MAGE     : 5,
    CharacterClass.VALKYRIE : 6,
    CharacterClass.TESTCHAR : 5,
}

# Approximate values how well each character class fares against each other character class.
# Scale: from 0 (very bad) to 10 (very good)
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
        CharacterClass.ARCHER   : 3,
        CharacterClass.ASSASSIN : 0,
        CharacterClass.CLERIC   : 9,
        CharacterClass.KNIGHT   : 1,
        CharacterClass.MAGE     : 7,
        CharacterClass.VALKYRIE : 10,
        CharacterClass.TESTCHAR : 0,
    },
    CharacterClass.ASSASSIN: {
        CharacterClass.ARCHER   : 5,
        CharacterClass.ASSASSIN : 3,
        CharacterClass.CLERIC   : 10,
        CharacterClass.KNIGHT   : 1,
        CharacterClass.MAGE     : 5,
        CharacterClass.VALKYRIE : 3,
        CharacterClass.TESTCHAR : 0,
    },
    CharacterClass.CLERIC: {
        CharacterClass.ARCHER   : 5,
        CharacterClass.ASSASSIN : 1,
        CharacterClass.CLERIC   : 5,
        CharacterClass.KNIGHT   : 5,
        CharacterClass.MAGE     : 5,
        CharacterClass.VALKYRIE : 5,
        CharacterClass.TESTCHAR : 0,
    },
    CharacterClass.KNIGHT: {
        CharacterClass.ARCHER   : 0,
        CharacterClass.ASSASSIN : 8,
        CharacterClass.CLERIC   : 9,
        CharacterClass.KNIGHT   : 2,
        CharacterClass.MAGE     : 5,
        CharacterClass.VALKYRIE : 0,
        CharacterClass.TESTCHAR : 0,
    },
    CharacterClass.MAGE: {
        CharacterClass.ARCHER   : 5,
        CharacterClass.ASSASSIN : 3,
        CharacterClass.CLERIC   : 6,
        CharacterClass.KNIGHT   : 9,
        CharacterClass.MAGE     : 4,
        CharacterClass.VALKYRIE : 3,
        CharacterClass.TESTCHAR : 0,
    },
    CharacterClass.VALKYRIE: {
        CharacterClass.ARCHER   : 0,
        CharacterClass.ASSASSIN : 2,
        CharacterClass.CLERIC   : 5,
        CharacterClass.KNIGHT   : 5,
        CharacterClass.MAGE     : 4,
        CharacterClass.VALKYRIE : 3,
        CharacterClass.TESTCHAR : 0,
    },
}


def get_move(game, player_color) -> Move:
    '''
    Generates and returns a move to be executed.
    '''
    player = game.get_player(player_color)
    
    chars = [char for char in player.get_characters() if not char.is_ready() ]
    if len(chars) == 0:
        return
    # Tähän joku sorttausalgoritmi

    char = chars[0]
    possible_moves = []
    
    possible_moves.append(Move( char.get_square(), char.get_square(), None, 'p', None ))

    for square in char.get_legal_squares():
        activated_skills = [sk for sk in char.get_full_skills() if sk.type in skill.Skill.active_skills]
        skill_targets  = [(target_square, sk.type) for sk in activated_skills for target_square in char.define_attack_targets(square, sk.get_range(), sk.targets_enemy()) ]
        attack_targets = [(target_square, att.type) for att in char.get_attacks() for target_square in char.define_attack_targets(square, att.get_range()[1], True) ]
        
        for skill_target, skill_type in skill_targets:
            possible_moves.append( Move( char.get_square(), square, skill_target, 's', skill_type ) )
        
        for attack_target, attack_type in attack_targets:
            possible_moves.append( Move( char.get_square(), square, attack_target, 'a', attack_type ) )
        
        if len(skill_targets) == 0 and len(attack_targets) == 0:
            possible_moves.append( Move( char.get_square(), square, None, 'p', None ) )

    # Find best
    best_move = possible_moves[0]
    best_value = -math.inf

    for move in possible_moves:
        game_copy = copy.deepcopy(game)
        try:
            apply_candidate_move(game_copy, move)
        except IllegalMoveException:
            continue
        value = get_heuristic_board_value_3(game_copy, player_color)
        move.value = value
        if value.get() > best_value:
            best_move = move
            best_value = value.get()
    return best_move


def apply_candidate_move(game, move):
    '''
    Function behaves like game.apply_move, but deals average damage instead of random :D
    '''
            
    # Move character
    char = game.board.get_piece(move.source_square)
    game.move_character(char, move.destination_square, verbose=False)

    # Attack
    if move.action_type == 'a':
        # Find the attack from the character which matches the chosen one
        attack = char.get_attack_by_id(move.action_id)
        enemy_char = game.board.get_piece(move.target_square)
        dmg = attack.calculate_probable_damage(enemy_char)
        enemy_char.remove_hp(dmg, verbose=False)

    # Skill
    elif move.action_type == 's':
        # Find the attack from the character which matches the chosen one
        skill = char.get_skill_by_id(move.action_id)
        game.use_skill(char, move.target_square, skill, verbose=False)

    else:
        char.set_ready()


def get_heuristic_board_value_3(game, player_color):
    '''
    Returns a heuristically determined value of how good a given board situation is to a player.
    '''
    value = Value()

    # Game has been determined
    if game.get_winner() is not None:
        # Current player won
        if game.get_winner() == player_color:
            value.add('Winner', math.inf)
            return value
        # Current player lost
        else:
            value.add('Winner', -math.inf)
            return value
        
    # Helper function
    def distance_between_two_characters(first,second):
        return  abs(first.get_square()[0]-second.get_square()[0]) + abs(first.get_square()[1]-second.get_square()[1] ) 

    player = game.get_player(player_color)
    enemy = game.get_blue_player() if player_color == PlayerColor.RED else game.get_red_player()

    # Points for each character who is alive based on their current HP
    value += ( 'Characters',     2*sum([ BASE_VALUES[char.type] * (1 + char.get_hp() / char.get_maxhp()) for char in player.get_characters()]) )
    value -= ( 'En. characters', 2*sum([ BASE_VALUES[char.type] * (1 + char.get_hp() / char.get_maxhp()) for char in enemy .get_characters()]) )

    # Points for advantages
    value += ( 'PlAdv', statistics.mean([ ADVANTAGES[char.type][enemy_char.type] * (      char.get_hp() /       char.get_maxhp()) for char in player.get_characters() for enemy_char in enemy.get_characters()]) )
    value -= ( 'EnAdv', statistics.mean([ ADVANTAGES[enemy_char.type][char.type] * (enemy_char.get_hp() / enemy_char.get_maxhp()) for char in player.get_characters() for enemy_char in enemy.get_characters()]) )

    # Prefer positions where characters are close to each other
    avedist_allies = statistics.mean([PREFER_ALLY_COMPANY[first.type]*distance_between_two_characters(first, second) for first in player.get_characters() for second in player.get_characters()])
    value -= ('Allies close', math.tanh(avedist_allies/100 ) )

    # To avoid games where no player does anything, slightly favor positions where characters are closer to enemies
    avedist_enemies = statistics.mean([ math.tanh( PREFER_ENEMY_COMPANY[first.type]*distance_between_two_characters(first, second) / 100 ) for first in player.get_characters() for second in enemy.get_characters()])
    value -= ('Enemies close', avedist_enemies )

    # Add some randomness
    value += ('Random', random.gauss(0,0.01) )

    return value
