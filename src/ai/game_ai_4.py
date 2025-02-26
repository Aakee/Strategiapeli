'''
Module has a set of AI functions to run.
These functions are curently deemed to be the best.
'''

import random
import skill
from game_enums import CharacterClass, PlayerColor, SkillType, Stats
from move import Move, Value
import game_errors

import copy
import math
import random
import statistics
import itertools

# Priority: which characters move first
PRIORITY = {
    CharacterClass.CLERIC   : 3.5,
    CharacterClass.KNIGHT   : 2,
    CharacterClass.ASSASSIN : 3,
    CharacterClass.ARCHER   : 3.1,
    CharacterClass.MAGE     : 3.1,
    CharacterClass.VALKYRIE : 4,
    CharacterClass.TESTCHAR : 5,
}

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
    #enemy = game.get_blue_player() if player_color == PlayerColor.RED else game.get_red_player()
    
    chars = [char for char in player.get_characters() if not char.is_ready() ]
    if len(chars) == 0:
        return

    # Sort the characters by priority, but add a bit of randomness
    chars.sort(key=lambda c: PRIORITY[c.type] + random.gauss(0,0.1))
    char = chars[0]

    # Calculate and return the best move for the chosen character
    return get_best_move_for_character(game, char, player_color)


def get_best_move_for_character(game, char, player_color):
    '''
    Calculates and returns the best move the character can do.
    '''
    player = game.get_player(player_color)
    enemy = game.get_blue_player() if player_color == PlayerColor.RED else game.get_red_player()

    # Compute the threat boards for both player and their enemy
    player_threat_board = construct_player_threat_board(game, player)
    enemy_threat_board  = construct_player_threat_board(game, enemy)

    # Set up the tmp stats used by the heuristics function
    original_square = char.get_square()
    prepare_game_copy(game)

    # Initialize the current best move
    best_move, best_value = None, -math.inf

    # Loop through all possible squares and generate the all possible moves
    for square in char.get_legal_squares():

        # Move to the square in question
        move = Move( char.get_square(), square, None, 'p', None )
        move.value = apply_candidate_move(game, char, move, player.color, player_threat_board, enemy_threat_board)
        if move.value.get() > best_value:
            best_move, best_value = move, move.value.get()

        # Check value for each attack from this square
        attack_targets = [(target_square, att.type) for att in char.get_attacks() for target_square in char.define_attack_targets(square, att.get_range()[1], True) ]
        for attack_target, attack_type in attack_targets:
            move = Move( char.get_square(), square, attack_target, 'a', attack_type )
            if is_redundant_move(game, char, move):
                continue
            move.value = apply_candidate_move(game, char, move, player.color, player_threat_board, enemy_threat_board)
            if move.value.get() > best_value:
                best_move, best_value = move, move.value.get()

        # Check value for each skill from this square
        activated_skills = [sk for sk in char.get_full_skills() if sk.type in skill.Skill.active_skills]
        skill_targets  = [(target_square, sk.type) for sk in activated_skills for target_square in char.define_attack_targets(square, sk.get_range(), sk.targets_enemy()) ]
        for skill_target, skill_type in skill_targets:
            move = Move( char.get_square(), square, skill_target, 's', skill_type )
            if is_redundant_move(game, char, move):
                continue
            move.value = apply_candidate_move(game, char, move, player.color, player_threat_board, enemy_threat_board)
            if move.value.get() > best_value:
                best_move, best_value = move, move.value.get()
    
    # Move back to original square and check its value
    # This should be applicable even without any legal moves -> should always be at least one legal move (passing the turn)
    move = Move( char.get_square(), original_square, None, 'p', None )
    move.value = apply_candidate_move(game, char, move, player.color, player_threat_board, enemy_threat_board)
    if move.value.get() > best_value:
        best_move, best_value = move, move.value.get()

    # Because of the logic used, the character's source square in Move can be pretty much any square.
    # Thus, determine that it needs to be moved from its original square
    best_move.source_square = original_square

    # Return best move
    return best_move


