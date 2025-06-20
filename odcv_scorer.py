"""
ODCV Opportunity Scoring Algorithm
Evaluates buildings for Occupancy-Driven Control Ventilation potential
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class ODCVScorer:
    """Calculate ODCV opportunity scores for buildings"""
    
    def __init__(self):
        self.params = config.ODCV_PARAMS
    
    def score_building(self, building: Dict) -> Dict:
        """
        Score a building for ODCV opportunity
        
        Returns dict with:
        - total_score: 0-100
        - savings_potential: estimated % HVAC savings
        - deployment_ease: how easy to implement
        - implementation_plan: deployment details
        - recommendations: specific actions
        """
        # Initialize scoring components
        result = {
            'bbl': building.get('bbl'),
            'address': building.get('address'),
            'total_score': 0,
            'score_components': {},
            'savings_potential_percent': 0,
            'annual_savings_dollars': 0,
            'deployment_complexity': 'Unknown',
            'implementation_plan': {},
            'recommendations': [],
            'flags': []
        }
        
        # Check basic compatibility
        if not self._check_compatibility(building, result):
            return result
        
        # Calculate component scores
        savings_score = self._score_savings_potential(building, result)
        deployment_score = self._score_deployment_ease(building, result)
        
        # Calculate total score (0-100)
        result['total_score'] = min(100, savings_score + deployment_score)
        
        # Generate implementation plan
        self._generate_implementation_plan(building, result)
        
        # Generate recommendations
        self._generate_recommendations(building, result)
        
        # Calculate financial metrics
        self._calculate_financials(building, result)
        
        # Determine opportunity level
        if result['total_score'] >= 80:
            result['opportunity_level'] = 'HIGH'
            result['action'] = 'Immediate implementation recommended'
        elif result['total_score'] >= 60:
            result['opportunity_level'] = 'MEDIUM-HIGH'
            result['action'] = 'Schedule detailed assessment'
        elif result['total_score'] >= 40:
            result['opportunity_level'] = 'MEDIUM'
            result['action'] = 'Consider with other upgrades'
        else:
            result['opportunity_level'] = 'LOW'
            result['action'] = 'Focus on other measures'
        
        return result
    
    def _check_compatibility(self, building: Dict, result: Dict) -> bool:
        """Check if building is compatible with ODCV"""
        # Must have VAV system
        if not building.get('has_vav'):
            result['flags'].append('INCOMPATIBLE: No VAV system')
            result['recommendations'].append(
                'Building has CAV system - VAV retrofit required before ODCV'
            )
            return False
        
        # Check size
        size = building.get('size_sqft', 0)
        if size < self.params['min_building_size']:
            result['flags'].append('WARNING: Below minimum size threshold')
        
        return True
    
    def _score_savings_potential(self, building: Dict, result: Dict) -> float:
        """Score the energy savings potential (0-50 points)"""
        score = 0
        components = {}
        
        # 1. Occupancy factor (0-20 points) - Most important!
        occupancy = building.get('occupancy_percent', 100)
        if occupancy < 60:
            score += 20
            components['occupancy'] = 20
            result['savings_potential_percent'] = 30
            result['flags'].append(f'MAJOR OPPORTUNITY: Only {occupancy}% occupied')
        elif occupancy < 80:
            score += 12
            components['occupancy'] = 12
            result['savings_potential_percent'] = 20
            result['flags'].append(f'GOOD OPPORTUNITY: {occupancy}% occupied')
        else:
            score += 5
            components['occupancy'] = 5
            result['savings_potential_percent'] = 10
        
        # 2. Energy performance (0-15 points)
        grade = building.get('energy_grade', 'N')
        if grade in self.params['poor_grades']:
            score += 15
            components['energy_grade'] = 15
            result['flags'].append(f'Poor energy grade: {grade}')
        elif grade == self.params['medium_grade']:
            score += 8
            components['energy_grade'] = 8
        else:
            score += 3
            components['energy_grade'] = 3
        
        # 3. EUI factor (0-10 points)
        eui = building.get('site_eui', 0)
        if eui > self.params['high_eui_threshold']:
            score += 10
            components['eui'] = 10
            result['flags'].append(f'High EUI: {eui} kBtu/sq ft')
        elif eui > 80:
            score += 5
            components['eui'] = 5
        
        # 4. System age (0-5 points)
        year_built = building.get('year_built', 2020)
        age = datetime.now().year - year_built
        if age > 40:
            score += 5
            components['building_age'] = 5
        elif age > 20:
            score += 3
            components['building_age'] = 3
        
        result['score_components']['savings_potential'] = components
        return score
    
    def _score_deployment_ease(self, building: Dict, result: Dict) -> float:
        """Score how easy it is to deploy ODCV (0-50 points)"""
        score = 0
        components = {}
        
        # 1. BMS presence (0-20 points)
        if building.get('has_bms'):
            score += 20
            components['bms'] = 20
            result['deployment_complexity'] = 'LOW'
            result['flags'].append('BMS present - easy integration')
        else:
            score += 5
            components['bms'] = 5
            result['deployment_complexity'] = 'MEDIUM'
            result['flags'].append('No BMS - standalone system needed')
        
        # 2. Existing DCV (0-15 points)
        if building.get('has_dcv'):
            score += 15
            components['existing_dcv'] = 15
            result['flags'].append('Has CO2 DCV - upgrade to ODCV')
        else:
            score += 10
            components['existing_dcv'] = 10
            result['flags'].append('No DCV - new installation')
        
        # 3. Owner type (0-10 points)
        owner_type = building.get('owner_type', '')
        if owner_type == 'C':  # Corporate
            score += 10
            components['owner_type'] = 10
            result['flags'].append('Corporate owner - faster decisions')
        else:
            score += 5
            components['owner_type'] = 5
        
        # 4. M&V capability (0-5 points)
        meters = building.get('active_meters', 1)
        if meters >= 3:
            score += 5
            components['metering'] = 5
            result['flags'].append(f'{meters} active meters - good M&V')
        
        result['score_components']['deployment_ease'] = components
        return score
    
    def _generate_implementation_plan(self, building: Dict, result: Dict):
        """Generate specific implementation plan"""
        floors = building.get('floors', 10)
        size = building.get('size_sqft', 100000)
        has_bms = building.get('has_bms', False)
        
        # Estimate AHU count
        ahu_count = max(1, floors // self.params['ahu_per_floors'])
        
        # Sensor deployment strategy
        if has_bms:
            sensor_count = ahu_count + 2  # AHUs + lobby + sample
            integration = 'BACnet integration with existing BMS'
            weeks = self.params['integration_weeks_with_bms']
        else:
            sensor_count = ahu_count + floors // 3  # More sensors needed
            integration = 'Standalone ODCV system with cloud connectivity'
            weeks = self.params['integration_weeks_without_bms']
        
        result['implementation_plan'] = {
            'ahu_count': ahu_count,
            'sensor_count': sensor_count,
            'sensor_locations': 'Mechanical rooms and lobbies only',
            'integration_type': integration,
            'deployment_weeks': weeks,
            'tenant_disruption': 'None - all work in mechanical spaces',
            'control_points': f'{ahu_count} OA dampers at AHU level',
            'estimated_cost': sensor_count * self.params['sensor_cost'],
            'cost_per_sqft': (sensor_count * self.params['sensor_cost']) / size
        }
    
    def _generate_recommendations(self, building: Dict, result: Dict):
        """Generate specific recommendations"""
        recs = result['recommendations']
        
        # Primary recommendation based on score
        if result['total_score'] >= 80:
            recs.append('IMMEDIATE ACTION: Schedule ODCV deployment assessment')
        elif result['total_score'] >= 60:
            recs.append('GOOD CANDIDATE: Include in next quarter planning')
        
        # Specific technical recommendations
        if building.get('has_dcv'):
            recs.append(
                'Upgrade existing CO2-based DCV to occupancy-based control '
                'for 10-15% additional savings'
            )
        else:
            recs.append(
                'Install new ODCV system with occupancy sensors at AHU level'
            )
        
        if building.get('has_bms'):
            recs.append(
                'Integrate ODCV with existing BMS for centralized control'
            )
        else:
            recs.append(
                'Deploy standalone ODCV system with cloud-based monitoring'
            )
        
        # Occupancy-specific recommendations
        occupancy = building.get('occupancy_percent', 100)
        if occupancy < 60:
            recs.append(
                f'With only {occupancy}% occupancy, prioritize vacant floor '
                'detection to maximize savings'
            )
        
        # Energy grade recommendations
        grade = building.get('energy_grade', 'N')
        if grade in self.params['poor_grades']:
            recs.append(
                f'Current grade {grade} indicates significant waste - '
                'ODCV can help achieve grade C or better'
            )
    
    def _calculate_financials(self, building: Dict, result: Dict):
        """Calculate financial metrics"""
        size = building.get('size_sqft', 100000)
        
        # Estimate annual energy cost (very rough)
        # Assume $3.50/sqft for NYC office building
        annual_energy_cost = size * 3.50
        hvac_portion = 0.40  # 40% of energy is HVAC
        annual_hvac_cost = annual_energy_cost * hvac_portion
        
        # Calculate savings
        savings_percent = result['savings_potential_percent'] / 100
        annual_savings = annual_hvac_cost * savings_percent
        
        # Implementation cost
        impl_cost = result['implementation_plan']['estimated_cost']
        
        # Payback
        if annual_savings > 0:
            simple_payback = impl_cost / annual_savings
        else:
            simple_payback = 999
        
        result['financial_analysis'] = {
            'estimated_annual_hvac_cost': round(annual_hvac_cost),
            'annual_savings_dollars': round(annual_savings),
            'implementation_cost': impl_cost,
            'simple_payback_years': round(simple_payback, 1),
            'roi_percent': round((annual_savings / impl_cost) * 100, 1) if impl_cost > 0 else 0,
            'npv_10_year': round(annual_savings * 10 - impl_cost)
        }
        
        result['annual_savings_dollars'] = round(annual_savings)


def score_buildings_bulk(buildings: List[Dict]) -> List[Dict]:
    """Score multiple buildings and rank by opportunity"""
    scorer = ODCVScorer()
    results = []
    
    for building in buildings:
        score = scorer.score_building(building)
        results.append(score)
    
    # Sort by total score descending
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    return results
