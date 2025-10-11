import React, { useState } from "react";
import "./App.css";

function App() {
  const [routeNo, setRouteNo] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  // when the app is loaded in the browser, window.location.hostname is the host (e.g., localhost)
  const API_URL =
    process.env.REACT_APP_API_URL ||
    `${window.location.protocol}//${window.location.hostname}:8000`;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!routeNo) return alert("Enter route number");
    setLoading(true);
    setData(null);
    try {
      const res = await fetch(`${API_URL}/optimize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ route_no: Number(routeNo) }),
      });
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("Fetch error:", err);
      alert(
        "Error connecting to backend. Make sure backend is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>🚌 Bus Route Optimizer</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Route No:&nbsp;
          <input
            type="number"
            value={routeNo}
            onChange={(e) => setRouteNo(e.target.value)}
          />
        </label>
        &nbsp;
        <button type="submit">Optimize</button>
      </form>

      {loading && <p>Calculating best route...</p>}

      {data && data.error && <p style={{ color: "red" }}>⚠ {data.error}</p>}

      {data && data.optimized_order && (
        <div style={{ marginTop: 16 }}>
          <h2>Optimized Route (#{data.route_no})</h2>
          <p>Total Distance: {data.total_distance_km} km</p>
          <p>Estimated Time: {data.estimated_time_min} minutes</p>
          <table>
            <thead>
              <tr>
                <th>Order</th>
                <th>Stop Name</th>
                <th>Latitude</th>
                <th>Longitude</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {data.optimized_order.map((stop, i) => (
                <tr key={i}>
                  <td>{i + 1}</td>
                  <td>{stop["Boarding Point"]}</td>
                  <td>{stop.lat}</td>
                  <td>{stop.lon}</td>
                  <td>{stop.Time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
