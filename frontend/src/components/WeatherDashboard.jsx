import React, { useState, useEffect } from "react";
import axios from "axios";
import { Search } from "lucide-react";
import jwtDecode from "jwt-decode";
import LocationUpdater from "./LocationUpdater";

const WeatherDashboard = () => {
  const [city, setCity] = useState("");
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState("");

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    if (storedToken) {
      setToken(storedToken);
      setIsLoggedIn(true);
      fetchInitialWeather(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchWeatherByCoordinates = async (authToken) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get("/weather/coordinates", {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      setWeatherData(response.data.weather);
      setCity(response.data.city);
    } catch (err) {
      setError("Failed to fetch weather data for your location");
    } finally {
      setLoading(false);
    }
  };

  const fetchInitialWeather = async (authToken) => {
    try {
      const response = await axios.get("/initial-weather", {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      setWeatherData(response.data);
    } catch (err) {
      setError("Failed to fetch initial weather data");
    } finally {
      setLoading(false);
    }
  };

  const fetchWeather = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/weather/compare/${city}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setWeatherData(response.data);
    } catch (err) {
      setError("Failed to fetch weather data");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    try {
      const response = await axios.post("/register", { username, password });
      setToken(response.data.access_token);
      localStorage.setItem("token", response.data.access_token);
      setIsLoggedIn(true);
      updateLocation(response.data.access_token);
    } catch (err) {
      setError("Registration failed");
    }
  };

  const handleLogin = async () => {
    try {
      const response = await axios.post(
        "/token",
        `username=${username}&password=${password}`,
        {
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
        },
      );
      setToken(response.data.access_token);
      localStorage.setItem("token", response.data.access_token);
      setIsLoggedIn(true);
      updateLocation(response.data.access_token);
    } catch (err) {
      setError("Login failed");
    }
  };

  const handleLogout = () => {
    setToken("");
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    setWeatherData(null);
  };

  const updateLocation = async (authToken) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(async (position) => {
        try {
          await axios.post(
            "/update-location",
            {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            },
            {
              headers: { Authorization: `Bearer ${authToken}` },
            },
          );
        } catch (err) {
          console.error("Failed to update location");
        }
      });
    }
  };

  const handleLocationUpdate = () => {
    fetchWeatherByCoordinates(token);
  };

  if (!isLoggedIn) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-4">Weather Dashboard</h1>
        <div className="mb-4">
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
            className="w-full px-4 py-2 mb-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="w-full px-4 py-2 mb-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleLogin}
            className="w-full bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
          >
            Login
          </button>
          <button
            onClick={handleRegister}
            className="w-full bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            Register
          </button>
        </div>
        {error && <p className="text-red-500">{error}</p>}
      </div>
    );
  }

  return (
    <div className="bg-gray-800 shadow-lg rounded-lg p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-orange-500">
          Weather Dashboard
        </h1>
        <button
          onClick={handleLogout}
          className="bg-red-600 text-gray-100 px-4 py-2 rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 transition duration-300"
        >
          Logout
        </button>
      </div>
      <LocationUpdater onLocationUpdate={handleLocationUpdate} />
      <div className="flex mb-6">
        <input
          type="text"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          placeholder="Enter city name"
          className="flex-grow px-4 py-2 bg-gray-700 border border-gray-600 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-gray-100"
        />
        <button
          onClick={fetchWeather}
          className="bg-orange-600 text-gray-100 px-6 py-2 rounded-r-lg hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 transition duration-300"
        >
          <Search size={20} />
        </button>
      </div>

      {loading && <p className="text-gray-400">Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {weatherData && (
        <div className="bg-gray-700 shadow-md rounded-lg p-6">
          <h2 className="text-2xl font-semibold mb-4 text-orange-500">
            Weather in {weatherData.city || city || "Latest City"}
          </h2>
          <div className="grid grid-cols-2 gap-6">
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
  <div className="bg-gray-800 p-4 rounded-lg shadow-md">
    <h3 className="text-lg font-semibold mb-2 text-orange-400">{title}</h3>
    <p className="text-2xl text-gray-100">{value}</p>
  </div>
);

export default WeatherDashboard;
