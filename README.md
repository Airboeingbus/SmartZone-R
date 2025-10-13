
# ✈️ SmartZone-R

<div align="center">

![SmartZone-R Logo](https://img.shields.io/badge/SmartZone-R-blue?style=for-the-badge&logo=airport&logoColor=white)

**A Dashboard-Powered Solution for Real-Time Runway Surface Monitoring**

*Optimized for Deployment in Small Airports*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 🎯 Overview

**SmartZone-R** is a comprehensive Streamlit-based dashboard designed to monitor runway surface conditions in real time. The system simulates flight landings across multiple runway zones, capturing critical sensor-based metrics to ensure aviation safety and optimize maintenance operations.

### Why SmartZone-R?

- 🛫 **Proactive Maintenance**: Detect runway issues before they become safety hazards
- 📊 **Data-Driven Decisions**: Leverage analytics to optimize maintenance schedules
- 💰 **Cost-Effective**: Designed specifically for small airports with limited budgets
- 🔄 **Real-Time Monitoring**: Continuous tracking of runway conditions
- 🎨 **Intuitive Dashboard**: Easy-to-use interface for airport operations staff

---

## ✨ Features

### 📈 Data Simulation
- Generates realistic aircraft, weather, and runway metrics
- Simulates runway degradation across configurable zones
- Flexible storage options: SQLite database or CSV files
- Customizable simulation parameters for different runway types

### 📊 Analytics Page
- **Data Table Preview**: Filter by zone, aircraft type, and time range
- **Correlation Heatmap**: Assess relationships among runway metrics
- **Time-Series Trends**: Visualize degradation patterns per zone
- **Aircraft Impact Analysis**: Analyze stress readings across different aircraft types

### 🗺️ Runway Maps
- **Visual Mapping**: Average stress, FOD levels, and rubber thickness by zone
- **Time-Trend Overlays**: Track stress, FOD, and rubber degradation over time
- **Interactive Plots**: Export visualizations as HTML for reports
- **Zone-Based Analysis**: Identify high-risk areas on the runway

### 🚨 Alerts Page
- **Adjustable Thresholds**: Customize limits for stress, rubber, cracks, water, and FOD
- **Severity Classification**: Normal, Medium, High, Critical alert levels
- **KPI Overview**: Track records, flagged anomalies, and top alert zones
- **Detailed Reports**: Downloadable tables in CSV format
- **Time-Series Tracking**: Alert trends by hour for pattern recognition
- **Quick Actions**: One-click exports and summary generation

---

## 📁 Repository Structure

```
SmartZone-R/
│
├── hardware/                 # Hardware components & IoT integration
│   ├── esp32/               # ESP32 sensor code
│   └── wokwi/               # Wokwi simulation files
│
├── software/                 # Main application code
│   ├── analytics/           # Data analysis modules
│   │   ├── analyzer.py      # Core analytics engine
│   │   └── test_db.py       # Database testing utilities
│   │
│   ├── dashboard/           # Streamlit web application
│   │   ├── pages/           # Multi-page dashboard
│   │   │   ├── alerts.py    # Alert management page
│   │   │   ├── analytics.py # Analytics dashboard
│   │   │   ├── runway_maps.py # Visual runway mapping
│   │   │   └── __init__.py
│   │   ├── app.py           # Main application entry
│   │   ├── utils.py         # Utility functions
│   │   └── __init__.py
│   │
│   ├── data/                # Data storage
│   │   ├── runway_data.csv  # CSV data export
│   │   └── smartzone_r.db   # SQLite database
│   │
│   └── simulator/           # Data simulation engine
│       ├── config.py        # Configuration settings
│       ├── flights.py       # Flight simulation logic
│       ├── generator.py     # Data generation
│       └── weather.py       # Weather simulation
│
├── tests/                   # Unit and integration tests
│   └── test_generator.py    # Simulator tests
│
├── requirements.txt         # Python dependencies
├── repo_tree.txt           # Repository structure
└── README.md               # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Airboeingbus/SmartZone-R.git
   cd SmartZone-R
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Usage

### Running the Dashboard

```bash
cd software/dashboard
streamlit run app.py
```

The dashboard will be available at: **http://localhost:8501**

### Running the Simulator

```bash
cd software/simulator
python generator.py
```

### Running Tests

```bash
pytest tests/
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│                  SmartZone-R System                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐      ┌──────────────┐          │
│  │   Hardware   │      │  Simulator   │          │
│  │              │─────▶│              │          │
│  │ ESP32 Sensors│      │ Data Gen     │          │
│  └──────────────┘      └──────────────┘          │
│         │                      │                  │
│         ▼                      ▼                  │
│  ┌─────────────────────────────────┐             │
│  │        Data Storage             │             │
│  │  (SQLite / CSV)                 │             │
│  └─────────────────────────────────┘             │
│         │                                         │
│         ▼                                         │
│  ┌─────────────────────────────────┐             │
│  │      Analytics Engine           │             │
│  │  • Data Processing              │             │
│  │  • Correlation Analysis         │             │
│  │  • Alert Generation             │             │
│  └─────────────────────────────────┘             │
│         │                                         │
│         ▼                                         │
│  ┌─────────────────────────────────┐             │
│  │    Streamlit Dashboard          │             │
│  │  • Analytics View               │             │
│  │  • Runway Maps                  │             │
│  │  • Alert Management             │             │
│  └─────────────────────────────────┘             │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Key Technologies

- **Frontend**: Streamlit for interactive web dashboard
- **Backend**: Python for data processing and analysis
- **Database**: SQLite for efficient data storage
- **Visualization**: Plotly, Matplotlib for interactive charts
- **Hardware**: ESP32 microcontrollers for sensor integration
- **Testing**: Pytest for automated testing

---

## 📊 Monitored Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| **Rubber Build-up** | Accumulated rubber deposits from tire contact | > 5mm |
| **Surface Cracking** | Structural integrity of runway surface | > 10% coverage |
| **Water Accumulation** | Standing water depth | > 3mm |
| **FOD (Foreign Object Debris)** | Detection of objects on runway | Any detection |
| **Stress Readings** | Structural stress from aircraft weight | > 85% capacity |

---

## 🎨 Dashboard Screenshots

### Analytics Dashboard
*[Add screenshot of analytics page]*

### Runway Heat Map
*[Add screenshot of runway maps page]*

### Alert Management
*[Add screenshot of alerts page]*

---

## 🛣️ Roadmap

- [x] Core dashboard functionality
- [x] Multi-zone simulation
- [x] Alert system with severity levels
- [x] Data export capabilities
- [ ] Machine learning predictive maintenance
- [ ] Mobile application for field inspections
- [ ] Integration with weather APIs
- [ ] Multi-airport support
- [ ] Real-time hardware sensor integration
- [ ] Email/SMS alert notifications

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Contribution Guidelines

- Follow PEP 8 style guidelines for Python code
- Write tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

---

## 🐛 Bug Reports & Feature Requests

Found a bug or have an idea? Please open an issue on GitHub:

[Report Bug](https://github.com/Airboeingbus/SmartZone-R/issues) | [Request Feature](https://github.com/Airboeingbus/SmartZone-R/issues)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**Airboeingbus** - *Initial work* - [@Airboeingbus](https://github.com/Airboeingbus)

---

## 🙏 Acknowledgments

- Airport operations teams for domain expertise
- Open-source community for amazing tools and libraries
- Contributors who help improve SmartZone-R

---

## 📧 Contact

For questions, suggestions, or collaboration opportunities:

- **GitHub**: [@Airboeingbus](https://github.com/Airboeingbus)
- **Project Link**: [SmartZone-R](https://github.com/Airboeingbus/SmartZone-R)

---

<div align="center">

**Made with ❤️ for Aviation Safety**

⭐ Star this repository if you find it helpful!

[Back to Top](#-smartzone-r)

</div>
