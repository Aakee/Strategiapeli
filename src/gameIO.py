from tile import *
from game_errors import *
from game_enums import PlayerColor
import character
from game import Game
import yaml

'''
Functions to manage loading a game from and saving a game to file.
'''
    
def load_game(input_file):
    try:
        return load_game_with_new_format(input_file)
    except Exception as err1:
        try:
            return load_game_with_old_format(input_file)
        except Exception as err2:
            raise CorruptedSaveFileException(f"Save couldnt be read!\n\nNew format:\n{err1}\n\nOld format:\n{err2}")


def load_game_with_new_format(input_file):
    '''
    Function loads and returns a game from the information from file input_file.
    @param input_file: Path to the save file as a string
    @returns: a Game object
    '''

    # Load data
    try:
        with open(input_file, 'r') as file:
            data = yaml.safe_load(file)
    except yaml.parser.ParserError:
        raise CorruptedSaveFileException("")
    
    # Players
    if 'blue_control' in data['game'] and data['game']['blue_control'].lower() == 'ai':
        blue_ai = True
    else:
        blue_ai = False
    if 'red_control' in data['game'] and data['game']['red_control'].lower() == 'player':
        red_ai = False
    else:
        red_ai = True

    # The resulting Game object
    game = Game(blue_controlled_by_ai=blue_ai, red_controlled_by_ai=red_ai)

    # Construct map
    map = [[new_tile(data['map_keys'][sym], game) for sym in row if sym.rstrip() != ''] for row in data['map'].split('\n') if len(row) > 0]
    game.board.set_board(map)

    # Set other game settings
    if 'whose_turn' in data['game']:
        if data['game']['whose_turn'].lower() in ('red', 'r'):
            game.whose_turn = PlayerColor.RED

    # Load characters
    for char_data in data['characters']:
        character.from_dict(char_data, game)
                
    return game


def load_game_with_old_format(input_file):
    '''
    Loads the game from a file using the old save format.
    '''
    def new_char(owner,type,tile,hp, game):
        '''
        Method creates a new character according to parameters it gets.
        @param owner: Human- or AI-object, who controls character
        @param type: Character's class as a string
        @param tile: Tile from which the character starts from
        '''
        try:
            type = type.strip()
            if type == "testchar":
                char = character.TestChar(game,owner)
            elif type == "knight":
                char = character.Knight(game,owner)
            elif type == "archer":
                char = character.Archer(game,owner)
            elif type == "mage":
                char = character.Mage(game,owner)
            elif type == "cleric":
                char = character.Cleric(game,owner)
            elif type == "assassin":
                char = character.Assassin(game,owner)
            elif type == "valkyrie":
                char = character.Valkyrie(game,owner)
            else:
                char = character.TestChar(game,owner)
                
            game.get_board().set_object(tile, char)
            if hp != None:
                char.set_hp(hp)
            
        except IndexError:
            raise CorruptedSaveFileException("Koordinaatit kartan ulkopuolella!")
        
    # The resulting Game object
    game = Game()

    # 2D list where the game information is loaded to
    map = []
    
    # Flags to see if certain sections and attributes have already been loaded
    info_ready  = False
    map_ready   = False
    turns_set   = False
    spawn_set   = False

    # Current section in the file
    current     = None

    # Parameters for the board; this will be changed in the future
    width = 0
    
    # Open save file
    try:
        input = open(input_file, "r")
    except IOError as e:
        raise CorruptedSaveFileException("Save file couldn't be opened!\nInfo: " + str(e))
    
    # Loop through the lines and read data
    
    current_line = input.readline()
    keys = {}
    
    try:
        while current_line != "":
            pass_this = False
            
            if current_line.strip() == "":
                pass
                
            elif current_line[0] == "#":
                if current_line.lower().strip() == "#game":
                    current = "game"
                    
                if current_line.lower().strip() == "#info":
                    current = "info"

                if current_line.lower().strip() == "#map":
                    if current != "info":
                        raise CorruptedSaveFileException("Map info must be first!")
                    info_ready = True
                    current = "map"

                if current_line.lower().strip() == "#char":
                    if not info_ready and current == "map":
                        raise CorruptedSaveFileException("Map info and data must be first!")
                    if not map_ready:
                        game.board.set_board(map)
                    map_ready = True
                    current = "char"

            elif current == "game":
                
                lines = current_line.split(" ")
                setting = lines[0].lower().strip()
                choice = lines[1].lower().strip()
                        
                if setting == 'turns':
                    if turns_set:
                        raise CorruptedSaveFileException("")
                    try:
                        turns = int(choice)
                        game.set_turns(turns)
                    except ValueError:
                        raise CorruptedSaveFileException("Faulty number of turns: " + str(turns) + "\nLine: " + str(line))
                    
                if setting == 'spawn':
                    try:
                        spawn = int(choice)
                        if not 0 <= spawn <= 100:
                            raise CorruptedSaveFileException("Spawn percent must be between 0 and 100!\nLine: " + str(line))
                        game.set_spawn(spawn)
                    except ValueError:
                        raise CorruptedSaveFileException("Faulty spawn percent: " + str(spawn) + "\nLine: " + str(line))
                    
            elif current == "info":
                
                lines = current_line.split(" ")
                sign = lines[0]
                type = lines[1].strip()
                
                try:
                    keys[sign] = type
                except KeyError:
                    raise CorruptedSaveFileException("Keys must be declared on #Info!\nFaulty key: " + str(sign) + "\nLine: " + str(line))
                
            elif current == "map":
                
                current_line = current_line.strip()
                width=set_width(len(current_line), width)
                line = []
                for sign in current_line:
                    type = keys[sign]
                    tile = new_tile(type, game)
                    line.append(tile)
                map.append(line)
                
            elif current == "char":
                
                owner_set = None
                class_set = None
                tile_set = None
                hp_set = None
                
                #while owner_set == None or class_set == None or tile_set == None:
                while True:
                    
                    if current_line == "" or current_line[0] == "#":
                        pass_this = True
                        break
                    
                    current_line = current_line.split(" ")

                    if current_line[0].lower() == "o":
                        if owner_set != None:
                            raise CorruptedSaveFileException
                        if current_line[1].lower().strip() == "player":
                            owner_set = PlayerColor.BLUE
                        elif current_line[1].lower().strip() == "computer":
                            owner_set = PlayerColor.RED
                        elif current_line[1].lower().strip() == "blue":
                            owner_set = PlayerColor.BLUE
                        elif current_line[1].lower().strip() == "red":
                            owner_set = PlayerColor.RED
                        else:
                            raise CorruptedSaveFileException("Hahmon omistajaa ei tunnistettu!\nRivi: " + str(line))
                            
                    if current_line[0].lower() == "c":
                        if class_set != None:
                            raise CorruptedSaveFileException("Hahmolla ei voi olla kahta luokkaa!\nRivi: " + str(line))
                        class_set = current_line[1].lower().rstrip()
                        
                    if current_line[0].lower() == "s":
                        if tile_set != None:
                            raise CorruptedSaveFileException("Hahmolla ei voi olla kahta ruutua!\n Rivi: " + str(line))
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
                            raise CorruptedSaveFileException("Hahmolla ei voi olla useita elamatietoja!\nRivi: " + str(line))
                        hp_set = int(current_line[1])
                        
                    current_line = input.readline()
                    
                if owner_set == None or class_set == None or tile_set == None:
                    string = "Owner: " + str(owner_set) + "\nTile: " + str(tile_set) + "\nClass: " + str(class_set)
                    raise CorruptedSaveFileException("Hahmolta puuttuu tarvittava kentta!\nRivi: " + str(line) + "\n" + string)
                
                new_char(owner_set, class_set, tile_set, hp_set, game)

                pass_this = True
            
            if not pass_this:
                current_line = input.readline()
    
        input.close()
        
    #except Exception as e: # Basically any kind of error should raise the eception
    except IndexError as e:
        raise CorruptedSaveFileException(e)
        
    if not info_ready or not map_ready:
        raise CorruptedSaveFileException("Save file was faulty!\nEither #Info or #Map missing")

    return game


