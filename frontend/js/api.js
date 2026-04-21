/**
 * SmartZone-R - API Module
 * All fetch calls to FastAPI backend
 */

// Use window.location.origin for cross-domain compatibility
const BASE_URL = window.location.origin + '/api';

// === ERROR HANDLING ===
function handleApiError(functionName, error) {
  console.error(`[API Error] ${functionName}:`, error);
  return null;
}

// === STATUS ENDPOINTS ===
async function fetchStatus() {
  try {
    const response = await fetch(`${BASE_URL}/status`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return handleApiError('fetchStatus', error);
  }
}

// === FLIGHTS ENDPOINTS ===
async function fetchFlights(zone = null) {
  try {
    const url = zone ? `${BASE_URL}/flights?zone=${zone}` : `${BASE_URL}/flights`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return handleApiError('fetchFlights', error);
  }
}

async function fetchFlightsForZone(zone) {
  try {
    const response = await fetch(`${BASE_URL}/flights/zone/${zone}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return handleApiError('fetchFlightsForZone', error);
  }
}

async function fetchLatestFlight() {
  try {
    const response = await fetch(`${BASE_URL}/flights/latest`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return handleApiError('fetchLatestFlight', error);
  }
}

// === ANALYTICS ENDPOINTS ===
async function fetchAnalyticsSummary() {
  try {
    const response = await fetch(`${BASE_URL}/analytics/summary`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return handleApiError('fetchAnalyticsSummary', error);
  }
}

async function fetchZones() {
  try {
    const response = await fetch(`${BASE_URL}/analytics/zones`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return handleApiError('fetchZones', error);
  }
}

async function fetchTimeSeries(metric, zone = null) {
  try {
    const url = zone 
      ? `${BASE_URL}/analytics/timeseries?metric=${metric}&zone=${zone}`
      : `${BASE_URL}/analytics/timeseries?metric=${metric}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return handleApiError('fetchTimeSeries', error);
  }
}

async function fetchHeatmap() {
  try {
    const response = await fetch(`${BASE_URL}/analytics/heatmap`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return handleApiError('fetchHeatmap', error);
  }
}

// === ALERTS ENDPOINTS ===
async function fetchAlerts(severity = null) {
  try {
    const url = severity 
      ? `${BASE_URL}/alerts?severity=${severity}`
      : `${BASE_URL}/alerts`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return handleApiError('fetchAlerts', error);
  }
}

async function fetchCriticalAlerts() {
  try {
    const response = await fetch(`${BASE_URL}/alerts/critical`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return handleApiError('fetchCriticalAlerts', error);
  }
}

async function fetchAlertsSummary() {
  try {
    const response = await fetch(`${BASE_URL}/alerts/summary`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return handleApiError('fetchAlertsSummary', error);
  }
}

async function fetchAlertsByZone() {
  try {
    const response = await fetch(`${BASE_URL}/alerts/zones`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return handleApiError('fetchAlertsByZone', error);
  }
}

// === EXPORT ALL FUNCTIONS ===
export {
  fetchStatus,
  fetchFlights,
  fetchFlightsForZone,
  fetchLatestFlight,
  fetchAnalyticsSummary,
  fetchZones,
  fetchTimeSeries,
  fetchHeatmap,
  fetchAlerts,
  fetchCriticalAlerts,
  fetchAlertsSummary,
  fetchAlertsByZone,
};
