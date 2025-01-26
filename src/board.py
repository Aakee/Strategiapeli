from game_errors import IllegalMoveException
import threading
import queue
import ai.distance
from game_enums import Stats

class Board:
    
    DIRECTIONS = [[-1,0],[0,1],[1,0],[0,-1]]
    
    def set_board(self,board):
        self.board = board
        self.height = len(self.board)
        self.width  = len(self.board[0])
        self.distmap = ai.distance.DistanceMap(self)
    
    def get_height(self):
        return self.height
    
    
    def get_width(self):
        return self.width
    
    
    def get_piece(self,coordinates):
        '''
        Returns the object in chosen square.
        @param coordinates: Coordinates in format (x,y)
        @return: Object in tile in chosen square
        ''' 
        return self.board[coordinates[1]][coordinates[0]].get_object()
    
    def set_tile(self,tile,coordinates):
        '''
        Sets the given tile to given coordinates.
        @param tile: A tile-type object
        '''
        self.board[coordinates[1]][coordinates[0]] = tile
    
    def get_tile(self,coordinates):
        '''
        Returns the tile in chosen square (for example the plain object, not character object)
        @param coordinates: Coordinates in format (x,y)
        @return: Tile in chosen square
        '''
        return self.board[coordinates[1]][coordinates[0]]
    
    
    def set_object(self,coordinates,object):
        '''
        Sets the given object in given square, if it is empty; otherwise, raise KeyError
        @param coordinates: Coordinates in format (x,y)
        @param object: Object we wish to place
        '''
        if self.get_tile(coordinates).get_object() == None:
            self.board[coordinates[1]][coordinates[0]].set_object(object)
            return
        else:
            raise KeyError("Square is already occupied!")
        
    def remove_object(self, coordinates):
        '''
        Removes character from tile in the chosen coordinates.
        @param coordinates: Coordinates in format (x,y)
        '''
        tile = self.get_tile(coordinates)
        #gui_tile = tile.get_gui_tile()
        tile.remove_object()
        #if gui_tile != None: # If playing without gui, or testing
        #    gui_tile.set_image(None,True)
    
    
    def get_square(self, object):
        '''
        Returns coordinates for the square the object
        in parameter is in, or None if nowhere.
        @param object: The object we are looking for.
        @return: Coordinates for the squre where the object is found (or none).
        '''
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x].get_object() == object:
                    return (x,y)
                
        return None
    
    
    def move_char(self,src,dst, verbose=True):
        '''
        Moves the piece from square src OR char src to square dst if able.
        Src can be either the actual object or coordinates it is in.
        Method doesn't check if character should be able to move to chosen tile; it
        should be checked by other methods.
        @param src: Original square in format (x,y) OR char we want to move
        @param dst: Destination square in format (x,y)
        '''
        type = None
        try: # src is coordinates
            char = self.get_piece(src)
            type = 0
        except TypeError: # src is object
            char = src
            type = 1
          
        if char == None:
            raise IllegalMoveException("Source tile is empty!")
        
        coordinates = self.get_square(char)
        legal_squares = char.get_legal_squares()
    
        if dst not in legal_squares:
            raise IllegalMoveException("Cannot move to chosen tile!")
        
        
        if type == 0:
            self.remove_object(src)
        if type == 1:
            self.remove_object(coordinates)
        self.set_object(dst, char)
        
        if verbose:
            print("\n{} liikkui ruudusta ({},{}) ruutuun ({},{}).".format(char.get_name(),coordinates[0]+1,coordinates[1]+1,dst[0]+1,dst[1]+1))
    

    def legal_squares(self, char):
        '''
        Method defines all squares object can move to.
        @param char: Character whose legit squares we are intrested in
        @return: List of legit squares in format (x,y)
        '''
        return self.legal_squares_from_tile(char, char.get_square())
    

    def legal_squares_from_tile(self,char,init_square):
        '''
        Method defines all squares object can move to from a chosen square.
        Note that character doesn't have to be currently on said tile.
        @param char: Character whose legit squares we are intrested in
        @param square: Coordinates of starting tile in format (x,y)
        @return: List of legit squares in format (x,y)
        '''
        # Helper function to turn cordinates into strings
        def coord2str(coord):
            return f"{coord[0]},{coord[1]}"
        
        legal_squares   = []
        init_range      = char.get_stats()[Stats.RANGE]
        
        # Check if the character can stay on the very first square
        can_stay, _     = self.get_tile(init_square).pass_by(char,init_range)
        if can_stay:
            legal_squares.append(init_square)

        # Dictionary keeping track which squares has already been traversed, and which is the current maximum steps left it has been reached
        shortest_paths = {coord2str(init_square): init_range} 
        
        # Queue for the BFS
        q = queue.Queue()
        q.put((init_range, init_square))

        # Conduct the breadth-first search
        while not q.empty():

            # How many steps the character can still take, what is the current square in the search
            steps_left, curr_square = q.get()

            # Loop through all four neighbouring squares
            for direction in Board.DIRECTIONS:
                new_square = (curr_square[0]+direction[0], curr_square[1]+direction[1])

                # Skip if out of bounds
                if not 0 <= new_square[0] < self.width or not 0 <= new_square[1] < self.height:
                    continue
                can_stay, steps_after_moving =  self.get_tile(new_square).pass_by(char, steps_left)
                
                # Add to list if the character can stay in this square
                if can_stay and new_square not in legal_squares:
                    legal_squares.append(new_square)

                # Add to list if tile.pass_by_square did not tell that the character can stand on this tile due to it already being there
                elif not can_stay and self.get_piece(new_square) == char and new_square not in legal_squares:
                    legal_squares.append(new_square)

                # If there are steps left and this is the currently best path to the square, add to queue
                if steps_after_moving > 0:
                    if coord2str(new_square) not in shortest_paths or shortest_paths[coord2str(new_square)] < steps_after_moving:
                        q.put((steps_after_moving, new_square))
                        shortest_paths[coord2str(new_square)] = steps_after_moving
        
        return legal_squares
    

    def legal_attack_targets(self,init_tile,range,target):
        '''
        Defines all legal attack targets' coordinates.
        (Because no actual damage is done, can also be used to define legal heal targets, skill targets, etc)
        Also because parameters has only coordinates and not actual character,
        method can be used with ai to map potential tiles to attack from.
        @param init_tile: Tile from which the attack will come
        @param range: Range of the attack in squares
        @param target: Player whose characters we are seeking (generally AI or Human)
        @return: List of legal squares' coordinates in format (x,y)
        '''
        squares = []
        for square in self.get_tiles_in_range(init_tile,range):
            target_char = self.get_piece(square)
            if target_char is not None and target_char.get_owner() == target:
                squares.append(square)
        return squares
        
    
    def get_tiles_in_range(self,init_coordinates,d):
        '''
        Defines all tiles in range of range from square init_coordinates.
        @param init_coordinates: Coordinates we start from
        @param range: How far can we go from init_coordinates
        @return: List of all applicable squares in format (x,y)
        '''
        x0, y0 = init_coordinates
        return [ (x,y) for x in range(x0-d, x0+d+1) for y in range(y0-(d-abs(x0-x)),y0+(d-abs(x0-x))+1) if 0<=x<self.width and 0<=y<self.height ]
    
                
    def distance_to(self,square1,square2):
        '''
        Method defines shortest route between square1 and square2. It doesn't
        check what obstacles is between them.
        Method can be used by ai to define distance to player's characters.
        '''
        x = abs(square1[0]-square2[0])
        y = abs(square1[1]-square2[1])
        return x+y
