'''
The source class of the game.
Holds all vital information.
'''
class Game:
    
    def __init__(self):
        self.gui        = False
        self.capture    = True
        self.mode       = 'dm'
        self.vip        = False
        self.init_turns = False
        self.turns      = False
        self.spawn      = 0

        self.board      = None  # Board object
        self.human      = None  # Human player
        self.ai         = None  # Computer player

        self.whose_turn = None

    
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
