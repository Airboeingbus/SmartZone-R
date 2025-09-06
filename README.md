# SmartZone-R: Runway Health Monitoring Dashboard

SmartZone-R is a Streamlit-based dashboard designed to monitor runway surface conditions in real time. It simulates flight landings across multiple runway zones, capturing sensor-based metrics like rubber build-up, cracking, water accumulation, and foreign object debris (FOD). The dashboard offers analytics, visualization, and customizable alerts to aid in proactive runway maintenance.

## Live Demo

[View the live dashboard here](https://smartzone-r-zbvpyayj8d944fgfec7wbm.streamlit.app/)

---

## Key Features

- **Data Simulation**
  - Generates realistic aircraft, weather, and runway metrics.
  - Simulates runway degradation across configurable zones.
  - Stores results in SQLite or CSV for flexibility and reliability.

- **Analytics Page**
  - Data table preview with filters by zone, aircraft, and time range.
  - Correlation heatmap to assess relationships among runway metrics.
  - Time-series trends visualized per zone.
  - Aircraft impact analysis across stress readings.

- **Runway Maps**
  - Visual mapping of average stress, FOD levels, and rubber thickness by zone.
  - Time-trend overlays for stress, FOD, and rubber degradation.
  - Options to export interactive plots as HTML.

- **Alerts Page**
  - Adjustable thresholds for stress, rubber, cracks, water, and FOD.
  - Severity classification: Normal, Medium, High, Critical.
  - KPI overview (records, flagged anomalies, top alert zones).
  - Detailed tables with download options (CSV).
  - Time-series alert tracking by hour.
  - Quick actions for exports and summaries.

---

## Getting Started

### Repository Structure
