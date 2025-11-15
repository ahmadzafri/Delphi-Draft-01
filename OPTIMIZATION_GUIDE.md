# Enhanced Optimization Recommendations Implementation Guide

## Current Implementation (reporting_page.py)

The optimization recommendations are implemented through:

1. **Data Analysis**: `generate_recommendations(summary, equipment_df)` function
2. **UI Display**: Professional cards with titles, descriptions, and savings calculations
3. **Calculations**: Percentage-based savings estimates

## Key Enhancement Areas:

### 1. EQUIPMENT-SPECIFIC ANALYSIS

```python
def generate_enhanced_recommendations(summary: Dict, equipment_df: pd.DataFrame) -> List[Dict]:
    """Enhanced recommendation engine with detailed analysis"""
    recommendations = []

    # Analyze by equipment category
    for category in equipment_df['Category'].unique():
        category_equipment = equipment_df[equipment_df['Category'] == category]
        recommendations.extend(analyze_category_specific(category, category_equipment))

    # Add cross-cutting recommendations
    recommendations.extend(analyze_operational_efficiency(equipment_df))
    recommendations.extend(analyze_fuel_optimization(equipment_df))
    recommendations.extend(analyze_technology_upgrades(equipment_df, summary))

    return recommendations

def analyze_category_specific(category: str, equipment_df: pd.DataFrame) -> List[Dict]:
    """Generate category-specific recommendations"""
    recommendations = []

    if category == "Power Generation":
        # Gas Turbine Recommendations
        turbines = equipment_df[equipment_df['Name'].str.contains('Turbine', na=False)]
        if not turbines.empty:
            recommendations.append({
                'title': 'Gas Turbine Efficiency Optimization',
                'category': 'Power Generation',
                'priority': 'High',
                'description': f'Optimize {len(turbines)} gas turbine(s) through advanced controls and maintenance.',
                'actions': [
                    'Install advanced combustion controls',
                    'Implement predictive maintenance',
                    'Upgrade to high-efficiency turbine blades',
                    'Add heat recovery steam generator (HRSG)'
                ],
                'investment': '$200K - $1M per turbine',
                'payback': '3-5 years',
                'potential_savings': turbines['CO2 Emissions (kg/year)'].sum() * 0.12,
                'implementation_timeline': '6-12 months',
                'difficulty': 'Medium'
            })

        # Diesel Generator Recommendations
        diesel_gens = equipment_df[equipment_df['Name'].str.contains('Diesel', na=False)]
        if not diesel_gens.empty:
            recommendations.append({
                'title': 'Diesel Generator Fuel Switch',
                'category': 'Power Generation',
                'priority': 'Medium',
                'description': f'Replace {len(diesel_gens)} diesel generator(s) with cleaner alternatives.',
                'actions': [
                    'Switch to natural gas generators',
                    'Install battery energy storage',
                    'Add solar PV with battery backup',
                    'Consider biogas fuel options'
                ],
                'investment': '$300K - $800K per generator',
                'payback': '4-7 years',
                'potential_savings': diesel_gens['CO2 Emissions (kg/year)'].sum() * 0.30,
                'implementation_timeline': '8-18 months',
                'difficulty': 'High'
            })

    elif category == "Process Heating & Steam":
        # Boiler Recommendations
        boilers = equipment_df[equipment_df['Name'].str.contains('Boiler', na=False)]
        if not boilers.empty:
            recommendations.append({
                'title': 'Boiler System Efficiency Upgrade',
                'category': 'Process Heating',
                'priority': 'High',
                'description': f'Improve efficiency of {len(boilers)} boiler system(s).',
                'actions': [
                    'Install oxygen trim control systems',
                    'Add economizers for flue gas heat recovery',
                    'Implement blowdown heat recovery',
                    'Upgrade to condensing boiler technology'
                ],
                'investment': '$75K - $300K per boiler',
                'payback': '2-4 years',
                'potential_savings': boilers['CO2 Emissions (kg/year)'].sum() * 0.15,
                'implementation_timeline': '3-6 months',
                'difficulty': 'Low'
            })

    elif category == "Flaring & Destructor":
        # Flare Stack Recommendations
        flares = equipment_df[equipment_df['Name'].str.contains('Flare', na=False)]
        if not flares.empty:
            recommendations.append({
                'title': 'Flare Gas Recovery System',
                'category': 'Gas Recovery',
                'priority': 'High',
                'description': f'Implement gas recovery for {len(flares)} flare system(s).',
                'actions': [
                    'Install flare gas recovery units',
                    'Add gas compression systems',
                    'Implement flare minimization controls',
                    'Consider thermal oxidizer upgrade'
                ],
                'investment': '$500K - $2M per system',
                'payback': '3-6 years',
                'potential_savings': flares['CO2 Emissions (kg/year)'].sum() * 0.80,
                'implementation_timeline': '12-24 months',
                'difficulty': 'High'
            })

    return recommendations
```

### 2. OPERATIONAL ANALYSIS

