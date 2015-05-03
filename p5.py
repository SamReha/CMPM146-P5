import sys
import json
from collections import namedtuple

import planner as Plan

# Helper functions!
def graph(state):
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)
            
def is_goal(state):
    goal_state = make_state(goal, items)
    for i in range(0, len(goal_state)):
        if state[i] < goal_state[i]:
            return False
    return True
    
def heuristic(state, goal_state):
    return 0
    
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
Recipe = namedtuple('Recipe',['name','check','effect','cost'])
all_recipes = []
for name, rule in Crafting['Recipes'].items():
    checker = make_checker(rule)
    effector = make_effector(rule)
    recipe = Recipe(name, checker, effector, rule['Time'])
    all_recipes.append(recipe)
    
initial_state = make_state(inventory, items)

cost, plan = Plan.search(graph, initial_state, is_goal, 10000, heuristic)

# Display plan
if plan is None:
    print "No plan could be found!"
else:
    print "Total Cost: " + str(cost)
    print plan