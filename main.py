"""
ODCV Building Intelligence API
FastAPI application for building assessment and ODCV opportunity scoring
"""
import logging
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import pandas as pd
from pathlib import Path

import config
from data_loader import NYCDataLoader
from geocoder import NYCGeocoder
from odcv_scorer import ODCVScorer, score_buildings_bulk

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_loader = NYCDataLoader()
geocoder = NYCGeocoder()
scorer = ODCVScorer()

# Load data on startup
@app.on_event("startup")
async def startup_event():
    """Load all datasets on startup"""
    logger.info("Starting ODCV API...")
    try:
        data_loader.load_all_datasets()
        logger.info("Data loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")


# Pydantic models
class AddressRequest(BaseModel):
    address: str = Field(..., example="1155 Avenue of the Americas, Manhattan")
    borough: Optional[str] = Field(None, example="Manhattan")


class BuildingProfile(BaseModel):
    bbl: str
    address: str
    size_sqft: Optional[float]
    year_built: Optional[int]
    floors: Optional[int]
    owner: Optional[str]
    occupancy_percent: Optional[float]
    site_eui: Optional[float]
    energy_grade: Optional[str]
    has_vav: Optional[bool]
    has_dcv: Optional[bool]
    has_bms: Optional[bool]


class ODCVScore(BaseModel):
    bbl: str
    address: str
    total_score: float
    opportunity_level: str
    savings_potential_percent: float
    annual_savings_dollars: float
    deployment_complexity: str
    implementation_plan: Dict
    recommendations: List[str]
    financial_analysis: Dict


class SearchFilters(BaseModel):
    min_size: Optional[int] = Field(None, ge=0)
    max_occupancy: Optional[int] = Field(None, le=100)
    has_vav: Optional[bool] = None
    energy_grade: Optional[str] = None


# Serve static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)

# Save index.html to static directory if it doesn't exist
index_path = static_path / "index.html"
if not index_path.exists():
    # This would normally be copied from the index.html artifact
    # For now, we'll serve from root
    pass

# API Endpoints
@app.get("/", response_class=FileResponse)
async def root():
    """Serve the web interface"""
    # Check if index.html exists in static directory
    if index_path.exists():
        return FileResponse(index_path)
    else:
        # Return the embedded HTML for now
        return HTMLResponse(content=open('index.html').read() if Path('index.html').exists() else """
        <html>
            <body>
                <h1>ODCV Building Intelligence</h1>
                <p>Please ensure index.html is in the project root directory.</p>
                <p>API Documentation: <a href="/docs">/docs</a></p>
            </body>
        </html>
        """)


@app.get("/api/geocode")
async def geocode_address(
    address: str = Query(..., description="Street address"),
    borough: Optional[str] = Query(None, description="Borough name")
):
    """Geocode an address to get BBL"""
    result = geocoder.geocode_address(address, borough)
    if not result:
        raise HTTPException(status_code=404, detail="Address not found")
    return result


@app.get("/api/building/{bbl}", response_model=BuildingProfile)
async def get_building(bbl: str):
    """Get building profile by BBL"""
    building = data_loader.get_building_by_bbl(bbl)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building


@app.post("/api/score", response_model=ODCVScore)
async def score_building(request: AddressRequest):
    """Score a building for ODCV opportunity"""
    # Geocode address
    geo_result = geocoder.geocode_address(request.address, request.borough)
    if not geo_result:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Get building data
    building = data_loader.get_building_by_bbl(geo_result['bbl'])
    if not building:
        raise HTTPException(
            status_code=404, 
            detail=f"No building data found for BBL {geo_result['bbl']}"
        )
    
    # Add address to building data
    building['address'] = geo_result['address']
    
    # Score building
    score = scorer.score_building(building)
    return score


@app.post("/api/score/bulk")
async def score_buildings_batch(addresses: List[str]):
    """Score multiple buildings at once"""
    results = []
    
    for address in addresses[:50]:  # Limit to 50 addresses
        try:
            geo_result = geocoder.geocode_address(address)
            if geo_result:
                building = data_loader.get_building_by_bbl(geo_result['bbl'])
                if building:
                    building['address'] = geo_result['address']
                    score = scorer.score_building(building)
                    results.append(score)
        except Exception as e:
            logger.error(f"Error scoring {address}: {e}")
    
    # Sort by score
    results.sort(key=lambda x: x['total_score'], reverse=True)
    return results


@app.get("/api/search")
async def search_buildings(
    min_size: Optional[int] = Query(None, description="Minimum building size (sq ft)"),
    max_occupancy: Optional[int] = Query(None, description="Maximum occupancy (%)"),
    has_vav: Optional[bool] = Query(None, description="Has VAV system"),
    energy_grade: Optional[str] = Query(None, description="Energy efficiency grade")
):
    """Search for buildings matching criteria"""
    filters = {
        'min_size': min_size,
        'max_occupancy': max_occupancy,
        'has_vav': has_vav,
        'energy_grade': energy_grade
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    results_df = data_loader.search_buildings(filters)
    
    if results_df.empty:
        return []
    
    # Convert to dict and score each building
    buildings = results_df.to_dict('records')
    scored = score_buildings_bulk(buildings)
    
    return scored[:50]  # Return top 50


@app.get("/api/opportunities")
async def get_top_opportunities(limit: int = Query(10, le=100)):
    """Get top ODCV opportunities"""
    # Query for high-opportunity buildings
    filters = {
        'has_vav': True,
        'max_occupancy': 80  # Focus on low occupancy
    }
    
    results_df = data_loader.search_buildings(filters)
    
    if results_df.empty:
        return []
    
    buildings = results_df.to_dict('records')
    scored = score_buildings_bulk(buildings)
    
    return scored[:limit]


@app.get("/api/stats")
async def get_statistics():
    """Get dataset statistics"""
    stats_query = """
    SELECT 
        COUNT(*) as total_buildings,
        COUNT(CASE WHEN has_vav = true THEN 1 END) as vav_buildings,
        COUNT(CASE WHEN occupancy_percent < 70 THEN 1 END) as low_occupancy,
        COUNT(CASE WHEN energy_grade IN ('D', 'F') THEN 1 END) as poor_grade,
        AVG(CAST(site_eui AS FLOAT)) as avg_eui,
        AVG(CAST(occupancy_percent AS FLOAT)) as avg_occupancy
    FROM building_profiles
    """
    
    result = data_loader.conn.execute(stats_query).fetchone()
    
    return {
        'total_buildings': result[0],
        'vav_buildings': result[1],
        'low_occupancy_buildings': result[2],
        'poor_grade_buildings': result[3],
        'average_eui': round(result[4], 1) if result[4] else 0,
        'average_occupancy': round(result[5], 1) if result[5] else 0
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": config.API_VERSION,
        "data_loaded": data_loader.data_loaded
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
