'''
The source class of the game.
Holds all vital information.
'''
from game_enums import PlayerColor
import player
from board import Board
import game_ai
from game_errors import IllegalMoveException
import copy

class Game:
    
    def __init__(self, blue_controlled_by_ai=True, red_controlled_by_ai=True):
        self.board      = Board()  # Board object
        self.players    = {  
                           PlayerColor.BLUE : player.create_new_player(color=PlayerColor.BLUE, ai_controlled=blue_controlled_by_ai),
                            PlayerColor.RED : player.create_new_player(color=PlayerColor.RED, ai_controlled=red_controlled_by_ai)
                          }
        self.whose_turn = PlayerColor.BLUE


    def move_character(self, char, target_coordinates):
        if char.get_owner() != self.get_current_player() or char.is_ready():
            return
        self.board.move_char(char, target_coordinates)

    def use_attack(self, char, target_coordinates, attack):
        if char.get_owner() != self.get_current_player() or char.is_ready():
            return
        char.attack(attack, target_coordinates)

    def use_skill(self, char, target_coordinates, skill):
        if char.get_owner() != self.get_current_player() or char.is_ready():
            return
        char.attack(skill, target_coordinates)

    def pass_character_turn(self, char):
        if char.get_owner() != self.get_current_player() or char.is_ready():
            return
        char.set_ready()

    def ai_make_turn(self):
        if self.players[self.whose_turn].is_ai():
            game_copy = copy.deepcopy(self)
            move = game_ai.get_ai_move_2(game_copy, self.whose_turn)
            print(game_ai.get_heuristic_board_value(game_copy, self.whose_turn))
            self.apply_move(move)

    def apply_move(self, move):
            
        # Move character
        char = self.board.get_piece(move.source_square)
        self.move_character(char, move.destination_square)

        # Attack
        if move.action_type == 'a':
            # Find the attack from the character which matches the chosen one
            attack = char.get_attack_by_id(move.action_id)
            self.use_attack(char, move.target_square, attack)

        # Skill
        elif move.action_type == 's':
            # Find the attack from the character which matches the chosen one
            skill = char.get_skill_by_id(move.action_id)
            self.use_skill(char, move.target_square, skill)

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
