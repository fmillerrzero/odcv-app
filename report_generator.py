"""
ODCV Sales Report Generator
Generates professional reports for building assessments
"""
import json
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate sales-ready reports for ODCV opportunities"""
    
    def generate_executive_summary(self, assessment: Dict) -> str:
        """Generate executive summary for C-suite"""
        
        # Extract key metrics
        score = assessment['total_score']
        savings = assessment['annual_savings_dollars']
        payback = assessment['financial_analysis']['simple_payback_years']
        level = assessment['opportunity_level']
        
        # Generate appropriate messaging based on opportunity level
        if level == 'HIGH':
            urgency = "immediate action recommended"
            value_prop = "exceptional ROI with minimal disruption"
        elif level == 'MEDIUM-HIGH':
            urgency = "strong candidate for Q1 implementation"
            value_prop = "proven technology with rapid payback"
        else:
            urgency = "consider as part of broader efficiency program"
            value_prop = "incremental improvements available"
        
        summary = f"""
EXECUTIVE SUMMARY
================

Building: {assessment['address']}
Opportunity Score: {score}/100 ({level})

FINANCIAL IMPACT
• Annual Savings: ${savings:,}
• Simple Payback: {payback} years
• 10-Year NPV: ${assessment['financial_analysis']['npv_10_year']:,}

KEY FINDINGS
{self._generate_key_findings(assessment)}

RECOMMENDATION
Based on our analysis, {urgency}. This building presents {value_prop}.

NEXT STEPS
1. Schedule technical assessment (2 hours)
2. Review implementation plan with facilities team
3. Execute deployment ({assessment['implementation_plan']['deployment_weeks']} weeks)
"""
        return summary
    
    def generate_technical_report(self, assessment: Dict) -> str:
        """Generate detailed technical report for facilities team"""
        
        impl = assessment['implementation_plan']
        
        report = f"""
TECHNICAL ASSESSMENT REPORT
==========================

Building: {assessment['address']}
Date: {datetime.now().strftime('%B %d, %Y')}

SYSTEM COMPATIBILITY
-------------------
• HVAC Type: Variable Air Volume (VAV) ✓
• Building Automation: {'Yes - BACnet ready' if impl.get('integration_type', '').startswith('BACnet') else 'Standalone system required'}
• Current DCV: {'Upgrade from CO2-based' if 'CO2' in str(assessment.get('flags', [])) else 'New installation'}

DEPLOYMENT STRATEGY
------------------
• Control Points: {impl['control_points']}
• Sensor Locations: {impl['sensor_locations']}
• Integration Method: {impl['integration_type']}
• Tenant Disruption: {impl['tenant_disruption']}

IMPLEMENTATION DETAILS
---------------------
• Sensor Count: {impl['sensor_count']} units
• AHU Count: {impl['ahu_count']} air handlers
• Deployment Timeline: {impl['deployment_weeks']} weeks
• Estimated Cost: ${impl['estimated_cost']:,}
• Cost per Sq Ft: ${impl['cost_per_sqft']:.2f}

ENERGY SAVINGS ANALYSIS
----------------------
• Current HVAC Cost: ${assessment['financial_analysis']['estimated_annual_hvac_cost']:,}
• Projected Savings: {assessment['savings_potential_percent']}% reduction
• Annual Dollar Savings: ${assessment['annual_savings_dollars']:,}

SYSTEM ARCHITECTURE
------------------
The ODCV system will control outdoor air (OA) dampers at the AHU level, 
not individual VAV boxes. This approach:
- Minimizes complexity (control {impl['ahu_count']} points vs hundreds of VAV boxes)
- Eliminates tenant disruption (all work in mechanical rooms)
- Enables rapid deployment ({impl['deployment_weeks']} weeks vs months)
- Provides centralized control via {'existing BMS' if 'BACnet' in impl['integration_type'] else 'cloud platform'}

MEASUREMENT & VERIFICATION
-------------------------
{self._generate_mv_section(assessment)}
"""
        return report
    
    def generate_comparison_report(self, buildings: List[Dict]) -> str:
        """Generate portfolio comparison report"""
        
        # Sort by score
        buildings.sort(key=lambda x: x['total_score'], reverse=True)
        
        report = f"""
PORTFOLIO ODCV OPPORTUNITY ANALYSIS
==================================

Date: {datetime.now().strftime('%B %d, %Y')}
Buildings Analyzed: {len(buildings)}

TOP OPPORTUNITIES
----------------
"""
        
        for i, building in enumerate(buildings[:10], 1):
            report += f"""
{i}. {building['address']}
   Score: {building['total_score']}/100 | Savings: ${building['annual_savings_dollars']:,}/year | Payback: {building['financial_analysis']['simple_payback_years']} years
   Key Factor: {building.get('flags', [''])[0] if building.get('flags') else 'High potential'}
