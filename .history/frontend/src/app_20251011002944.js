import React, { useState } from "react";
import RouteInput from "./components/RouteInput";
import RouteMap from "./components/RouteMap";
import RouteList from "./components/RouteList";
import "./App.css";

function App() {
  const [optimizedRoute, setOptimizedRoute] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleOptimize = async (routeNo) => {
    setLoading(true);
    setError("");
    setOptimizedRoute(null);

    try {
      const response = await fetch("http://localhost:8000/optimize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ route_no: parseInt(routeNo) }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to optimize route");
      }

      setOptimizedRoute(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🚌 Bus Route Optimizer</h1>
        <p>Enter a route number to find the optimized bus route</p>
      </header>

      <main className="app-main">
        <RouteInput onOptimize={handleOptimize} loading={loading} />

        {error && <div className="error-message">❌ {error}</div>}

        {optimizedRoute && (
          <div className="results-container">
            <div className="route-summary">
              <h2>Route {optimizedRoute.route_no} - Optimized Path</h2>
              <div className="stats">
                <span className="stat">
                  📏 Total Distance:{" "}
                  <strong>{optimizedRoute.total_distance_km} km</strong>
                </span>
                <span className="stat">
                  ⏱️ Estimated Time:{" "}
                  <strong>{optimizedRoute.estimated_time_min} min</strong>
                </span>
                <span className="stat">
                  🛑 Total Stops:{" "}
                  <strong>{optimizedRoute.optimized_order.length}</strong>
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
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
