# Enhanced Optimization Recommendations for CO2 Sim WebApp

def generate_advanced_recommendations(summary: dict, equipment_df, facility_layout=None):
    """
    Enhanced recommendation engine with more sophisticated analysis
    """
    recommendations = []
    
    # 1. EQUIPMENT-SPECIFIC RECOMMENDATIONS
    # Analyze each equipment type individually
    for category in equipment_df['Category'].unique():
        category_equipment = equipment_df[equipment_df['Category'] == category]
        
        if category == "Power Generation":
            recommendations.extend(analyze_power_generation(category_equipment))
        elif category == "Process Heating & Steam":
            recommendations.extend(analyze_heating_systems(category_equipment))
        elif category == "Flaring & Destructor":
            recommendations.extend(analyze_flaring_systems(category_equipment))
    
    # 2. OPERATIONAL OPTIMIZATION
    recommendations.extend(analyze_operational_patterns(equipment_df))
    
    # 3. TECHNOLOGY UPGRADE RECOMMENDATIONS
    recommendations.extend(analyze_technology_upgrades(equipment_df))
    
    # 4. FACILITY LAYOUT OPTIMIZATION
    if facility_layout:
        recommendations.extend(analyze_layout_efficiency(equipment_df, facility_layout))
    
    # 5. REGULATORY COMPLIANCE
    recommendations.extend(analyze_regulatory_opportunities(summary))
    
    # 6. ECONOMIC ANALYSIS
    recommendations = add_economic_analysis(recommendations, summary)
    
    return recommendations

def analyze_power_generation(equipment_df):
    """Analyze power generation equipment for optimization"""
    recommendations = []
    
    # Gas Turbine Analysis
    turbines = equipment_df[equipment_df['Name'].str.contains('Turbine', na=False)]
    if not turbines.empty:
        avg_efficiency = calculate_turbine_efficiency(turbines)
        if avg_efficiency < 35:  # Industry benchmark
            recommendations.append({
                'title': 'Gas Turbine Efficiency Upgrade',
                'category': 'Technology Upgrade',
                'priority': 'High',
                'description': f'Your gas turbines operate at {avg_efficiency:.1f}% efficiency. Modern turbines achieve 40-45% efficiency.',
                'implementation': [
                    'Upgrade to high-efficiency gas turbines',
                    'Install heat recovery systems',
                    'Implement predictive maintenance'
                ],
                'investment_range': '$500K - $2M per turbine',
                'payback_period': '3-5 years',
                'potential_savings': calculate_turbine_upgrade_savings(turbines),
                'co2_reduction_percent': 15
            })
    
    # Diesel Generator Analysis
    diesel_gens = equipment_df[equipment_df['Name'].str.contains('Diesel', na=False)]
    if not diesel_gens.empty:
        recommendations.append({
            'title': 'Diesel Generator Replacement',
            'category': 'Fuel Switch',
            'priority': 'Medium',
            'description': f'Replace {len(diesel_gens)} diesel generators with cleaner alternatives.',
            'implementation': [
                'Install natural gas generators',
                'Consider battery storage + solar',
                'Hybrid diesel-battery systems'
            ],
            'investment_range': '$200K - $800K per generator',
            'payback_period': '4-7 years',
            'potential_savings': calculate_diesel_replacement_savings(diesel_gens),
            'co2_reduction_percent': 25
        })
    
    return recommendations

