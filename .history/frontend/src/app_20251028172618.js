import React, { useState } from "react";
import RouteInput from "./components/RouteInput";
import RouteMap from "./components/RouteMap";
import RouteList from "./components/RouteList";
import "./App.css";

function App() {
  const [optimizedRoute, setOptimizedRoute] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const BACKEND_URL =
    process.env.REACT_APP_BACKEND_URL ||
    "https://bro-backend-app.azurewebsites.net";

  const handleOptimize = async (routeNo) => {
    setLoading(true);
    setError("");
    setOptimizedRoute(null);

    try {
      console.log(`🔄 Optimizing route ${routeNo}...`);

      const response = await fetch(`${BACKEND_URL}/optimize`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ route_no: parseInt(routeNo) }),
      });

      const body = await response.json().catch(() => ({}));

      if (!response.ok) {
        // prefer server message if present
        const serverMsg =
          body && body.error ? body.error : `HTTP error ${response.status}`;
        throw new Error(serverMsg);
      }

      // server may return an error message even with 200 - handle that
      if (body && body.error) {
        throw new Error(body.error);
      }

      // expected success payload: { route_no, optimized_order, total_distance_km, estimated_time_min, total_students? }
      setOptimizedRoute(body);
    } catch (err) {
      console.error("❌ Optimization failed:", err);
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    const testBackend = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/`);
        if (response.ok) console.log("✅ Backend connection successful");
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

        {/* If backend responded with a skip message, it will be in `error` shown above.
            If we have optimizedRoute, render it. */}
        {optimizedRoute &&
          optimizedRoute.optimized_order &&
          optimizedRoute.optimized_order.length > 0 && (
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
                    🧑‍🤝‍🧑 Total Students:{" "}
                    <strong>{optimizedRoute.total_students ?? "N/A"}</strong>
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

        {/* If backend returned success but no stops */}
        {optimizedRoute &&
          (!optimizedRoute.optimized_order ||
            optimizedRoute.optimized_order.length === 0) &&
          !error && (
            <div className="info-message">
              No optimized stops returned by server.
            </div>
          )}
      </main>
    </div>
  );
}

export default App;
