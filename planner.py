from math import sqrt
from heapq import heappush, heappop

def search(graph, back_graph, initial, goal, limit, heuristic):
    def is_equal(state, goal_state):
        for i in range(0, len(goal_state)):
            if state[i] < goal_state[i]:
                return False
        return True
        
    found_path = False

    total_cost = 0
    plan = None
    iterations = 0
    
    cost = {}
    back_cost = {}
    prev = {}
    back_prev = {}
    
    visit = []
    back_visit = []
    
    verbose = {}
    q = []

    cost[initial] = 0
    prev[initial] = None
    
    back_cost[goal] = 0
    back_prev[goal] = None
    
    verbose[initial] = ("no_action", initial, 0)
    verbose[goal] = ("no_action", goal, 0)      # This is not correct, but will stop it from crashing.
    heappush(q, (cost[initial], initial, "forward"))
    heappush(q, (back_cost[goal], goal, "backward"))

    while len(q) > 0 and iterations < limit:
        _, u, direction = heappop(q)
        
        if (direction is "forward" and u in back_visit) or is_equal(u, goal):
            found_path = True
            break
        elif direction is "backward" and u in visit:
            found_path = True
            break

        if direction is "forward":
            neighborhood = graph(u, goal)

            for neighbor in neighborhood:
                name, effect, neighborCost = neighbor
                alt = cost[u] + neighborCost
                if effect not in cost or alt < cost[effect]:
                    visit.append(effect)
                    cost[effect] = alt
                    prev[effect] = u
                    verbose[effect] = neighbor
                    heappush(q, (alt + heuristic(effect, goal), effect, "forward"))
        else:
            neighborhood = back_graph(u, initial)

            for neighbor in neighborhood:
                name, uneffect, neighborCost = neighbor
                alt = back_cost[u] + neighborCost
                if uneffect not in back_cost or alt < back_cost[uneffect]:
                    back_visit.append(uneffect)
                    back_cost[uneffect] = alt
                    back_prev[uneffect] = u
                    verbose[uneffect] = neighbor
                    heappush(q, (alt + heuristic(uneffect, initial), uneffect, "backward"))
                
        iterations += 1
        
    print "Iterations: " + str(iterations)

    if found_path:
        backward_u = u
        forward_u = u
        
        plan = []
        total_cost = cost[u]    # This wont work bidirectionally
        
        while forward_u:
            plan.append(verbose[forward_u])
            forward_u = prev[forward_u]
        plan.reverse()
        
        while backward_u:
            print "AAAAAAAHHHHHH"
            plan.append(verbose[backward_u])    # This does repeat u.
            backward_u = back_prev.get(backward_u, None)
        
        return total_cost, plan
    else:
        return 0, None

    return total_cost, plan