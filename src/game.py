'''
The source class of the game.
Holds all vital information.
'''
from game_enums import PlayerColor
import player
from board import Board
import ai.game_ai_1 as game_ai_1
import ai.game_ai_2 as game_ai_2
import ai.game_ai_3 as game_ai_3
import ai.game_ai_4 as game_ai_4
import copy

class Game:
    
    def __init__(self, blue_controlled_by_ai=False, red_controlled_by_ai=True):
        self.board      = Board()  # Board object
        self.players    = {  
                            PlayerColor.BLUE : player.create_new_player(color=PlayerColor.BLUE, ai_controlled=blue_controlled_by_ai, ai_func=game_ai_4.get_move),
                            PlayerColor.RED  : player.create_new_player(color=PlayerColor.RED,  ai_controlled=red_controlled_by_ai,  ai_func=game_ai_4.get_move)
                          }
        self.whose_turn = PlayerColor.BLUE


    def move_character(self, char, target_coordinates, verbose=True):
        if char.get_owner() != self.get_current_player() or char.is_ready():
            return
        self.board.move_char(char, target_coordinates, verbose=verbose)

    def use_attack(self, char, target_coordinates, attack, verbose=True):
        if char.get_owner() != self.get_current_player() or char.is_ready():
            return
        char.attack(attack, target_coordinates, verbose=verbose)

    def use_skill(self, char, target_coordinates, skill, verbose=True):
        if char.get_owner() != self.get_current_player() or char.is_ready():
            return
        char.attack(skill, target_coordinates, verbose=verbose)

    def pass_character_turn(self, char):
        if char.get_owner() != self.get_current_player() or char.is_ready():
            return
        char.set_ready()

    def ai_make_turn(self, verbose=True):
        if self.players[self.whose_turn].is_ai():
            game_copy = copy.deepcopy(self)
            move = self.get_current_player().ai_func(game_copy, self.whose_turn)
            self.apply_move(move, verbose=verbose)

    def apply_move(self, move, verbose=True):
            
        # Move character
        char = self.board.get_piece(move.source_square)
        self.move_character(char, move.destination_square, verbose=verbose)

        # Attack
        if move.action_type == 'a':
            # Find the attack from the character which matches the chosen one
            attack = char.get_attack_by_id(move.action_id)
            self.use_attack(char, move.target_square, attack, verbose=verbose)

        # Skill
        elif move.action_type == 's':
            # Find the attack from the character which matches the chosen one
            skill = char.get_skill_by_id(move.action_id)
            self.use_skill(char, move.target_square, skill, verbose=verbose)

        else:
            char.set_ready()


    def end_turn(self):
        if not self.get_current_player().is_ai():
            self.get_current_player().end_turn()

    def change_turn(self):
        if self.players[self.whose_turn].is_ready():
            self.players[self.whose_turn].set_all_not_ready()
            self.whose_turn = PlayerColor.BLUE if self.whose_turn == PlayerColor.RED else PlayerColor.RED
            self.players[self.whose_turn].new_turn()
            return True
        return False

    def is_player_ready(self):
        if self.players[self.whose_turn].is_ready():
            return True
        return False

    def get_player(self, color: PlayerColor):
        return self.players[color]
    
    def get_blue_player(self):
        return self.players[PlayerColor.BLUE]
    
    def get_red_player(self):
        return self.players[PlayerColor.RED]
    
    def get_current_player(self):
        return self.players[self.whose_turn]
    
    def is_game_over(self):
        return not self.get_blue_player().is_alive() or not self.get_red_player().is_alive() or self.get_blue_player().is_won() or self.get_red_player().is_won()
    
    def get_winner(self):
        if self.get_blue_player().is_won():
            return PlayerColor.BLUE
        if self.get_red_player().is_won():
            return PlayerColor.RED
        if not self.get_blue_player().is_alive():
            return PlayerColor.RED
        if not self.get_red_player().is_alive():
            return PlayerColor.BLUE
        return None

    def set_board(self, board):
        self.board = board
        
    def get_board(self):
        return self.board
