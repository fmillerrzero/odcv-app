# ODCV App Quick Reference

## 🚀 For Sales Team

### Finding High-Value Targets

1. **Open the app**: http://your-app-url.com
2. **Quick wins**: Click "Show Top 10 Opportunities"
3. **Specific building**: Enter address in search box

### Understanding Scores

| Score | Opportunity | Action |
|-------|------------|--------|
| 80-100 | HIGH | Call immediately - exceptional ROI |
| 60-79 | MEDIUM-HIGH | Schedule for this quarter |
| 40-59 | MEDIUM | Include in efficiency discussions |
| 0-39 | LOW | Not a priority |

### Key Selling Points by Score Component

**Low Occupancy (<70%)**
- "You're conditioning empty floors"
- "30% HVAC savings possible"
- "Perfect for hybrid work reality"

**Poor Energy Grade (D/F)**
- "Your building scored poorly on NYC's report card"
- "ODCV helps achieve C or better"
- "Avoid future penalties"

**Has CO2 DCV Already**
- "Upgrade to occupancy-based sensing"
- "10-15% additional savings"
- "Faster response than CO2"

**No BMS**
- "Standalone cloud-based system"
- "No complex integration needed"
- "Modern IoT solution"

### Financial Talking Points

**Payback <3 years**: "Pays for itself before your next lease renewal"
**Payback 3-5 years**: "Strong ROI with proven technology"
**Large buildings**: "Every month of delay costs $[monthly_savings]"

### Implementation Simplicity

**Always emphasize**:
- ✅ Zero tenant disruption
- ✅ All work in mechanical rooms
- ✅ 2-4 week installation
- ✅ No ceiling work required

**Never say**:
- ❌ "Control every VAV box"
- ❌ "Sensors in every room"
- ❌ "Complex integration"
- ❌ "Months of work"

## 📊 For Technical Team

### API Quick Reference

**Analyze one building**:
```bash
curl -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{"address": "1155 Avenue of the Americas"}'
```

**Find opportunities**:
```bash
# Low occupancy buildings
curl "http://localhost:8000/api/search?max_occupancy=70&has_vav=true"

# Poor energy grades
curl "http://localhost:8000/api/search?energy_grade=D&has_vav=true"
```

**Bulk analysis**:
```bash
curl -X POST http://localhost:8000/api/score/bulk \
  -H "Content-Type: application/json" \
  -d '["address1", "address2", "address3"]'
```

### Database Queries

**Top opportunities**:
```sql
SELECT * FROM building_profiles 
WHERE has_vav = true 
AND occupancy_percent < 70 
AND energy_grade IN ('D', 'F')
ORDER BY size_sqft DESC
```

## 🔍 Prospect Research Tips

### Best Targets
1. **Office buildings** (not retail/residential)
2. **Built 1960-2000** (old enough to be inefficient, new enough to have VAV)
3. **>100,000 sq ft** (bigger = more savings)
4. **Corporate owners** (faster decisions)

### Red Flags
- ⚠️ CAV systems (need VAV retrofit first)
- ⚠️ Recent major renovation (less opportunity)
- ⚠️ A/B energy grade (already efficient)
- ⚠️ Full occupancy (less waste to capture)

### Data Interpretation

**"No data found"**: Building might be <75,000 sq ft or residential
**High EUI + Good grade**: Check for data center or 24/7 operations
**Low score + VAV**: Look for high occupancy or recent upgrades

## 📈 Reporting

### Executive Summary Should Include
1. Dollar savings (annual)
2. Payback period (years)
3. Implementation timeline (weeks)
4. Tenant impact (none)

### Technical Report Should Include
1. Current systems (VAV, BMS status)
2. Sensor locations (AHUs only)
3. Integration method
4. M&V approach

### Common Questions

**Q: What if they already have DCV?**
A: "Your CO2 sensors are a good start. Occupancy-based control is 2x faster and more accurate."

**Q: How is this different from smart thermostats?**
A: "We control fresh air at the source, not temperature at zones. Much bigger savings."

**Q: What about our VAV boxes?**
A: "We don't touch them. We control outdoor air at the AHU level - simpler and more effective."

## 🎯 Closing Techniques

### For High Scores (80+)
"Every month you delay costs you $[monthly_savings]. Let's schedule a technical assessment this week."

### For Medium Scores (60-79)
"You're leaving money on the table. Our assessment will show exactly how much."

### For Upgrade Opportunities
"You've already invested in DCV. For a fraction of that cost, we can double your savings."

## 📞 Escalation

**Technical questions**: Forward to engineering team
**Pricing exceptions**: Check with sales manager
**Custom implementations**: Require technical assessment

## 🔗 Resources

- **Live App**: http://your-app-url.com
- **API Docs**: http://your-app-url.com/docs
- **Case Studies**: [Internal drive link]
- **ROI Calculator**: [Spreadsheet link]
