
const API_KEY = 'c615ae5163bc6bc26a485372b305b501';

const cities = [
  {
    name: 'New York',
    backgroundImage: 'new-york.jpg'
  },
  {
    name: 'London',
    backgroundImage: 'london.jpg'
  },
  {
    name: 'Tokyo',
    backgroundImage: 'tokyo.jpg'
  },
  {
    name: 'Colombo',
    backgroundImage: 'colombo.jpg'
  },
  {
    name: 'Dubai',
    backgroundImage: 'dubai.jpg'
  }
];

const cityButtonsContainer = document.getElementById('city-buttons');
const weatherDisplay = document.getElementById('weather-display');
const errorDisplay = document.getElementById('error-display');

// Generate buttons for each city
cities.forEach(city => {
  const button = document.createElement('button');
  button.textContent = city.name;
  button.addEventListener('click', () => fetchWeatherData(city));
  cityButtonsContainer.appendChild(button);
});

// Fetch weather data
async function fetchWeatherData(city) {
  // Clear previous data
  weatherDisplay.innerHTML = '';
  errorDisplay.textContent = '';

  try {
    const response = await fetch(
        `https://api.openweathermap.org/data/2.5/weather?q=${city.name}&appid=${API_KEY}&units=metric`
    );

    if (!response.ok) {
      throw new Error('Failed to fetch weather data');
    }

    const data = await response.json();

    const weatherInfo = {
      city: data.name,
      temperature: Math.round(data.main.temp),
      description: data.weather[0].description,
      windSpeed: data.wind.speed,
      backgroundImage: city.backgroundImage
    };

    setDynamicBackground(weatherInfo);
    displayWeather(weatherInfo);
  } catch (err) {
    errorDisplay.textContent = err.message;
  }
}

// Set background based on city and temperature
function setDynamicBackground({ temperature, backgroundImage }) {
  const body = document.body;

  // Set city-specific background
  body.style.backgroundImage = `url('${backgroundImage}')`;
  body.style.backgroundSize = 'cover';
  body.style.backgroundPosition = 'center';

  // Optionally, you can still adjust background overlay based on temperature
  const overlay = document.createElement('div');
  overlay.style.position = 'fixed';
  overlay.style.top = '0';
  overlay.style.left = '0';
  overlay.style.width = '100%';
  overlay.style.height = '100%';
  overlay.style.zIndex = '-1';

  if (temperature <= 5) {
    overlay.style.backgroundColor = 'rgba(0, 0, 255, 0.2)'; // Blue tint for cold
  } else if (temperature >= 40) {
    overlay.style.backgroundColor = 'rgba(255, 0, 0, 0.2)'; // Red tint for hot
  }

 
  const existingOverlay = document.body.querySelector('.temperature-overlay');
  if (existingOverlay) {
    existingOverlay.remove();
  }

  overlay.classList.add('temperature-overlay');
  document.body.appendChild(overlay);
}

// Display weather data
function displayWeather({ city, temperature, description, windSpeed }) {
  weatherDisplay.innerHTML = `
    <div>
      <h2>${city}</h2>
      <p><strong>Temperature:</strong> ${temperature}°C</p>
      <p><strong>Description:</strong> ${description}</p>
      <p><strong>Wind Speed:</strong> ${windSpeed} m/s</p>
    </div>
  `;
}