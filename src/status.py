'''
Classes to represent various status effects characters can have
'''

class Status:
    '''
    Base class for statuses
    '''
    def __init__(self, char) -> None:
        self.name = ""
        self.flavor = ""
        self.harmful = False
        self.max_duration = 0
        self.duration_used = 0
        self.char = char

    def get_stats(self):
        return self.char.get_stats()
    
    def new_turn(self):
        return


class Fortify(Status):
    '''
    Enhances character's defensive stats.
    '''
    def __init__(self) -> None:
        super().__init__()
        self.name = "Fortify"
        self.flavor = "Enhances defense and resistance"
        self.max_duration = 1