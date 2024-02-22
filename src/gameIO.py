

import board
from tile import *
from game_errors import *
import human
import ai
import CharacterData
from character import Character
from board import Board
from game import Game



class IO:
    '''
    Class manages writing from and reading to files.
    '''
        
    def load_game(self, input_file):
        '''
        Method creates and returns a game from the information from file
        input_file.
        @param input_file: Name of the file class tries to load game from
        @return: a Game object
        '''
        
        self.map = []
        
        self.game = Game()
        
        self.info_ready = False
        self.map_ready = False
        self.turns_set = False
        self.spawn_set = False
        self.current = None
        self.line = 0

        self.width = 0
        self.height = 0
        self.board = Board(self.game)
        self.game.set_board(self.board)
        
        self.game.set_human(human.Human(self.game))
        self.game.set_ai(ai.AI(self.game))
           
        try:
            input = open(input_file, "r")
        except IOError as e:
            raise CorruptedSaveFileException("Save file couldn't be opened!\nInfo: " + str(e))
        
        current_line = input.readline()
        keys = {}
        
        try:
            while current_line != "":
                pass_this = False
                self.line += 1
                
                if current_line.strip() == "":
                    pass
                    
                elif current_line[0] == "#":
                    if current_line.lower().strip() == "#game":
                        self.current = "game"
                        
                    if current_line.lower().strip() == "#info":
                        self.current = "info"

                    if current_line.lower().strip() == "#map":
                        if self.current != "info":
                            raise CorruptedSaveFileException("Map info must be first!")
                        self.info_ready = True
                        self.current = "map"

                    if current_line.lower().strip() == "#char":
                        if not self.info_ready and self.current == "map":
                            raise CorruptedSaveFileException("Map info and data must be first!")
                        self.map_ready = True
                        self.board.set_board(self.map, self.height, self.width)
                        self.current = "char"
                        

                elif self.current == "game":
                    
                    lines = current_line.split(" ")
                    setting = lines[0].lower().strip()
                    choice = lines[1].lower().strip()
                    
                    '''
                    if setting == 'mode':
                        if choice == 'dm':
                            self.game.set_mode('dm')
                        if choice == 'survive':
                            self.game.set_mode('survive')
                    '''
                            
                    if setting == 'turns':
                        if self.turns_set:
                            raise CorruptedSaveFileException("")
                        try:
                            turns = int(choice)
                            self.game.set_turns(turns)
                        except ValueError:
                            raise CorruptedSaveFileException("Faulty number of turns: " + str(turns) + "\nLine: " + str(self.line))
                        
                    if setting == 'spawn':
                        try:
                            spawn = int(choice)
                            if not 0 <= spawn <= 100:
                                raise CorruptedSaveFileException("Spawn percent must be between 0 and 100!\nLine: " + str(self.line))
                            self.game.set_spawn(spawn)
                        except ValueError:
                            raise CorruptedSaveFileException("Faulty spawn percent: " + str(spawn) + "\nLine: " + str(self.line))
                        
                            
    
                        
                elif self.current == "info":
                    
                    lines = current_line.split(" ")
                    sign = lines[0]
                    type = lines[1].strip()
                    
                    try:
                        keys[sign] = type
                    except KeyError:
                        raise CorruptedSaveFileException("Keys must be declared on #Info!\nFaulty key: " + str(sign) + "\nLine: " + str(self.line))
                    
                    
                elif self.current == "map":
                    
                    current_line = current_line.strip()
                    self.set_width(len(current_line))
                    line = []
                    for sign in current_line:
                        type = keys[sign]
                        tile = self.new_tile(type)
                        line.append(tile)
                    self.map.append(line)
                    self.height += 1
                    
                    
                elif self.current == "char":
                    
                    owner_set = None
                    class_set = None
                    tile_set = None
                    hp_set = None
                    
                    #while owner_set == None or class_set == None or tile_set == None:
                    while True:
                        
                        self.line += 1
                        
                        if current_line == "" or current_line[0] == "#":
                            pass_this = True
                            break
                        
                        current_line = current_line.split(" ")

                        if current_line[0].lower() == "o":
                            if owner_set != None:
                                raise CorruptedSaveFileException
                            if current_line[1].lower().strip() == "player":
                                owner_set = self.game.get_human()
                            elif current_line[1].lower().strip() == "computer":
                                owner_set = self.game.get_ai()
                            else:
                                raise CorruptedSaveFileException("Hahmon omistajaa ei tunnistettu!\nRivi: " + str(self.line))
                                
                        if current_line[0].lower() == "c":
                            if class_set != None:
                                raise CorruptedSaveFileException("Hahmolla ei voi olla kahta luokkaa!\nRivi: " + str(self.line))
                            class_set = current_line[1].lower().rstrip()
                            
                        if current_line[0].lower() == "s":
                            if tile_set != None:
                                raise CorruptedSaveFileException("Hahmolla ei voi olla kahta ruutua!\n Rivi: " + str(self.line))
                            tile = current_line[1]
                            bfr = current_line[1].split(",")
                            bfr2 = bfr[0].split("(")
                            x = int(bfr2[1])
                            bfr2 = bfr[1].split(")")
                            y = int(bfr2[0])
                            coordinates = (x,y)
                            tile_set = coordinates
                            
                        if current_line[0].lower() == "h":
                            if hp_set != None:
                                raise CorruptedSaveFileException("Hahmolla ei voi olla useita elamatietoja!\nRivi: " + str(self.line))
                            hp_set = int(current_line[1])
                            
                        current_line = input.readline()
                        
                    if owner_set == None or class_set == None or tile_set == None:
                        string = "Owner: " + str(owner_set) + "\nTile: " + str(tile_set) + "\nClass: " + str(class_set)
                        raise CorruptedSaveFileException("Hahmolta puuttuu tarvittava kentta!\nRivi: " + str(self.line) + "\n" + string)
                    
                    self.new_char(owner_set, class_set, tile_set, hp_set)
                    pass_this = True
                
                if not pass_this:
                    current_line = input.readline()
        
        
            input.close()
            
        except Exception as e: # Basically any kind of error should raise the eception
            raise CorruptedSaveFileException(e)
            
        if not self.info_ready or not self.map_ready:
            raise CorruptedSaveFileException("Save file was faulty!\nEither #Info or #Map missing")
        
        
        
        return self.game
               
            
    def new_tile(self,key):
        '''
        Method creates a new tile according to key it gets.
        '''
        if key.lower() == "plain":
            tile = Plain(self.game)
        elif key.lower() == "wall":
            tile = Wall(self.game)
        elif key.lower() == "sand":
            tile = Sand(self.game)
        elif key.lower() == "mountain":
            tile = Mountain(self.game)
        elif key.lower() == "forest":
            tile = Forest(self.game)
        elif key.lower() == "water":
            tile = Water(self.game)
        elif key.lower() == "snow":
            tile = Snow(self.game)
        elif key.lower() == "wood":
            tile = Wood(self.game)
        elif key.lower() == "goal":
            tile = Goal(self.game)
        else:
            tile = Plain(self.game)
        return tile
    
    def new_char(self,owner,type,tile,hp):
        '''
        Method creates a new character according to parameters it gets.
        @param owner: Human- or AI-object, who controls character
        @param type: Character's class as a string
        @param tile: Tile from which the character starts from
        '''
        try:
            type = type.strip()
            if type == "testchar":
                char = CharacterData.TestChar(self.game,owner)
            elif type == "knight":
                char = CharacterData.Knight(self.game,owner)
            elif type == "archer":
                char = CharacterData.Archer(self.game,owner)
            elif type == "mage":
                char = CharacterData.Mage(self.game,owner)
            elif type == "cleric":
                char = CharacterData.Cleric(self.game,owner)
            elif type == "assassin":
                char = CharacterData.Assassin(self.game,owner)
            elif type == "valkyrie":
                char = CharacterData.Valkyrie(self.game,owner)
            else:
                char = CharacterData.TestChar(self.game,owner)
                
            self.board.set_object(tile, char)
            if hp != None:
                char.set_hp(hp)
            
        except IndexError:
            raise CorruptedSaveFileException("Koordinaatit kartan ulkopuolella!")
        
        
    def set_width(self,width):
        '''
        Assistant method of load_game. Because maps must be rectangular,
        method makes sure that different rows doesn't have different amount
        of tiles.
        '''
        if self.width != 0 and self.width != width:
            raise CorruptedMapDataException("Different rows cannot have varying amount of tiles!")
        elif self.width == 0:
            self.width = width
            
    
    def save_game(self, game, filename):
        '''
        Method saves the state of the board to a text file.
        @param game: Game object the save file is created from
        @param filename: Name of the file method tries to write to
        '''
        try:
            tiedosto = open(filename, "w")
        except IOError:
            raise CorruptedSaveFileException("Couldn't save to destination!")
        
        tiles = {}
        keys = "abcdefghijklmn"
        
        board = game.get_board()
        i = 0
        
        try:
            for y in range(board.get_height()):
                for x in range(board.get_width()):
                    tile = board.get_tile((x,y))
                    name = tile.get_type()
                    if name not in tiles:
                        tiles[name] = keys[i]
                        i += 1
                        
            tiedosto.write("#Info\n\n")
            for key in tiles:
                string = tiles[key] + " " + key + "\n"
                tiedosto.write(string)
                
            tiedosto.write("\n#Map\n\n")
            
            
            for y in range(board.get_height()):
                string = ""
                for x in range(board.get_width()):
                    tile = board.get_tile((x,y))
                    type = tile.get_type()
                    string += tiles[type]
                string += "\n"
                tiedosto.write(string)
            
            '''    
            for char in game.get_human().get_characters():
                name = char.get_name()
                square = char.get_square()
                x = square[0]
                y = square[1]
                square = "(" + str(x) + "," + str(y) + ")"
                string = "\n#Char\nO Player\nC " + name + "\nS " + square + "\n"
                if char.get_hp() != char.get_maxhp():
                    string += "H " + str(char.get_hp())
                tiedosto.write(string)
                
            for char in game.get_ai().get_characters():
                name = char.get_name()
                square = char.get_square()
                x = square[0]
                y = square[1]
                square = "(" + str(x) + "," + str(y) + ")"
                string = "\n#Char\nO Computer\nC " + name + "\nS " + square + "\n"
                if char.get_hp() != char.get_maxhp():
                    string += "H " + str(char.get_hp()) + "\n"
                tiedosto.write(string)
            '''
                
            for y in range(board.get_height()):
                for x in range(board.get_width()):
                    char = board.get_piece((x,y))
                    if char != None:
                        string = "\n#Char\n"
                        name = char.get_name()
                        square = char.get_square()
                        x = square[0]
                        y = square[1]
                        square = "(" + str(x) + "," + str(y) + ")"
                        if char.get_owner() == game.get_human():
                            string += "O Player\n"
                        else:
                            string += "O Computer\n"
                        string += "C " + name + "\n"
                        string += "S " + square + "\n"
                        if char.get_hp() != char.get_maxhp():
                            string += "H " + str(char.get_hp()) + "\n"

                        
                        tiedosto.write(string)
                        
                
            tiedosto.close()
            
            
        except:
            raise CorruptedSaveFileException("Couldn't write to file!")
        

    def parse_ai(self):
        pass
    
    def get_input(self):
        return self.input