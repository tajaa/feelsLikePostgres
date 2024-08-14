import React, { useState, useEffect } from "react";
import axios from "axios";
import { Search } from "lucide-react";

const WeatherDashboard = () => {
  const [city, setCity] = useState("");
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchInitialWeather = async () => {
    try {
      const response = await axios.get("/initial-weather");
      setWeatherData(response.data);
    } catch (err) {
      setError("Failed to fetch initial weather data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInitialWeather();
  }, []);

  const fetchWeather = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/weather/compare/${city}`);
      setWeatherData(response.data);
    } catch (err) {
      setError("Failed to fetch weather data");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Weather Dashboard</h1>
      <div className="flex mb-4">
        <input
          type="text"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          placeholder="Enter city name"
          className="flex-grow px-4 py-2 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={fetchWeather}
          className="bg-blue-500 text-white px-4 py-2 rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <Search size={20} />
        </button>
      </div>

      {loading && <p className="text-gray-600">Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {weatherData && (
        <div className="bg-white shadow-md rounded-lg p-4">
          <h2 className="text-2xl font-semibold mb-2">
            Weather in {weatherData.city || "Latest City"}
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <WeatherCard
              title="Temperature"
              value={weatherData.average.temperature}
            />
            <WeatherCard
              title="Humidity"
              value={weatherData.average.humidity}
            />
            <WeatherCard
              title="Feels Like"
              value={weatherData.average.feels_like}
            />
            <WeatherCard
              title="Wind Speed"
              value={weatherData.average.wind_speed}
            />
          </div>
        </div>
      )}
    </div>
  );
};

const WeatherCard = ({ title, value }) => (
  <div className="bg-gray-100 p-4 rounded-lg">
    <h3 className="text-lg font-semibold mb-2">{title}</h3>
    <p className="text-2xl">{value}</p>
  </div>
);

export default WeatherDashboard;
