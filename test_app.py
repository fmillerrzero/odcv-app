"""
Basic tests for ODCV app
Run with: pytest test_app.py
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from odcv_scorer import ODCVScorer
from geocoder import NYCGeocoder

client = TestClient(app)


def test_health_check():
    """Test the health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_docs():
    """Test that API docs are accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_geocoding():
    """Test address geocoding"""
    geocoder = NYCGeocoder()
    result = geocoder.geocode_address("1155 Avenue of the Americas", "Manhattan")
    assert result is not None
    assert "bbl" in result


def test_scoring_algorithm():
    """Test ODCV scoring"""
    scorer = ODCVScorer()
    
    # Test high-opportunity building
    building = {
        'bbl': '1000700001',
        'address': '77 WATER STREET',
        'size_sqft': 546882,
        'year_built': 1969,
        'occupancy_percent': 55,  # Low occupancy
        'site_eui': 120,  # High EUI
        'energy_grade': 'D',  # Poor grade
        'has_vav': True,
        'has_dcv': False,
        'has_bms': True
    }
    
    result = scorer.score_building(building)
    
    assert result['total_score'] > 70  # Should be high opportunity
    assert result['opportunity_level'] in ['HIGH', 'MEDIUM-HIGH']
    assert result['savings_potential_percent'] >= 20
    assert result['implementation_plan']['sensor_count'] > 0


def test_incompatible_building():
    """Test building without VAV"""
    scorer = ODCVScorer()
    
    # CAV building - not compatible
    building = {
        'bbl': '1000420031',
        'address': '80 MAIDEN LANE',
        'size_sqft': 527605,
        'has_vav': False,  # No VAV!
        'has_dcv': False,
        'has_bms': True
    }
    
    result = scorer.score_building(building)
    
    assert result['total_score'] == 0
    assert 'INCOMPATIBLE' in str(result['flags'])


def test_score_endpoint():
    """Test the scoring API endpoint"""
    response = client.post("/api/score", json={
        "address": "77 Water Street",
        "borough": "Manhattan"
    })
    
    # Should work with mock data even without real geocoding
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "total_score" in data
        assert "opportunity_level" in data
        assert "recommendations" in data


def test_search_endpoint():
    """Test the search endpoint"""
    response = client.get("/api/search?has_vav=true")
    assert response.status_code == 200
    # Results depend on loaded data


def test_opportunities_endpoint():
    """Test the opportunities endpoint"""
    response = client.get("/api/opportunities?limit=5")
    assert response.status_code == 200
    # Results depend on loaded data


def test_financial_calculations():
    """Test financial metrics calculation"""
    scorer = ODCVScorer()
    
    building = {
        'bbl': 'test',
        'address': 'TEST BUILDING',
        'size_sqft': 100000,
        'occupancy_percent': 50,  # Very low
        'has_vav': True,
        'has_bms': True,
        'energy_grade': 'F'
    }
    
    result = scorer.score_building(building)
    
    # Check financial calculations make sense
    assert result['annual_savings_dollars'] > 0
    assert result['financial_analysis']['simple_payback_years'] > 0
    assert result['financial_analysis']['simple_payback_years'] < 10  # Reasonable payback
    assert result['financial_analysis']['roi_percent'] > 0


if __name__ == "__main__":
    # Run basic tests
    print("Running ODCV app tests...")
    
    test_health_check()
    print("✅ Health check passed")
    
    test_geocoding()
    print("✅ Geocoding passed")
    
    test_scoring_algorithm()
    print("✅ Scoring algorithm passed")
    
    test_incompatible_building()
    print("✅ Incompatible building handling passed")
    
    test_financial_calculations()
    print("✅ Financial calculations passed")
    
    print("\n✨ All tests passed!")
