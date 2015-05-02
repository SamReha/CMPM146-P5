import sys
import json
from collections import namedtuple

import planner as Plan

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

# Convert recipes into more efficient format
Recipe = namedtuple('Recipe',['name','check','effect','cost'])
all_recipes = []
for name, rule in Crafting['Recipes'].items():
    checker = make_checker(rule)
    effector = make_effector(rule)
    recipe = Recipe(name, checker, effector, rule['Time'])
    all_recipes.append(recipe)

plan = Plan.get_plan(items, inventory, goal, all_recipes)

# Display plan
if plan is None:
    print "No plan could be found!"
else:
    print plan