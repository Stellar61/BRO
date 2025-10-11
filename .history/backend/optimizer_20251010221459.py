import math
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def haversine_m(a, b):
    R = 6371000.0  # meters
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    aa = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return int(R * 2 * math.atan2(math.sqrt(aa), math.sqrt(1-aa)))

def build_distance_matrix(coords):
    n = len(coords)
    d = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                d[i][j] = haversine_m(coords[i], coords[j])
    return d

def solve_tsp(coords, depot=0):
    n = len(coords)
    dm = build_distance_matrix(coords)
    manager = pywrapcp.RoutingIndexManager(n, 1, depot)
    routing = pywrapcp.RoutingModel(manager)

    def dist_fn(i, j):
        return dm[manager.IndexToNode(i)][manager.IndexToNode(j)]

    transit_idx = routing.RegisterTransitCallback(dist_fn)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_params)
    if not solution:
        return []

    index = routing.Start(0)
    route = []
    while not routing.IsEnd(index):
        route.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    route.append(manager.IndexToNode(index))
    return route
