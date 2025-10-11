from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
from optimizer import solve_tsp

app = FastAPI()

# Comprehensive CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only - allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Handle preflight OPTIONS requests globally
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Add CORS headers to all responses
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
    return response

# Explicit OPTIONS handler for /optimize
@app.options("/optimize")
async def options_optimize():
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

class OptimizeRequest(BaseModel):
    route_no: int

@app.post("/optimize")
def optimize(req: OptimizeRequest):
    try:
        # Load cleaned CSV with lat/lon already present
        df = pd.read_csv("data/routes_clean.csv")

        # make robust string match for route number
        stops_for_route = df[df["R.No"].astype(str).str.strip() == str(req.route_no)]

        if stops_for_route.empty:
            return {"error": f"No stops found for Route {req.route_no}"}

        # Create coordinate list (lat, lon)
        pts = [(row["lat"], row["lon"]) for _, row in stops_for_route.iterrows()]

        # Solve TSP (returns order + totals)
        res = solve_tsp(pts, depot=0)

        if not res.get("order"):
            return {"error": "Could not compute route"}

        order = res["order"]

        # Map back to stop names (use iloc positions)
        ordered_points = []
        for i in order:
            # protect against indexes out of range
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
    return {"message": "Bus Route Optimizer is running!"}