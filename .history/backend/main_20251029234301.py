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
    route_no: str

# --- CONSTANTS ---
COLLEGE_NAME = "Rajalakshmi Engineering College"
COLLEGE_COORDS = (13.008313, 80.003310)

@app.post("/optimize")
def optimize(req: OptimizeRequest):
    # --- Load dataset ---
    df = pd.read_csv("data/routes_sorted_with_students.csv")

    # --- Clean and normalize route numbers ---
    df["R.No"] = (
        df["R.No"]
        .astype(str)
        .str.replace(" ", "", regex=False)
        .str.strip()
        .str.upper()
    )

    route_str = str(req.route_no).replace(" ", "").strip().upper()

    stops_for_route = df[df["R.No"] == route_str]

    if stops_for_route.empty:
        return {"error": f"No stops found for Route {req.route_no}. "
                         f"Available routes: {sorted(df['R.No'].unique().tolist())[:10]}..."}

    # --- Check total students ---
    total_students = stops_for_route["students per stop"].sum()
    if total_students < 15:
        return {"message": f"This bus route ({req.route_no}) is removed — total students ({total_students}) < 15"}

    # --- Create coordinates list ---
    pts = [(row["lat"], row["lon"]) for _, row in stops_for_route.iterrows()]
    pts.append(COLLEGE_COORDS)  # Add final destination

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
