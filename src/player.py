from tile import Tile
from character import Character

class Player:
    
    def __init__(self, game):
        self.game = game
        self.characters = []
        self.backpack = {}
        self.alive = True
        self.won = False    # Set to true if won by some other condition than killing all enemies
        self.lost = False   # Set to true if lost by some other condition than getting all characters killed
        self.vip = False    # Determines the type of game; if there's at least one vip, self.vip is True
        self.first = True   # True only on first turn.
        
                
        
    def is_alive(self):
        '''
        Returns the value of self.alive, i.e. if the player is
        alive or not.
        '''
        if len(self.characters) == 0:
            self.alive = False
        if self.lost == True:
            self.alive = False
        return self.alive
    
    def is_ready(self):
        '''
        Tells if player has already moven all their characters.
        @return: True if player is ready, False if not
        '''
        ready = True
        for char in self.characters:
            if not char.is_ready():
                ready = False
        return ready
    
    def add_character (self, char):
        self.characters.append(char)
        self.alive = True
        
    def remove_character (self, char):
        self.characters.remove(char)
        if len(self.characters) == 0:
            self.alive = False
            
    def get_characters(self):
        return self.characters
    
    def is_won(self):
        return self.won
    
    def set_lost(self):
        self.lost = True
    
    def set_vip(self):
        '''
        Sets the game to be vip game:
        - If vip dies, it's controller dies
        - Only vip can seize goals
        '''
        self.vip = True
        self.game.set_vip()
    
    def new_turn(self):
        '''
        Initialized all characters for new turn.
        Also on first turn adds skills to eveyone if it is a vip game.
        '''
        if self.game.is_vip() and self.first:
            for char in self.characters:
                char.add_vip()
             
        for char in self.characters:
            char.new_turn()
            tile = self.game.get_board().get_tile(char.get_square())
            if tile.get_type() == Tile.GOAL and self == self.game.get_human() and not self.game.is_vip():
                self.won = True
            elif tile.get_type() == Tile.GOAL and self == self.game.get_human():
                if char.get_type() == Character.VIP:
                    self.won = True
                elif char.get_carrying() != None:
                    if char.get_carrying().get_type() == Character.VIP:
                        self.won = True
                  
        if self.game.get_init_turns():
            if (self == self.game.get_human() and self.game.get_init_turns() > 0) or (self == self.game.get_ai() and self.game.get_init_turns() < 0):
                self.game.next_turn(self.first and self == self.game.get_human())
                if self.game.get_turns() == 0:
                    self.won = True
            
                
                    
        self.first = False
        
    def end_turn(self):
        '''
        Player ends their turn, even if there are characters that haven't moven
        '''
        for char in self.characters:
            char.set_ready()
                
    
    def set_all_not_ready(self):
        '''
        Sets all characters ready-state False. Useful if wanting
        to draw original sprites to map instead of grey.
        '''
        for char in self.characters:
            char.set_not_ready()    