def is_redundant_move(game, char, move):
    '''
    Function determines if a move is redundant in such way that there is no point in doing that.
    '''
    # Attack: an attack is redundant if a) the maximum damage it could do is zero, or b) the user has strictly better
    # attacks for the situation
    if move.action_type == 'a':
        attack      = char.get_attack_by_id(move.action_id)
        target_char = game.board.get_piece(move.target_square)
        max_dmg     = attack.calculate_max_damage(target_char)
        accuracy    = attack.calculate_accuracy(target_char)
        # Skip if can't deal any damage
        if max_dmg <= 0:
            return True
        for other_attack in char.get_attacks():
            if other_attack.type == attack.type:
                continue
            other_attack_max_range  = other_attack.get_range()[1]
            if abs(char.get_square()[0]-target_char.get_square()[0]) + abs(char.get_square()[1]-target_char.get_square()[1]) > other_attack_max_range:
                continue
            other_attack_accuracy   = attack.calculate_accuracy(target_char)
            other_attack_max_damage = attack.calculate_max_damage(target_char)
            # Skip if there is another, strictly better attack for this situation
            if other_attack_accuracy > accuracy and other_attack_max_damage >= max_dmg:
                return True
            if other_attack_accuracy >= accuracy and other_attack_max_damage > max_dmg:
                return True
            if other_attack_accuracy > accuracy and other_attack_max_damage >= target_char.tmp_hp:
                return True
            
    if move.action_type == 's':
        # Skip if aoe that targets allies if the target char is not the char itself (the other variants
        # have the exact same effect)
        sk = char.get_skill_by_id(move.action_id)
        if sk.affect_all and not sk.target_enemy:
            target_char = game.board.get_piece(move.target_square)
            if target_char != char:
                return True
        # Skip heal if it would not heal anything
        if move.action_id == SkillType.HEAL:
            target_char = game.board.get_piece(move.target_square)
            if target_char is None:
                target_char = char
            if target_char.hp >= target_char.get_maxhp():
                return True

    return False


def apply_candidate_move(game, char, move, player_color, player_threat_board, enemy_threat_board):
    '''
    Function applies the given move, but has a few key differences to game.apply_move:
    - All changes to HP is made to char.tmp_hp rather than char.hp, meaning that characters cannot die even if their (tmp) hp would drop to zero
    - Heuristic value of the board state after the action is calculated and returned
    - All changes to stats and tmp_hp are reseted afterwards
    - Character is moved back to the original square afterwards.
    '''
    #reset_tmp_stats(game)
    value = None
    bonus_value = 0

    # Move character
    game.board.move_char(char, move.destination_square, verbose=False)
    
    # Attack
    if move.action_type == 'a':
        # Find the attack from the character which matches the chosen one
        attack      = char.get_attack_by_id(move.action_id)
        target_char = game.board.get_piece(move.target_square)
        #dmg         = attack.calculate_max_damage(target_char)
        #accuracy    = attack.calculate_accuracy(target_char)
        #miss       = random.randint(1,100)
        damage      = attack.calculate_damage(target_char, verbose=False)
        target_char.remove_hp(damage, verbose=False)
        #if miss <= accuracy:
        #    calculate_tmp_hp(target_char, -dmg)
        accuracy    = attack.calculate_accuracy(target_char)
        bonus_value += accuracy/100

    # Skill
    elif move.action_type == 's':
        # If no characters in the target square: act if the chosen target was the moved character itself
        if game.board.get_piece(move.target_square) is None:
            move.target_square = move.destination_square
        
        # Use the skill. If it is an illegal move, return a value of -inf.
        sk = char.get_skill_by_id(move.action_id)
        try:
            sk.use(move.target_square, verbose=False)
        except game_errors.IllegalMoveException:
            reset_game_copy(game)
            value = Value("Illegal move", -math.inf)
            return value
    
    # Calculate the heuristic value
    value = get_heuristic_board_value(game, char, player_color, player_threat_board, enemy_threat_board)
    value += ("Bonus value", bonus_value)

    # Move back to original square and reset temporary stats
    game.board.move_char(char, move.source_square, verbose=False)
    reset_game_copy(game)
    return value


