# Data Preparation Guide

This guide helps you download and prepare the NYC datasets needed for the ODCV app.

## 📁 Required Directory Structure

```
odcv-app/
├── data/
│   ├── pluto/
│   │   ├── MN.csv    # Manhattan
│   │   ├── BX.csv    # Bronx
│   │   ├── BK.csv    # Brooklyn
│   │   ├── QN.csv    # Queens
│   │   └── SI.csv    # Staten Island
│   ├── ll84_monthly.csv
│   ├── ll87_2019_2024.csv
│   └── ll33_grades.csv
└── cache/
    └── odcv.db       # Created automatically
```

## 📥 Dataset Download Instructions

### 1. PLUTO (Property Land Use Tax Lot Output)

**What it provides**: Building size, age, floors, owner information

**Download from**: https://www.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page

**Steps**:
1. Click "Download PLUTO" 
2. Select the latest version (e.g., "24v2")
3. Download "CSV format" for each borough:
   - Manhattan → save as `data/pluto/MN.csv`
   - Bronx → save as `data/pluto/BX.csv`
   - Brooklyn → save as `data/pluto/BK.csv`
   - Queens → save as `data/pluto/QN.csv`
   - Staten Island → save as `data/pluto/SI.csv`

### 2. LL84 Energy Benchmarking Data

**What it provides**: Energy consumption, occupancy rates, EUI

**Download from**: https://www.nyc.gov/site/buildings/codes/benchmarking.page

**Steps**:
1. Find "LL84 Benchmarking Data Disclosure"
2. Download the latest "Monthly Data" CSV
3. Save as `data/ll84_monthly.csv`

**Alternative direct link**: 
- 2023 Data: https://data.cityofnewyork.us/Environment/NYC-Building-Energy-and-Water-Data-Disclosure/7x8b-9xir

### 3. LL87 Energy Audit Data

**What it provides**: HVAC system details, BMS presence, DCV status

**Download from**: https://data.cityofnewyork.us/Environment/LL87-Energy-Audit-Data/au6c-jqvf

**Steps**:
1. Click "Export"
2. Select "CSV for Excel"
3. Save as `data/ll87_2019_2024.csv`

### 4. LL33/95 Energy Grades

**What it provides**: Building energy efficiency grades (A-F)

**Download from**: https://www.nyc.gov/site/buildings/codes/energy-grades.page

**Steps**:
1. Find "Building Energy Efficiency Rating Labels"
2. Download the latest disclosure file
3. Save as `data/ll33_grades.csv`

**Alternative**: Check NYC Open Data for "DOB Sustainability Compliance Map"

## 🔧 Data Preparation Tips

### File Size Expectations
- PLUTO: ~50-100 MB per borough
- LL84: ~200-500 MB
- LL87: ~100-200 MB
- LL33: ~10-50 MB

### Common Issues and Solutions

**Issue**: Files are in Excel format (.xlsx)
```python
# Convert to CSV using pandas
import pandas as pd
df = pd.read_excel('file.xlsx')
df.to_csv('file.csv', index=False)
```

**Issue**: Different column names across years
- The app handles common variations
- Check logs for any unrecognized columns

**Issue**: BBL format inconsistencies
- Should be 10 digits: 1 (borough) + 5 (block) + 4 (lot)
- The app automatically formats BBLs

### Minimal Dataset for Testing

If you want to test with minimal data:
1. Download just Manhattan PLUTO (`MN.csv`)
2. Use the sample data provided in the repository
3. The app includes mock data for demos

## 🧪 Verify Data Loading

After placing files, test data loading:

```python
python -c "from data_loader import NYCDataLoader; loader = NYCDataLoader(); loader.load_all_datasets(); print('✅ Data loaded successfully')"
```

## 📊 Sample Data Statistics

When properly loaded, you should see approximately:
- PLUTO: ~850,000 total properties
- LL84: ~15,000 benchmarked buildings
- LL87: ~5,000 audited buildings
- LL33: ~15,000 graded buildings

## 🔄 Updating Data

NYC releases updated data:
- PLUTO: 2-3 times per year
- LL84: Annually (October)
- LL87: Ongoing updates
- LL33: Annually

Set a calendar reminder to update datasets quarterly.

## 🤔 Troubleshooting

**"No data found" errors**:
- Check file paths match exactly
- Ensure CSV format (not Excel)
- Verify BBL columns exist

**Performance issues**:
- Consider using a subset of boroughs
- Increase memory allocation
- Use data sampling for development

**Missing buildings**:
- Not all buildings are in all datasets
- LL84/87/33 only cover buildings >25,000 sq ft
- Some buildings may not have reported

## 📧 Support

For NYC data questions:
- PLUTO: https://www.nyc.gov/site/planning/data-maps/open-data.page
- Energy data: https://www.nyc.gov/site/buildings/codes/benchmarking.page

For app issues: Create an issue on GitHub
