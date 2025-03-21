// Plain JavaScript version of the Google Routes API test script
import fetch from 'node-fetch';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Configuration
const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY;
const GOOGLE_MAPS_ROUTES_API_URL = 'https://routes.googleapis.com/directions/v2:computeRoutes';

// Test data
const currentStationLat = 4.58598283;
const currentStationLng = -74.20546046;
const destinationStationLat = 4.65729068;
const destinationStationLng = -74.07766289;
const routeName = "E42"; // Example route name to search for, modify as needed

// Function to calculate time to departure
const calculateTimeToDeparture = (departureTime) => {
  const now = new Date();

  // Parse departure time ("HH:MM")
  const [departureHours, departureMinutes] = departureTime.split(':').map(Number);

  // Create Date object for departure time today
  const departureDate = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate(),
    departureHours,
    departureMinutes
  );

  // Calculate difference in milliseconds and convert to minutes
  const diffMs = departureDate.getTime() - now.getTime();
  const diffMinutes = diffMs / (1000 * 60);
  
  // minutes as a string rounded to the nearest integer
  return diffMinutes.toFixed(0);
};

// Function to extract route data
const extractGoogleRouteData = (googleRouteData, routeName) => {
  console.log(`Looking for route: ${routeName}`);

  for (const route of googleRouteData.routes) {
    for (const routeLeg of route.legs) {
      const routeSteps = routeLeg.steps;
      for (const step of routeSteps) {
        if (step.travelMode === "TRANSIT" && step.transitDetails) {
          const transitDetails = step.transitDetails;
          const transitLineName = transitDetails.transitLine.nameShort;
          console.log("Transit line found:", transitLineName);
          
          if (transitLineName === routeName) {
            const departureTime = transitDetails.localizedValues.departureTime.time.text;
            console.log("Departure time:", departureTime);
            const timeToDeparture = calculateTimeToDeparture(departureTime);
            console.log("Time to departure (minutes):", timeToDeparture);
            return timeToDeparture;
          }
        }
      }
    }
  }
  
  console.error("Bus route not found in Google Maps data.");
  return null;
};

// Function to fetch Google Maps route data
const fetchGoogleRouteData = async () => {
  console.log(`Requesting Google Maps route data:
from (${currentStationLat}, ${currentStationLng})
to (${destinationStationLat}, ${destinationStationLng})`);
  
  if (!GOOGLE_MAPS_API_KEY) {
    throw new Error("Google Maps API key is missing. Set GOOGLE_MAPS_API_KEY in your .env file.");
  }

  try {
    const response = await fetch(GOOGLE_MAPS_ROUTES_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "routes.legs",
      },
      body: JSON.stringify({
        "origin": { "location": { "latLng": { "latitude": currentStationLat, "longitude": currentStationLng } } },
        "destination": { "location": { "latLng": { "latitude": destinationStationLat, "longitude": destinationStationLng } } },
        "travelMode": "TRANSIT",
        "computeAlternativeRoutes": true,
      }),
    });

    if (!response.ok) {
      throw new Error(`Google API error: ${response.status} - ${await response.text()}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching Google Maps data:", error);
    throw error;
  }
};

// Main testing function
const runTest = async () => {
  console.log("Starting test of Google Routes API...");
  console.log("--------------------------------------");
  
  try {
    // Test API connection and data fetching
    console.log("1. Testing API connection and data fetching...");
    const routeData = await fetchGoogleRouteData();
    console.log("✅ Successfully fetched route data");
    console.log(`Found ${routeData.routes.length} route(s)`);
    
    // Validate response structure
    console.log("\n2. Validating response structure...");
    if (!routeData.routes || !Array.isArray(routeData.routes)) {
      throw new Error("Invalid response: 'routes' property missing or not an array");
    }
    
    if (routeData.routes.length === 0) {
      console.warn("⚠️ No routes found between the specified coordinates");
    } else {
      console.log("✅ Response structure is valid");
      
      // Log route summary
      console.log("\n3. Available transit options:");
      const transitOptions = new Set();
      
      routeData.routes.forEach((route, routeIndex) => {
        route.legs.forEach(leg => {
          leg.steps.forEach(step => {
            if (step.travelMode === "TRANSIT" && step.transitDetails) {
              transitOptions.add(step.transitDetails.transitLine.nameShort || step.transitDetails.transitLine.name);
            }
          });
        });
      });
      
      if (transitOptions.size === 0) {
        console.warn("⚠️ No transit options found in the routes");
      } else {
        console.log("Available transit lines:", Array.from(transitOptions).join(", "));
      }
      
      // Test time calculation with our specific route
      console.log("\n4. Testing time calculation for route:", routeName);
      const timeToDeparture = extractGoogleRouteData(routeData, routeName);
      
      if (timeToDeparture !== null) {
        console.log(`✅ Successfully calculated time to departure: ${timeToDeparture} minutes`);
      } else {
        console.warn(`⚠️ Could not find route "${routeName}" in the results. Try one of these routes instead: ${Array.from(transitOptions).join(", ")}`);
      }
    }
    
    console.log("\nTest completed successfully!");
    
  } catch (error) {
    console.error("\n❌ Test failed:", error);
  }
};

// Run the test
runTest();