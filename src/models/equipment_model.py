from dataclasses import dataclass
from typing import Dict, List, Optional
import uuid

# Equipment categories as defined in requirements
EQUIPMENT_CATEGORIES = {
    "Power Generation": ["Gas Turbine", "Diesel Gen-set", "Gas Engine Generator", "Motor Control Centre (MCC)", "SCADA Control System"],
    "Process Heating & Steam": ["Boiler", "Process Heater", "Furnace", "Atmospheric Distillation Column", "Column Reboiler", "Overhead Condenser", "Preheat Train", "Desalter", "Dehydrator"],
    "Flaring & Destructor": ["Flare Stack", "Thermal Oxidizer", "Incinerator", "Flare Knock-out Drum", "Fire Water Pump", "Wastewater Treatment Plant (ETP)"],
    "Utility": ["Heater", "Chiller", "Glycol Reboiler", "Cooling Tower"],
    "Drivers & Machinery": ["Gas Engine Compressor", "Pump Engine Drive", "Motor-driven Compressors"],
    "Non-Combustion": ["Storage Tank", "Crude Tank", "Pipeline", "Control Building", "Fence", "Entrance"],
    "Fluid Handling": ["Feed Pump", "Product Pump", "Cooling Pump"]
}

# Fuel types available
FUEL_TYPES = ["LPG", "Diesel", "Gasoline", "Natural Gas", "None", "Gas", "Electric"]

# CO2 emission factors (kg CO2 per unit) - Based on EPA and industry standards
EMISSION_FACTORS = {
    "Natural Gas": {"factor": 0.0551, "unit": "kg CO2/kWh"},  # 0.0551 kg CO2/kWh thermal (EPA standard)
    "Gas": {"factor": 0.0551, "unit": "kg CO2/kWh"},  # same as natural gas
    "Diesel": {"factor": 2.68, "unit": "kg CO2/liter"},  # 2.68 kg CO2/liter (EPA standard)
    "LPG": {"factor": 1.51, "unit": "kg CO2/liter"},  # 1.51 kg CO2/liter (EPA standard)
    "Gasoline": {"factor": 2.31, "unit": "kg CO2/liter"},  # 2.31 kg CO2/liter (EPA standard)
    "Electric": {"factor": 0.4233, "unit": "kg CO2/kWh"},  # US grid average (EPA eGRID 2021)
    "None": {"factor": 0.0, "unit": "kg CO2/unit"}
}

