import utils, draw, itertools

################### GAME SETTINGS ###################
FONT_SIZE        = 8
FLOOR_LEVEL      = 0.43
WATER_LEVEL      = 0.0000049
STONE_LEVEL      = 0.95
WIDTH, HEIGHT    = int(1380/FONT_SIZE), int(800/FONT_SIZE)
FOV              = True
CUMULATE_FOV     = True
MESSAGE_NUMBER   = 31
FOREST_LEVELS    = 0
MAX_ROOMS        = 70
ITEMS_PER_ROOM   = 2
DUNGEON_LEVELS   = 21
DEBUG            = True

MIN_ROOM_WIDTH = 8
MIN_ROOM_HEIGHT = 4
MAX_ROOM_SIZE = 20

MAP = {
    'OCTAVES': 2, # Controls the amount of detail in the noise.
    
    'DIMS': 2,    # n of dimensions
    
    'HURST': 0.9, # The hurst exponent describes the raggedness of the resultant
                  # noise, with a higher value leading to a smoother noise. It
                  # should be in the 0.0-1.0 range.
    
    'LA': 0.2     # A multiplier that determines how quickly the frequency
                  # increases for each successive octave.
}

################### PLAYER MOVEMENT ###################
GAME_MOVEMENT_KEYS = {
    'L': [1, 0],
    'H': [-1, 0],
    'K': [0, -1],
    'J': [0, 1],
    'Y': [-1, -1],
    'U': [1, -1],
    'N': [-1, 1],
    'B': [1, 1],

    # For losers
    'RIGHT': [1, 0],
    'LEFT': [-1, 0],
    'UP': [0, -1],
    'DOWN': [0, 1],
}

################### PLAYER ACTIONS ###################

# Have the player pick up an item
def pickup(GS, p):
    dun_items = GS['terrain_map'].dungeon['items']
    if DEBUG: print('Dungeon items: ' + str(dun_items) + ', position: ' + str(p.pos))
    if p.pos in dun_items:
        item = dun_items[p.pos]
        GS['messages'].insert(0, 'You pick up a '+item.name)
        
        del dun_items[p.pos]
        p.add_inventory_item(item)

# Have the player rest until no more rest is needed.
# Hunger builds more slowly and monsters each get a turn.
def auto_rest(GS, p):
    while p.health < p.max_health:
        p.rest()
        utils.monster_turn(GS)
        
        if GS['turns'] % 6 == 0: p.hunger += 1
        GS['turns'] += 1

# Fire the first available missle using the player's current ranged weapon at
# the closest monster that A* can find a path to and is in the player's LoS.
def fire(GS, p):
    targets = list(filter(
        lambda m:
        GS['terrain_map'].lighted_terrain.compute_path(p.x, p.y, m.x, m.y,
                                                   diagonal_cost=0) != [] and\
        utils.dist(m, p) < p.ranged_weapon.range,
        GS['terrain_map'].proweling_monsters))
    if p.ranged_weapon != None and len(targets) > 0:
        target = min(targets, key=lambda m: utils.dist(m, p))
        missle = list(filter(lambda m: m.missle_type == p.ranged_weapon.missle_type, p.missles))[0]
        target.health -= missle.hit
        p.missles.remove(missle)
        adj = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]
        for a in adj:
            x = target.x + a[0]
            y = target.y + a[1]
            if GS['terrain_map'].get_type(x, y) != 'STONE':
                GS['terrain_map'].spawned_items[x, y] = missle

# Switches between inventory and HUD screens.
def inventory(GS, p):
    if GS['side_screen'] == 'INVENTORY':
        GS['side_screen'] == 'HUD'
    else:
        GS['side_screen'] = 'INVENTORY'

# Resets all screens back to the default playing setup. 
def reset(GS, p):
    if DEBUG: print('Screens reset')
    GS['side_screen'] = 'HUD'
    
    if GS['screen'] != 'DEATH' or GS['screen'] != 'CHARSEL' or GS['screen'] != 'INTRO':
        GS['screen'] = 'GAME'

# Quits the game and prints ending player state.
def quit(GS, p):
    print('\nGame Stats')
    print('----------')
    print('  Turns: ' + str(GS['turns']))
    print('  Score: ' + str(p.score()))
    print('  Inventory:\n' +\
          ',\n'.join(list(map(lambda x:
                              '    '+x[0].name+' x'+str(len(list(x[1]))),
                              itertools.groupby(p.inventory)))))
    exit(0)


GAME_ACTION_KEYS = {
    '.': lambda GS, p: p.rest(),
    ',': pickup,
    ';': auto_rest,
    'F': fire,
    'I': inventory,
    'ESCAPE': reset,
    'Q': quit
}

 
################### ALL GAME KEYS ###################
GAME_KEYS = {
    'M': GAME_MOVEMENT_KEYS,
    'A': GAME_ACTION_KEYS
}


################### HELPER CONSTS ###################
# Abbreviations of the player's stats for use on the HUD bar.
ABBREV = {
    'LL': 'level',
    'HT': 'health',
    'ST': 'strength',
   'AT': 'attack',
    'SP': 'speed',
    'DF': 'defence'
}
