import React, { useState, useEffect } from "react";
import axios from "axios";

const SurveyDashboard = ({ token }) => {
  const [nearbyScores, setNearbyScores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const getFeelingDescription = (score) => {
    switch (score) {
      case 1:
        return "Freezing Cold";
      case 2:
        return "Slightly Cold";
      case 3:
        return "Cool";
      case 4:
        return "Warm";
      case 5:
        return "Hot";
      default:
        return "Unknown";
    }
  };

  useEffect(() => {
    const fetchNearbyScores = async () => {
      try {
        const response = await axios.get("/nearby-scores", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setNearbyScores(response.data);
      } catch (err) {
        setError("Failed to fetch nearby feeling scores");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchNearbyScores();
  }, [token]);

  if (loading)
    return <p className="text-gray-400">Loading nearby feelings...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="bg-gray-700 shadow-md rounded-lg p-6 mt-6">
      <h2 className="text-2xl font-semibold mb-4 text-orange-500">
        Nearby Weather Feelings
      </h2>
      {nearbyScores.length === 0 ? (
        <p className="text-gray-300">No nearby weather feelings available.</p>
      ) : (
        <ul className="space-y-2">
          {nearbyScores.map((score, index) => (
            <li
              key={index}
              className="bg-gray-800 p-3 rounded-lg flex justify-between items-center"
            >
              <span className="text-gray-300">
                Feeling: {getFeelingDescription(score.feeling_score)}
              </span>
              <span className="text-gray-400 text-sm">
                Distance: {(score.distance * 111).toFixed(2)} km
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SurveyDashboard;
