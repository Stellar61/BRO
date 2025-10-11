# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from optimizer import solve_tsp
import os
import requests

app = FastAPI()

class Stop(BaseModel):
    stop: str
    lat: float
    lon: float

class OptimizeRequest(BaseModel):
    route_no: int    # R.No to optimize
    # either provide points inline or server will look up stops from CSV
    points: list[Stop] = None

@app.post("/optimize")
def optimize(req: OptimizeRequest):
    # load stops mapping if not provided
    if not req.points:
        df = pd.read_csv("routes.csv")
        stops_for_route = df[df["R.No"] == req.route_no]["Boarding Point"].tolist()
        # assume stops_geocoded.csv exists
        geo = pd.read_csv("stops_geocoded.csv").set_index("stop")
        pts = []
        for s in stops_for_route:
            lat = geo.loc[s]["lat"]
            lon = geo.loc[s]["lon"]
            pts.append((float(lat), float(lon)))
    else:
        pts = [(p.lat, p.lon) for p in req.points]
    order = solve_tsp(pts, depot=0)
    ordered_points = [ {"index": i, "lat": pts[i][0], "lon": pts[i][1]} for i in order ]
    # optional: call Azure OpenAI to explain
    explanation = ""
    if os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_KEY") and os.getenv("AZURE_OPENAI_DEPLOYMENT"):
        summary = f"Route {req.route_no} optimized visiting order: {ordered_points}"
        try:
            explanation = call_openai(summary)
        except Exception as e:
            explanation = f"openai error: {e}"
    return {"route_no": req.route_no, "ordered_points": ordered_points, "explanation": explanation}

def call_openai(summary: str):
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    key = os.getenv("AZURE_OPENAI_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    url = f"{endpoint}/openai/deployments/{deployment}/completions?api-version=2023-05-15"
    payload = {"prompt": f"Explain this bus route and suggest 3 improvements:\n\n{summary}\n", "max_tokens":200}
    resp = requests.post(url, json=payload, headers={"api-key":key})
    resp.raise_for_status()
    j = resp.json()
    return j.get("choices", [{}])[0].get("text","")
