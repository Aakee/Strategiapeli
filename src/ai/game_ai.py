'''
Module has functions for the AI to run.
'''

import random
import skill
from game_enums import CharacterClass, PlayerColor, SkillType, Stats
from game_errors import IllegalMoveException
from move import Move, Value
import ai.distance

import copy
import math
import statistics
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

BASE_VALUES = {
    CharacterClass.ARCHER   : 5,
    CharacterClass.ASSASSIN : 5,
    CharacterClass.CLERIC   : 10,
    CharacterClass.KNIGHT   : 5,
    CharacterClass.MAGE     : 5,
    CharacterClass.VALKYRIE : 7,
    CharacterClass.TESTCHAR : 5,
}

PREFER_ALLY_COMPANY = {
    CharacterClass.ARCHER   : 4,
    CharacterClass.ASSASSIN : 1,
    CharacterClass.CLERIC   : 10,
    CharacterClass.KNIGHT   : 7,
    CharacterClass.MAGE     : 5,
    CharacterClass.VALKYRIE : 7,
    CharacterClass.TESTCHAR : 5,
}

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
# Scale: from -10 (very bad) to 10 (very good). 0 is neutral.
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


    # For each character, -10 to +10 points based on how well it fares against remaining enemy characters

    #for player_char, enemy_char in itertools.product(player.get_characters(), enemy.get_characters()):
    #    player_against_enemy_val += (nof_player_characters/nof_enemy_characters) * ADVANTAGES[player_char.type][enemy_char.type] / len(enemy.get_characters())
    #    enemy_against_player_val += (nof_enemy_characters/nof_player_characters) * ADVANTAGES[enemy_char.type][player_char.type] / len(player.get_characters())
    value += ('Player advantage', player_against_enemy_val)
    value -= ('Enemy advantage', enemy_against_player_val)



    # Prefer positions where characters are close to each other
    value -= ('Allies close', 0.2 * sum([PREFER_ALLY_COMPANY[char.type]*distance_between_two_characters(char, second_char) / (nof_player_characters**2) for char in player.get_characters() for second_char in player.get_characters() ]) )

    # To avoid games where no player does anything, slightly favor positions where characters are closer to enemies
    value -= ('Enemies close', 0.1 * (nof_player_characters/nof_enemy_characters) * sum([ PREFER_ENEMY_COMPANY[char.type]*distance_between_two_characters(char, enemy_char) / (nof_player_characters * nof_enemy_characters) for char in player.get_characters() for enemy_char in enemy.get_characters() ]) )

    # Add random noise
    value += ('Noise', random.gauss(0, 0.3))

    return value



def get_ai_move_2(game, player_color):
    player = game.get_player(player_color)
    enemy = game.get_blue_player() if player_color == PlayerColor.RED else game.get_red_player()
    
    chars = [char for char in player.get_characters() if not char.is_ready() ]
    if len(chars) == 0:
        return
    # Tähän joku sorttausalgoritmi

    char = chars[0]
    possible_moves = []
    
    '''
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
    '''
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

    copy_time   = datetime.timedelta()
    apply_time  = datetime.timedelta()
    heur_time   = datetime.timedelta()

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
        print(move)
        if value.get() > best_value:
            best_move = move
            best_value = value.get()

    #print(f"copy: {copy_time}, apply: {apply_time}, heur: {heur_time}")
    print("Best:")
    print(best_move)
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
        if enemy_char.get_hp() == 0:
            continue
        dmg = attack.calculate_max_damage(char)
        if enemy_char not in char_attack or dmg > char_attack[enemy_char]:
            char_attack[enemy_char] = dmg
    return sum([dmg for key, dmg in char_attack.items()])

def get_probable_enemy_damage(board, char, coordinates):
    all_attacks = board[coordinates[1]][coordinates[0]]
    char_attack = {}
    for enemy_char, attack in all_attacks:
        if enemy_char.get_hp() == 0:
            continue
        dmg = attack.calculate_probable_damage(char)
        if enemy_char not in char_attack or dmg > char_attack[enemy_char]:
            char_attack[enemy_char] = dmg
    return sum([dmg for key, dmg in char_attack.items()])


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
        enemy_char.remove_hp(dmg)

    # Skill
    elif move.action_type == 's':
        # Find the attack from the character which matches the chosen one
        skill = char.get_skill_by_id(move.action_id)
        game.use_skill(char, move.target_square, skill, verbose=False)

    else:
        char.set_ready()




