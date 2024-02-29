from game_errors import IllegalMoveException
import tile

class Board:
    
    DIRECTIONS = [[-1,0],[0,1],[1,0],[0,-1]]
    
    def set_board(self,board):
        self.board = board
        self.height = len(self.board)
        self.width  = len(self.board[0])
    
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
        squares = []
        init_range = char.get_range()
        init_tile = char.get_square()
        squares.append(init_tile)
        for direction in Board.DIRECTIONS:
            try:
                new_coordinates = (init_tile[0]+direction[0],init_tile[1]+direction[1])
                self.pass_by_square(char, init_range, new_coordinates, squares)
            except IndexError:
                pass
        return squares
    
    
    def legal_squares_from_tile(self, char, square):
        '''
        Method defines all squares object can move to from a chosen square.
        Note that character doesn't have to be currently on said tile.
        @param char: Character whose legit squares we are intrested in
        @param square: Coordinates of starting tile in format (x,y)
        @return: List of legit squares in format (x,y)
        '''
        squares = []
        init_range = char.get_range()
        init_square = square
        init_tile = self.get_tile(init_square)
        if init_tile.get_object() == None:
            if 0 <= init_square[0] < self.width and 0 <= init_square[1] < self.height:
                squares.append(init_square)
        for direction in Board.DIRECTIONS:
            try:
                new_coordinates = (init_square[0]+direction[0],init_square[1]+direction[1])
                self.pass_by_square(char, init_range, new_coordinates, squares)
            except IndexError:
                pass
        return squares
    
    def pass_by_square(self,char,steps,coordinates,squares):
        '''
        An assistant method of legal_squares -method.
        @param char: Character who is moving
        @param steps: Amount of steps which are left
        @param coordinates: The tile we are currently inspecting
        @param squares: List of legal squares' coordinates in format (x,y)
        '''
        new_tile = self.get_tile(coordinates)
        result = new_tile.pass_by(char, steps) # result[0] = add, result[1] = steps_left
        add = result[0]
        steps_left = result[1]
        if add and (coordinates not in squares):
            if 0 <= coordinates[0] < self.width and 0 <= coordinates[1] < self.height:
                squares.append(coordinates)
        elif not add and coordinates not in squares:
            if char.get_square() == coordinates:
                squares.append(coordinates)
        if steps_left > 0:
            for direction in Board.DIRECTIONS:
                try:
                    new_coordinates = (coordinates[0] + direction[0], coordinates[1] + direction[1])
                    if 0 <= new_coordinates[0] < self.width and 0 <= new_coordinates[1] < self.height:
                        self.pass_by_square(char,steps_left,new_coordinates,squares)
                except IndexError:
                    pass
        return
    
    
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
                
        for direction in Board.DIRECTIONS:
            try:
                new_coordinates = (init_tile[0] + direction[0], init_tile[1] + direction[1])
                self.attack_through_square(new_coordinates, range, target, squares)
            except IndexError:
                pass
        return squares
                
        
    def attack_through_square(self, coordinates, range, target,squares):
        '''
        An assistant method of legal_attack_targets -method.
        @param coordinates: Coordinates of the tile we are now inspecting
        @param range: Amount of range still left in squares
        @param target: Owner of the characters we are looking for
        @param squares: List of legal attack targets in format (x,y) 
        '''
        if self.get_piece(coordinates) != None:
            if self.get_piece(coordinates).get_owner() == target and coordinates not in squares:
                if coordinates[0] >= 0 and coordinates[1] >= 0:
                    squares.append(coordinates)
        range -= 1
        if range > 0:
            for direction in Board.DIRECTIONS:
                try:
                    new_coordinates = (coordinates[0] + direction[0], coordinates[1] + direction[1])
                    self.attack_through_square(new_coordinates, range, target, squares)
                except IndexError:
                    pass
        return
    
    def get_tiles_in_range(self,init_coordinates,range):
        '''
        Defines all tiles in range of range from square init_coordinates.
        @param init_coordinates: Coordinates we start from
        @param range: How far can we go from init_coordinates
        @return: List of all applicable squares in format (x,y)
        '''
        if range == 0:
            return [init_coordinates]
        squares = []
        init_tile = init_coordinates
        squares.append(init_tile)
        for direction in Board.DIRECTIONS:
            try:
                new_coordinates = (init_tile[0]+direction[0],init_tile[1]+direction[1])
                self.tiles_in_direction(squares, new_coordinates, range)
            except IndexError:
                pass
        return squares
    
    def tiles_in_direction(self,squares,coordinates,left):
        '''
        Assistant method of tiles_in_range.
        @param squares: List of applicable squares
        @param coordinates: Coordinates of square we are currently on
        @param left: Steps we have left
        '''
        if coordinates not in squares:
            if coordinates[0] >= 0 and coordinates[1] >= 0 and coordinates[0] < self.width and coordinates[1] < self.height:
                squares.append(coordinates)
        left -= 1
        if left > 0:
            for direction in Board.DIRECTIONS:
                try:
                    new_coordinates = (coordinates[0]+direction[0],coordinates[1]+direction[1])
                    self.tiles_in_direction(squares, new_coordinates, left)
                except IndexError:
                    pass
        return
                
    def distance_to(self,square1,square2):
        '''
        Method defines shortest route between square1 and square2. It doesn't
        check what obstacles is between them.
        Method can be used by ai to define distance to player's characters.
        '''
        x = abs(square1[0]-square2[0])
        y = abs(square1[1]-square2[1])
        return x+y
