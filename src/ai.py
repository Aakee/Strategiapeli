from player import Player
from CharacterData import *
import random

class AI(Player):

    def __init__(self,game):
        Player.__init__(self, game)
        
        
    def make_turn(self):
        not_ready = []
        for char in self.characters:
            if not char.is_ready():
                not_ready.append(char)
                
        size = len(not_ready)
        next = random.randint(0,size-1)
        char = not_ready[next]
        char.ai_make_turn()
        a = 2
        
    def spawn_enemy(self):
        '''
        Spawns a random enemy to the map.
        '''
        
        spawn = self.game.get_spawn()
        
        rng = random.randint(1,100)
        if spawn < rng:
            return
        
        ready = False
        effort = 0 # How many times ai has tried to find a possible square
        
        while not ready:
            effort += 1
            if effort >= 20:
                return # In case there are no possible squares
            
            ready = True
            x = random.randint(0,self.game.get_board().get_width()-1)
            y = random.randint(0,self.game.get_board().get_height()-1)
            
            if self.game.get_board().get_tile((x,y)).get_endable() != True:
                ready = False
            
            if self.game.get_board().get_piece((x,y)) != None:
                ready = False
            
            player_chars = self.game.get_human().get_characters()
            for player_char in player_chars:
                if self.game.get_board().distance_to((x,y),player_char.get_square()) < 4:
                    ready = False
                    
        rng = random.randint(1,9)
        if rng <= 1:
            char = Knight(self.game,self)
        elif rng <= 3:
            char = Archer(self.game,self)
        elif rng <= 5:
            char = Mage(self.game,self)
        elif rng <= 7:
            char = Mage(self.game,self)
        elif rng <= 8:
            char = Cleric(self.game,self)
        elif rng <= 9:
            char = Valkyrie(self.game,self)
            
        self.game.get_board().set_object((x,y),char)
        print("Vihollisen {} ilmestyi ruutuun ({},{})!".format(char.get_name(),x+1,y+1))