# ===============================================
        

def get_heuristic_board_value_3(game, player_color, enemy_threat_board):
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
    nof_player_characters = len(player.get_characters())
    nof_enemy_characters = len(enemy.get_characters())

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



def get_ai_move_3(game, player_color):
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

    copy_time   = datetime.timedelta()
    apply_time  = datetime.timedelta()
    heur_time   = datetime.timedelta()

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
        value = get_heuristic_board_value_3(game_copy, player_color, enemy_threat_board)
        move.value = value
        print(move)
        if value.get() > best_value:
            best_move = move
            best_value = value.get()

    #print(f"copy: {copy_time}, apply: {apply_time}, heur: {heur_time}")
    print("Best:")
    print(best_move)
    return best_move



def apply_candidate_move_3(game, move):
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
        enemy_char.remove_hp(dmg)

    # Skill
    elif move.action_type == 's':
        # Find the attack from the character which matches the chosen one
        skill = char.get_skill_by_id(move.action_id)
        game.use_skill(char, move.target_square, skill, verbose=False)

    else:
        char.set_ready()



# ===============================================
        

def get_heuristic_board_value_4(game, moven_char, player_color, player_threat_board, enemy_threat_board):
    '''
    Returns a heuristically determined value of how good a given board situation is to a player.
    '''
    value = Value()

    # Game has been determined
    if get_winner(game) is not None:
        # Current player won
        if get_winner(game) == player_color:
            value.add('Winner', math.inf)
            return value
        # Current player lost
        else:
            value.add('Winner', -math.inf)
            return value
        
    player = game.get_player(player_color)
    enemy = game.get_blue_player() if player.color == PlayerColor.RED else game.get_red_player()
    nof_player_characters = len(player.get_characters())
    nof_enemy_characters = len(enemy.get_characters())

    # Points for each character who is alive based on their current HP
    value += ( 'Characters',     2*sum([ BASE_VALUES[char.type] * (1 + calculate_tmp_hp(char) / char.get_maxhp()) for char in player.get_characters() if calculate_tmp_hp(char) > 0]) )
    value -= ( 'En. characters', 2*sum([ BASE_VALUES[char.type] * (1 + calculate_tmp_hp(char) / char.get_maxhp()) for char in enemy .get_characters() if calculate_tmp_hp(char) > 0]) )

    # Points for advantages
    player_advantage    = statistics.mean([ ADVANTAGES[char.type][enemy_char.type] * (0.8 + 0.2*       calculate_tmp_hp(char) /       char.get_maxhp()) for char in player.get_characters() for enemy_char in enemy.get_characters() if calculate_tmp_hp(char) > 0])
    enemy_advantage     = statistics.mean([ ADVANTAGES[enemy_char.type][char.type] * (0.8 + 0.2* calculate_tmp_hp(enemy_char) / enemy_char.get_maxhp()) for char in player.get_characters() for enemy_char in enemy.get_characters() if calculate_tmp_hp(enemy_char) > 0]) 
    
    value += ( 'PlAdv', player_advantage )
    value -= ( 'EnAdv', enemy_advantage )

    # Prefer positions where characters are close to each other
    avedist_allies = statistics.mean([PREFER_ALLY_COMPANY[moven_char.type]*math.tanh(game.board.distmap.distance_between_characters(moven_char, other)/100) for other in player.get_characters() if calculate_tmp_hp(other) > 0])
    value -= ('Allies close', 2*avedist_allies )

    # To avoid games where no player does anything, slightly favor positions where characters are closer to enemies
    avedist_enemies = statistics.mean([ PREFER_ENEMY_COMPANY[moven_char.type]*math.tanh(game.board.distmap.distance_between_characters(moven_char, other) / 100 ) for other in enemy.get_characters() if calculate_tmp_hp(other) > 0])
    value -= ('Enemies close', max(3,(player_advantage/nof_player_characters)/(enemy_advantage/nof_enemy_characters))*avedist_enemies )

    # Very slightly prefer positions where characters total stats are higher (mainly to support using raise range and such)
    value += ('PlStats', 0.01*statistics.mean([stat_val for char in player.get_characters() for stat, stat_val in char.get_stats().items()]) )
    value -= ('EnStats', 0.01*statistics.mean([stat_val for char in enemy .get_characters() for stat, stat_val in char.get_stats().items()]) )

    # Avoid dangerous squares
    danger_value = 0
    for char in player.get_characters():

        # Probable (expected) damage, where key is the attacker and item is the damage
        prob_dmg_dict   = get_probable_enemy_damage_4(game, enemy_threat_board, char)
        prob_dmg        = sum([val for key, val in prob_dmg_dict.items()])

        # Same for max damage
        max_dmg_dict    = get_max_enemy_damage_4(game, enemy_threat_board,char)
        max_dmg         = sum([val for key, val in max_dmg_dict.items()])

        # Enemies that can attack to the character's square
        dmg_enemies     = [key for key in prob_dmg_dict]

        max_advantage    = max([ADVANTAGES[char.type][enemy_char.type] for enemy_char in dmg_enemies]) if len(dmg_enemies) > 0 else 0
        max_disadvantage = max([ADVANTAGES[enemy_char.type][char.type] for enemy_char in dmg_enemies]) if len(dmg_enemies) > 0 else 0
        n_could_be_killed = len([enemy_char for enemy_char in dmg_enemies if calculate_tmp_hp(enemy_char) < sum([val for key, val in get_probable_enemy_damage_4(game,player_threat_board, enemy_char, disregard_moven=True).items() ])]) if len(dmg_enemies) > 0 else 0

        fact = 1    # Base multiplier

        # Multiplier affected by the advantage/disadvantages, and if the attacking chars could be killed this turn
        if len(prob_dmg_dict) > 0:
            fact = 0.1* (max_disadvantage + 0.001) / (max_advantage + 0.001)
            fact = fact * ( len(prob_dmg_dict) - n_could_be_killed ) / len(prob_dmg_dict)

        # Very dangerous if enemy is expected to kill here
        if prob_dmg >= calculate_tmp_hp(char):
            danger_value += BASE_VALUES[char.type] * fact / nof_player_characters
        # Quite dangerous if the enemy can kill with a bit of luck
        elif max_dmg >= calculate_tmp_hp(char):
            danger_value += 0.8 * BASE_VALUES[char.type] * fact / nof_player_characters
        # Otherwise, add value based on the expected damage and multiplier
        else:
            danger_value += 0.3*BASE_VALUES[char.type] * (prob_dmg / char.get_maxhp() ) * fact / nof_player_characters

    value -= ("Dangerous squares", danger_value )

    # Add some randomness
    value += ('Random', random.gauss(0,0.01) )

    return value


