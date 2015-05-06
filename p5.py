import sys
import json
from collections import namedtuple

import planner as Plan

# Helper functions!
def graph(state, goal):
    for r in all_recipes:
        if r.check(state) and not_redundant(state, goal, r):
            yield (r.name, r.effect(state), r.cost)
            
def not_redundant(cur_state, end_state, rec):
    if rec.name is "craft wooden_pickaxe at bench":
        if cur_state[16] >= end_state[16]:
            return False
    elif rec.name is "craft stone_pickaxe at bench":
        if cur_state[13] >= end_state[13]:
            return False
    elif rec.name is "craft iron_pickaxe at bench":
        if cur_state[7] >= end_state[7]:
            return False
    elif rec.name is "craft wooden_axe at bench":
        if cur_state[15] >= end_state[15]:
            return False
    elif rec.name is "craft stone_axe at bench":
        if cur_state[12] >= end_state[12]:
            return False
    elif rec.name is "craft iron_pickaxe at bench":
        if cur_state[14] >= end_state[14]:
            return False
    elif rec.name is "craft furnace at bench":
        if cur_state[4] >= end_state[4]:
            return False
    elif rec.name is "craft bench":
        if cur_state[0] >= end_state[0]:
            return False
    else:
        return True

def back_graph(state, initial):
    for r in all_recipes:
        if r.uncheck(state):
            yield (r.name, r.uneffect(state), r.cost)
        
def heuristic(state, end_state):
    distance = 0
    
    for i in range(0, len(end_state)):
        sub_distance = end_state[i] - state[i]
        if sub_distance > 0:
            distance += sub_distance
    
    return distance
    
def make_state(inventory, item_set):
    state = []
    
    for i in range(0, len(item_set)):
        if item_set[i] in inventory:
            state.append(inventory[item_set[i]])
        else:
            state.append(0)
    
    return tuple(state)
    
def get_item_dictionary(item_set):
    itemDict = dict()
    for i in range(0, len(item_set)):
        itemDict[item_set[i]] = i
        
    return itemDict

# Prototypes for make_checker and make_effector. These will be used in the process of 
# converting the recipes into a more efficient format.
def make_checker(rule):
    # this code runs once
    # do something with rule['Consumes'] and rule['Requires']
    try:
        requirements = rule['Requires'].copy()
    except KeyError:
        requirements = dict()
    
    try:
        consumes = rule['Consumes'].copy()
    except KeyError:
        consumes = dict()
    
    for key in requirements:
        requirements[key] = 1
        
    consumes.update(requirements)
    def check(state):
        # this code runs millions of times
        for item in consumes:
            indexOfItem = itemDict[item]
            if consumes[item] > state[indexOfItem]:
                return False
        
        return True # or False
    
    return check

def make_effector(rule):
    # this code runs once
    # do something with rule['Produces'] and rule['Consumes']
    toAdd = {}
    toRemove = {}
    
    for item in rule['Produces']:
        toAdd[item] = rule['Produces'][item]
            
    try:
        for item in rule['Consumes']:
            toRemove[item] = rule['Consumes'][item]
    except KeyError:
        toRemove = {}
        
    def effect(state):
        # this code runs millions of times
        next_state = list(state)
        for item in toAdd:
            next_state[itemDict[item]] += toAdd[item]
            
        for item in toRemove:
            next_state[itemDict[item]] -= toRemove[item]
        
        return tuple(next_state)
    
    return effect
    
def make_unchecker(rule):
    try:
        produces = rule['Produces'].copy()
    except KeyError:
        produces = dict()

    def uncheck(state):
        # this code runs millions of times
        for item in produces:
            indexOfItem = itemDict[item]
            if produces[item] <= state[indexOfItem]:
                return True
        
        return False # or False
    
    return uncheck
    
def make_uneffector(rule):
    toAdd = {}
    toRemove = {}
    
    for item in rule['Produces']:
        toAdd[item] = rule['Produces'][item]
            
    try:
        for item in rule['Consumes']:
            toRemove[item] = rule['Consumes'][item]
    except KeyError:
        toRemove = {}
        
    def uneffect(state):
        # this code runs millions of times
        next_state = list(state)
        for item in toAdd:
            next_state[itemDict[item]] -= toAdd[item]
            
        for item in toRemove:
            next_state[itemDict[item]] += toRemove[item]
        
        return tuple(next_state)
    
    return uneffect

# Try to open up the passed-in file, handle errors nicely.
try:
    with open(sys.argv[1]) as f:
        Crafting = json.load(f)
except IndexError:
    print "Usage Error: p5.py [crafting_file]"
    exit()
except IOError:
    print "Usage Error: " + sys.argv[1] + " could not be found."
    exit()
    
items, inventory, goal = Crafting['Items'], Crafting['Initial'], Crafting['Goal']

itemDict = get_item_dictionary(items)

# Convert recipes into more efficient format
Recipe = namedtuple('Recipe',['name','check','effect','uncheck', 'uneffect', 'cost'])
all_recipes = []
for name, rule in Crafting['Recipes'].items():
    checker = make_checker(rule)
    effector = make_effector(rule)
    
    unchecker = make_unchecker(rule)
    uneffector = make_uneffector(rule)
    
    recipe = Recipe(name, checker, effector, unchecker, uneffector, rule['Time'])
    all_recipes.append(recipe)
    
initial_state = make_state(inventory, items)
goal_state = make_state(goal, items)

#cost, plan = Plan.search(graph, initial_state, goal_state, 166666, heuristic)
cost, plan = Plan.search(graph, back_graph, initial_state, goal_state, 333332, heuristic)

# Display plan
if plan is None:
    print "No plan could be found!"
else:
    print "Total Cost: " + str(cost)
    print plan