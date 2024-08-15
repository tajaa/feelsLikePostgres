import React, { useState } from "react";

const WeatherSurvey = ({ onComplete }) => {
  const [rating, setRating] = useState(null);

  const feelings = [
    { value: 1, label: "Freezing Cold" },
    { value: 2, label: "Slightly Cold" },
    { value: 3, label: "Cool" },
    { value: 4, label: "Warm" },
    { value: 5, label: "Hot" },
  ];

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
        How would you describe the current weather?
      </p>
      <div className="flex flex-wrap justify-between mb-6">
        {feelings.map((item) => (
          <button
            key={item.value}
            onClick={() => setRating(item.value)}
            className={`px-4 py-2 m-1 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 transition duration-300 ${
              rating === item.value
                ? "bg-orange-600 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            {item.label}
          </button>
        ))}
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