def construct_player_threat_board(game, player):
    '''
    Function constructs a 2D-board showing where the characters can attack to this turn and with which attacks.
    '''
    board = [[[] for col in range(game.board.width)] for row in range(game.board.height) ]
    # Loop through all characters
    for char in player.get_characters():
        legal_movement_squares = char.get_legal_squares()
        all_attacks = char.get_attacks()
        # Loop through all attacks this character has
        for square, attack in itertools.product(legal_movement_squares, all_attacks):
            attack_range = attack.get_range()[1]
            attack_squares = game.board.get_tiles_in_range(square, attack_range)
            # Add the attack to the board
            for attack_square in attack_squares:
                board[attack_square[1]][attack_square[0]].append([char.get_square(), attack.type])
    return board

def get_max_enemy_damage_4(game, threat_board, char, disregard_moven=False):
    '''
    Function calculates the maximum damage a character can get when standing on a square,
    based on the player threat board.
    Disregard moven: do not count possible damage from characters that have already ended their turn.
    '''
    coordinates = char.get_square()
    all_attacks = threat_board[coordinates[1]][coordinates[0]]
    char_attack = {}
    for enemy_char_square, attack_id in all_attacks:
        enemy_char = game.board.get_piece(enemy_char_square)
        if enemy_char is None:
            continue
        if enemy_char.get_hp() == 0:
            continue
        if disregard_moven and enemy_char.is_ready():
            continue
        attack = enemy_char.get_attack_by_id(attack_id)
        dmg = attack.calculate_max_damage(char)
        if enemy_char not in char_attack or dmg > char_attack[enemy_char]:
            char_attack[enemy_char] = dmg
    return char_attack

