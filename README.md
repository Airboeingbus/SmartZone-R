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
.
├── ## Repository Structure
└── Smartzone-R_Project/
    ├── hardware/
    │   ├── esp32/
    │   │   └── sample.txt
    │   ├── wokwi/
    │   │   └── sample.txt
    │   └── sample.txt
    ├── software/
    │   ├── analytics/
    │   │   ├── analyzer.py
    │   │   └── test_db.py
    │   ├── dashboard/
    │   │   ├── pages/
    │   │   │   ├── alerts.py
    │   │   │   ├── analytics.py
    │   │   │   ├── runway_maps.py
    │   │   │   └── __init__.py
    │   │   ├── app.py
    │   │   ├── utils.py
    │   │   └── __init__.py
    │   ├── data/
    │   │   ├── runway_data.csv
    │   │   └── smartzone_r.db
    │   └── simulator/
    │       ├── config.py
    │       ├── flights.py
    │       ├── generator.py
    │       └── weather.py
    ├── tests/
    │   └── test_generator.py
    ├── requirements.txt
    └── repo_tree.txt
    ---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Smartzone-R_Project.git
   cd Smartzone-R_Project
2. (Optional but recommended) Create a virtual environment:

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


3. Install dependencies:

pip install -r requirements.txt




---

## Usage

Run the Streamlit Dashboard

cd software/dashboard
streamlit run app.py

The dashboard will be available at:

http://localhost:8501


---

## Testing

Run tests using:

pytest tests/


---

## Contributing

Contributions are welcome!
To contribute:

1. Fork the repository


2. Create a feature branch (git checkout -b feature-name)


3. Commit your changes (git commit -m "Add new feature")


4. Push to your branch (git push origin feature-name)


5. Open a pull request




---

## License

This project is licensed under the MIT License.
See the LICENSE file for details.
