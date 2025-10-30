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
    route_no: str  # supports alphanumeric routes like '1B', '10C'

# --- CONSTANTS ---
COLLEGE_NAME = "Rajalakshmi Engineering College"
COLLEGE_COORDS = (13.008313, 80.003310)

@app.post("/optimize")
def optimize(req: OptimizeRequest):
    # --- Load dataset ---
    df = pd.read_csv("data/routes_sorted_with_students.csv")

    # --- Normalize route numbers for matching ---
    route_str = str(req.route_no).strip().upper()
    df["R.No"] = df["R.No"].astype(str).str.strip().str.upper()

    stops_for_route = df[df["R.No"] == route_str]

    # --- Handle missing routes ---
    if stops_for_route.empty:
        available_routes = df["R.No"].unique().tolist()
        sample_routes = available_routes[:50]  # avoid huge output
        return {
            "error": f"No stops found for Route {req.route_no}. "
                     f"Available routes (sample): {sample_routes}..."
        }

    # --- Student count validation ---
    total_students = stops_for_route["students per stop"].sum()
    if total_students < 15:
        return {
            "message": f"This bus route ({req.route_no}) is removed — total students ({total_students}) < 15"
        }

    # --- Create coordinates list for all stops ---
    pts = [(row["lat"], row["lon"]) for _, row in stops_for_route.iterrows()]

    # --- Add final destination (college) ---
    college_index = len(stops_for_route)
    pts.append(COLLEGE_COORDS)

    # --- Solve TSP ONLY for pickup stops (exclude college) ---
    res = solve_tsp(pts[:-1], depot=0)

    if not res.get("order"):
        return {"error": "Could not compute route"}

    order = res["order"]

    # --- Force the final destination to be college ---
    order.append(college_index)

    # --- Map back the ordered stops ---
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
            ordered_points.append({
                "Boarding Point": COLLEGE_NAME,
                "lat": COLLEGE_COORDS[0],
                "lon": COLLEGE_COORDS[1],
                "Time": "N/A",
                "students": 0
            })

    # --- Final response ---
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
    return {"message": "Bus Route Optimizer backend is running with final destination fixed!"}
