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

class SkillType(Enum):
    '''
    Different skills
    '''
    #Skills which affect moving.
    LEVITATE = 1    # Character can levitate for instance over gaps
    GHOST = 2       # Character can pass walls and enemy players (but not land on them)
    SNEAK = 3       # Character can pass enemy players
    
    #Skills which affect in combat.
    CAMOUFLAGE = 11
    BODYGUARD = 12
    MIRACLE = 13
    SNIPER = 14
    
    #Passive skills which affect outside of combat
    REST = 21       # Character gains HP at the start of each turn.
    
    #Active skills which affect outside of combat (must be activated)
    HEAL = 31       # Character can heal other characters (and themselves).
    RAISEDEF = 33   # Character raises defensive stats for nearby allies until start of next turn
    RAISERNG = 34   # Character raises range for nearby allies until start of next turn
    WISH = 39       # Another character can move second time