```python
def analyze_operational_efficiency(equipment_df: pd.DataFrame) -> List[Dict]:
    """Analyze operational patterns for optimization"""
    recommendations = []

    # High Runtime Equipment
    high_runtime = equipment_df[equipment_df['Operation Time (hours/year)'] > 6000]
    if not high_runtime.empty:
        recommendations.append({
            'title': 'Operational Schedule Optimization',
            'category': 'Operations',
            'priority': 'Medium',
            'description': f'{len(high_runtime)} equipment unit(s) operate >6000 hours/year.',
            'actions': [
                'Install energy management systems (EMS)',
                'Implement demand response programs',
                'Add variable frequency drives (VFDs)',
                'Optimize equipment sequencing'
            ],
            'investment': '$25K - $100K per unit',
            'payback': '1-3 years',
            'potential_savings': high_runtime['CO2 Emissions (kg/year)'].sum() * 0.08,
            'implementation_timeline': '2-4 months',
            'difficulty': 'Low'
        })

    # Load Factor Analysis
    avg_load_factor = 0.75  # Assumed average load factor
    if avg_load_factor < 0.80:
        recommendations.append({
            'title': 'Equipment Load Optimization',
            'category': 'Operations',
            'priority': 'Low',
            'description': 'Optimize equipment sizing and load factors.',
            'actions': [
                'Right-size equipment for actual loads',
                'Implement load balancing controls',
                'Add smart sequencing systems',
                'Consider equipment consolidation'
            ],
            'investment': '$50K - $200K',
            'payback': '2-5 years',
            'potential_savings': equipment_df['CO2 Emissions (kg/year)'].sum() * 0.05,
            'implementation_timeline': '3-6 months',
            'difficulty': 'Medium'
        })

    return recommendations
```

### 3. ECONOMIC ANALYSIS INTEGRATION

```python
def add_economic_analysis(recommendations: List[Dict], carbon_price: float = 50) -> List[Dict]:
    """Add detailed economic analysis to recommendations"""

    for rec in recommendations:
        if 'potential_savings' in rec and isinstance(rec['potential_savings'], (int, float)):
            # Calculate annual monetary savings
            annual_co2_reduction_tons = rec['potential_savings'] / 1000
            annual_cost_savings = annual_co2_reduction_tons * carbon_price

            # Add economic metrics
            rec['annual_cost_savings'] = f"${annual_cost_savings:,.0f}"
            rec['co2_reduction_tons'] = f"{annual_co2_reduction_tons:,.1f} tons/year"

            # Simple ROI calculation
            if 'investment' in rec:
                try:
                    # Parse investment range (e.g., "$200K - $1M")
                    investment_str = rec['investment'].replace('$', '').replace('K', '000').replace('M', '000000')
                    if ' - ' in investment_str:
                        min_inv = float(investment_str.split(' - ')[0].replace(',', ''))
                        max_inv = float(investment_str.split(' - ')[1].replace(',', ''))
                        avg_investment = (min_inv + max_inv) / 2
                    else:
                        avg_investment = float(investment_str.replace(',', ''))

                    if annual_cost_savings > 0:
                        simple_payback = avg_investment / annual_cost_savings
                        rec['calculated_payback'] = f"{simple_payback:.1f} years"
                        rec['roi_10_year'] = f"{((annual_cost_savings * 10 - avg_investment) / avg_investment * 100):.0f}%"

                except:
                    pass

    return recommendations
```

### 4. PRIORITY SCORING SYSTEM

```python
def calculate_priority_score(recommendation: Dict) -> float:
    """Calculate priority score for ranking recommendations"""
    score = 0

    # CO2 reduction potential (40% weight)
    if 'potential_savings' in recommendation:
        co2_reduction = recommendation['potential_savings']
        if co2_reduction > 50000:
            score += 40
        elif co2_reduction > 20000:
            score += 30
        elif co2_reduction > 5000:
            score += 20
        else:
            score += 10

    # Implementation difficulty (20% weight - easier = higher score)
    difficulty = recommendation.get('difficulty', 'Medium')
    if difficulty == 'Low':
        score += 20
    elif difficulty == 'Medium':
        score += 15
    else:  # High
        score += 10

    # Payback period (20% weight - shorter = higher score)
    payback = recommendation.get('payback', '')
    if '1-2' in payback or '1-3' in payback:
        score += 20
    elif '2-4' in payback or '2-5' in payback:
        score += 15
    elif '3-6' in payback:
        score += 10
    else:
        score += 5

    # Investment size (20% weight - lower = higher score)
    investment = recommendation.get('investment', '')
    if 'K' in investment and 'M' not in investment:
        score += 20
    elif '1M' in investment or '2M' in investment:
        score += 15
    else:
        score += 10

    return score
```

## Implementation Steps:

1. **Replace the current `generate_recommendations()` function** with the enhanced version
2. **Update the UI** to display additional fields (priority, actions, timeline, difficulty)
3. **Add interactive features** like filtering by category, priority, or investment range
4. **Include economic calculations** with current carbon pricing
5. **Add export functionality** for recommendation reports

This enhanced system provides much more detailed, actionable recommendations with economic analysis and implementation guidance.
