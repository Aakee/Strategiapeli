'''
Module contains class Move, which is a standardized way of conveying character turn
information.
'''

class Value:
    '''
    Class saves different aspects of the board heuristic values.
    Useful for dewbugging.
    '''
    def __init__(self, title=None, val=None) -> None:
        self.sections = []
        if not title is None and not val is None:
            self.add_section(title=title, val=val)

    def add(self,title,val):
        self.sections.append([title, val])

    def get(self):
        return round(sum([val for title, val in self.sections]), 2)
    
    def __iadd__(self, other):
        if type(other) is float:
            self.add('', other)
        else:
            self.add(other[0], other[1])
        return self
    
    def __isub__(self, other):
        if type(other) is float:
            self.add('', -other)
        else:
            self.add(other[0], -other[1])
        return self
    
    def __repr__(self) -> str:
        return '\n\t' + ''.join([f"{title}: {round(val,2)}, " for title, val in self.sections]) + f"\n\tTotal: {self.get()}"



class Move:
    '''
    Describes one action on the board: movement, and from there using an attack/skill/passing the turn.
    '''

    def __init__(self, source_square, destination_square, target_square, action_type=None, action_id=None, value=0) -> None:
        
        self.source_square      = source_square
        self.destination_square = destination_square
        self.target_square      = target_square
        self.action_type        = action_type           # 'a' for attack, 's' for skill, 'p' for passing the turn
        self.action_id          = action_id             # Attack or Skill id, or None
        self.value              = value

    def __repr__(self) -> str:
        return f"MOVE: Source: {self.source_square}, destination: {self.destination_square}, target:{self.target_square}, type: {self.action_type}, id: {self.action_id}, value: {self.value}"