import React from "react";
import "./RouteList.css";

const RouteList = ({ stops }) => {
  if (!stops || stops.length === 0) {
    return <div className="route-list-empty">No stops to display</div>;
  }

  return (
    <div className="route-list">
      <div className="route-list-header">
        <h3>Optimized Route Sequence</h3>
        <div className="route-info">Total Stops: {stops.length}</div>
      </div>

      <div className="stops-container">
        {stops.map((stop, index) => (
          <div key={index} className="stop-item">
            <div className="stop-marker">
              {index === 0 && <span className="marker start">🚩</span>}
              {index === stops.length - 1 && (
                <span className="marker end">🏁</span>
              )}
              {index > 0 && index < stops.length - 1 && (
                <span className="marker number">{index + 1}</span>
              )}
            </div>

            <div className="stop-details">
              <div className="stop-name">{stop["Boarding Point"]}</div>
              <div className="stop-time">⏰ {stop.Time}</div>
              <div className="stop-coords">
                📍 {stop.lat.toFixed(4)}, {stop.lon.toFixed(4)}
              </div>
            </div>

            <div className="stop-position">#{index + 1}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RouteList;