def get_probable_enemy_damage_4(game, threat_board, char, disregard_moven=False):
    '''
    Function calculates the expected value of the damage a character can get when standing on a square,
    based on the player threat board.
    Disregard moven: do not count possible damage from characters that have already ended their turn.
    '''
    coordinates = char.get_square()
    all_attacks = threat_board[coordinates[1]][coordinates[0]]
    char_attack = {}
    for enemy_char_square, attack_id in all_attacks:
        enemy_char = game.board.get_piece(enemy_char_square)
        if enemy_char is None:
            continue
        if enemy_char.get_hp() == 0:
            continue
        if disregard_moven and enemy_char.is_ready():
            continue
        attack = enemy_char.get_attack_by_id(attack_id)
        dmg = attack.calculate_probable_damage(char)
        if enemy_char not in char_attack or dmg > char_attack[enemy_char]:
            char_attack[enemy_char] = dmg
    return char_attack



def get_ai_move_4(game, player_color):
    '''
    Generates and returns a move to be executed.
    '''
    player = game.get_player(player_color)
    #enemy = game.get_blue_player() if player_color == PlayerColor.RED else game.get_red_player()
    
    chars = [char for char in player.get_characters() if not char.is_ready() ]
    if len(chars) == 0:
        return
    
    # Priority: which characters move first
    priority = {
        CharacterClass.CLERIC   : 3.5,
        CharacterClass.KNIGHT   : 2,
        CharacterClass.ASSASSIN : 3,
        CharacterClass.ARCHER   : 3.1,
        CharacterClass.MAGE     : 3.1,
        CharacterClass.VALKYRIE : 4,
        CharacterClass.TESTCHAR : 5,
    }

    # Sort the characters by priority, but add a bit of randomness
    chars.sort(key=lambda c: priority[c.type] + random.gauss(0,0.1))
    char = chars[0]

    # Calculate and return the best move for the chosen character
    return get_best_move_for_character(game, char, player_color)