def analyze_heating_systems(equipment_df):
    """Analyze heating and steam systems"""
    recommendations = []
    
    # Boiler Efficiency Analysis
    boilers = equipment_df[equipment_df['Name'].str.contains('Boiler', na=False)]
    if not boilers.empty:
        recommendations.append({
            'title': 'Boiler System Optimization',
            'category': 'Efficiency Improvement',
            'priority': 'High',
            'description': 'Implement advanced boiler controls and heat recovery systems.',
            'implementation': [
                'Install oxygen trim control systems',
                'Add economizers for heat recovery',
                'Implement blowdown heat recovery',
                'Upgrade to condensing boilers where applicable'
            ],
            'investment_range': '$50K - $300K per boiler',
            'payback_period': '2-4 years',
            'potential_savings': boilers['CO2 Emissions (kg/year)'].sum() * 0.12,
            'co2_reduction_percent': 12
        })
    
    # Process Heater Analysis
    heaters = equipment_df[equipment_df['Name'].str.contains('Heater', na=False)]
    if not heaters.empty:
        recommendations.append({
            'title': 'Process Heater Electrification',
            'category': 'Electrification',
            'priority': 'Medium',
            'description': 'Convert process heaters to electric heating where feasible.',
            'implementation': [
                'Install electric heating elements',
                'Upgrade electrical infrastructure',
                'Implement smart heating controls'
            ],
            'investment_range': '$100K - $500K per heater',
            'payback_period': '5-8 years',
            'potential_savings': heaters['CO2 Emissions (kg/year)'].sum() * 0.40,
            'co2_reduction_percent': 40
        })
    
    return recommendations

def analyze_operational_patterns(equipment_df):
    """Analyze operational patterns for optimization opportunities"""
    recommendations = []
    
    # High Operating Hours Analysis
    high_runtime = equipment_df[equipment_df['Operation Time (hours/year)'] > 6000]
    if not high_runtime.empty:
        recommendations.append({
            'title': 'Operational Schedule Optimization',
            'category': 'Operational Efficiency',
            'priority': 'Medium',
            'description': f'{len(high_runtime)} equipment units operate >6000 hours/year. Optimize schedules to reduce runtime.',
            'implementation': [
                'Install energy management systems',
                'Implement demand-response programs',
                'Optimize equipment sequencing',
                'Add variable frequency drives (VFDs)'
            ],
            'investment_range': '$20K - $100K per unit',
            'payback_period': '1-3 years',
            'potential_savings': high_runtime['CO2 Emissions (kg/year)'].sum() * 0.08,
            'co2_reduction_percent': 8
        })
    
    # Load Factor Analysis
    recommendations.append({
        'title': 'Load Factor Optimization',
        'category': 'Operational Efficiency',
        'priority': 'Low',
        'description': 'Optimize equipment load factors to improve efficiency.',
        'implementation': [
            'Implement load balancing systems',
            'Right-size equipment for actual loads',
            'Install smart controls for load optimization'
        ],
        'investment_range': '$30K - $150K',
        'payback_period': '2-4 years',
        'potential_savings': equipment_df['CO2 Emissions (kg/year)'].sum() * 0.05,
        'co2_reduction_percent': 5
    })
    
    return recommendations

def analyze_technology_upgrades(equipment_df):
    """Identify technology upgrade opportunities"""
    recommendations = []
    
    # Carbon Capture Opportunities
    high_co2_equipment = equipment_df.nlargest(3, 'CO2 Emissions (kg/year)')
    if not high_co2_equipment.empty:
        total_emissions = high_co2_equipment['CO2 Emissions (kg/year)'].sum()
        if total_emissions > 50000:  # Threshold for carbon capture viability
            recommendations.append({
                'title': 'Carbon Capture and Storage (CCS)',
                'category': 'Advanced Technology',
                'priority': 'Long-term',
                'description': f'Install CCS systems for your highest-emitting equipment ({total_emissions:.0f} kg CO2/year).',
                'implementation': [
                    'Feasibility study for CCS integration',
                    'Partner with CCS technology providers',
                    'Evaluate CO2 utilization opportunities',
                    'Consider carbon credits and incentives'
                ],
                'investment_range': '$1M - $10M',
                'payback_period': '8-15 years',
                'potential_savings': total_emissions * 0.90,
                'co2_reduction_percent': 90
            })
    
    # Heat Recovery Opportunities
    recommendations.append({
        'title': 'Waste Heat Recovery Systems',
        'category': 'Energy Recovery',
        'priority': 'Medium',
        'description': 'Implement waste heat recovery from high-temperature equipment.',
        'implementation': [
            'Install heat exchangers',
            'Implement organic Rankine cycle (ORC) systems',
            'Add heat pumps for low-grade heat recovery',
            'Consider district heating/cooling integration'
        ],
        'investment_range': '$200K - $1M',
        'payback_period': '3-6 years',
        'potential_savings': equipment_df['CO2 Emissions (kg/year)'].sum() * 0.10,
        'co2_reduction_percent': 10
    })
    
    return recommendations