def new_tile(key, game):
    '''
    Method creates a new tile according to key it gets.
    '''
    if key.lower() == "plain":
        tile = Plain(game)
    elif key.lower() == "wall":
        tile = Wall(game)
    elif key.lower() == "sand":
        tile = Sand(game)
    elif key.lower() == "mountain":
        tile = Mountain(game)
    elif key.lower() == "forest":
        tile = Forest(game)
    elif key.lower() == "water":
        tile = Water(game)
    elif key.lower() == "snow":
        tile = Snow(game)
    elif key.lower() == "wood":
        tile = Wood(game)
    elif key.lower() == "goal":
        tile = Goal(game)
    else:
        tile = Plain(game)
    return tile

    
def set_width(width, previous_width):
    '''
    Assistant method of load_game. Because maps must be rectangular,
    method makes sure that different rows doesn't have different amount
    of tiles.
    '''
    if previous_width != 0 and width != previous_width:
        raise CorruptedMapDataException("Different rows cannot have varying amount of tiles!")
    return width
        

def save_game(game, filename):
    '''
    Method saves the state of the board to a text file.
    @param game: Game object the save file is created from
    @param filename: Name of the file method tries to write to
    '''
    savedata = {}

    # Game section
    game_section = {}
    game_section['whose_turn'] = 'blue' if game.whose_turn == PlayerColor.BLUE else 'red'
    game_section['blue_control'] = 'ai' if game.get_blue_player().ai else 'player'
    game_section['red_control'] = 'ai' if game.get_red_player().ai else 'player'
    savedata['game'] = game_section
    
    # map_keys section
    sym2tile = {'_':'plain',
            's':'sand',
            '^':'forest',
            'w':'water',
            '+':'mountain',
            'X':'wall'}
    savedata['map_keys'] = sym2tile

    tile2sym = {}
    for sym, terrain in sym2tile.items():
        tile2sym[terrain] = sym

    # Parse through the map tiles (map section)
    map_str = ''
    for row in game.board.board:
        for tile in row:
            sym = tile2sym[tile.terrain]
            map_str += sym
        map_str += '\n'
    savedata['map'] = map_str

    # Parse through characters (characters section)
    all_characters = []
    for char in game.get_blue_player().get_characters() + game.get_red_player().get_characters():
        char_data = char.to_dict()
        all_characters.append(char_data)
    savedata['characters'] = all_characters

    with open(filename, 'w') as file:
        yaml.safe_dump(savedata, file)
