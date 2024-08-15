import React, { useEffect, useState } from "react";
import axios from "axios";

const LocationUpdater = ({ onLocationUpdate }) => {
  const [error, setError] = useState(null);

  useEffect(() => {
    updateLocation();
  }, []);

  const updateLocation = () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("No authentication token found");
      return;
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            await axios.post(
              "/update-location",
              {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
              },
              {
                headers: { Authorization: `Bearer ${token}` },
              },
            );
            onLocationUpdate();
          } catch (err) {
            setError("Failed to update location");
            console.error("Failed to update location:", err);
          }
        },
        (err) => {
          setError("Failed to get location: " + err.message);
          console.error("Geolocation error:", err);
        },
      );
    } else {
      setError("Geolocation is not supported by this browser");
    }
  };

  return (
    <div>
      <button
        onClick={updateLocation}
        className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
      >
        Update Location
      </button>
      {error && <p className="text-red-500">{error}</p>}
    </div>
  );
};

export default LocationUpdater;