def analyze_layout_efficiency(equipment_df, facility_layout):
    """Analyze facility layout for efficiency improvements"""
    recommendations = []
    
    # This would analyze the 3D layout from your builder page
    # to identify optimization opportunities based on equipment positioning
    
    recommendations.append({
        'title': 'Facility Layout Optimization',
        'category': 'Layout Efficiency',
        'priority': 'Low',
        'description': 'Optimize equipment placement to reduce piping losses and improve efficiency.',
        'implementation': [
            'Relocate equipment to minimize distances',
            'Optimize piping and electrical routing',
            'Improve maintenance access',
            'Consider future expansion needs'
        ],
        'investment_range': '$100K - $500K',
        'payback_period': '5-10 years',
        'potential_savings': equipment_df['CO2 Emissions (kg/year)'].sum() * 0.03,
        'co2_reduction_percent': 3
    })
    
    return recommendations

def analyze_regulatory_opportunities(summary):
    """Identify regulatory compliance and incentive opportunities"""
    recommendations = []
    
    recommendations.append({
        'title': 'Carbon Credit Opportunities',
        'category': 'Financial Incentives',
        'priority': 'High',
        'description': 'Explore carbon credit programs and environmental incentives.',
        'implementation': [
            'Register for voluntary carbon markets',
            'Apply for government incentives',
            'Implement carbon accounting systems',
            'Consider renewable energy certificates (RECs)'
        ],
        'investment_range': '$10K - $50K',
        'payback_period': 'Immediate revenue',
        'potential_savings': 'Revenue generation opportunity',
        'co2_reduction_percent': 0
    })
    
    return recommendations

def add_economic_analysis(recommendations, summary):
    """Add economic analysis to recommendations"""
    for rec in recommendations:
        # Add NPV calculation
        if 'potential_savings' in rec and isinstance(rec['potential_savings'], (int, float)):
            co2_price = 50  # $/ton CO2 (carbon price assumption)
            annual_savings = (rec['potential_savings'] / 1000) * co2_price  # Convert kg to tons
            
            rec['annual_cost_savings'] = f"${annual_savings:,.0f}"
            rec['co2_price_assumption'] = f"${co2_price}/ton CO2"
            
            # Simple NPV calculation (10 year horizon, 8% discount rate)
            if 'payback_period' in rec:
                try:
                    payback_years = float(rec['payback_period'].split('-')[0])
                    npv = calculate_npv(annual_savings, payback_years, 0.08, 10)
                    rec['npv_10_year'] = f"${npv:,.0f}"
                except:
                    pass
    
    return recommendations

def calculate_npv(annual_cash_flow, initial_investment_years, discount_rate, years):
    """Calculate Net Present Value"""
    initial_investment = annual_cash_flow * initial_investment_years
    npv = -initial_investment
    
    for year in range(1, years + 1):
        npv += annual_cash_flow / ((1 + discount_rate) ** year)
    
    return npv

# Helper functions for calculations
def calculate_turbine_efficiency(turbines):
    """Calculate average turbine efficiency"""
    # Simplified calculation - in real implementation, 
    # this would use actual efficiency data
    return 32  # Placeholder efficiency percentage

def calculate_turbine_upgrade_savings(turbines):
    """Calculate CO2 savings from turbine upgrades"""
    return turbines['CO2 Emissions (kg/year)'].sum() * 0.15

def calculate_diesel_replacement_savings(diesel_equipment):
    """Calculate CO2 savings from diesel replacement"""
    return diesel_equipment['CO2 Emissions (kg/year)'].sum() * 0.25