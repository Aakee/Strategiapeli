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
    for char_data in data['characters']:
        character.from_dict(char_data, game)
                
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
            terrain = tile.terrain.value
            sym = tile2sym[terrain]
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
