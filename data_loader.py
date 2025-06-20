"""
Data loader for NYC datasets
Handles PLUTO, LL84, LL87, and LL33 data
"""
import pandas as pd
import duckdb
import logging
from pathlib import Path
from typing import Dict, Optional
import config

logger = logging.getLogger(__name__)


class NYCDataLoader:
    """Load and merge NYC building datasets"""
    
    def __init__(self):
        self.conn = duckdb.connect(config.DB_PATH)
        self.data_loaded = False
        
    def load_all_datasets(self):
        """Load all datasets into DuckDB"""
        logger.info("Loading NYC datasets...")
        
        try:
            # Load PLUTO
            self._load_pluto()
            
            # Load LL84
            self._load_ll84()
            
            # Load LL87
            self._load_ll87()
            
            # Load LL33
            self._load_ll33()
            
            # Create merged view
            self._create_merged_view()
            
            self.data_loaded = True
            logger.info("All datasets loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
            raise
    
    def _load_pluto(self):
        """Load PLUTO data from borough files"""
        logger.info("Loading PLUTO data...")
        
        pluto_dfs = []
        for borough, file_path in config.PLUTO_FILES.items():
            if file_path.exists():
                df = pd.read_csv(file_path, low_memory=False)
                df['Borough'] = borough
                pluto_dfs.append(df)
                logger.info(f"Loaded {len(df)} records from {borough}")
        
        if pluto_dfs:
            pluto_combined = pd.concat(pluto_dfs, ignore_index=True)
            
            # Create BBL if not present
            if 'BBL' not in pluto_combined.columns:
                pluto_combined['BBL'] = (
                    pluto_combined['BoroCode'].astype(str) + 
                    pluto_combined['Block'].astype(str).str.zfill(5) + 
                    pluto_combined['Lot'].astype(str).str.zfill(4)
                )
            
            # Select key fields
            pluto_fields = [
                'BBL', 'Address', 'ZipCode', 'BldgArea', 'ComArea', 'ResArea',
                'OfficeArea', 'RetailArea', 'NumFloors', 'UnitsTotal', 'YearBuilt',
                'YearAlter1', 'YearAlter2', 'OwnerName', 'OwnerType', 'BldgClass',
                'LandUse', 'Easements', 'AssessTot', 'Borough'
            ]
            
            # Keep only fields that exist
            pluto_fields = [f for f in pluto_fields if f in pluto_combined.columns]
            pluto_final = pluto_combined[pluto_fields]
            
            # Load into DuckDB
            self.conn.execute("DROP TABLE IF EXISTS pluto")
            self.conn.execute("CREATE TABLE pluto AS SELECT * FROM pluto_final")
            self.conn.execute("CREATE INDEX idx_pluto_bbl ON pluto(BBL)")
            
            logger.info(f"Loaded {len(pluto_final)} PLUTO records")
        else:
            logger.warning("No PLUTO files found")
    
    def _load_ll84(self):
        """Load LL84 energy benchmarking data"""
        logger.info("Loading LL84 data...")
        
        if not config.LL84_FILE.exists():
            logger.warning("LL84 file not found")
            return
            
        # Load LL84 data
        ll84_df = pd.read_csv(config.LL84_FILE, low_memory=False)
        
        # Create BBL from Property ID if needed (example logic)
        if 'Borough/Block/Lot (BBL)' in ll84_df.columns:
            ll84_df['BBL'] = ll84_df['Borough/Block/Lot (BBL)'].astype(str)
        
        # Aggregate to annual metrics (latest year)
        latest_year = ll84_df['Calendar Year'].max()
        ll84_annual = ll84_df[ll84_df['Calendar Year'] == latest_year].groupby('Property Id').agg({
            'Site EUI (kBtu/ft²)': 'mean',
            'ENERGY STAR Score': 'first',
            'Target ENERGY STAR Score': 'first',
            'Occupancy': 'first',
            'Electricity Use (kBtu)': 'sum',
            'Natural Gas Use - Monthly (kBtu)': 'sum',
            'Annual Maximum Demand (kW)': 'max',
            'Office - Worker Density (Number per 1,000 sq ft)': 'first',
            'Number of Active Energy Meters - Total': 'first',
            'Metered Areas (Energy)': 'first'
        }).reset_index()
        
        # Map Property ID to BBL (you'll need a mapping table)
        # For now, we'll use Property ID as a proxy
        ll84_annual['BBL'] = ll84_annual['Property Id'].astype(str)
        
        # Load into DuckDB
        self.conn.execute("DROP TABLE IF EXISTS ll84")
        self.conn.execute("CREATE TABLE ll84 AS SELECT * FROM ll84_annual")
        self.conn.execute("CREATE INDEX idx_ll84_bbl ON ll84(BBL)")
        
        logger.info(f"Loaded {len(ll84_annual)} LL84 records")
    
    def _load_ll87(self):
        """Load LL87 audit data"""
        logger.info("Loading LL87 data...")
        
        if not config.LL87_FILE.exists():
            logger.warning("LL87 file not found")
            return
            
        # Load LL87 data
        ll87_df = pd.read_csv(config.LL87_FILE, low_memory=False)
        
        # Ensure BBL column
        if 'Borough/Block/Lot (BBL)' in ll87_df.columns:
            ll87_df['BBL'] = ll87_df['Borough/Block/Lot (BBL)'].astype(str)
        
        # Select key ODCV fields
        ll87_fields = [
            'BBL', 'Building Name', 'Year Completed', 'Total Floor Area',
            'Building automation system? (Y/N)',
            'Central Distribution Type: HVAC Sys 1',
            'Terminal Unit Type: HVAC Sys 1',
            'Demand Control Ventilation: HVAC Sys 1',
            'Heating System Type: HVAC Sys 1',
            'Heating System Approximate Year Installed: HVAC Sys 1',
            'Cooling System Type: HVAC Sys 1',
            'Cooling System Approximate Year Installed: HVAC Sys 1'
        ]
        
        # Keep only fields that exist
        ll87_fields = [f for f in ll87_fields if f in ll87_df.columns]
        ll87_final = ll87_df[ll87_fields].drop_duplicates(subset=['BBL'])
        
        # Create binary features
        ll87_final['has_vav'] = ll87_final.get(
            'Central Distribution Type: HVAC Sys 1', ''
        ).str.contains('Variable Air Volume', na=False)
        
        ll87_final['has_dcv'] = ll87_final.get(
            'Demand Control Ventilation: HVAC Sys 1', ''
        ) == 'Yes'
        
        ll87_final['has_bms'] = ll87_final.get(
            'Building automation system? (Y/N)', ''
        ) == 'Yes'
        
        # Load into DuckDB
        self.conn.execute("DROP TABLE IF EXISTS ll87")
        self.conn.execute("CREATE TABLE ll87 AS SELECT * FROM ll87_final")
        self.conn.execute("CREATE INDEX idx_ll87_bbl ON ll87(BBL)")
        
        logger.info(f"Loaded {len(ll87_final)} LL87 records")
    
    def _load_ll33(self):
        """Load LL33 energy grades"""
        logger.info("Loading LL33 data...")
        
        if not config.LL33_FILE.exists():
            logger.warning("LL33 file not found")
            return
            
        # Load LL33 data
        ll33_df = pd.read_csv(config.LL33_FILE, low_memory=False)
        
        # Ensure BBL column
        if 'CBL 10 Digit BBL' in ll33_df.columns:
            ll33_df['BBL'] = ll33_df['CBL 10 Digit BBL'].astype(str)
        elif 'BBL' not in ll33_df.columns:
            logger.warning("No BBL column found in LL33 data")
            return
        
        # Select key fields
        ll33_fields = ['BBL', 'Building Energy Efficiency Grade', 
                       'ENERGY STAR Score', 'Site EUI (kBtu/ft²)']
        ll33_fields = [f for f in ll33_fields if f in ll33_df.columns]
        ll33_final = ll33_df[ll33_fields].drop_duplicates(subset=['BBL'])
        
        # Load into DuckDB
        self.conn.execute("DROP TABLE IF EXISTS ll33")
        self.conn.execute("CREATE TABLE ll33 AS SELECT * FROM ll33_final")
        self.conn.execute("CREATE INDEX idx_ll33_bbl ON ll33(BBL)")
        
        logger.info(f"Loaded {len(ll33_final)} LL33 records")
    
    def _create_merged_view(self):
        """Create a merged view of all datasets"""
        logger.info("Creating merged building view...")
        
        merge_query = """
        CREATE OR REPLACE VIEW building_profiles AS
        SELECT 
            p.BBL,
            p.Address,
            p.ZipCode,
            p.Borough,
            p.BldgArea as size_sqft,
            p.OfficeArea as office_sqft,
            p.NumFloors as floors,
            p.YearBuilt as year_built,
            p.OwnerName as owner,
            p.OwnerType as owner_type,
            p.BldgClass as building_class,
            
            -- LL84 Energy Data
            l84."Site EUI (kBtu/ft²)" as site_eui,
            l84."ENERGY STAR Score" as energy_star_score,
            l84."Target ENERGY STAR Score" as target_energy_star_score,
            l84."Occupancy" as occupancy_percent,
            l84."Annual Maximum Demand (kW)" as peak_demand_kw,
            l84."Number of Active Energy Meters - Total" as active_meters,
            
            -- LL87 System Data
            l87."Building automation system? (Y/N)" as has_bms_text,
            l87."Central Distribution Type: HVAC Sys 1" as hvac_type,
            l87."Demand Control Ventilation: HVAC Sys 1" as dcv_status,
            l87.has_vav,
            l87.has_dcv,
            l87.has_bms,
            
            -- LL33 Grades
            l33."Building Energy Efficiency Grade" as energy_grade
            
        FROM pluto p
        LEFT JOIN ll84 l84 ON p.BBL = l84.BBL
        LEFT JOIN ll87 l87 ON p.BBL = l87.BBL
        LEFT JOIN ll33 l33 ON p.BBL = l33.BBL
        WHERE p.BldgArea >= 75000
        AND p.YearBuilt < 2010
        AND p.BldgClass LIKE 'O%'
        """
        
        self.conn.execute(merge_query)
        logger.info("Created merged building view")
    
    def get_building_by_bbl(self, bbl: str) -> Optional[Dict]:
        """Get building profile by BBL"""
        if not self.data_loaded:
            self.load_all_datasets()
            
        result = self.conn.execute(
            "SELECT * FROM building_profiles WHERE BBL = ?", [bbl]
        ).fetchone()
        
        if result:
            columns = [desc[0] for desc in self.conn.description]
            return dict(zip(columns, result))
        return None
    
    def search_buildings(self, filters: Dict) -> pd.DataFrame:
        """Search buildings with filters"""
        if not self.data_loaded:
            self.load_all_datasets()
            
        query = "SELECT * FROM building_profiles WHERE 1=1"
        params = []
        
        if filters.get('min_size'):
            query += " AND size_sqft >= ?"
            params.append(filters['min_size'])
            
        if filters.get('max_occupancy'):
            query += " AND occupancy_percent <= ?"
            params.append(filters['max_occupancy'])
            
        if filters.get('has_vav'):
            query += " AND has_vav = true"
            
        if filters.get('energy_grade'):
            query += " AND energy_grade = ?"
            params.append(filters['energy_grade'])
            
        query += " LIMIT 100"
        
        return self.conn.execute(query, params).df()
