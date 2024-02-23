from player import Player

class Human(Player):
    
    def __init__(self):
        Player.__init__(self)
        
    '''    
    def make_turn(self):
        ready = True
        for i in range(len(self.characters)):
            if not self.characters[i].is_ready():
                ready = False
                
        while not ready:
            coordinates = (0,0) # Gets coordinates from gui
            piece = self.game.get_board().get_object(coordinates)
            dst = (1,1) # From gui
            legal_squares = piece.define_legal_squares()
            if dst not in legal_squares:
                raise IllegalMoveException
            self.game.get_board().move_char(piece,dst)
            
            while True:
                action = [] # From gui
                break
            
            piece.set_ready()
            for i in range(len(self.characters)):
                if not self.characters[i].is_ready():
                    ready = False
    '''