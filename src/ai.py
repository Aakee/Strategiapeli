from player import Player
import random

class AI(Player):

    def __init__(self):
        Player.__init__(self)
        
        
    def make_turn(self):
        not_ready = []
        for char in self.characters:
            if not char.is_ready():
                not_ready.append(char)
                
        size = len(not_ready)
        next = random.randint(0,size-1)
        char = not_ready[next]
        char.ai_make_turn()
