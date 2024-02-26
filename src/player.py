import random

class Player:
    
    def __init__(self, color):
        self.characters = []
        self.alive = True
        self.won = False    # Set to true if won by some other condition than killing all enemies
        self.lost = False   # Set to true if lost by some other condition than getting all characters killed
        self.vip = False    # Determines the type of game; if there's at least one vip, self.vip is True
        self.first = True   # True only on first turn.
        self.ai = False
        self.color=color
        
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

    def is_ai(self):
        return self.ai
    
    def set_vip(self):
        '''
        Sets the game to be vip game:
        - If vip dies, it's controller dies
        - Only vip can seize goals
        '''
        self.vip = True
    
    def new_turn(self):
        '''
        Initialized all characters for new turn.
        Also on first turn adds skills to eveyone if it is a vip game.
        '''
        for char in self.characters:
            char.new_turn()

        
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


class Human(Player):
    '''
    Player controlled by a human player
    '''
    def __init__(self, color):
        Player.__init__(self, color)
        self.ai = False
        

class AI(Player):
    '''
    Player controlled by an AI
    '''
    def __init__(self, color):
        Player.__init__(self, color)
        self.ai = True
        
    def make_turn(self):
        not_ready = []
        for char in self.characters:
            if not char.is_ready():
                not_ready.append(char)
                
        size = len(not_ready)
        next = random.randint(0,size-1)
        char = not_ready[next]
        char.ai_make_turn()


def create_new_player(color,ai_controlled):
    '''
    Creates and returns a Player character based on whether a player or AI controls it.
    @param player_controlled: True if a human controls the player, False if it is controlled by AI
    '''
    if ai_controlled:
        return AI(color=color)
    else:
        return Human(color=color)