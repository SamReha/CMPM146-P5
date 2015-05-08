import sys
import json
from collections import namedtuple

import planner as Plan

# Helper functions!
def graph(state, goal):
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)

def back_graph(state, initial):
    for r in all_recipes:
        if r.uncheck(state):
            yield (r.name, r.uneffect(state), r.cost)
        
def heuristic(state, end_state):
    distance = 0
    
    # Check that we aren't redundant for non-consumable items
    for item in non_consumables:
        index = itemDict[item]
        if state[index] > end_state[index] and state[index] > 1:
            return sys.maxint

    # Check that we aren't redundant for consumable items
    for item in consumables:
        index = itemDict[item]
        if state[index] > consumables[item] and state[index] > end_state[index]:
            return sys.maxint
    
    # If we've gotten this far, we know this state has no redundancies. Return diff of current state and end_state
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
    consumes, requires = rule.get('Consumes', {}), rule.get('Requires', {})
    consumption_pairs = [(itemDict[item],consumes[item]) for item in consumes]
    requirement_pairs = [(itemDict[item],1) for item in requires]
    both_pairs = consumption_pairs + requirement_pairs

    def check(state):
        return all([state[i] >= v for i,v in both_pairs])

    return check
    
def make_effector(rule):
    produces, consumes = rule.get('Produces', {}), rule.get('Consumes', {})
    willProduce = [(itemDict[item], produces[item]) for item in produces]
    willConsume = [(itemDict[item], consumes[item]*(-1)) for item in consumes]
    delta_pairs = willProduce + willConsume
    
    def effect(state):
        new_state = list(state)
        for pair in delta_pairs:
            index, shift = pair
            new_state[index] += shift
        return tuple(new_state)
        
    return effect
  
def make_unchecker(rule):
    produces = rule.get('Produces', {})
    willProduce = [(itemDict[item], produces[item]) for item in produces]
    
    def uncheck(state):
        return all([state[i] >= v for i, v in willProduce])

    return uncheck
    
def make_uneffector(rule):
    produces, consumes = rule.get('Produces', {}), rule.get('Consumes', {})
    willProduce = [(itemDict[item], produces[item]*(-1)) for item in produces]
    willConsume = [(itemDict[item], consumes[item]) for item in consumes]
    delta_pairs = willProduce + willConsume
    
    def uneffect(state):
        new_state = list(state)
        for pair in delta_pairs:
            index, shift = pair
            new_state[index] += shift
        return tuple(new_state)

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
non_consumables = []
consumables = {}

# Build list of non_consumables
for i in [0, 1, 4, 6, 7, 12, 13, 15, 16]:
    non_consumables.append(items[i])
    
# Build dictionary of max number of required consumables
consumables['coal'] = 1
consumables['ore'] = 1
consumables['ingot'] = 6
consumables['plank'] = 4
consumables['stick'] = 4
consumables['wood'] = 1
consumables['cobble'] = 8

    

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
    for i in range(0, len(plan)):
        print plan[i]