"""
        
        # Summary statistics
        total_savings = sum(b['annual_savings_dollars'] for b in buildings)
        avg_payback = sum(b['financial_analysis']['simple_payback_years'] for b in buildings) / len(buildings)
        
        report += f"""

PORTFOLIO SUMMARY
----------------
• Total Annual Savings Potential: ${total_savings:,}
• Average Payback Period: {avg_payback:.1f} years
• High-Priority Buildings (Score >80): {sum(1 for b in buildings if b['total_score'] > 80)}
• Quick Wins (Payback <3 years): {sum(1 for b in buildings if b['financial_analysis']['simple_payback_years'] < 3)}

RECOMMENDED IMPLEMENTATION SEQUENCE
----------------------------------
Phase 1 (Immediate): Buildings with score >80 and BMS present
Phase 2 (Q2): Buildings with score >60 and occupancy <70%
Phase 3 (Q3-Q4): Remaining VAV buildings with proven savings potential
"""
        return report
    
    def generate_proposal_outline(self, assessment: Dict) -> str:
        """Generate proposal outline for sales team"""
        
        outline = f"""
ODCV PROPOSAL OUTLINE
====================

Building: {assessment['address']}

1. EXECUTIVE SUMMARY
   - ${assessment['annual_savings_dollars']:,} annual savings
   - {assessment['financial_analysis']['simple_payback_years']} year payback
   - Zero tenant disruption

2. CURRENT SITUATION
   - Building operates at {assessment.get('occupancy_percent', 'N/A')}% occupancy
   - Energy grade: {assessment.get('energy_grade', 'N/A')}
   - Ventilating vacant spaces at full capacity

3. PROPOSED SOLUTION
   - Occupancy-based control at AHU level
   - {assessment['implementation_plan']['sensor_count']} sensors total
   - {assessment['implementation_plan']['integration_type']}

4. FINANCIAL ANALYSIS
   - Implementation cost: ${assessment['implementation_plan']['estimated_cost']:,}
   - Annual savings: ${assessment['annual_savings_dollars']:,}
   - ROI: {assessment['financial_analysis']['roi_percent']}%
   - 10-year NPV: ${assessment['financial_analysis']['npv_10_year']:,}

5. IMPLEMENTATION PLAN
   - Week 1-2: Engineering and permits
   - Week 3-{assessment['implementation_plan']['deployment_weeks']}: Installation
   - Week {assessment['implementation_plan']['deployment_weeks']+1}: Commissioning
   - Ongoing: Performance monitoring

6. RISK MITIGATION
   - No tenant disruption (mechanical room work only)
   - Proven technology with 100+ installations
   - Performance guarantee available

7. REFERENCES
   - Similar building case studies
   - Energy savings validation
   - Customer testimonials

8. NEXT STEPS
   - Technical site assessment
   - Final proposal with fixed pricing
   - Implementation timeline confirmation
"""
        return outline
    
    def _generate_key_findings(self, assessment: Dict) -> str:
        """Generate key findings bullets"""
        findings = []
        
        # Check occupancy
        if 'occupancy' in str(assessment.get('flags', [])):
            findings.append("• Building operates at low occupancy, wasting energy on vacant spaces")
        
        # Check energy grade
        if assessment.get('energy_grade') in ['D', 'F']:
            findings.append(f"• Energy grade {assessment.get('energy_grade')} indicates significant inefficiency")
        
        # Check existing systems
        if 'BMS present' in str(assessment.get('flags', [])):
            findings.append("• Existing BMS enables seamless integration")
        elif 'No BMS' in str(assessment.get('flags', [])):
            findings.append("• Standalone ODCV system recommended")
        
        # Add savings potential
        findings.append(f"• {assessment['savings_potential_percent']}% HVAC energy reduction achievable")
        
        return '\n'.join(findings)
    
    def _generate_mv_section(self, assessment: Dict) -> str:
        """Generate measurement and verification section"""
        
        mv_text = """
The building's energy savings will be measured through:
• Direct monitoring of outdoor air flow rates
• Occupancy tracking and correlation
• Comparison of pre/post installation energy consumption
• Weather-normalized analysis
"""
        
        # Add specific meter info if available
        if assessment.get('active_meters'):
            mv_text += f"\n• Existing {assessment['active_meters']} energy meters enable precise tracking"
        
        return mv_text


def generate_all_reports(assessment: Dict) -> Dict[str, str]:
    """Generate all report types for a building assessment"""
    generator = ReportGenerator()
    
    return {
        'executive_summary': generator.generate_executive_summary(assessment),
        'technical_report': generator.generate_technical_report(assessment),
        'proposal_outline': generator.generate_proposal_outline(assessment)
    }