@dataclass
class EquipmentModel:
    """Base equipment model with CO2 calculation capabilities"""
    id: str
    name: str
    category: str
    power_rate_kw: float = 0.0
    operation_time_hours: float = 0.0
    fuel_type: str = "None"
    fuel_consumption_rate: float = 0.0  # liters/hour or kWh/hour
    description: str = ""
    icon: str = "🏭"
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
    
    @property
    def has_combustion(self) -> bool:
        """Check if equipment has combustion properties"""
        # Non-combustion categories
        if self.category in ["Non-Combustion", "Fluid Handling"]:
            return False
        
        # Equipment with no fuel or electric fuel don't combust
        if self.fuel_type in ["None", "Electric"]:
            return False
            
        return True
    
    @property
    def requires_power_config(self) -> bool:
        """Check if equipment requires power configuration"""
        non_power_equipment = ["Storage Tank", "Crude Tank", "Pipeline", "Control Building", "Fence", "Entrance"]
        return self.name not in non_power_equipment
    
    def calculate_fuel_consumption(self) -> float:
        """Calculate total fuel consumption based on equipment type and engineering principles"""
        if not self.has_combustion or not self.requires_power_config:
            return 0.0
        
        # Equipment-specific fuel consumption calculations based on real engineering data
        daily_operation_hours = min(24, self.operation_time_hours / 365)  # Convert annual to daily
        
        if self.category == "Power Generation":
            if self.name == "Gas Turbine":
                if self.fuel_type in ["Natural Gas", "Gas"]:
                    # Gas turbine: ~10,000-12,000 BTU/kWh = ~10.5-12.6 kWh thermal/kWh electrical
                    heat_rate = 11.0  # kWh thermal input per kWh electrical output
                    thermal_consumption = self.power_rate_kw * heat_rate * daily_operation_hours
                    return thermal_consumption
                else:
                    return 0.0  # Gas turbines typically only use gas
                    
            elif self.name == "Gas Engine Generator":
                if self.fuel_type in ["Natural Gas", "Gas"]:
                    # Gas engine: ~9,000-10,000 BTU/kWh = ~9.5-10.5 kWh thermal/kWh electrical
                    heat_rate = 10.0  # kWh thermal input per kWh electrical output
                    thermal_consumption = self.power_rate_kw * heat_rate * daily_operation_hours
                    return thermal_consumption
                else:
                    return 0.0
                    
            elif self.name == "Diesel Gen-set":
                if self.fuel_type == "Diesel":
                    # Diesel generator: ~0.25-0.3 L/kWh
                    fuel_consumption_rate = 0.28  # L/kWh
                    return self.power_rate_kw * fuel_consumption_rate * daily_operation_hours
                else:
                    return 0.0
                    
        elif self.category == "Process Heating & Steam":
            if self.fuel_type in ["Natural Gas", "Gas"]:
                # Boilers, heaters, furnaces: direct thermal usage
                # Efficiency: 80-90%, so thermal input = thermal output / efficiency
                thermal_efficiency = 0.85  # 85% average efficiency
                thermal_consumption = self.power_rate_kw * (1/thermal_efficiency) * daily_operation_hours
                return thermal_consumption
            elif self.fuel_type == "Diesel":
                # Process heater using diesel
                fuel_consumption_rate = 0.30  # L/kWh thermal
                return self.power_rate_kw * fuel_consumption_rate * daily_operation_hours
                
        elif self.category == "Utility":
            if self.name == "Heater":
                if self.fuel_type in ["Natural Gas", "Gas"]:
                    thermal_efficiency = 0.80  # 80% efficiency for utility heaters
                    thermal_consumption = self.power_rate_kw * (1/thermal_efficiency) * daily_operation_hours
                    return thermal_consumption
                elif self.fuel_type == "Diesel":
                    fuel_consumption_rate = 0.32  # L/kWh thermal
                    return self.power_rate_kw * fuel_consumption_rate * daily_operation_hours
                    
            elif self.name == "Chiller":
                if self.fuel_type == "Electric":
                    # Electric chiller
                    return self.power_rate_kw * daily_operation_hours
                elif self.fuel_type in ["Natural Gas", "Gas"]:
                    # Gas-fired absorption chiller: COP ~1.2, so thermal input = cooling output / COP
                    cop = 1.2  # Coefficient of performance
                    thermal_consumption = self.power_rate_kw * (1/cop) * daily_operation_hours
                    return thermal_consumption
                    
            elif self.name == "Glycol Reboiler":
                if self.fuel_type in ["Natural Gas", "Gas"]:
                    thermal_efficiency = 0.75  # 75% reboiler efficiency
                    thermal_consumption = self.power_rate_kw * (1/thermal_efficiency) * daily_operation_hours
                    return thermal_consumption
                    
        elif self.category == "Drivers & Machinery":
            if self.name == "Gas Engine Compressor":
                if self.fuel_type in ["Natural Gas", "Gas"]:
                    # Gas engine compressor: ~10-11 kWh thermal per kWh shaft power
                    heat_rate = 10.5  # kWh thermal input per kWh shaft power
                    thermal_consumption = self.power_rate_kw * heat_rate * daily_operation_hours
                    return thermal_consumption
                    
            elif self.name == "Pump Engine Drive":
                if self.fuel_type == "Diesel":
                    # Diesel engine drive: ~0.26-0.30 L/kWh shaft power
                    fuel_consumption_rate = 0.28  # L/kWh
                    return self.power_rate_kw * fuel_consumption_rate * daily_operation_hours
                elif self.fuel_type in ["Natural Gas", "Gas"]:
                    # Gas engine drive
                    heat_rate = 10.0  # kWh thermal input per kWh shaft power
                    thermal_consumption = self.power_rate_kw * heat_rate * daily_operation_hours
                    return thermal_consumption
                    
        elif self.category == "Flaring & Destructor":
            if self.name == "Flare Stack":
                if self.fuel_type in ["Natural Gas", "Gas"]:
                    # Flare Stack: power_rate_kw represents thermal capacity (heat rate) of gas being burned
                    # NOT electrical output - flares consume gas to burn waste gases safely
                    
                    # Pilot gas: continuous small flame (~50-100 kW thermal)
                    pilot_gas_thermal = 75  # kW thermal for pilot
                    pilot_consumption = pilot_gas_thermal * 24  # 24 hours/day
                    
                    # Main flare operation: power_rate_kw is thermal capacity
                    # For normal operation, flares operate at fraction of capacity
                    # Emergency/upset conditions may use full capacity intermittently
                    flare_utilization = 0.15  # 15% average utilization of rated capacity
                    main_flare_consumption = self.power_rate_kw * daily_operation_hours * flare_utilization
                    
                    total_thermal_kwh = pilot_consumption + main_flare_consumption
                    
                    # Convert thermal kWh to energy for proper CO₂ calculation
                    # 1 kWh = 3.6 MJ, using natural gas emission factor of 0.0561 kg CO₂/MJ
                    energy_mj = total_thermal_kwh * 3.6  # Convert kWh to MJ
                    return energy_mj  # Return MJ for CO₂ calculation
                    
            elif self.name in ["Thermal Oxidizer", "Incinerator"]:
                if self.fuel_type in ["Natural Gas", "Gas"]:
                    # Thermal oxidizer/incinerator: auxiliary fuel consumption
                    # Typically 20-40% auxiliary fuel, rest from waste heat
                    auxiliary_fuel_fraction = 0.30  # 30% auxiliary fuel
                    thermal_consumption = self.power_rate_kw * auxiliary_fuel_fraction * daily_operation_hours
                    return thermal_consumption
        
        # Default fallback for electric equipment
        if self.fuel_type == "Electric":
            return self.power_rate_kw * daily_operation_hours
            
        return 0.0
    
    def calculate_co2_emission(self) -> float:
        """Calculate CO2 emissions in kg CO2"""
        if not self.has_combustion:
            return 0.0
        
        fuel_consumption = self.calculate_fuel_consumption()
        
        # Special handling for flares - they return MJ, not kWh
        if self.name == "Flare Stack" and self.fuel_type in ["Natural Gas", "Gas"]:
            # fuel_consumption is in MJ, use direct emission factor
            emission_factor_mj = 0.0561  # kg CO₂/MJ for natural gas
            return fuel_consumption * emission_factor_mj
        
        # Standard calculation for other equipment (kWh or liters)
        if self.fuel_type in EMISSION_FACTORS:
            emission_factor = EMISSION_FACTORS[self.fuel_type]["factor"]
            return fuel_consumption * emission_factor
        
        return 0.0
    
    def calculate_power_production(self) -> float:
        """Calculate electrical power production capacity in kW based on engineering principles"""
        if not self.requires_power_config:
            return 0.0
        
        if self.category == "Power Generation":
            # Primary electrical power generation equipment
            # Note: power_rate_kw for generators typically represents their electrical output rating
            if self.name == "Gas Turbine":
                # Industrial gas turbine - show net electrical capacity
                # Apply minimal derating for real-world conditions
                capacity_factor = 0.95  # 95% of nameplate (maintenance, minor derating)
                net_capacity = self.power_rate_kw * capacity_factor
                return net_capacity
                
            elif self.name == "Gas Engine Generator":
                # Reciprocating gas engine generator - very reliable
                capacity_factor = 0.92  # 92% of nameplate (slightly lower due to maintenance)
                net_capacity = self.power_rate_kw * capacity_factor
                return net_capacity
                
            elif self.name == "Diesel Gen-set":
                # Diesel generator set - backup/standby power
                # For standby generators, show available capacity when needed
                capacity_factor = 0.90  # 90% of nameplate (backup equipment derating)
                net_capacity = self.power_rate_kw * capacity_factor
                return net_capacity
                
        elif self.category == "Flaring & Destructor":
            # Heat recovery and waste-to-energy systems
            if self.name == "Thermal Oxidizer":
                # Heat recovery from thermal oxidizer exhaust
                heat_recovery_efficiency = 0.25  # 25% heat-to-power conversion
                availability_factor = 0.92  # High availability for continuous process
                net_capacity = self.power_rate_kw * heat_recovery_efficiency * availability_factor
                return net_capacity
                
            elif self.name == "Incinerator":
                # Waste-to-energy from incinerator
                waste_to_energy_efficiency = 0.18  # 18% waste heat to electricity
                availability_factor = 0.85  # Lower availability due to waste variability
                net_capacity = self.power_rate_kw * waste_to_energy_efficiency * availability_factor
                return net_capacity
                
            elif self.name == "Flare Stack":
                # Modern flares with heat recovery systems
                heat_recovery_efficiency = 0.12  # 12% heat recovery to power
                utilization_factor = 0.30  # 30% utilization (emergency operation)
                net_capacity = self.power_rate_kw * heat_recovery_efficiency * utilization_factor
                return net_capacity
                
        # REMOVED: Process Heating & Steam equipment (boilers, heaters, furnaces)
        # These generate heat/steam for processing, NOT electrical power
        # Only dedicated power generation equipment should contribute to electrical output
        
        # Other equipment categories consume power but don't generate electricity
        # (Process heating, utilities, machinery, etc. are all power consumers)
        return 0.0
    
    def calculate_crude_processing_capacity(self) -> float:
        """Calculate crude oil processing capacity in bbl/day based on rigorous engineering principles"""
        if not self.requires_power_config:
            return 0.0
        
        # Thermodynamic constants for crude oil processing
        CRUDE_DENSITY_KG_PER_BBL = 136  # kg per barrel (API 30° crude oil)
        CRUDE_SPECIFIC_HEAT = 2.0  # kJ/kg·K (crude oil specific heat capacity)
        DELTA_T_HEATING = 290  # K (60°C to 350°C typical refinery heating)
        MJ_PER_KWH = 3.6  # Conversion factor
        
        # Energy required per barrel for sensible heating
        energy_per_barrel_mj = (CRUDE_DENSITY_KG_PER_BBL * CRUDE_SPECIFIC_HEAT * DELTA_T_HEATING) / 1000
        # = 136 * 2.0 * 290 / 1000 = 78.88 MJ per barrel
        
        # Daily operation hours (convert annual hours to daily average)
        daily_operation_hours = min(24, self.operation_time_hours / 365)  # Convert annual to daily, max 24h
        
        if self.category == "Process Heating & Steam":
            if self.name == "Process Heater":
                # Direct fired heater - following your calculation pattern
                thermal_efficiency = 0.85  # 85% thermal efficiency
                energy_per_day_mj = self.power_rate_kw * daily_operation_hours * MJ_PER_KWH * thermal_efficiency
                return energy_per_day_mj / energy_per_barrel_mj
                
            elif self.name == "Furnace":
                # Process furnace - high-temperature operations
                thermal_efficiency = 0.80  # 80% efficiency for furnaces
                energy_per_day_mj = self.power_rate_kw * daily_operation_hours * MJ_PER_KWH * thermal_efficiency
                return energy_per_day_mj / energy_per_barrel_mj
                
            elif self.name == "Boiler":
                # Steam boiler - following your exact calculation method
                # energy_per_day = power_kw * hours_per_day * 3.6 * efficiency
                boiler_efficiency = 0.85  # Standard boiler efficiency
                energy_per_day_mj = self.power_rate_kw * daily_operation_hours * MJ_PER_KWH * boiler_efficiency
                raw_throughput = energy_per_day_mj / energy_per_barrel_mj
                return raw_throughput
                
        elif self.category == "Utility":
            if self.name == "Heater":
                # Utility heater - supplementary heating using same thermodynamic approach
                thermal_efficiency = 0.80  # 80% efficiency for utility heaters
                energy_per_day_mj = self.power_rate_kw * daily_operation_hours * MJ_PER_KWH * thermal_efficiency
                return energy_per_day_mj / energy_per_barrel_mj
                
            elif self.name == "Chiller":
                # Chillers enable crude processing by cooling product streams
                # Using thermodynamic approach - cooling capacity supports crude throughput
                # 1 kW cooling = ~0.3 kW equivalent thermal processing capacity
                cooling_thermal_equivalent = 0.30  # 30% thermal equivalent
                energy_per_day_mj = self.power_rate_kw * cooling_thermal_equivalent * daily_operation_hours * MJ_PER_KWH
                return energy_per_day_mj / energy_per_barrel_mj
                
            elif self.name == "Glycol Reboiler":
                # Glycol reboiler for gas dehydration - uses thermal energy approach
                thermal_efficiency = 0.75  # 75% reboiler efficiency
                energy_per_day_mj = self.power_rate_kw * daily_operation_hours * MJ_PER_KWH * thermal_efficiency
                return energy_per_day_mj / energy_per_barrel_mj
                
        elif self.category == "Drivers & Machinery":
            if self.name == "Pump Engine Drive":
                # Pump drives ENABLE crude processing by providing pumping capacity
                # Pumps don't create crude but are essential for moving it through process
                # Conservative approach: 1 kW pumping = 0.5 kW equivalent thermal processing
                pumping_thermal_equivalent = 0.50  # 50% thermal equivalent for essential pumping
                energy_per_day_mj = self.power_rate_kw * pumping_thermal_equivalent * daily_operation_hours * MJ_PER_KWH
                return energy_per_day_mj / energy_per_barrel_mj
                
            elif self.name == "Gas Engine Compressor":
                # Gas compression enables crude processing by handling associated gas
                # Without gas compression, crude processing would be severely limited
                # Conservative approach: 1 kW compression = 0.4 kW equivalent thermal processing
                compression_thermal_equivalent = 0.40  # 40% thermal equivalent
                energy_per_day_mj = self.power_rate_kw * compression_thermal_equivalent * daily_operation_hours * MJ_PER_KWH
                return energy_per_day_mj / energy_per_barrel_mj
                
        elif self.category == "Flaring & Destructor":
            if self.name == "Flare Stack":
                # Flare stacks enable safe crude processing by providing emergency relief
                # Essential safety equipment - without flares, processing rates must be severely limited
                # Conservative approach: flare capacity enables processing but with low thermal equivalent
                safety_thermal_equivalent = 0.10  # 10% thermal equivalent for essential safety
                energy_per_day_mj = self.power_rate_kw * safety_thermal_equivalent * daily_operation_hours * MJ_PER_KWH
                return energy_per_day_mj / energy_per_barrel_mj
                
            elif self.name == "Thermal Oxidizer":
                # VOC thermal oxidizers enable environmental compliance for higher throughput
                # Required for regulatory compliance - enables continuous operation
                environmental_thermal_equivalent = 0.15  # 15% thermal equivalent for compliance
                energy_per_day_mj = self.power_rate_kw * environmental_thermal_equivalent * daily_operation_hours * MJ_PER_KWH
                return energy_per_day_mj / energy_per_barrel_mj
                
            elif self.name == "Incinerator":
                # Waste incinerators enable continuous operation by destroying waste streams
                # Essential for continuous processing operations
                waste_thermal_equivalent = 0.12  # 12% thermal equivalent for waste handling
                energy_per_day_mj = self.power_rate_kw * waste_thermal_equivalent * daily_operation_hours * MJ_PER_KWH
                return energy_per_day_mj / energy_per_barrel_mj
                
        # REMOVED: Power Generation equipment from crude processing
        # Power generation equipment (turbines, generators, gen-sets) ONLY generate electricity
        # They do NOT directly process crude oil or contribute to bbl/day throughput
        # Their role is to provide electrical power to support facility operations
        
        # Non-combustion equipment (storage, pipeline, etc.) doesn't directly contribute
        # to processing capacity but could be modeled for logistics in future
        return 0.0
    
    def get_equipment_info(self) -> Dict:
        """Get comprehensive equipment information"""
        co2_emission = self.calculate_co2_emission()
        fuel_consumption = self.calculate_fuel_consumption()
        
        info = {
            "basic_info": {
                "name": self.name,
                "category": self.category,
                "description": self.description,
                "has_combustion": self.has_combustion
            },
            "operational_data": {},
            "environmental_impact": {
                "co2_emission_kg": round(co2_emission, 2),
                "emission_factor": EMISSION_FACTORS.get(self.fuel_type, {"factor": 0, "unit": "N/A"})
            }
        }
        
        if self.requires_power_config:
            info["operational_data"] = {
                "power_rate_kw": self.power_rate_kw,
                "operation_time_hours": self.operation_time_hours,
                "fuel_type": self.fuel_type,
                "fuel_consumption": round(fuel_consumption, 2),
                "fuel_unit": "liters" if self.fuel_type in ["Diesel", "LPG", "Gasoline"] else "kWh"
            }
        
        return info
    
    def to_dict(self) -> Dict:
        """Convert equipment model to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "power_rate_kw": self.power_rate_kw,
            "operation_time_hours": self.operation_time_hours,
            "fuel_type": self.fuel_type,
            "fuel_consumption_rate": self.fuel_consumption_rate,
            "description": self.description,
            "icon": self.icon
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EquipmentModel':
        """Create equipment model from dictionary"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            category=data.get("category", ""),
            power_rate_kw=data.get("power_rate_kw", 0.0),
            operation_time_hours=data.get("operation_time_hours", 0.0),
            fuel_type=data.get("fuel_type", "None"),
            fuel_consumption_rate=data.get("fuel_consumption_rate", 0.0),
            description=data.get("description", ""),
            icon=data.get("icon", "⚡")
        )

