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
    blue_player = game.get_blue_player()
    red_player  = game.get_red_player()
    for char_data in data['characters']:
        if char_data['color'].lower() == 'blue':
            controller = blue_player
        elif char_data['color'].lower() == 'red':
            controller = red_player
        else:
            raise CorruptedSaveFileException("")
        char_class = char_data['class']
        char = new_char(controller, char_class, game)

        x,y = char_data['loc'].split(',')
        x,y = int(x), int(y)
        game.get_board().set_object((x,y), char)

        if 'hp' in char_data:
            char.set_hp(char_data['hp'])

        if 'moven' in char_data:
            if char_data['moven'] in (True, False):
                char.ready = char_data['moven']
            else:
                raise CorruptedSaveFileException(f"Corrupted character movement status: {char_data['moven']}")

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

def new_char(owner,type,game):
    '''
    Method creates a new character according to parameters it gets.
    @param owner: Human- or AI-object, who controls character
    @param type: Character's class as a string
    @param tile: Tile from which the character starts from
    '''
    type = type.strip().lower()
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
    
    return char
    
    
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
            terrain = tile.terrain.value
            sym = tile2sym[terrain]
            map_str += sym
        map_str += '\n'
    savedata['map'] = map_str

    # Parse through characters (characters section)
    all_characters = []
    for char in game.get_blue_player().get_characters() + game.get_red_player().get_characters():
        char_data = {}
        print(char)
        char_data['class'] = char.type.value
        char_data['color'] = char.owner.color.value
        char_data['loc']   = f'{char.get_square()[0]},{char.get_square()[1]}'
        char_data['hp']    = char.get_hp()
        if char.ready:
            char_data['moven'] = True
        all_characters.append(char_data)
    savedata['characters'] = all_characters

    with open(filename, 'w') as file:
        yaml.safe_dump(savedata, file)
