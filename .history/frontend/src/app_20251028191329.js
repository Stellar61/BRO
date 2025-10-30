// import React, { useState } from "react";
// import RouteMap from "./components/RouteMap";
// import RouteList from "./components/RouteList";
// import "./App.css";

// function App() {
//   const [routeNo, setRouteNo] = useState("");
//   const [optimizedRoute, setOptimizedRoute] = useState(null);
//   const [error, setError] = useState("");
//   const [loading, setLoading] = useState(false);

//   // ✅ Fix: Use environment variable for backend
//   const backendUrl =
//     process.env.REACT_APP_BACKEND_URL ||
//     "https://bro-backend-app.azurewebsites.net";

//   const handleOptimize = async () => {
//     setLoading(true);
//     setError("");
//     setOptimizedRoute(null);

//     try {
//       // ✅ Fix: Encode route number to handle letters like 1B, 40C
//       const response = await fetch(`${backendUrl}/optimize`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ route_no: routeNo.trim() }),
//       });

//       const data = await response.json();
//       if (!response.ok) throw new Error(data.detail || "Failed to fetch route");

//       setOptimizedRoute(data);
//     } catch (err) {
//       console.error("Error:", err);
//       setError("Unable to fetch data. Please check connection or backend.");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="App">
//       <header className="app-header">
//         <h1>🚍 Bus Route Optimizer</h1>
//         <p>
//           Plan and visualize optimized routes for Rajalakshmi Engineering
//           College
//         </p>
//       </header>

//       <main className="app-main">
//         <div className="route-input-container">
//           <input
//             type="text"
//             value={routeNo}
//             onChange={(e) => setRouteNo(e.target.value)}
//             placeholder="Enter bus route number (e.g. 1B, 40C)"
//             className="route-input"
//           />
//           <button onClick={handleOptimize} disabled={!routeNo || loading}>
//             {loading ? "Optimizing..." : "Optimize Route"}
//           </button>
//         </div>

//         {error && <div className="error-message">{error}</div>}

//         {optimizedRoute && (
//           <div className="results-container">
//             {optimizedRoute.removed_stops?.length > 0 ? (
//               <div className="removed-route">
//                 <h2>❌ Route {optimizedRoute.route_no} Removed</h2>
//                 <p>{optimizedRoute.message}</p>
//                 <div className="removed-list">
//                   <h3>Removed Stops:</h3>
//                   <ul>
//                     {optimizedRoute.removed_stops.map((stop, i) => (
//                       <li key={i}>
//                         🚌 {stop.stop_name || stop["Boarding Point"]} —{" "}
//                         {stop.students_per_stop} students
//                       </li>
//                     ))}
//                   </ul>
//                 </div>
//               </div>
//             ) : (
//               <>
//                 <div className="route-summary">
//                   <h2>✅ Route {optimizedRoute.route_no} - Optimized Path</h2>
//                   <div className="stats">
//                     <span className="stat">
//                       📏 <strong>{optimizedRoute.total_distance_km} km</strong>
//                     </span>
//                     <span className="stat">
//                       ⏱️{" "}
//                       <strong>{optimizedRoute.estimated_time_min} min</strong>
//                     </span>
//                     <span className="stat">
//                       🛑{" "}
//                       <strong>{optimizedRoute.optimized_order.length}</strong>{" "}
//                       stops
//                     </span>
//                   </div>
//                 </div>

//                 <div className="results-layout">
//                   <div className="map-container">
//                     <RouteMap stops={optimizedRoute.optimized_order} />
//                   </div>
//                   <div className="list-container">
//                     <RouteList stops={optimizedRoute.optimized_order} />
//                   </div>
//                 </div>
//               </>
//             )}
//           </div>
//         )}
//       </main>
//     </div>
//   );
// }

// export default App;

import React, { useState } from "react";
import "./App.css";
import RouteInput from "./components/RouteInput";
import RouteList from "./components/RouteList";
import RouteMap from "./components/RouteMap";

function App() {
  const [routeData, setRouteData] = useState(null);
  const [error, setError] = useState("");

  const handleOptimize = async (busNumber) => {
    try {
      setError("");
      const response = await fetch(
        `https://bro-backend-app.azurewebsites.net/optimize-route?bus_number=${busNumber}`
      );
      const data = await response.json();
      if (data.error) {
        setError(data.error);
        setRouteData(null);
      } else {
        setRouteData(data);
      }
    } catch {
      setError("Failed to connect to backend. Please try again later.");
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🚌 Bus Route Optimizer</h1>
        <p>
          Plan and visualize optimized routes for Rajalakshmi Engineering
          College
        </p>
      </header>

      <main className="app-main">
        <RouteInput onOptimize={handleOptimize} />
        {error && <div className="error-message">{error}</div>}
        {routeData && (
          <div className="results-container">
            <div className="route-summary">
              <h2>Route Summary</h2>
              <div className="stats">
                <p>
                  <strong>Bus Number:</strong> {routeData.bus_number}
                </p>
                <p>
                  <strong>Total Stops:</strong> {routeData.total_stops}
                </p>
                <p>
                  <strong>Start:</strong> {routeData.start}
                </p>
                <p>
                  <strong>End:</strong> {routeData.end}
                </p>
              </div>
            </div>
            <div className="results-layout">
              <RouteList route={routeData.route} />
              <RouteMap route={routeData.route} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
