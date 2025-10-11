import React, { useState } from "react";

function App() {
  const [routeNo, setRouteNo] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const API_URL = process.env.REACT_APP_API_URL || "http://backend:8000";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setData(null);
    try {
      const res = await fetch(`${API_URL}/optimize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ route_no: routeNo }),
      });
      const json = await res.json();
      setData(json);
    } catch (err) {
      alert("Error connecting to backend");
    }
    setLoading(false);
  };

  return (
    <div style={{ margin: "30px", fontFamily: "Arial" }}>
      <h1>🚌 Bus Route Optimization</h1>
      <form onSubmit={handleSubmit}>
        <label>Enter Route No: </label>
        <input
          type="number"
          value={routeNo}
          onChange={(e) => setRouteNo(e.target.value)}
          style={{ marginRight: "10px" }}
        />
        <button type="submit">Optimize</button>
      </form>

      {loading && <p>Calculating best route...</p>}

      {data && data.optimized_order && (
        <div style={{ marginTop: "20px" }}>
          <h2>Optimized Route (#{data.route_no})</h2>
          <p>Total Distance: {data.total_distance_km} km</p>
          <p>Estimated Time: {data.estimated_time_min} minutes</p>
          <table border="1" cellPadding="6">
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

      {data && data.error && <p style={{ color: "red" }}>⚠️ {data.error}</p>}
    </div>
  );
}

export default App;
