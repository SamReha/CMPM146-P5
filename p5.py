import json
from collections import namedtuple

# Prototypes for make_checker and make_effector. These will be used in the process of 
# converting the recipes into a more efficient format.
def make_checker(rule):
    # this code runs once
    # do something with rule['Consumes'] and rule['Requires']
    def check(state):
        # this code runs millions of times
        return True # or False
    
    return check

def make_effector(rule):
    # this code runs once
    # do something with rule['Produces'] and rule['Consumes']
    def effect(state):
        # this code runs millions of times
        return next_state
    
    return effect

with open('Crafting.json') as f:
	Crafting = json.load(f)
    
items, inventory, goal = Crafting['Items'], Crafting['Initial'], Crafting['Goal']

Recipe = namedtuple('Recipe',['name','check','effect','cost'])
all_recipes = []
for name, rule in Crafting['Recipes'].items():
    checker = make_checker(rule)
    effector = make_effector(rule)
    recipe = Recipe(name, checker, effector, rule['Time'])
    all_recipes.append(recipe)
    
# Test json reading by printing some crap out to the console.
# List of items that can be in your inventory:
print "Item Set: " + str(items)

# List of items in your initial inventory with amounts:
print "Inventory: " + str(inventory)

# List of items needed to be in your inventory at the end of the plan:
# (okay to have more than this; some might be satisfied by initial inventory)
print "Goal: " + str(goal)