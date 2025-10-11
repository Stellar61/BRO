from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

app = FastAPI()

class Point(BaseModel):
    lat: float
    lon: float

class RequestData(BaseModel):
    points: List[Point]

def haversine(a, b):
    import math
    R = 6371  # km
    dlat = math.radians(b.lat - a.lat)
    dlon = math.radians(b.lon - a.lon)
    aa = math.sin(dlat/2)**2 + math.cos(math.radians(a.lat)) * math.cos(math.radians(b.lat)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(aa), math.sqrt(1-aa))

def build_distance_matrix(points):
    size = len(points)
    return [[0 if i==j else int(haversine(points[i], points[j])*1000) for j in range(size)] for i in range(size)]

@app.post("/optimize")
def optimize_route(req: RequestData):
    points = req.points
    if len(points) < 2:
        return {"error": "At least two points required"}
    
    dist_matrix = build_distance_matrix(points)
    manager = pywrapcp.RoutingIndexManager(len(points), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        f, t = manager.IndexToNode(from_index), manager.IndexToNode(to_index)
        return dist_matrix[f][t]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(params)
    if not solution:
        return {"error": "No route found"}

    index = routing.Start(0)
    route_order = []
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        route_order.append(node)
        index = solution.Value(routing.NextVar(index))
    route_order.append(0)
    ordered_points = [points[i] for i in route_order]
    return {"optimized_order": ordered_points}
