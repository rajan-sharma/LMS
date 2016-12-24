FONT_SIZE        = 8
FLOOR_LEVEL      = 0.4
WATER_LEVEL      = 0.0000049
LARGE_TREE_LEVEL = 0.9
WIDTH, HEIGHT    = int(1280/FONT_SIZE), int(480/FONT_SIZE)
FOV              = True
MESSAGE_NUMBER   = 21
FOREST_LEVELS    = 7
DUNGEON_LEVELS   = 10

GAME_MOVEMENT_KEYS = {
    'L':     [1, 0],
    'H':     [-1, 0],
    'K':     [0, -1],
    'J':     [0, 1],
}
def pickup(GS, p):
    item = GS['terrain_map'].spawned_items[p.x, p.y]
    GS['messages'].insert(0, 'You pick up a '+item.name)
    GS['terrain_map'].spawned_items.remove(item)
    p.add_inventory_item(item)
    
GAME_ACTION_KEYS = {
    '.': lambda GS, p: p.rest(),
    ',': pickup
}
GAME_KEYS = {
    'M': GAME_MOVEMENT_KEYS,
    'A': GAME_ACTION_KEYS
}

INVENTORY_MOVEMENT_KEYS = {}
INVENTORY_ACTION_KEYS = {}
INVENTORY_KEYS = {
    'M': INVENTORY_MOVEMENT_KEYS,
    'A': INVENTORY_ACTION_KEYS
}

CHARACTER_MOVEMENT_KEYS = {}
CHARACTER_ACTION_KEYS = {}

CHARACTER_KEYS = {
    'M': CHARACTER_MOVEMENT_KEYS,
    'A': CHARACTER_ACTION_KEYS
}

ABBREV = {
    'LL': 'level',
    'HT': 'health',
    'ST': 'strength',
    'AT': 'attack',
    'SP': 'speed'
}