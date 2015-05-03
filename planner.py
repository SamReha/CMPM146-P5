from math import sqrt
from heapq import heappush, heappop

def search(graph, initial, is_goal, limit, heuristic):
    total_cost = 0
    plan = None
    
    cost = {}
    prev = {}
    verbose = {}
    q = []

    cost[initial] = 0
    prev[initial] = None
    verbose[initial] = ("no_action", initial, 0)
    heappush(q, (cost[initial], initial))

    while len(q) > 0:
        _, u = heappop(q)

        if is_goal(u):
            break

        neighborhood = graph(u)

        for neighbor in neighborhood:
            name, effect, neighborCost = neighbor
            alt = cost[u] + neighborCost
            if effect not in cost or alt < cost[effect]:
                cost[effect] = alt
                prev[effect] = u
                verbose[effect] = neighbor
                heappush(q, (alt, effect))

    if is_goal(u):
        plan = []
        total_cost = cost[u]
        while u:
            plan.append(verbose[u])
            u = prev[u]
        plan.reverse()
        return total_cost, plan
    else:
        return 0, []

    return total_cost, plan