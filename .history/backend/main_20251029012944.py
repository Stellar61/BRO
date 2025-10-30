# from fastapi import FastAPI
# from pydantic import BaseModel
# import pandas as pd
# from optimizer import solve_tsp
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# # Updated CORS configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://localhost:3001",
#         "http://127.0.0.1:3000",
#         "http://127.0.0.1:3001",
#         "https://bro-frontend-pk.azurewebsites.net"  # Add this for Azure
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
# )

# class OptimizeRequest(BaseModel):
#     route_no: int

# @app.post("/optimize")
# def optimize(req: OptimizeRequest):
#     # Load cleaned CSV with lat/lon already present
#     df = pd.read_csv("data/routes_clean.csv")

#     # make robust string match for route number
#     stops_for_route = df[df["R.No"].astype(str).str.strip() == str(req.route_no)]

#     if stops_for_route.empty:
#         return {"error": f"No stops found for Route {req.route_no}"}

#     # Create coordinate list (lat, lon)
#     pts = [(row["lat"], row["lon"]) for _, row in stops_for_route.iterrows()]

#     # Solve TSP (returns order + totals)
#     res = solve_tsp(pts, depot=0)

#     if not res.get("order"):
#         return {"error": "Could not compute route"}

#     order = res["order"]

#     # Map back to stop names (use iloc positions)
#     ordered_points = []
#     for i in order:
#         # protect against indexes out of range
#         if 0 <= i < len(stops_for_route):
#             stop_info = stops_for_route.iloc[i]
#             ordered_points.append({
#                 "Boarding Point": stop_info["Boarding Point"],
#                 "lat": float(stop_info["lat"]),
#                 "lon": float(stop_info["lon"]),
#                 "Time": str(stop_info["Time"])
#             })

#     return {
#         "route_no": req.route_no,
#         "optimized_order": ordered_points,
#         "total_distance_km": res.get("total_distance_km", 0.0),
#         "estimated_time_min": res.get("estimated_time_min", 0.0)
#     }

# # Add this to handle OPTIONS requests explicitly
# @app.options("/optimize")
# async def options_optimize():
#     return {"message": "OK"}

# @app.get("/")
# def home():
#     return {"message": "Bus Route Optimizer is running!"}

from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from optimizer import solve_tsp
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- CORS SETTINGS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://bro-frontend-pk.azurewebsites.net"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- INPUT MODEL ---
class OptimizeRequest(BaseModel):
    route_no: str  # changed from int to str

# --- CONSTANTS ---
COLLEGE_NAME = "Rajalakshmi Engineering College"
COLLEGE_COORDS = (13.008313, 80.003310)

@app.post("/optimize")
def optimize(req: OptimizeRequest):
    # --- Load new dataset ---
    df = pd.read_csv("data/routes_sorted_with_students.csv")

    # --- Filter by route number (string-safe) ---
    route_str = str(req.route_no).strip().upper()
    df["R.No"] = df["R.No"].astype(str).str.strip().str.upper()

    stops_for_route = df[df["R.No"] == route_str]

    if stops_for_route.empty:
        return {"error": f"No stops found for Route {req.route_no}"}

    # --- Check total students ---
    total_students = stops_for_route["students per stop"].sum()
    if total_students < 15:
        return {"message": f"This bus route ({req.route_no}) is removed — total students ({total_students}) < 15"}

    # --- Create coordinates list ---
    pts = [(row["lat"], row["lon"]) for _, row in stops_for_route.iterrows()]

    # --- Add final destination (college) ---
    pts.append(COLLEGE_COORDS)

    # --- Solve TSP ---
    res = solve_tsp(pts, depot=0)

    if not res.get("order"):
        return {"error": "Could not compute route"}

    order = res["order"]

    # --- Map back to stops ---
    ordered_points = []
    for i in order:
        if i < len(stops_for_route):
            stop_info = stops_for_route.iloc[i]
            ordered_points.append({
                "Boarding Point": stop_info["Boarding Point"],
                "lat": float(stop_info["lat"]),
                "lon": float(stop_info["lon"]),
                "Time": str(stop_info["Time"]),
                "students": int(stop_info["students per stop"])
            })
        elif i == len(stops_for_route):
            # Add college stop as final
            ordered_points.append({
                "Boarding Point": COLLEGE_NAME,
                "lat": COLLEGE_COORDS[0],
                "lon": COLLEGE_COORDS[1],
                "Time": "N/A",
                "students": 0
            })

    return {
        "route_no": req.route_no,
        "optimized_order": ordered_points,
        "total_students": int(total_students),
        "total_distance_km": res.get("total_distance_km", 0.0),
        "estimated_time_min": res.get("estimated_time_min", 0.0),
        "final_stop": COLLEGE_NAME
    }

@app.options("/optimize")
async def options_optimize():
    return {"message": "OK"}

@app.get("/")
def home():
    return {"message": "Bus Route Optimizer backend is running!"}
