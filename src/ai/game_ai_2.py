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
import itertools


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
    enemy = game.get_blue_player() if player_color == PlayerColor.RED else game.get_red_player()
    
    chars = [char for char in player.get_characters() if not char.is_ready() ]
    if len(chars) == 0:
        return
    # Tähän joku sorttausalgoritmi

    char = chars[0]
    possible_moves = []

    possible_moves.append(Move( char.get_square(), char.get_square(), None, 'p', None ))

    for square in char.get_legal_squares():
        activated_skills = [sk for sk in char.skills if sk.type in skill.Skill.active_skills]
        skill_targets  = [(target_square, sk.type) for sk in activated_skills for target_square in char.define_attack_targets(square, sk.get_range(), sk.targets_enemy()) ]
        attack_targets = [(target_square, att.type) for att in char.get_attacks() for target_square in char.define_attack_targets(square, att.get_range()[1], True) ]
        
        for skill_target, skill_type in skill_targets:
            possible_moves.append( Move( char.get_square(), square, skill_target, 's', skill_type ) )
        
        for attack_target, attack_type in attack_targets:
            possible_moves.append( Move( char.get_square(), square, attack_target, 'a', attack_type ) )
        
        if len(skill_targets) == 0 and len(attack_targets) == 0:
            possible_moves.append( Move( char.get_square(), square, None, 'p', None ) )

    # Find best
    enemy_threat_board = construct_enemy_threat_board(game, enemy)
    best_move = possible_moves[0]
    best_value = -math.inf

    for move in possible_moves:
        game_copy = copy.deepcopy(game)
        try:
            apply_candidate_move(game_copy, move)
        except IllegalMoveException:
            continue
        value = get_heuristic_board_value(game_copy, player_color, enemy_threat_board)
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


def get_heuristic_board_value(game, player_color, enemy_threat_board):
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
        
    def distance_between_two_characters(first,second):
        return  abs(first.get_square()[0]-second.get_square()[0]) + abs(first.get_square()[1]-second.get_square()[1] ) 


    player = game.get_player(player_color)
    enemy = game.get_blue_player() if player_color == PlayerColor.RED else game.get_red_player()

    nof_player_characters = len(player.get_characters())
    nof_enemy_characters = len(enemy.get_characters())

    # Base value for each character which is alive
    value += ( 'Characters', sum([BASE_VALUES[char.type] for char in player.get_characters()]) )
    value -= ( 'En. characters', sum([BASE_VALUES[char.type] for char in enemy.get_characters()]) )

    # Points based on the current hp of the characters
    value += ( 'HP', 0.2*sum([BASE_VALUES[char.type] * char.get_hp() / char.get_maxhp() for char in player.get_characters()]) )
    value -= ( 'EHP', 0.2*sum([BASE_VALUES[char.type] * char.get_hp() / char.get_maxhp() for char in enemy.get_characters()]) )

    value += ( 'Average HP', 0.1*sum([char.get_hp()/nof_player_characters for char in player.get_characters()]) )
    value -= ( 'Average EHP', 0.1*sum([char.get_hp()/nof_enemy_characters for char in enemy.get_characters()]) )

    # For each char, drop the value if enemy can deal damage to this square
    player_against_enemy_val = 0
    enemy_against_player_val = 0
    for char in player.get_characters():
        char_danger_val = 0
        prob_dmg = get_probable_enemy_damage(enemy_threat_board, char, char.get_square())
        max_dmg  = get_max_enemy_damage(enemy_threat_board, char, char.get_square())

        for enemy_char in enemy.get_characters():
            if max_dmg < char.get_hp():
                player_against_enemy_val += (nof_player_characters/nof_enemy_characters) * ( (char.get_hp()-prob_dmg) / char.get_maxhp() ) * ADVANTAGES[char.type][enemy_char.type] / len(enemy.get_characters())
                enemy_against_player_val += (nof_enemy_characters/nof_player_characters) * ( enemy_char.get_hp() / enemy_char.get_maxhp() ) * ADVANTAGES[enemy_char.type][char.type] / len(player.get_characters())

            elif prob_dmg < char.get_hp():
                player_against_enemy_val += 0.5*(nof_player_characters/nof_enemy_characters) * ( (char.get_hp()-prob_dmg) / char.get_maxhp() ) * ADVANTAGES[char.type][enemy_char.type] / len(enemy.get_characters())
                enemy_against_player_val += (nof_enemy_characters/nof_player_characters) * ( enemy_char.get_hp() / enemy_char.get_maxhp() ) * ADVANTAGES[enemy_char.type][char.type] / len(player.get_characters())

            else:
                enemy_against_player_val += (nof_enemy_characters/nof_player_characters) * ( enemy_char.get_hp() / enemy_char.get_maxhp() ) * ADVANTAGES[enemy_char.type][char.type] / len(player.get_characters())

        char_danger_val -= 0.4 * BASE_VALUES[char.type] * ( max(0, prob_dmg ) / char.get_maxhp() )
        if prob_dmg > char.get_hp():
            char_danger_val -= 0.4 * BASE_VALUES[char.type]
        elif max_dmg > char.get_hp():
            char_danger_val -= 0.2 * BASE_VALUES[char.type]
        value.add(f'{char.name} danger', char_danger_val)

    # For each character, give points based on how well it fares against remaining enemy characters
    value += ('Player advantage', player_against_enemy_val)
    value -= ('Enemy advantage', enemy_against_player_val)

    # Prefer positions where characters are close to each other
    value -= ('Allies close', 0.2 * sum([PREFER_ALLY_COMPANY[char.type]*distance_between_two_characters(char, second_char) / (nof_player_characters**2) for char in player.get_characters() for second_char in player.get_characters() ]) )

    # To avoid games where no player does anything, slightly favor positions where characters are closer to enemies
    value -= ('Enemies close', 0.1 * (nof_player_characters/nof_enemy_characters) * sum([ PREFER_ENEMY_COMPANY[char.type]*distance_between_two_characters(char, enemy_char) / (nof_player_characters * nof_enemy_characters) for char in player.get_characters() for enemy_char in enemy.get_characters() ]) )

    # Add random noise
    value += ('Noise', random.gauss(0, 0.3))

    return value


def construct_enemy_threat_board(game, enemy):
    '''
    Function constructs a 2D-board showing where the enemy characters can attack to this turn and with which attacks.
    '''
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
    '''
    Function calculates the maximum damage a character can get when standing on a square with 'coordinates',
    based on the player threat board.
    '''
    all_attacks = board[coordinates[1]][coordinates[0]]
    char_attack = {}
    for enemy_char, attack in all_attacks:
        if enemy_char.get_hp() == 0:
            continue
        dmg = attack.calculate_max_damage(char)
        if enemy_char not in char_attack or dmg > char_attack[enemy_char]:
            char_attack[enemy_char] = dmg
    return sum([dmg for key, dmg in char_attack.items()])


def get_probable_enemy_damage(board, char, coordinates):
    '''
    Function calculates the expected value of damage a character can get when standing on a square with 'coordinates',
    based on the player threat board.
    '''
    all_attacks = board[coordinates[1]][coordinates[0]]
    char_attack = {}
    for enemy_char, attack in all_attacks:
        if enemy_char.get_hp() == 0:
            continue
        dmg = attack.calculate_probable_damage(char)
        if enemy_char not in char_attack or dmg > char_attack[enemy_char]:
            char_attack[enemy_char] = dmg
    return sum([dmg for key, dmg in char_attack.items()])