def get_best_move_for_character(game, char, player_color):
    '''
    Calculates and returns the best move the character can do.
    '''
    # Collect all possible moves here
    #possible_moves = []
    #possible_moves.append(Move( char.get_square(), char.get_square(), None, 'p', None ))

    player = game.get_player(player_color)
    enemy = game.get_blue_player() if player_color == PlayerColor.RED else game.get_red_player()

    # Compute the threat boards for both player and their enemy
    player_threat_board = construct_player_threat_board(game, player)
    enemy_threat_board  = construct_player_threat_board(game, enemy)

    init_tmp_stats(game)
    reset_tmp_stats(game)

    original_square = char.get_square()

    best_move, best_value = None, -math.inf

    # Loop through all possible squares and generate the all possible moves
    for square in char.get_legal_squares():

        # Move to the square in question
        move = Move( char.get_square(), square, None, 'p', None )
        move.value = apply_candidate_move_4(game, char, move, player.color, player_threat_board, enemy_threat_board)
        #possible_moves.append(move)
        if move.value.get() > best_value:
            best_move, best_value = move, move.value.get()

        # Check value for each attack from this square
        attack_targets = [(target_square, att.type) for att in char.get_attacks() for target_square in char.define_attack_targets(square, att.get_range()[1], True) ]
        for attack_target, attack_type in attack_targets:
            #possible_moves.append( Move( char.get_square(), square, attack_target, 'a', attack_type ) )
            move = Move( char.get_square(), square, attack_target, 'a', attack_type )
            move.value = apply_candidate_move_4(game, char, move, player.color, player_threat_board, enemy_threat_board)
            if move.value.get() > best_value:
                best_move, best_value = move, move.value.get()

        # Check value for each skill from this square
        activated_skills = [sk for sk in char.skills if sk.type in skill.Skill.active_skills]
        skill_targets  = [(target_square, sk.type) for sk in activated_skills for target_square in char.define_attack_targets(square, sk.get_range(), sk.targets_enemy()) ]
        for skill_target, skill_type in skill_targets:
            #possible_moves.append( Move( char.get_square(), square, skill_target, 's', skill_type ) )
            move = Move( char.get_square(), square, skill_target, 's', skill_type )
            move.value = apply_candidate_move_4(game, char, move, player.color, player_threat_board, enemy_threat_board)
            if move.value.get() > best_value:
                best_move, best_value = move, move.value.get()
    
    # Move back to original square and check its value
    # This should be applicable even without any legal moves -> should always be at least one legal move (passing the turn)
    move = Move( char.get_square(), original_square, None, 'p', None )
    move.value = apply_candidate_move_4(game, char, move, player.color, player_threat_board, enemy_threat_board)
    if move.value.get() > best_value:
        best_move, best_value = move, move.value.get()

    '''
    best_move = possible_moves[0]
    best_value = -math.inf

    for move in possible_moves:
        #game_copy = copy.deepcopy(game)
        #new_char = game_copy.board.get_piece(char.get_square())
        try:
            value = apply_candidate_move_4(game, char, move, player.color, player_threat_board, enemy_threat_board)
        except IllegalMoveException:
            continue
        #value = get_heuristic_board_value_4(game_copy, new_char, player.color, player_threat_board, enemy_threat_board)
        move.value = value
        #print(move)
        if value.get() > best_value:
            best_move = move
            best_value = value.get()

    #print(f"copy: {copy_time}, apply: {apply_time}, heur: {heur_time}")
    '''
    best_move.source_square = original_square
    print("Best:")
    print(best_move)
    return best_move

def init_tmp_stats(game):
    for char in game.get_blue_player().get_characters():
        char.tmp_hp = 0
        char.original_stats = dict(char.stats)
        char.original_range = char.range
    for char in game.get_red_player().get_characters():
        char.tmp_hp = 0
        char.original_stats = dict(char.stats)
        char.original_range = char.range

def reset_tmp_stats(game):
    for char in game.get_blue_player().get_characters():
        char.tmp_hp = 0
        char.stats = dict(char.original_stats)
        char.range = char.original_range
    for char in game.get_red_player().get_characters():
        char.tmp_hp = 0
        char.stats = dict(char.original_stats)
        char.range = char.original_range

def calculate_tmp_hp(char):
    hp = char.get_hp() + char.tmp_hp
    hp = min(hp, char.get_maxhp())
    hp = max(hp, 0)
    return hp

def get_winner(game):
    if game.get_winner() is not None:
        return game.get_winner()
    n_blue_chars = len([char for char in game.get_blue_player().get_characters() if calculate_tmp_hp(char) > 0])
    n_red_chars = len([char for char in game.get_red_player().get_characters() if calculate_tmp_hp(char) > 0])
    if n_blue_chars == 0:
        return PlayerColor.RED
    elif n_red_chars == 0:
        return PlayerColor.BLUE

def is_player_won():
    pass

