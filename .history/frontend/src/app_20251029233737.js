import React, { useState } from "react";
import RouteInput from "./components/RouteInput";
import RouteMap from "./components/RouteMap";
import RouteList from "./components/RouteList";
import "./App.css";

function App() {
  const [optimizedRoute, setOptimizedRoute] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [routeRemoved, setRouteRemoved] = useState(false);

  const BACKEND_URL =
    process.env.REACT_APP_BACKEND_URL ||
    "https://bro-backend-pk.azurewebsites.net";

  const handleOptimize = async (routeNo) => {
    setLoading(true);
    setError("");
    setOptimizedRoute(null);
    setRouteRemoved(false);

    try {
      console.log(`🔄 Optimizing route ${routeNo}...`);

      const response = await fetch(`${BACKEND_URL}/optimize`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ route_no: routeNo }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      // If backend says route is removed
      if (data.message && data.message.includes("removed")) {
        setRouteRemoved(true);
        return;
      }

      setOptimizedRoute(data);
      console.log("✅ Optimization successful:", data);
    } catch (err) {
      console.error("❌ Optimization failed:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    const testBackend = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/`);
        if (response.ok) {
          console.log("✅ Backend connection successful");
        }
      } catch (err) {
        console.warn("⚠️ Backend connection test failed:", err.message);
      }
    };
    testBackend();
  }, [BACKEND_URL]);

  return (
    <div className="App">
      <header className="app-header">
        <h1>🚌 Bus Route Optimizer</h1>
        <p>Enter a route number to find the optimized bus route</p>
        <p style={{ fontSize: "0.9rem", opacity: 0.8 }}>
          Backend: {BACKEND_URL}{" "}
          {optimizedRoute ? "✅ Connected" : "⚠️ Checking..."}
        </p>
      </header>

      <main className="app-main">
        <RouteInput onOptimize={handleOptimize} loading={loading} />

        {error && (
          <div className="error-message">
            ❌ {error}
            <br />
            <small>Make sure the backend is running on {BACKEND_URL}</small>
          </div>
        )}

        {routeRemoved && (
          <div
            className="error-message"
            style={{
              background: "#fff3cd",
              borderColor: "#ffeeba",
              color: "#856404",
            }}
          >
            ⚠️ This bus route has been removed due to fewer than 15 students.
          </div>
        )}

        {/* 🛠️ Added safety check to prevent undefined.length error */}
        {optimizedRoute && !routeRemoved && !optimizedRoute.optimized_order && (
          <div className="error-message">
            ⚠️ No optimized route data returned for this bus. Please check the
            backend.
          </div>
        )}

        {optimizedRoute && !routeRemoved && optimizedRoute.optimized_order && (
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
