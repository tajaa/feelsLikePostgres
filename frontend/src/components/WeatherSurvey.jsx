import React, { useState } from "react";

const WeatherSurvey = ({ onComplete }) => {
  const [rating, setRating] = useState(null);

  const handleSubmit = () => {
    if (rating !== null) {
      onComplete(rating);
    }
  };

  return (
    <div className="bg-gray-800 shadow-lg rounded-lg p-6 mb-6">
      <h2 className="text-2xl font-semibold mb-4 text-orange-500">
        Weather Survey
      </h2>
      <p className="text-gray-300 mb-4">
        How would you rate the current weather?
      </p>
      <div className="flex justify-between mb-6">
        {[1, 2, 3, 4, 5].map((value) => (
          <button
            key={value}
            onClick={() => setRating(value)}
            className={`px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 transition duration-300 ${
              rating === value
                ? "bg-orange-600 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            {value}
          </button>
        ))}
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>Freezing Cold</span>
        <span>Slightly Cold</span>
        <span>Cool</span>
        <span>Warm</span>
        <span>Hot</span>
      </div>
      <button
        onClick={handleSubmit}
        disabled={rating === null}
        className={`mt-6 w-full px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 transition duration-300 ${
          rating !== null
            ? "bg-orange-600 text-white hover:bg-orange-700"
            : "bg-gray-600 text-gray-400 cursor-not-allowed"
        }`}
      >
        Submit
      </button>
    </div>
  );
};

export default WeatherSurvey;
