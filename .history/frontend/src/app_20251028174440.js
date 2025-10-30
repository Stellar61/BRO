import React, { useState } from "react";
import RouteMap from "./RouteMap";
import RouteList from "./RouteList";
import "./App.css";

function App() {
  const [routeNo, setRouteNo] = useState("");
  const [optimizedRoute, setOptimizedRoute] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const backendUrl = "https://bro-backend-app.azurewebsites.net";

  const handleOptimize = async () => {
    setLoading(true);
    setError("");
    setOptimizedRoute(null);

    try {
      const response = await fetch(`${backendUrl}/optimize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ route_no: routeNo.trim() }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to fetch route");
      }

      setOptimizedRoute(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1 className="title">🚍 Bus Route Optimizer</h1>

      <div className="input-container">
        <input
          type="text"
          value={routeNo}
          onChange={(e) => setRouteNo(e.target.value)}
          placeholder="Enter bus route number (e.g. 1B, 40C)"
          className="route-input"
        />
        <button onClick={handleOptimize} disabled={!routeNo || loading}>
          {loading ? "Optimizing..." : "Optimize Route"}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {optimizedRoute && (
        <div className="results-container">
          {/* Case 1: Route Removed (<= 15 students) */}
          {optimizedRoute.removed_stops &&
          optimizedRoute.removed_stops.length > 0 ? (
            <div className="removed-route">
              <h2>❌ Route {optimizedRoute.route_no} Removed</h2>
              <p>{optimizedRoute.message}</p>
              <div className="removed-list">
                <h3>Removed Stops:</h3>
                <ul>
                  {optimizedRoute.removed_stops.map((stop, i) => (
                    <li key={i}>
                      🚌{" "}
                      <strong>
                        {stop.stop_name || stop["Boarding Point"]}
                      </strong>{" "}
                      — {stop.students_per_stop} students
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            /* Case 2: Valid Optimized Route */
            <>
              <div className="route-summary">
                <h2>✅ Route {optimizedRoute.route_no} - Optimized Path</h2>
                <div className="stats">
                  <span className="stat">
                    📏 <strong>{optimizedRoute.total_distance_km} km</strong>
                  </span>
                  <span className="stat">
                    ⏱️ <strong>{optimizedRoute.estimated_time_min} min</strong>
                  </span>
                  <span className="stat">
                    🛑 <strong>{optimizedRoute.optimized_order.length}</strong>{" "}
                    stops
                  </span>
                </div>
              </div>

              <div className="results-layout">
                <div className="map-container">
                  <RouteMap stops={optimizedRoute.optimized_order} />
                </div>
                <div className="list-container">
                  <RouteList stops={optimizedRoute.optimized_order} />
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
