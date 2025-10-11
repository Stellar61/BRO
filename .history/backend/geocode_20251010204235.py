import requests, time
import pandas as pd

df = pd.read_excel("C:\BRO\Main Routes (1).xlsx")

def geocode(name):
    r = requests.get("https://nominatim.openstreetmap.org/search",
                     params={"q": name, "format": "json", "limit": 1},
                     headers={"User-Agent": "bus-route-opt-demo/1.0"})
    if r.ok and r.json():
        return float(r.json()[0]["lat"]), float(r.json()[0]["lon"])
    return None, None

rows = []
for _, row in df.iterrows():
    stop = row["Boarding Point"]
    lat, lon = geocode(stop)
    if lat is not None and lon is not None:
        rows.append({"R.No": row["R.No"], "Boarding Point": stop,
                     "Time": row["Time"], "lat": lat, "lon": lon})
    else:
        print(f"Skipping '{stop}' (no result found)")
    time.sleep(1)  # respect rate limit

clean_df = pd.DataFrame(rows)
clean_df.to_csv("routes_clean.csv", index=False)
print(f"Saved {len(clean_df)} valid stops to routes_clean.csv")
