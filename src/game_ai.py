'''
Module has functions for the AI to run.
'''

import random
import skill
from game_enums import CharacterClass, PlayerColor
from move import Move


def get_next_move(game, player_color: PlayerColor):

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