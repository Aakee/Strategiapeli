'''
The source class of the game.
Holds all vital information.
'''
from game_errors import IllegalMoveException
from human import Human
from ai import AI
from board import Board

class Game:
    
    def __init__(self):
        self.board      = Board()  # Board object
        self.human      = Human()  # Human player
        self.ai         = AI()     # Computer player

        self.capture    = True
        self.mode       = 'dm'
        self.vip        = False
        self.init_turns = False
        self.turns      = False
        self.spawn      = 0

        self.whose_turn = self.human


    def move_character(self, char, target_coordinates):
        if char.get_owner() != self.whose_turn or char.is_ready():
            return
        self.board.move_char(char, target_coordinates)

    def use_attack(self, char, target_coordinates, attack):
        if char.get_owner() != self.whose_turn or char.is_ready():
            return
        char.attack(attack, target_coordinates)
        char.set_ready()

    def use_skill(self, char, target_coordinates, skill):
        if char.get_owner() != self.whose_turn or char.is_ready():
            return
        char.attack(skill, target_coordinates)
        char.set_ready()

    def ai_make_turn(self):
        self.ai.make_turn()

    def end_turn(self):
        player = self.whose_turn
        player.end_turn()

    def change_turn(self):
        if self.whose_turn.is_ready():
            self.whose_turn.set_all_not_ready()
            self.whose_turn = self.human if self.whose_turn == self.ai else self.ai
            self.whose_turn.new_turn()
            return True
        return False

    def is_player_ready(self):
        if self.whose_turn.is_ready():
            return True
        return False

    def is_game_over(self):
        return not self.human.is_alive() or not self.ai.is_alive() or self.human.is_won() or self.ai.is_won()
    
    def get_winner(self):
        if self.human.is_won():
            return 1
        if self.ai.is_won():
            return -1
        if not self.human.is_alive():
            return -1
        if not self.ai.is_alive():
            return 1
        return 0

    def set_board(self, board):
        self.board = board
        
    def set_human(self,human):
        self.human = human
        
    def set_ai(self,ai):
        self.ai = ai
        
    def get_board(self):
        return self.board
    
    def get_human(self):
        return self.human
    
    def get_ai(self):
        return self.ai
    
    def get_io(self):
        return self.io
    
    def get_capture(self):
        return self.capture
    
    def set_gui(self,gui):
        self.gui = gui
        
    def get_gui(self):
        return self.gui
    
    def set_vip(self):
        self.vip = True
        
    def is_vip(self):
        return self.vip
    
    def set_mode(self, mode):
        self.mode = mode
        
    def get_mode(self):
        return self.mode
        
    def set_turns(self, turns):
        self.init_turns = turns
        self.turns      = turns
        
    def next_turn(self,first_turn):
        if first_turn:
            return
        if self.init_turns > 0:
            self.turns -= 1
        if self.init_turns < 0:
            self.turns += 1
        
    def get_init_turns(self):
        return self.init_turns
        
    def get_turns(self):
        return self.turns
        
    def set_spawn(self, spawn):
        self.spawn = spawn
        
    def get_spawn(self):
        return self.spawn