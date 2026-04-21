
# ✈️ SmartZone-R

<div align="center">

**Real-Time Runway Monitoring System with Role-Based Access Control**

*FastAPI Backend • WebSocket Real-Time Updates • Retro ATC Aesthetic Dashboard*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009485?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![WebSocket](https://img.shields.io/badge/WebSocket-Live-green?style=flat)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Status](#status) • [Features](#features) • [Quick Start](#quick-start) • [API](#api-endpoints) • [Architecture](#architecture)

</div>

---

## Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Dashboard UI** | ✅ Complete | Retro ATC aesthetic with 4 pages (runway, alerts, analytics, runway maps) |
| **Backend API** | ✅ Complete | FastAPI with 25+ endpoints for data, alerts, hardware monitoring |
| **Authentication (RBAC)** | ✅ Complete | JWT-based with admin/maintenance/viewer roles |
| **WebSocket Real-Time** | ✅ Complete | Live runway & alert updates via `/ws/live` |
| **ESP32 Serial Integration** | 🔄 In Progress | Hardware listener configured, awaiting physical device |
| **Automated Tests** | ⏳ Pending | Test suite framework ready for implementation |

---

## Quick Start

### 1. **Clone & Setup**
```bash
git clone https://github.com/Airboeingbus/SmartZone-R.git
cd SmartZone-R

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configure Environment**
```bash
# Copy template
cp .env.example .env

# Edit .env with your configuration
nano .env
# Set: JWT_SECRET, ADMIN_PASSWORD, MAINTENANCE_PASSWORD, VIEWER_PASSWORD
```

### 3. **Initialize Data**
```bash
# Generate initial flight data
python software/simulator/generator.py --days 7 --output both
```

### 4. **Run Backend**
```bash
cd software && python -c "from backend.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"
```

### 5. **Access Dashboard**
- Open browser: **http://localhost:8000**
- Login with credentials from `.env` file

---

## API Endpoints

### Authentication
| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/login` | Public | JWT login (returns access + refresh tokens) |
| `POST` | `/api/auth/refresh` | Public | Refresh access token |
| `GET` | `/api/auth/me` | Any | Get current user profile |

### Runway Data
| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/api/runway/zones` | viewer | Get all runway zones |
| `GET` | `/api/runway/zones/{id}` | viewer | Get specific zone data |
| `GET` | `/api/runway/landing` | viewer | Get landing data |
| `GET` | `/api/runway/zones/{id}/export` | maintenance | Download zone CSV |

### Alerts
| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/api/alerts` | viewer | Get all alerts |
| `POST` | `/api/alerts/threshold` | admin | Set alert threshold |
| `GET` | `/api/alerts/download` | maintenance | Export alerts CSV |

### Hardware Status
| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/api/hardware/status` | viewer | Get sensor status |
| `GET` | `/api/hardware/serial` | admin | Get serial connection logs |

### WebSocket
| Endpoint | Role | Description |
|----------|------|-------------|
| `GET` | `/ws/live` | viewer | Live runway + alert updates |

### Health Check
| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | Public | System health status |

---

## Architecture

### Backend (FastAPI)
```
backend/
├── main.py              # FastAPI app, WebSocket, auth routes
├── auth.py              # JWT + RBAC (require_role decorator)
├── database.py          # SQLite connector, context managers
├── serial_listener.py   # ESP32 serial data daemon
└── websocket.py         # Live update broadcaster
```

### Frontend (HTML/CSS + JavaScript)
```
frontend/
├── index.html           # Dashboard home page
├── runway.html          # Runway pressure/friction visualization
├── alerts.html          # Alert management & threshold controls
├── analytics.html       # Historical trends & correlation heatmap
└── login.html           # JWT authentication UI (retro ATC aesthetic)
```

### Data Layer
```
software/
├── simulator/
│   ├── generator.py     # Flight data generation
│   ├── flights.py       # Aircraft stress modeling
│   ├── weather.py       # Environmental conditions
│   └── config.py        # Simulation parameters
└── data/
    ├── runway_data.csv  # Flight records
    └── smartzone_r.db   # SQLite database
```

### Technology Stack
- **Framework**: FastAPI (async Python web framework)
- **Auth**: JWT with RS256 signing
- **Real-Time**: WebSocket for live updates
- **Database**: SQLite3 with context manager patterns
- **Logging**: Python logging module (production-grade)
- **Frontend**: Vanilla HTML/CSS/JavaScript (no build required)

---

## Role-Based Access Control

### Roles & Permissions

| Role | Permissions |
|------|-------------|
| **admin** | Create/modify thresholds, view all alerts, manage system, access hardware logs, force serial reconnect |
| **maintenance** | Read all data, download/export CSV, view hardware status |
| **viewer** | Read-only dashboard access, view alerts, no exports |

### Protected Endpoints
All protected endpoints return **403 INSUFFICIENT CLEARANCE** for unauthorized roles:
```
GET    /api/alerts/threshold      → admin only
POST   /api/alerts/threshold      → admin only
GET    /api/alerts/download       → maintenance+ 
GET    /api/hardware/serial       → admin only
POST   /api/hardware/reconnect    → admin only
```

---

## Environment Variables

```env
# JWT Configuration
JWT_SECRET=your-super-secret-key-min-32-chars

# Role Passwords (use strong values)
ADMIN_PASSWORD=secure_admin_password
MAINTENANCE_PASSWORD=secure_maintenance_password
VIEWER_PASSWORD=secure_viewer_password

# Hardware
SERIAL_PORT=/dev/ttyUSB0     # ESP32 port (Windows: COM3, etc.)

# Database
DB_PATH=software/data/smartzone_r.db
CSV_PATH=software/data/runway_data.csv
AIRPORT_CODE=KJFK
```

---

## Development

### Running Tests
```bash
pytest tests/ -v
pytest tests/test_generator.py -v
```

### Logging
All modules use Python `logging` with proper levels (INFO, WARNING, ERROR):
```bash
# Check logs
tail -f smartzone_r.log
```

### Code Quality
```bash
# Find any remaining print() calls
grep -r "print(" . --include="*.py"  # Should be 0

# Check imports
python -c "from software.simulator.generator import generate_data"
```

---

## Known Issues

| Issue | Status | Notes |
|-------|--------|-------|
| ESP32 serial connection | 🔄 In Progress | Requires physical device for testing |
| Multi-facility support | ⏳ Not Started | Currently designed for single runway |
| Automated tests | ⏳ Pending | Test infrastructure ready, coverage needed |
| Data persistence after restart | ✅ Complete | SQLite handles state recovery |

---

## Security Checklist

Before deploying to production:
- [ ] Change all passwords in `.env`
- [ ] Set `JWT_SECRET` to cryptographically secure 32+ char string
- [ ] Ensure `.env` is in `.gitignore` (already configured)
- [ ] Run `grep -r "admin\|maintain\|viewer" . --include="*.html"` → verify no hardcoded defaults
- [ ] Test `curl http://localhost:8000/health` → verify server running
- [ ] Test role-based access: `curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/alerts/download` → verify 403 for viewer

---

## License

MIT License - See LICENSE file for details

---

<div align="center">

**Built for Aviation Safety with Real-Time Runway Monitoring**

[GitHub](https://github.com/Airboeingbus/SmartZone-R) | [Issues](https://github.com/Airboeingbus/SmartZone-R/issues)

</div>
