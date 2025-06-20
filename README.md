# ODCV Building Intelligence App

Transform NYC building data into actionable ODCV (Occupancy-Driven Control Ventilation) opportunities. This app helps R-Zero's sales team proactively identify and assess buildings for ODCV retrofits.

## 🚀 Features

- **Instant Building Assessment**: Enter any NYC address and get ODCV opportunity score in seconds
- **Comprehensive Scoring**: Evaluates savings potential, deployment ease, and ROI
- **Implementation Planning**: Automated sensor count, timeline, and cost estimates
- **Sales Reports**: Generate executive summaries and technical proposals
- **Portfolio Analysis**: Bulk assess multiple buildings and rank opportunities

## 📊 Data Sources

The app integrates four NYC datasets:
- **PLUTO**: Building characteristics (size, age, owner)
- **LL84**: Energy consumption and occupancy data
- **LL87**: HVAC system details and audit information
- **LL33/95**: Energy efficiency grades

## 🛠️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/odcv-app.git
cd odcv-app
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.template .env
# Edit .env with your NYC Geoclient API credentials
```

Get NYC Geoclient API credentials from: https://developer.cityofnewyork.us/

### 4. Download NYC datasets

Create a `data` directory structure:
```
data/
├── pluto/
│   ├── MN.csv  # Manhattan
│   ├── BX.csv  # Bronx
│   ├── BK.csv  # Brooklyn
│   ├── QN.csv  # Queens
│   └── SI.csv  # Staten Island
├── ll84_monthly.csv
├── ll87_2019_2024.csv
└── ll33_grades.csv
```

Download datasets from:
- **PLUTO**: https://www.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page
- **LL84**: https://www.nyc.gov/site/buildings/codes/benchmarking.page
- **LL87**: https://data.cityofnewyork.us/Environment/LL87-Energy-Audit-Data/au6c-jqvf
- **LL33/95**: https://www.nyc.gov/site/buildings/codes/energy-grades.page

### 5. Run the application

#### Development
```bash
python main.py
```

#### Production
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 🌐 API Endpoints

### Analyze a single building
```bash
curl -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{"address": "1155 Avenue of the Americas"}'
```

### Get top opportunities
```bash
curl http://localhost:8000/api/opportunities?limit=10
```

### Search buildings
```bash
curl "http://localhost:8000/api/search?has_vav=true&max_occupancy=70"
```

## 🖥️ Web Interface

Open http://localhost:8000 in your browser to use the web interface.

## 📈 Scoring Algorithm

The app scores buildings on a 0-100 scale based on:

### Savings Potential (50 points)
- **Occupancy** (20 points): Low occupancy = high waste
- **Energy Grade** (15 points): D/F grades = poor performance
- **EUI** (10 points): High energy intensity
- **Building Age** (5 points): Older = less efficient

### Deployment Ease (50 points)
- **BMS Presence** (20 points): Easier integration
- **Existing DCV** (15 points): Upgrade opportunity
- **Owner Type** (10 points): Corporate = faster decisions
- **Metering** (5 points): Better M&V capability

## 🚢 Deployment on Render

1. Push code to GitHub
2. Connect repository to Render
3. Use the included `render.yaml` configuration
4. Set environment variables in Render dashboard
5. Deploy!

## 📝 Sample Output

```json
{
  "bbl": "1000700001",
  "address": "77 WATER STREET",
  "total_score": 87,
  "opportunity_level": "HIGH",
  "savings_potential_percent": 30,
  "annual_savings_dollars": 145000,
  "deployment_complexity": "LOW",
  "implementation_plan": {
    "sensor_count": 12,
    "deployment_weeks": 2,
    "estimated_cost": 24000
  },
  "financial_analysis": {
    "simple_payback_years": 1.7,
    "roi_percent": 604,
    "npv_10_year": 1426000
  }
}
```

## 🔧 Customization

### Adjust scoring parameters in `config.py`:
```python
ODCV_PARAMS = {
    "min_building_size": 75000,  # sq ft
    "high_eui_threshold": 100,   # kBtu/sq ft
    "low_occupancy_threshold": 70,  # %
    # ... more parameters
}
```

## 📄 License

MIT

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Support

For questions or issues, contact: support@r-zero.com
