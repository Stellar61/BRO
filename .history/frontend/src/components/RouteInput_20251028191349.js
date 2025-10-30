// import React, { useState } from "react";
// import "./RouteInput.css";

// const RouteInput = ({ onOptimize, loading }) => {
//   const [routeNo, setRouteNo] = useState("");

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     if (routeNo.trim()) {
//       onOptimize(routeNo.trim());
//     }
//   };

//   return (
//     <div className="route-input-container">
//       <form onSubmit={handleSubmit} className="route-input-form">
//         <div className="input-group">
//           <label htmlFor="routeNo">Enter Route Number:</label>
//           <input
//             type="text"
//             id="routeNo"
//             value={routeNo}
//             onChange={(e) => setRouteNo(e.target.value)}
//             placeholder="e.g., 101, 202, etc."
//             disabled={loading}
//           />
//         </div>
//         <button
//           type="submit"
//           disabled={!routeNo.trim() || loading}
//           className="optimize-btn"
//         >
//           {loading ? "🔄 Optimizing..." : "🚀 Optimize Route"}
//         </button>
//       </form>
//     </div>
//   );
// };

// export default RouteInput;

import React, { useState } from "react";
import "./RouteInput.css";

function RouteInput({ onOptimize }) {
  const [busNumber, setBusNumber] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (busNumber.trim()) {
      onOptimize(busNumber.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="route-input">
      <input
        type="text"
        placeholder="Enter bus route number (e.g., 12A)"
        value={busNumber}
        onChange={(e) => setBusNumber(e.target.value)}
      />
      <button type="submit">Optimize Route</button>
    </form>
  );
}

export default RouteInput;