def apply_candidate_move_4(game, char, move, player_color, player_threat_board, enemy_threat_board):
    '''
    Function behaves like game.apply_move, but deals average damage instead of random :D
    '''
    reset_tmp_stats(game)

    # Move character
    game.board.move_char(char, move.destination_square, verbose=False)
    
    # Attack
    if move.action_type == 'a':
        # Find the attack from the character which matches the chosen one
        attack = char.get_attack_by_id(move.action_id)
        enemy_char = game.board.get_piece(move.target_square)
        dmg = attack.calculate_probable_damage(enemy_char)
        enemy_char.tmp_hp -= dmg
        value = get_heuristic_board_value_4(game, char, player_color, player_threat_board, enemy_threat_board)

    # Skill
    # A bit ugly, but hard-coded logic for each activated skill
    # Could be possible to enhance in future
    elif move.action_type == 's':
        if move.action_id == SkillType.HEAL:
            target_char = game.board.get_piece(move.target_square)
            if target_char is None:
                target_char = char
            target_char.tmp_hp += round(char.get_stats()[Stats.MAGIC] / 2)
            value = get_heuristic_board_value_4(game, char, player_color, player_threat_board, enemy_threat_board)
            if target_char.get_hp() == target_char.get_maxhp(): # Should not matter, but more clean to not heal characters with full hp
                value = Value("Healing character with full HP", -math.inf)

        elif move.action_id == SkillType.RAISEDEF:
            # These should in future be somehow fetched from the skill itself rather than hard-coded here
            stats = {Stats.ATTACK: 0, Stats.DEFENSE: 4, Stats.MAGIC: 0,\
                        Stats.RESISTANCE: 3, Stats.SPEED: 0, Stats.EVASION: 0}
            skill = char.get_skill_by_id(move.action_id)
            all_squares = game.board.get_tiles_in_range(char.get_square(),skill.range)
            for square in all_squares:
                other_char = game.board.get_piece(square)
                if other_char != None:
                    owner = other_char.get_owner()
                    if owner.color == char.get_owner().color:
                        other_char.modify_stats(stats,0)
            value = get_heuristic_board_value_4(game, char, player_color, player_threat_board, enemy_threat_board)

        elif move.action_id == SkillType.RAISERNG:
            # These should in future be somehow fetched from the skill itself rather than hard-coded here
            stats = {Stats.ATTACK: 0, Stats.DEFENSE: 0, Stats.MAGIC: 0,\
                        Stats.RESISTANCE: 0, Stats.SPEED: 0, Stats.EVASION: 0}
            range_increase = 1
            skill = char.get_skill_by_id(move.action_id)
            all_squares = game.board.get_tiles_in_range(char.get_square(),skill.range)
            for square in all_squares:
                other_char = game.board.get_piece(square)
                if other_char != None:
                    owner = other_char.get_owner()
                    if owner.color == char.get_owner().color:
                        other_char.modify_stats(stats,range_increase)
            value = get_heuristic_board_value_4(game, char, player_color, player_threat_board, enemy_threat_board)

        elif move.action_id == SkillType.WISH:
            # These should in future be somehow fetched from the skill itself rather than hard-coded here
            stats = {Stats.ATTACK: 1, Stats.DEFENSE: 1, Stats.MAGIC: 1,\
                        Stats.RESISTANCE: 0, Stats.SPEED: 0, Stats.EVASION: 0}
            range_increase = 0
            skill = char.get_skill_by_id(move.action_id)
            target_char = game.board.get_piece(move.target_square)
            if target_char is None:
                value = Value("Wish on empty square", -math.inf)
            elif target_char.get_owner().color != char.get_owner().color:
                value =Value("Wish on enemy char", -math.inf)
            elif not target_char.is_ready():
                value = Value("Wish on non-moven char", -math.inf)
            elif SkillType.WISH in target_char.get_skills():
                value = Value("Wish on another player with wish", -math.inf)
            else:
                target_char.modify_stats(stats, range_increase)
                target_char.ready = False
                char.ready = True
                value = get_best_move_for_character(game, target_char, player_color).value
                target_char.ready = True
                char.ready = False

        else:
            game_copy = copy.deepcopy(game)
            new_char = game_copy.board.get_piece(char.get_square())
            skill = new_char.get_skill_by_id(move.action_id)
            game_copy.use_skill(new_char, move.target_square, skill, verbose=False)
            value = get_heuristic_board_value_4(game_copy, new_char, player_color, player_threat_board, enemy_threat_board)

    else:
        value = get_heuristic_board_value_4(game, char, player_color, player_threat_board, enemy_threat_board)

    #game.board.move_char(char, move.source_square, verbose=False)
    reset_tmp_stats(game)
    return value

