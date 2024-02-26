'''
Module contains class Move, which is a standardized way of conveying character turn
information.
'''

class Move:

    def __init__(self, source_square, destination_square, target_square, action_type=None, action_id=None) -> None:
        
        self.source_square      = source_square
        self.destination_square = destination_square
        self.target_square      = target_square
        self.action_type        = action_type
        self.action_id          = action_id
