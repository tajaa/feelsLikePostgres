import React from "react";
import "./App.css";
import WeatherDashboard from "./components/WeatherDashboard";
import SurveyDashboard from "./components/SurveyDashboard";

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <WeatherDashboard />
      </div>
    </div>
  );
}

export default App;
