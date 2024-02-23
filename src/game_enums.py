'''
Includes some enumerations used in the game.
'''
from enum import Enum

class Stats(Enum):
    '''
    Character stats
    '''
    ATTACK      = "att"
    DEFENSE     = "def"
    MAGIC       = "mag"
    RESISTANCE  = "res"
    SPEED       = "spd"
    EVASION     = "eva"
    MAXHP       = "max"
    RANGE       = "rng"

class CharacterClass(Enum):
    '''
    Character classes
    '''
    TESTCHAR    = "testchar"
    KNIGHT      = "knight"
    ARCHER      = "archer"
    MAGE        = "mage"
    CLERIC      = "cleric"
    ASSASSIN    = "assassin"
    VALKYRIE    = "valkyrie"
    VIP         = "vip"
    STUCK_VIP   = "stuck_vip"

class Terrain(Enum):
    '''
    Different terrains for Tiles
    '''
    PLAIN       = "plain"
    SAND        = "sand"
    WALL        = "wall"
    FOREST      = "forest"
    MOUNTAIN    = "mountain"
    WATER       = "water"
    GOAL        = "goal"
    SNOW        = "snow"
    WOOD        = "wood"
