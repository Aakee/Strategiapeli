'''
Functions to finds distances between to tiles in a board.
'''
import itertools
import queue
import skill


class DistanceMap:
    '''
    Class calculates and handles the distance between two squares.
    '''
    def __init__(self, board) -> None:
        self.build(board)

    def build(self, board):
        '''
        Method builds its distance maps, that is, distances between any two squares.
        '''
        self.maps = {}
        self.maps[None] = calculate_distances(board)
        movement_skills = skill.Skill.movement_skills
        for sk in movement_skills:
            self.maps[sk] = calculate_distances(board, movement_skills=[sk])

    def get_distance_with_skill(self, start, end, skill_id=None):
        '''
        Returns distance between two tiles when the character has a movement id with 'skill_id'.
        If skill_id=None, returns distance when no skills are applied.
        '''
        dist = self.maps[skill_id][coord2str(start)][coord2str(end)]
        if dist is None:
            dist = abs(start[0]-end[0]) + abs(start[1]-end[1])
        return dist
        
    def get_distance(self, char, start, end):
        '''
        Method returns distance between two squares when traversen by character 'char'.
        Takes possible movement skills into account.
        '''
        char_movement_skills = [sk for sk in char.get_skills() if sk in skill.Skill.movement_skills]
        min_dist = self.get_distance_with_skill(start, end, None)
        for sk in char_movement_skills:
            min_dist = min(min_dist, self.get_distance_with_skill(start, end, sk))
        return min_dist
    
    def distance_between_characters(self, first, second):
        '''
        Returns distance between two characters, that is, number of steps needed for character 'first'
        to reach character 'second'.
        '''
        return self.get_distance(first, first.get_square(), second.get_square())
    

def coord2str(coord):
    '''
    Transforms coordinates in format (x,y) into a string of format 'x,y'.
    '''
    return f"{coord[0]},{coord[1]}"

def str2coord(str):
    '''
    Transforms coordinates in a string of format 'x,y' into a tuple in format (x,y).
    '''
    splitted = str.split(',')
    return (int(splitted[0]), int(splitted[1]))


def calculate_distances(board, movement_skills=None):
    '''
    Function applies breadth-first search to find the distance of any two squares, when movement skills given in
    list 'movement_skills' is applied.
    Returns a dictionary 'distance_board' in following format:
        distance_board['x1,y1']['x2,y2']
        is the distance between squares (x1,y1) and (x2,y2).
    '''
    DIRECTIONS = ((0,1),(1,0),(0,-1),(-1,0))

    if movement_skills is None:
        movement_skills = []
    max_x = board.width  -1
    max_y = board.height -1
    distance_board = {}

    # Initialize the dictionaries
    for x,y in itertools.product(list(range(board.width)),list(range(board.height))):
        distance_board[coord2str((x,y))] = {}
        for x2,y2 in itertools.product(list(range(board.width)),list(range(board.height))):
            distance_board[coord2str((x,y))][coord2str((x2,y2))] = None

    all_squares = [(x,y) for x in range(board.width) for y in range(board.height)]

    # Conduct the search starting once from each square
    for starting_square in all_squares:
        traversed = []

        # Format of q: (square, distance), where 'square' is the coordinates (x,y) and 'distance' is the number
        # of steps from 'starting_square' to 'square'.
        q = queue.Queue()
        q.put((starting_square,0))

        # Breadth-first search
        while not q.empty():
            curr_coord, curr_length = q.get()

            # Update distances if needed
            if distance_board[coord2str(starting_square)][coord2str(curr_coord)] is None or curr_length < distance_board[coord2str(starting_square)][coord2str(curr_coord)]:
                distance_board[coord2str(starting_square)][coord2str(curr_coord)] = curr_length

            # Handle each neighbour of the current square
            for direction in DIRECTIONS:
                neighbour_coordinates = (curr_coord[0] + direction[0], curr_coord[1] + direction[1])
                
                # Out of bounds
                if not 0 <= neighbour_coordinates[0] <= max_x or not 0 <= neighbour_coordinates[1] <= max_y:
                    continue

                # Has already been traversed to 
                if neighbour_coordinates in traversed:
                    continue

                neighbour_tile = board.get_tile(neighbour_coordinates)

                # Cannot be traversed at all
                if neighbour_tile.passable == False:
                    continue
                # Can be traversed but character does not have the needed skills
                elif neighbour_tile.passable != True and not any([sk for sk in movement_skills if sk in neighbour_tile.passable]):
                    continue

                # If none of the previous apply, add this square to the queue
                traversed.append(neighbour_coordinates)
                q.put(( neighbour_coordinates, curr_length+1 ))

    return distance_board

