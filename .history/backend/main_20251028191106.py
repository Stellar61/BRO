# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# import math
# from itertools import permutations

# app = FastAPI()

# # Allow CORS for frontend (update URL if needed)
# origins = [
#     "https://bro-frontend-app.azurewebsites.net",
#     "http://localhost:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Dataset file path
# DATA_PATH = "data/routes_sorted_with_students.csv"

# # College coordinates (Final Destination)
# COLLEGE_NAME = "Rajalakshmi Engineering College"
# COLLEGE_LAT = 13.008313
# COLLEGE_LON = 80.003310


# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371  # Earth radius in km
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
#     return 2 * R * math.asin(math.sqrt(a))


# @app.get("/")
# def home():
#     return {"message": "Backend is running successfully"}


# @app.post("/optimize")
# def optimize_route(data: dict):
#     route_no = str(data.get("route_no")).strip().upper()  # Accept "1B", "40C" etc.

#     # Load dataset
#     df = pd.read_csv(DATA_PATH)

#     # Filter bus route
#     route_df = df[df["route_no"].astype(str).str.upper() == route_no]

#     if route_df.empty:
#         raise HTTPException(status_code=404, detail=f"Route {route_no} not found in dataset")

#     # 1️⃣ Filter routes with total students <= 15
#     total_students = route_df["students_per_stop"].sum()
#     if total_students <= 15:
#         removed_stops = route_df.to_dict(orient="records")
#         return {
#             "route_no": route_no,
#             "message": f"Removed route {route_no} — only {total_students} students total.",
#             "removed_stops": removed_stops,
#         }

#     # 2️⃣ Optimize stop order based on distance
#     stops = route_df[["stop_name", "latitude", "longitude"]].dropna().to_dict(orient="records")

#     # Append College as final destination
#     stops.append({
#         "stop_name": COLLEGE_NAME,
#         "latitude": COLLEGE_LAT,
#         "longitude": COLLEGE_LON
#     })

#     best_order = None
#     min_distance = float("inf")

#     for perm in permutations(stops[:-1]):  # keep college as last stop
#         order = list(perm) + [stops[-1]]
#         distance = sum(
#             haversine(order[i]["latitude"], order[i]["longitude"],
#                       order[i + 1]["latitude"], order[i + 1]["longitude"])
#             for i in range(len(order) - 1)
#         )
#         if distance < min_distance:
#             min_distance = distance
#             best_order = order

#     estimated_time = round((min_distance / 30) * 60, 2)  # assuming 30km/h average

#     return {
#         "route_no": route_no,
#         "optimized_order": best_order,
#         "total_distance_km": round(min_distance, 2),
#         "estimated_time_min": estimated_time,
#         "removed_stops": [],  # no stops removed in this valid route
#     }


from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from optimizer import optimize_route

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Bus Route Optimizer API is running!"}

@app.get("/optimize-route")
def optimize_route_api(bus_number: str = Query(..., description="Bus route number")):
    result = optimize_route(bus_number)
    return result
