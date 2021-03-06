import tdl, copy, random
from itertools import groupby
import utils, consts, math, items
from functools import *
import operator

class Player:
    def __init__(self, race):
        self.pos = (0, 0)
        
        self.light_source_radius = 1
        self.hands = 2
        self.hunger = 0
        self.killed_monsters = 0
        
        self.level = 0
        self.exp = 0
        self.skill_tree = {}
        
        self.prev_pos = (-1,-1)
        self.poisoned = 0
        self.frozen = 0

        # Setup character's race.
        self.race = race

        # Setup player's stats.
        self.max_health = self.health = self.race.first_level['max_health']
        self.speed = self.max_speed = self.race.speed
        
        self.max_strength = self.strength = self.race.first_level['strength']
        self.max_attack = self.attack = self.race.first_level['strength']
        self.max_defence = self.defence = 0

        # Setup player's inventory
        self.lin_inventory = list(map(copy.copy,
                                      self.race.first_level['inventory']))\
                                      +[items.FOOD_RATION]*8
        self.update_inventory()
        self.dequips = []
        
        # Book-keeping
        self.ranged_weapon = None
        self.missles = []

        for item in self.lin_inventory:
            if not isinstance(item, items.Food):
                item.equip(self)

    def get_skill_with_item(self, x):
        if isinstance(x, items.Weapon) or isinstance(x, items.RangedWeapon) or\
           isinstance(x, items.Armor):
            baseline = 0
            if isinstance(x, items.Weapon) or isinstance(x, items.RangedWeapon):
                baseline = 15
            elif isinstance(x, items.Armor):
                baseline = 20

            skill_levels = [(k, self.skill_tree.setdefault(k, (baseline, baseline)))
                            for k in x.category]
            return min(skill_levels, key=lambda x: x[1][0])[1]
        return (8,8)

    def get_skill(self, s):
        return self.skill_tree[s]
    
    def can_use(self, x):
        return self.get_skill_with_item(x)[0] <= x.probability
    
    def hands_left(self, x):
        return self.hands >= x.handedness
            
    def update_inventory(self):
        self.lin_inventory.sort(key = lambda x: x.weight)
        self.inventory = [(k, len(list(g))) for k, g in groupby(self.lin_inventory)]
        
    def has(self, x):
        return len([y for y in self.lin_inventory
                    if y.equipped and
                    (x.name == y.name or y.char == x.char)]) > 0
            
    # Calculate the player's overall score.
    def score(self, GS):
        return math.floor(GS['turns']/10) +\
            (self.level + self.killed_monsters + self.defence) * self.exp

    # Calculate new XP points based on monster danger-level.
    # If the XP is enough to graduate the player to the next level,
    # calls level_up with the current level calculated via the exp.
    def learn(self, GS, monster):
        self.exp += math.floor(monster.attack/2)
        s = math.floor(self.exp/(60+self.level*5))
        
        if s >= 1 and s <= self.race.levels:
            self.level_up(GS, s)

    # Convenience function for resting.
    def rest(self):
        if self.health < self.max_health:
            self.health += 1

    # Handles leveling a player up, takes the calculated level as an argument,
    # checks if it is a new level, and if so upgrades the player's stats.
    def level_up(self, GS, s):
        prevlev = self.level
        self.level = s
        if self.level > prevlev:
            GS['messages'].append('green: You have leveled up to level '+str(self.level))
            
        ratio = self.health/self.max_health
        self.max_health += self.race.level_up_bonus
        self.health = self.max_health*ratio
        self.max_strength += math.floor(self.race.level_up_bonus/10)
        self.strength = self.max_strength
        for item, lst in self.inventory:
            if item.equipped and (isinstance(item, items.Armor) or\
                                  isinstance(item, items.Weapon)):
                for category in item.category:
                    if self.skill_tree[category][0] > 5:
                        self.skill_tree[category] = (self.skill_tree[category][0]-1,
                                                     self.skill_tree[category][1])

    # If the monster is faster, the monster attacks first, otherwise the player
    # attacks first. The monster is passed a reference to the player to do special
    # actions and decrease health, then the player adds the defence number back to
    # his health and attacks the monster back if he is still alive.
    def attack_monster(self, GS, monster):
        if monster.speed < self.speed:
            monster.attack_player(self, GS)
            self.health += min(self.max_health - self.health, self.defence)
            skill = self.race.skills['weapon']
            if self.health > 0 and random.randint(0, 20+self.exp) <= self.exp*skill+10:
                monster.health -= self.attack
                GS['messages'].append('yellow: You hit the monster a blow.')
                GS['messages'].append('yellow: The monster\'s health is '\
                                      +str(monster.health)+'.')
            else:
                GS['messages'].append('red: You miss the monster.')
        elif monster.speed >= self.speed:
            monster.health -= self.attack
            if monster.health > 0:
                monster.attack_player(self, GS)
                self.health += min(self.max_health - self.health, self.defence)
                
        if self.health > 0 and monster.health <= 0:
            self.learn(GS, monster)
        if monster.health <= 0:
            self.killed_monsters += 1
            
            for r in GS['terrain_map'].dungeon['rooms']:
                if r.inside(self.pos):
                    r.kills += 1
                    if r.kills > 5:
                        GS['terrain_map'].dungeon['monsters_alerted'] = True
        return (self.health <= 0, monster.health <= 0)

    # Adds a copy of the inventory item to the inventory (this is because all
    # inventory items are the same object from the items.ITEMS list), sorts it,
    # And calculates the player's new speed value based on the new weight of the
    # combined inventory.
    def add_inventory_item(self, item):
        if len(self.inventory) < consts.MAX_INVENTORY:
            self.lin_inventory.append(copy.copy(item))
            self.update_inventory()
            self.speed = sum(list(map(lambda x: max(0, x.weight-self.strength), self.lin_inventory)))
        
            if isinstance(item, items.Missle):
                item.equip(self)
            return True
        else:
            return False

    # Removes the i-th item from the inventory, dequips it, and resorts the inventory.
    def remove_inventory_item(self, item):
        item.dequip(self)
        self.lin_inventory.remove(item)
        self.update_inventory()

    # Calculates the total weight of the player's entire inventory.
    def total_weight(self):
        total = 0
        for i in self.lin_inventory:
            total += i.weight
            
        return total

    # For the Ranger:
    # If the player has two or less armor items and three or less weapons,
    # he is light, and therefore quiet.
    # For others:
    # If he has less than two armor items and three or less weapons, he is light,
    # and quiet.
    def light(self):
        num_armor = len(list(filter(lambda a: isinstance(a, items.Armor), self.lin_inventory)))
        num_weapon = len(list(filter(lambda a: isinstance(a, items.Weapon), self.lin_inventory)))

        if self.race.name == 'Bowman':
            if num_armor <= 4 and num_weapon <= 3:
                return 'light'
        else:
            if num_armor <= 3 and num_weapon <= 3:
                return 'light'
        return None

    def fast(self):
        if self.speed <= 5:
            return 'fast'
        else:
            return None

    # Formats and calculates the player's attributes nicely.
    def attributes(self):
        attrs = [self.light(), self.fast()]
        attrs = [x for x in attrs if x is not None]
        
        return ', '.join(attrs)

    # Moves the player and deals with any results of that. FIXME: Refactor this!
    def move(self, event, GS):
        if self.poisoned > 0 and GS['turns'] % 2:
            self.poisoned -= 1
            self.health -= 1
            
        for item in self.dequips:
            item.lasts -= 1
            if item.lasts <= 0:
                item.dequip(self)
                GS['messages'].append('yellow: Your '+item.name+' flickers out.')
                self.dequips.remove(item)
                
        if self.health < self.max_health and GS['turns'] % 3 == 0:
            self.health += 1
            
        if GS['turns'] % 4 == 0:
            self.hunger += 1

        if self.hunger > 20 and GS['turns'] % 3 == 0:
            descriptor = 'hungry'
            if self.hunger > 40:
                descriptor = 'Ravinous'
            elif self.hunger > 60:
                descriptor = 'Starving'
                
            GS['messages'].append('red: You feel '+descriptor+'.')
            self.health -= int(self.hunger/20)
        elif self.hunger >= 80:
            self.health = 0

        delta = consts.GAME_KEYS['M'][event.keychar]
        new_pos = utils.tuple_add(self.pos, delta)
        n_x, n_y = new_pos
        
        if new_pos == GS['terrain_map'].dungeon['down_stairs'] and\
           GS['terrain_map'].is_dungeons():

            GS['messages'].append("light_blue: You decend.")
            self.pos = GS['terrain_map'].generate_new_map()

        if new_pos == GS['terrain_map'].dungeon['up_stairs'] and\
           len(GS['terrain_map'].dungeons) > 1:
            
            if GS['terrain_map'].restore_dungeon(GS['terrain_map'].dungeon_level-1):
                GS['messages'].append("light_blue: You ascend.")
                self.pos = GS['terrain_map'].dungeon['player_starting_pos']
                
        if new_pos in GS['terrain_map'].dungeon['doors'] and\
           not GS['terrain_map'].is_walkable(new_pos):
            
            GS['terrain_map'].dungeon['doors'][new_pos] = False
            GS['terrain_map'].dungeon['lighted'].walkable[new_pos] = True
            GS['terrain_map'].dungeon['lighted'].transparent[new_pos] = True
            new_pos = self.pos
            n_x, n_y = new_pos

        w, h = GS['terrain_map'].width, GS['terrain_map'].height
        self.frozen -= 1
        if GS['terrain_map'].is_walkable(new_pos) and self.frozen <= 0:
            self.prev_pos = self.pos
            self.pos = new_pos
            di = GS['terrain_map'].dungeon['items']
            if self.pos in di:
                i = di[self.pos]
                for e in i:
                    GS['messages'].append("You find a " + e.name + ".")
                    if isinstance(e, items.Light) or isinstance(e, items.Food)\
                       or isinstance(e, items.Missle):
                        if self.add_inventory_item(e):
                            GS['messages'].append("You pick up a " + e.name + ".")
                        else:
                            GS['messages'].append("Your inventory is full.")
                        for k, v in GS['terrain_map'].dungeon['items'].items():
                            if e in v:
                                GS['terrain_map'].dungeon['items'][k].remove(e)
                                break
            if new_pos in GS['terrain_map'].dungeon['water']:
                GS['messages'].append("blue: You slosh through the cold water.")
        else:
            if GS['terrain_map'].in_area(new_pos) == 'Cave':
                GS['terrain_map'].place_cell(new_pos)
                self.pos = new_pos
            elif self.frozen > 0:
                GS['messages'].append('You are frozen for '+str(self.frozen)+' more turns.')
            else:
                new_pos = self.pos
                n_x, n_y = new_pos
            
        m = GS['terrain_map'].monster_at(new_pos)
        speed = self.speed
        if utils.adjacent(self.prev_pos, new_pos) and self.light() and m:
            GS['messages'].append("green: You gallantly charge the monster!")
            self.speed = 0
            
        if m != None:
            (self_dead, monster_dead) = self.attack_monster(GS, m)
            GS['messages'].append("green: You attack the "+m.name)
            
            if not monster_dead:
                GS['messages'].append("red: The "+m.name+" attacks you")
                GS['messages'].append("red: It's health is now "+str(m.health))
            else:
                GS['messages'].append("green: You vanquish the "+m.name)
                
                GS['terrain_map'].dungeon['monsters'].remove(m)
                if m.pos in GS['terrain_map'].dungeon['items']:
                    GS['terrain_map'].dungeon['items'][m.pos].append(random.choice(m.drops))
                else:
                    GS['terrain_map'].dungeon['items'][m.pos]= [random.choice(m.drops)]
                
            self.speed = speed

        decor = GS['terrain_map'].dungeon['decor']
        if new_pos in decor:
            if decor[new_pos] == 'FR' or decor[new_pos] == 'FL':
                decor[new_pos] = None
                player.health -= 1
                GS['messages'].append('The fire burns you.')
            elif decor[new_pos] == 'TTRAP':
                self.pos = random.choice(GS['terrain_map'].dungeon['rooms']).center
                GS['messages'].append('red: You stumble apon a teleport trap.')
                decor[new_pos] = 'TTRAPD'
            elif decor[new_pos] == 'DTRAP':
                if GS['terrain_map'].is_dungeons():
                    GS['messages'].append("light_blue: You decend.")
                    self.pos = GS['terrain_map'].generate_new_map()
                GS['messages'].append('red: You fall down a trap door.')
                decor[new_pos] = 'DTRAPD'
            elif decor[new_pos] == 'ITRAP':
                GS['messages'].append('light_blue: Ice creeps up your legs. You are frozen!')
                self.pos = self.prev_pos
                self.frozen = 4
                decor[new_pos] = 'ITRAPD'