def get_heuristic_board_value(game, moven_char, player_color, player_threat_board, enemy_threat_board):
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
    value += ( 'Characters',     2*sum([ BASE_VALUES[char.type] * (1 + char.hp / char.get_maxhp()) for char in player.get_characters() if char.hp > 0]) )
    value -= ( 'En. characters', 2*sum([ BASE_VALUES[char.type] * (1 + char.hp / char.get_maxhp()) for char in enemy .get_characters() if char.hp > 0]) )

    # Points for advantages
    player_advantage    = statistics.mean([ ADVANTAGES[char.type][enemy_char.type] * (0.8 + 0.2*       char.hp /       char.get_maxhp()) for char in player.get_characters() for enemy_char in enemy.get_characters() if char.hp > 0 and enemy_char.hp > 0])
    enemy_advantage     = statistics.mean([ ADVANTAGES[enemy_char.type][char.type] * (0.8 + 0.2* enemy_char.hp / enemy_char.get_maxhp()) for char in player.get_characters() for enemy_char in enemy.get_characters() if char.hp > 0 and enemy_char.hp > 0]) 
    
    value += ( 'PlAdv', player_advantage )
    value -= ( 'EnAdv', enemy_advantage )

    # Prefer positions where characters are close to each other
    avedist_allies = statistics.mean([PREFER_ALLY_COMPANY[moven_char.type]*math.tanh( max(0, game.board.distmap.distance_between_characters(moven_char, other)-2) / (game.board.height+game.board.width) ) for other in player.get_characters() if other.hp > 0])
    value -= ('Allies close', 2*avedist_allies )

    # To avoid games where no player does anything, slightly favor positions where characters are closer to enemies
    avedist_enemies = statistics.mean([ PREFER_ENEMY_COMPANY[moven_char.type]*math.tanh( max(0, game.board.distmap.distance_between_characters(moven_char, other)-4) / (game.board.height+game.board.width) ) for other in enemy.get_characters() if other.hp > 0])
    value -= ('Enemies close', max(3,(player_advantage/nof_player_characters)/(enemy_advantage/nof_enemy_characters))*avedist_enemies )

    # Very slightly prefer positions where characters total stats are higher (mainly to support using raise range and such)
    value += ('PlStats', 0.01*statistics.mean([stat_val for char in player.get_characters() for stat, stat_val in char.get_stats().items()]) )
    value -= ('EnStats', 0.01*statistics.mean([stat_val for char in enemy .get_characters() for stat, stat_val in char.get_stats().items()]) )

    # Avoid dangerous squares
    danger_value = 0
    for char in player.get_characters():

        # Probable (expected) damage, where key is the attacker and item is the damage
        prob_dmg_dict   = get_probable_enemy_damage(game, enemy_threat_board, char)
        prob_dmg        = sum([val for key, val in prob_dmg_dict.items()])

        # Same for max damage
        max_dmg_dict    = get_max_enemy_damage(game, enemy_threat_board,char)
        max_dmg         = sum([val for key, val in max_dmg_dict.items()])

        # Enemies that can attack to the character's square
        dmg_enemies     = [key for key in prob_dmg_dict]

        max_advantage    = max([ADVANTAGES[char.type][enemy_char.type] for enemy_char in dmg_enemies]) if len(dmg_enemies) > 0 else 0
        max_disadvantage = max([ADVANTAGES[enemy_char.type][char.type] for enemy_char in dmg_enemies]) if len(dmg_enemies) > 0 else 0
        n_could_be_killed = len([enemy_char for enemy_char in dmg_enemies if enemy_char.hp < sum([val for key, val in get_probable_enemy_damage(game,player_threat_board, enemy_char, disregard_moven=True).items() ])]) if len(dmg_enemies) > 0 else 0

        fact = 1    # Base multiplier

        # Multiplier affected by the advantage/disadvantages, and if the attacking chars could be killed this turn
        if len(prob_dmg_dict) > 0:
            fact = 0.1* (max_disadvantage + 0.001) / (max_advantage + 0.001)
            fact = fact * ( len(prob_dmg_dict) - n_could_be_killed ) / len(prob_dmg_dict)

        # Very dangerous if enemy is expected to kill here
        if prob_dmg >= char.hp:
            danger_value += BASE_VALUES[char.type] * fact / nof_player_characters
        # Quite dangerous if the enemy can kill with a bit of luck
        elif max_dmg >= char.hp:
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


def get_max_enemy_damage(game, threat_board, char, disregard_moven=False):
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


def get_probable_enemy_damage(game, threat_board, char, disregard_moven=False):
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


def prepare_game_copy(game):
    '''
    Prepares the game copy to be used with the AI by saving the characters' initial stats and modifying their 'die'-methods
    such as they cannot really die.
    '''
    class TmpGameHandler:
        def __init__(self, char):
            self.char = char
        def die_dummy(self, verbose=False):
            if self.char.hp < 0:
                self.char.hp = 0
            self.char.alive = False
            
    for char in game.get_blue_player().get_characters() + game.get_red_player().get_characters():
        char.original_hp        = char.hp
        char.original_skills    = list(char.get_full_skills())
        char.original_ready     = char.ready
        char.original_alive     = char.alive
        tmp_handler = TmpGameHandler(char)
        char.die = tmp_handler.die_dummy

def reset_game_copy(game):
    '''
    Resets the given game copy to its original state. The 'prepare_game_copy' function must have been called earlier.
    '''
    for char in game.get_blue_player().get_characters() + game.get_red_player().get_characters():
        char.hp        = char.original_hp
        char.skills    = list(char.original_skills)
        char.ready     = char.original_ready
        char.alive     = char.original_alive


def get_winner(game):
    '''
    Returns the winner of the game is game has ended, or None if no winner has yet been determined.
    Determines whether the characters are dead or not based on the tmp hp rather than real hp.
    '''
    if game.get_winner() is not None:
        return game.get_winner()
    n_blue_chars = len([char for char in game.get_blue_player().get_characters() if char.hp > 0])
    n_red_chars  = len([char for char in game.get_red_player().get_characters()  if char.hp > 0])
    if n_blue_chars == 0:
        return PlayerColor.RED
    elif n_red_chars == 0:
        return PlayerColor.BLUE
