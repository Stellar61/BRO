from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from optimizer import solve_tsp
import os

app = FastAPI()

# Updated CORS configuration for port 3001
origins = [
    "http://localhost:3001",  # Primary frontend port
    "http://localhost:3000",  # Keep 3000 as fallback
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3000",
    "http://frontend:80",     # Docker service name
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

class OptimizeRequest(BaseModel):
    route_no: int

@app.post("/optimize")
def optimize(req: OptimizeRequest):
    try:
        # Load data
        df = pd.read_csv("data/routes_clean.csv")
        
        stops_for_route = df[df["R.No"].astype(str).str.strip() == str(req.route_no)]

        if stops_for_route.empty:
            return {"error": f"No stops found for Route {req.route_no}"}

        pts = [(row["lat"], row["lon"]) for _, row in stops_for_route.iterrows()]
        res = solve_tsp(pts, depot=0)

        if not res.get("order"):
            return {"error": "Could not compute route"}

        order = res["order"]
        ordered_points = []
        
        for i in order:
            if 0 <= i < len(stops_for_route):
                stop_info = stops_for_route.iloc[i]
                ordered_points.append({
                    "Boarding Point": stop_info["Boarding Point"],
                    "lat": float(stop_info["lat"]),
                    "lon": float(stop_info["lon"]),
                    "Time": str(stop_info["Time"])
                })

        return {
            "route_no": req.route_no,
            "optimized_order": ordered_points,
            "total_distance_km": res.get("total_distance_km", 0.0),
            "estimated_time_min": res.get("estimated_time_min", 0.0)
        }
    except Exception as e:
        return {"error": f"Server error: {str(e)}"}

@app.get("/")
def home():
    return {"message": "Bus Route Optimizer is running in Docker on port 3001!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Handle OPTIONS requests explicitly
@app.options("/optimize")
async def options_optimize():
    return {"message": "OK"}