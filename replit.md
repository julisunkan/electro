# ElectroHub - Electronics Engineering Platform

## Overview
ElectroHub is a comprehensive Flask-based web application for electronics engineering. It provides calculators, analysis tools, and virtual experiments for students, engineers, and hobbyists.

**Current State**: Fully functional MVP with all 9 modules implemented.

## Project Structure
```
ElectroHub/
├── app.py                 # Main Flask application with all routes
├── database.py            # SQLite database operations
├── requirements.txt       # Python dependencies
├── modules/
│   ├── calculator.py      # Electronics calculator functions
│   ├── circuit_analysis.py # DC/AC circuit analysis
│   ├── signal_processing.py # Signal generation and FFT
│   ├── antenna_rf.py      # Antenna and RF calculations
│   ├── solar_energy.py    # Solar system design
│   ├── energy_analyzer.py # Energy consumption analysis
│   ├── fault_diagnosis.py # Expert system for troubleshooting
│   ├── iot_api.py         # IoT sensor monitoring
│   └── virtual_lab.py     # Virtual electronics experiments
├── templates/
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Dashboard
│   ├── calculator.html    # Electronics calculator
│   ├── circuit.html       # Circuit analysis
│   ├── signal.html        # Signal processing
│   ├── antenna.html       # Antenna & RF design
│   ├── solar.html         # Solar energy design
│   ├── energy.html        # Energy analyzer
│   ├── iot.html           # IoT monitoring
│   └── lab.html           # Virtual lab
├── static/
│   ├── css/style.css      # Custom styles
│   └── plots/             # Generated plots and reports
└── electrohub.db          # SQLite database (auto-created)
```

## Features

### 1. Electronics Calculator
- Ohm's law calculations
- RC/RL/RLC circuit analysis
- Voltage divider calculator
- Tolerance analysis
- Power rating checker
- Unit converter (engineering prefixes)

### 2. Circuit Analysis
- DC analysis with Kirchhoff's laws
- AC analysis with impedance/phase
- Frequency response (Bode plots)
- Efficiency calculations

### 3. Signal Processing
- Signal generator (sine, square, triangle, sawtooth)
- FFT spectrum analysis
- Noise injection (Gaussian, uniform, pink)
- Bandwidth analysis
- Interactive Plotly charts

### 4. Antenna & RF Design
- Frequency/wavelength conversion
- Half-wave dipole calculator
- Yagi-Uda antenna design
- Impedance matching
- Link budget analysis

### 5. Solar & Energy Design
- Panel sizing calculator
- Battery bank sizing
- Inverter sizing
- System losses analysis
- ROI analysis
- PDF report generation

### 6. Energy Consumption Analyzer
- CSV file upload
- Peak detection
- Cost estimation (flat/TOU rates)
- Efficiency calculation
- Recommendations

### 7. Fault Diagnosis
- Symptom-based troubleshooting
- Rule-based expert system
- Repair priority recommendations
- Component test procedures

### 8. IoT Monitoring
- REST API for sensor data
- Device simulator
- Threshold-based alerts
- Historical data plots
- CSV export

### 9. Virtual Electronics Lab
- RC transient response
- RLC resonance experiment
- Diode I-V characteristics
- Amplifier gain measurement
- Tolerance simulation
- PDF lab report generation

## Tech Stack
- **Backend**: Python 3.11, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, Bootstrap 5, Vanilla JS
- **Scientific**: NumPy, SciPy, SymPy, Pandas
- **Visualization**: Plotly
- **Reports**: ReportLab

## Running the Application
```bash
python app.py
```
The app runs on port 5000.

## API Endpoints
All modules expose REST API endpoints under `/api/`:
- `/api/calculator/*` - Calculator functions
- `/api/circuit/*` - Circuit analysis
- `/api/signal/*` - Signal processing
- `/api/antenna/*` - Antenna & RF
- `/api/solar/*` - Solar energy
- `/api/energy/*` - Energy analysis
- `/api/fault/*` - Fault diagnosis
- `/api/iot/*` - IoT monitoring
- `/api/lab/*` - Virtual lab

## Database Tables
- `calculations` - Calculation history
- `iot_readings` - Sensor data
- `energy_data` - Energy analysis results
- `lab_reports` - Lab experiment reports

## User Preferences
- No login required - immediate access
- All calculations saved to history
- PDF reports can be generated
- CSV export available

## Recent Changes
- 2025-12-17: PWA Enhancement Update
  - Added Progressive Web App (PWA) support with manifest and service worker
  - Generated colorful PNG and maskable logos
  - Improved UI with modern animations and transitions
  - Fixed sidebar menu alignment with smooth hover effects
  - Added hero slideshow on homepage dashboard
  - Fixed PDF download functionality
  - Added gradient-colored module icons
  - Enhanced overall visual design with modern styling

- 2025-12-17: Initial implementation of all 9 modules
- Clean Bootstrap UI with responsive design
- Interactive Plotly charts for visualization
- SQLite database for data persistence

## PWA Features
- Installable as a standalone app on mobile and desktop
- Service worker for offline caching support
- Custom app icons (192x192 and 512x512)
- Maskable icon for adaptive display
- Theme color integration
