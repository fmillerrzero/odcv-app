"""
NYC Address Geocoding Module
Converts addresses to BBL using NYC Geoclient API
"""
import logging
from typing import Optional, Dict
from geoclient import Geoclient
import config

logger = logging.getLogger(__name__)


class NYCGeocoder:
    """Handle NYC address geocoding"""
    
    def __init__(self):
        if not config.GEOCLIENT_APP_ID or not config.GEOCLIENT_APP_KEY:
            logger.warning("Geoclient API credentials not configured")
            self.client = None
        else:
            self.client = Geoclient(
                config.GEOCLIENT_APP_ID,
                config.GEOCLIENT_APP_KEY
            )
    
    def geocode_address(self, address: str, borough: Optional[str] = None) -> Optional[Dict]:
        """
        Geocode an address to get BBL and other location data
        
        Args:
            address: Street address (e.g., "123 Main St")
            borough: Borough name (Manhattan, Brooklyn, etc.) or ZIP code
            
        Returns:
            Dict with BBL and other geocoded data, or None if not found
        """
        if not self.client:
            # Fallback for demo/testing without API credentials
            return self._mock_geocode(address, borough)
        
        try:
            # Parse address components
            if not borough and ',' in address:
                parts = address.split(',')
                address = parts[0].strip()
                if len(parts) > 1:
                    borough = parts[1].strip()
            
            # Try geocoding with borough
            if borough:
                result = self.client.address(address, borough)
            else:
                # Try to extract borough from address
                for b in ['Manhattan', 'Brooklyn', 'Bronx', 'Queens', 'Staten Island']:
                    if b.lower() in address.lower():
                        borough = b
                        address = address.replace(b, '').replace(',', '').strip()
                        result = self.client.address(address, borough)
                        break
                else:
                    # Default to Manhattan for demos
                    result = self.client.address(address, 'Manhattan')
            
            if result and 'bbl' in result:
                return {
                    'bbl': result['bbl'],
                    'address': result.get('houseNumber', '') + ' ' + 
                              result.get('firstStreetNameNormalized', ''),
                    'borough': result.get('firstBoroughName'),
                    'zipCode': result.get('zipCode'),
                    'bin': result.get('buildingIdentificationNumber'),
                    'latitude': result.get('latitude'),
                    'longitude': result.get('longitude')
                }
            
        except Exception as e:
            logger.error(f"Geocoding error for {address}: {e}")
        
        return None
    
    def _mock_geocode(self, address: str, borough: Optional[str]) -> Optional[Dict]:
        """Mock geocoding for testing without API credentials"""
        # Sample buildings for demo
        mock_data = {
            "1155 avenue of the americas": {
                'bbl': '1010130029',
                'address': '1155 AVENUE OF THE AMERICAS',
                'borough': 'MANHATTAN',
                'zipCode': '10036'
            },
            "80 maiden lane": {
                'bbl': '1000420031',
                'address': '80 MAIDEN LANE',
                'borough': 'MANHATTAN',
                'zipCode': '10038'
            },
            "77 water street": {
                'bbl': '1000700001',
                'address': '77 WATER STREET',
                'borough': 'MANHATTAN',
                'zipCode': '10005'
            },
            "140 broadway": {
                'bbl': '1000380001',
                'address': '140 BROADWAY',
                'borough': 'MANHATTAN',
                'zipCode': '10005'
            },
            "200 e 42nd street": {
                'bbl': '1000730001',
                'address': '200 E 42ND STREET',
                'borough': 'MANHATTAN',
                'zipCode': '10017'
            }
        }
        
        # Normalize address for lookup
        normalized = address.lower().strip()
        for key, data in mock_data.items():
            if key in normalized:
                return data
        
        # Generate a fake BBL for unknown addresses
        return {
            'bbl': '1000000001',
            'address': address.upper(),
            'borough': borough or 'MANHATTAN',
            'zipCode': '10001'
        }
    
    def batch_geocode(self, addresses: list) -> Dict[str, Optional[Dict]]:
        """Geocode multiple addresses"""
        results = {}
        for address in addresses:
            results[address] = self.geocode_address(address)
        return results