def create_equipment_defaults() -> Dict[str, EquipmentModel]:
    """Create default equipment configurations for each type"""
    defaults = {}
    
    # Power Generation equipment
    defaults["Gas Turbine"] = EquipmentModel(
        id="", name="Gas Turbine", category="Power Generation",
        power_rate_kw=5000, operation_time_hours=8760, fuel_type="Natural Gas",
        description="High-efficiency gas turbine for power generation",
        icon="⚡"
    )
    
    defaults["Diesel Gen-set"] = EquipmentModel(
        id="", name="Diesel Gen-set", category="Power Generation",
        power_rate_kw=1000, operation_time_hours=2000, fuel_type="Diesel",
        description="Backup diesel generator set",
        icon="⚡"
    )
    
    defaults["Gas Engine Generator"] = EquipmentModel(
        id="", name="Gas Engine Generator", category="Power Generation",
        power_rate_kw=2000, operation_time_hours=6000, fuel_type="Natural Gas",
        description="Gas-powered engine generator",
        icon="⚡"
    )
    
    defaults["Motor Control Centre (MCC)"] = EquipmentModel(
        id="", name="Motor Control Centre (MCC)", category="Power Generation",
        power_rate_kw=100, operation_time_hours=8760, fuel_type="Electric",
        description="Motor control center for electrical distribution",
        icon="⚡"
    )
    
    defaults["SCADA Control System"] = EquipmentModel(
        id="", name="SCADA Control System", category="Power Generation",
        power_rate_kw=50, operation_time_hours=8760, fuel_type="Electric",
        description="Supervisory control and data acquisition system",
        icon="⚡"
    )
    
    # Process Heating & Steam
    defaults["Boiler"] = EquipmentModel(
        id="", name="Boiler", category="Process Heating & Steam",
        power_rate_kw=3000, operation_time_hours=6000, fuel_type="Natural Gas",
        description="Steam generation boiler",
        icon="▲"
    )
    
    defaults["Process Heater"] = EquipmentModel(
        id="", name="Process Heater", category="Process Heating & Steam",
        power_rate_kw=1500, operation_time_hours=7000, fuel_type="Natural Gas",
        description="Process heating equipment",
        icon="▲"
    )
    
    defaults["Furnace"] = EquipmentModel(
        id="", name="Furnace", category="Process Heating & Steam",
        power_rate_kw=2500, operation_time_hours=5000, fuel_type="Natural Gas",
        description="Industrial furnace",
        icon="▲"
    )
    
    defaults["Atmospheric Distillation Column"] = EquipmentModel(
        id="", name="Atmospheric Distillation Column", category="Process Heating & Steam",
        power_rate_kw=3500, operation_time_hours=8500, fuel_type="Natural Gas",
        description="Atmospheric distillation column for crude oil refining",
        icon="▲"
    )
    
    defaults["Column Reboiler"] = EquipmentModel(
        id="", name="Column Reboiler", category="Process Heating & Steam",
        power_rate_kw=1800, operation_time_hours=8000, fuel_type="Natural Gas",
        description="Distillation column reboiler",
        icon="▲"
    )
    
    defaults["Overhead Condenser"] = EquipmentModel(
        id="", name="Overhead Condenser", category="Process Heating & Steam",
        power_rate_kw=400, operation_time_hours=8000, fuel_type="Electric",
        description="Column overhead condenser system",
        icon="▲"
    )
    
    defaults["Preheat Train"] = EquipmentModel(
        id="", name="Preheat Train", category="Process Heating & Steam",
        power_rate_kw=2200, operation_time_hours=8500, fuel_type="Natural Gas",
        description="Crude oil preheat train system",
        icon="▲"
    )
    
    defaults["Desalter"] = EquipmentModel(
        id="", name="Desalter", category="Process Heating & Steam",
        power_rate_kw=800, operation_time_hours=8000, fuel_type="Electric",
        description="Crude oil desalting unit",
        icon="▲"
    )
    
    defaults["Dehydrator"] = EquipmentModel(
        id="", name="Dehydrator", category="Process Heating & Steam",
        power_rate_kw=600, operation_time_hours=7500, fuel_type="Natural Gas",
        description="Gas dehydration unit",
        icon="▲"
    )
    
    # Flaring & Destructor
    defaults["Flare Stack"] = EquipmentModel(
        id="", name="Flare Stack", category="Flaring & Destructor",
        power_rate_kw=500, operation_time_hours=1000, fuel_type="Gas",
        description="Emergency flare stack for gas burning",
        icon="▲"
    )
    
    defaults["Thermal Oxidizer"] = EquipmentModel(
        id="", name="Thermal Oxidizer", category="Flaring & Destructor",
        power_rate_kw=800, operation_time_hours=8000, fuel_type="Natural Gas",
        description="Thermal oxidizer for waste gas treatment",
        icon="◆"
    )
    
    defaults["Incinerator"] = EquipmentModel(
        id="", name="Incinerator", category="Flaring & Destructor",
        power_rate_kw=1200, operation_time_hours=4000, fuel_type="Diesel",
        description="Waste incinerator",
        icon="▲"
    )
    
    defaults["Flare Knock-out Drum"] = EquipmentModel(
        id="", name="Flare Knock-out Drum", category="Flaring & Destructor",
        power_rate_kw=0, operation_time_hours=0, fuel_type="None",
        description="Flare system knock-out drum for liquid separation",
        icon="◆"
    )
    
    defaults["Fire Water Pump"] = EquipmentModel(
        id="", name="Fire Water Pump", category="Flaring & Destructor",
        power_rate_kw=750, operation_time_hours=200, fuel_type="Diesel",
        description="Emergency fire water pump system",
        icon="◆"
    )
    
    defaults["Wastewater Treatment Plant (ETP)"] = EquipmentModel(
        id="", name="Wastewater Treatment Plant (ETP)", category="Flaring & Destructor",
        power_rate_kw=2000, operation_time_hours=8500, fuel_type="Electric",
        description="Effluent treatment plant for wastewater processing",
        icon="◆"
    )
    
    # Utility
    defaults["Heater"] = EquipmentModel(
        id="", name="Heater", category="Utility",
        power_rate_kw=300, operation_time_hours=4000, fuel_type="Electric",
        description="Utility heater",
        icon="◆"
    )
    
    defaults["Chiller"] = EquipmentModel(
        id="", name="Chiller", category="Utility",
        power_rate_kw=500, operation_time_hours=6000, fuel_type="Electric",
        description="Cooling system chiller",
        icon="◇"
    )
    
    defaults["Glycol Reboiler"] = EquipmentModel(
        id="", name="Glycol Reboiler", category="Utility",
        power_rate_kw=200, operation_time_hours=8000, fuel_type="Natural Gas",
        description="Glycol regeneration reboiler",
        icon="◆"
    )
    
    defaults["Cooling Tower"] = EquipmentModel(
        id="", name="Cooling Tower", category="Utility",
        power_rate_kw=300, operation_time_hours=7000, fuel_type="Electric",
        description="Cooling tower for heat rejection",
        icon="◇"
    )
    
    # Drivers & Machinery
    defaults["Gas Engine Compressor"] = EquipmentModel(
        id="", name="Gas Engine Compressor", category="Drivers & Machinery",
        power_rate_kw=1500, operation_time_hours=8000, fuel_type="Natural Gas",
        description="Gas-driven compressor",
        icon="●"
    )
    
    defaults["Pump Engine Drive"] = EquipmentModel(
        id="", name="Pump Engine Drive", category="Drivers & Machinery",
        power_rate_kw=750, operation_time_hours=6000, fuel_type="Diesel",
        description="Engine-driven pump system",
        icon="●"
    )
    
    defaults["Motor-driven Compressors"] = EquipmentModel(
        id="", name="Motor-driven Compressors", category="Drivers & Machinery",
        power_rate_kw=1200, operation_time_hours=8000, fuel_type="Electric",
        description="Electric motor-driven compressor system",
        icon="●"
    )
    
    # Non-Combustion
    defaults["Storage Tank"] = EquipmentModel(
        id="", name="Storage Tank", category="Non-Combustion",
        description="Product storage tank",
        icon="▣"
    )
    
    defaults["Crude Tank"] = EquipmentModel(
        id="", name="Crude Tank", category="Non-Combustion",
        description="Crude oil storage tank",
        icon="▣"
    )
    
    defaults["Pipeline"] = EquipmentModel(
        id="", name="Pipeline", category="Non-Combustion",
        description="Transport pipeline",
        icon="━"
    )
    
    defaults["Control Building"] = EquipmentModel(
        id="", name="Control Building", category="Non-Combustion",
        description="Control room building",
        icon="▢"
    )
    
    defaults["Fence"] = EquipmentModel(
        id="", name="Fence", category="Non-Combustion",
        description="Perimeter fence",
        icon="┃"
    )
    
    defaults["Entrance"] = EquipmentModel(
        id="", name="Entrance", category="Non-Combustion",
        description="Facility entrance",
        icon="▣"
    )
    
    # Fluid Handling
    defaults["Feed Pump"] = EquipmentModel(
        id="", name="Feed Pump", category="Fluid Handling",
        power_rate_kw=500, operation_time_hours=7500, fuel_type="Electric",
        fuel_consumption_rate=500.0, description="Process feed pump system",
        icon="●"
    )
    
    defaults["Product Pump"] = EquipmentModel(
        id="", name="Product Pump", category="Fluid Handling",
        power_rate_kw=400, operation_time_hours=6500, fuel_type="Electric",
        fuel_consumption_rate=400.0, description="Product transfer pump",
        icon="●"
    )
    
    defaults["Cooling Pump"] = EquipmentModel(
        id="", name="Cooling Pump", category="Fluid Handling",
        power_rate_kw=300, operation_time_hours=8000, fuel_type="Electric",
        fuel_consumption_rate=300.0, description="Cooling water circulation pump",
        icon="●"
    )
    
    return defaults