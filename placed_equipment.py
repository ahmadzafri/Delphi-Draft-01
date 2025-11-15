from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
import uuid
from src.models.equipment_model import EquipmentModel

@dataclass 
class PlacedEquipment:
    """Equipment placed on the canvas with position and configuration"""
    equipment: EquipmentModel
    x_position: float  # Position in meters
    y_position: float  # Position in meters
    rotation: float = 0.0  # Rotation angle in degrees
    is_selected: bool = False
    connections: List[str] = None  # List of connected equipment IDs
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = []
    
    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """Get equipment bounding box (min_x, min_y, max_x, max_y)"""
        # Default equipment size (can be customized per equipment type)
        width, height = self.get_equipment_size()
        min_x = self.x_position - width/2
        min_y = self.y_position - height/2
        max_x = self.x_position + width/2
        max_y = self.y_position + height/2
        return (min_x, min_y, max_x, max_y)
    
    def get_equipment_size(self) -> Tuple[float, float]:
        """Get equipment size in meters (width, height)"""
        # Define size based on equipment type
        size_map = {
            "Gas Turbine": (20, 15),
            "Diesel Gen-set": (8, 6),
            "Gas Engine Generator": (12, 8),
            "Boiler": (15, 10),
            "Process Heater": (10, 8),
            "Furnace": (12, 10),
            "Flare Stack": (5, 25),  # Tall structure
            "Thermal Oxidizer": (8, 8),
            "Incinerator": (10, 8),
            "Heater": (6, 4),
            "Chiller": (8, 6),
            "Glycol Reboiler": (6, 8),
            "Gas Engine Compressor": (10, 8),
            "Pump Engine Drive": (8, 6),
            "Storage Tank": (15, 15),  # Circular tank
            "Crude Tank": (20, 20),    # Large circular tank
            "Pipeline": (50, 2),       # Long and narrow
            "Control Building": (12, 8),
            "Fence": (20, 1),         # Long and thin
            "Entrance": (6, 6)
        }
        return size_map.get(self.equipment.name, (8, 6))  # Default size
    
    def can_snap_to(self, other: 'PlacedEquipment', snap_distance: float = 5.0) -> bool:
        """Check if this equipment can snap to another equipment"""
        distance = self.distance_to(other)
        return distance <= snap_distance
    
    def distance_to(self, other: 'PlacedEquipment') -> float:
        """Calculate distance to another equipment"""
        dx = self.x_position - other.x_position
        dy = self.y_position - other.y_position
        return (dx**2 + dy**2)**0.5
    
    def overlaps_with(self, other: 'PlacedEquipment') -> bool:
        """Check if this equipment overlaps with another"""
        self_bounds = self.bounds
        other_bounds = other.bounds
        
        return not (self_bounds[2] < other_bounds[0] or  # self right < other left
                   self_bounds[0] > other_bounds[2] or   # self left > other right
                   self_bounds[3] < other_bounds[1] or   # self bottom < other top
                   self_bounds[1] > other_bounds[3])     # self top > other bottom
    
    def snap_to_position(self, other: 'PlacedEquipment', side: str = "right"):
        """Snap this equipment to another equipment's side"""
        other_bounds = other.bounds
        self_width, self_height = self.get_equipment_size()
        
        if side == "right":
            self.x_position = other_bounds[2] + self_width/2 + 2  # 2m gap
            self.y_position = other.y_position
        elif side == "left":
            self.x_position = other_bounds[0] - self_width/2 - 2
            self.y_position = other.y_position
        elif side == "top":
            self.x_position = other.x_position
            self.y_position = other_bounds[1] - self_height/2 - 2
        elif side == "bottom":
            self.x_position = other.x_position
            self.y_position = other_bounds[3] + self_height/2 + 2
    
    def add_connection(self, equipment_id: str):
        """Add connection to another equipment"""
        if equipment_id not in self.connections:
            self.connections.append(equipment_id)
    
    def remove_connection(self, equipment_id: str):
        """Remove connection to another equipment"""
        if equipment_id in self.connections:
            self.connections.remove(equipment_id)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "equipment": asdict(self.equipment),
            "x_position": self.x_position,
            "y_position": self.y_position,
            "rotation": self.rotation,
            "connections": self.connections
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PlacedEquipment':
        """Create from dictionary for deserialization"""
        equipment_data = data["equipment"]
        equipment = EquipmentModel(**equipment_data)
        
        return cls(
            equipment=equipment,
            x_position=data["x_position"],
            y_position=data["y_position"],
            rotation=data.get("rotation", 0.0),
            connections=data.get("connections", [])
        )

class CanvasManager:
    """Manages the canvas and placed equipment"""
    
    def __init__(self, facility_width_m: float, facility_height_m: float):
        self.facility_width_m = facility_width_m
        self.facility_height_m = facility_height_m
        self.placed_equipment: List[PlacedEquipment] = []
        self.grid_size = 5.0  # 5 meter grid
        self.snap_distance = 10.0  # 10 meter snap distance
    
    def add_equipment(self, equipment: EquipmentModel, x: float, y: float) -> PlacedEquipment:
        """Add equipment to canvas at specified position"""
        # Snap to grid
        snapped_x = round(x / self.grid_size) * self.grid_size
        snapped_y = round(y / self.grid_size) * self.grid_size
        
        # Ensure within bounds
        snapped_x = max(0, min(snapped_x, self.facility_width_m))
        snapped_y = max(0, min(snapped_y, self.facility_height_m))
        
        placed = PlacedEquipment(equipment=equipment, x_position=snapped_x, y_position=snapped_y)
        
        # Check for overlaps and adjust position if needed
        placed = self._resolve_overlaps(placed)
        
        # Check for snap opportunities
        self._auto_snap(placed)
        
        self.placed_equipment.append(placed)
        return placed
    
    def remove_equipment(self, equipment_id: str) -> bool:
        """Remove equipment from canvas"""
        for i, placed in enumerate(self.placed_equipment):
            if placed.equipment.id == equipment_id:
                # Remove connections to this equipment
                for other in self.placed_equipment:
                    other.remove_connection(equipment_id)
                
                self.placed_equipment.pop(i)
                return True
        return False
    
    def move_equipment(self, equipment_id: str, new_x: float, new_y: float) -> bool:
        """Move equipment to new position"""
        for placed in self.placed_equipment:
            if placed.equipment.id == equipment_id:
                # Snap to grid
                placed.x_position = round(new_x / self.grid_size) * self.grid_size
                placed.y_position = round(new_y / self.grid_size) * self.grid_size
                
                # Ensure within bounds
                placed.x_position = max(0, min(placed.x_position, self.facility_width_m))
                placed.y_position = max(0, min(placed.y_position, self.facility_height_m))
                
                # Check for snap opportunities
                self._auto_snap(placed)
                return True
        return False
    
    def select_equipment(self, equipment_id: str):
        """Select equipment (deselect others)"""
        for placed in self.placed_equipment:
            placed.is_selected = (placed.equipment.id == equipment_id)
    
    def get_selected_equipment(self) -> Optional[PlacedEquipment]:
        """Get currently selected equipment"""
        for placed in self.placed_equipment:
            if placed.is_selected:
                return placed
        return None
    
    def _resolve_overlaps(self, new_equipment: PlacedEquipment) -> PlacedEquipment:
        """Resolve overlaps by adjusting position"""
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            overlapping = False
            for existing in self.placed_equipment:
                if new_equipment.overlaps_with(existing):
                    overlapping = True
                    # Move to the right by equipment width
                    width, _ = new_equipment.get_equipment_size()
                    new_equipment.x_position += width + 5  # 5m gap
                    
                    # If moved out of bounds, try moving down
                    if new_equipment.x_position > self.facility_width_m:
                        new_equipment.x_position = width/2
                        new_equipment.y_position += new_equipment.get_equipment_size()[1] + 5
                    
                    break
            
            if not overlapping:
                break
            attempt += 1
        
        return new_equipment
    
    def _auto_snap(self, equipment: PlacedEquipment):
        """Auto-snap equipment to nearby equipment"""
        for other in self.placed_equipment:
            if other.equipment.id != equipment.equipment.id and equipment.can_snap_to(other, self.snap_distance):
                # Determine best snap position
                dx = equipment.x_position - other.x_position
                dy = equipment.y_position - other.y_position
                
                if abs(dx) > abs(dy):
                    side = "right" if dx > 0 else "left"
                else:
                    side = "bottom" if dy > 0 else "top"
                
                equipment.snap_to_position(other, side)
                break
    
    def get_canvas_bounds(self) -> Tuple[float, float]:
        """Get canvas bounds in meters, rounded up to appropriate grid increment for clean axis labels"""
        import math
        
        # Determine appropriate grid increment based on facility size
        max_dimension = max(self.facility_width_m, self.facility_height_m)
        
        if max_dimension <= 100:      # Small facilities - use 5m increment
            grid_increment = 5.0
        elif max_dimension <= 200:    # Medium facilities - use 10m increment  
            grid_increment = 10.0
        elif max_dimension <= 500:    # Large facilities - use 20m increment
            grid_increment = 20.0
        else:                         # Very large facilities - use 50m increment
            grid_increment = 50.0
        
        # Round up to nearest grid increment for clean axis labels
        width_rounded = math.ceil(self.facility_width_m / grid_increment) * grid_increment
        height_rounded = math.ceil(self.facility_height_m / grid_increment) * grid_increment
        
        return (width_rounded, height_rounded)
    
    def calculate_total_co2_emissions(self) -> float:
        """Calculate total CO2 emissions for all equipment"""
        total = 0.0
        for placed in self.placed_equipment:
            total += placed.equipment.calculate_co2_emission()
        return total
    
    def get_equipment_summary(self) -> Dict:
        """Get summary of all equipment and emissions"""
        total_crude_processing_bbl_day = 0.0
        
        for placed in self.placed_equipment:
            total_crude_processing_bbl_day += placed.equipment.calculate_crude_processing_capacity()
        
        # Calculate facilities efficiency using same method as builder page
        total_co2_kg = self.calculate_total_co2_emissions()
        
        # Use 365.25 days per year (same as builder page)
        total_crude_annual = total_crude_processing_bbl_day * 365.25
        total_co2_annual = total_co2_kg * 365.25
        crude_annual_tonnes = total_crude_annual * 0.136  # Convert bbl to tonnes
        co2_annual_tonnes = total_co2_annual / 1000  # Convert kg to tonnes
        
        facilities_efficiency = co2_annual_tonnes / crude_annual_tonnes if crude_annual_tonnes > 0 else 0
        
        summary = {
            "total_equipment": len(self.placed_equipment),
            "total_co2_kg": total_co2_kg,
            "total_crude_processing_bbl_day": total_crude_processing_bbl_day,
            "total_crude_processing_tonnes_year": crude_annual_tonnes,
            "facilities_efficiency": facilities_efficiency,
            "by_category": {},
            "by_fuel_type": {}
        }
        
        for placed in self.placed_equipment:
            equipment = placed.equipment
            category = equipment.category
            fuel_type = equipment.fuel_type
            
            # By category
            if category not in summary["by_category"]:
                summary["by_category"][category] = {"count": 0, "co2_kg": 0.0}
            summary["by_category"][category]["count"] += 1
            summary["by_category"][category]["co2_kg"] += equipment.calculate_co2_emission()
            
            # By fuel type
            if fuel_type not in summary["by_fuel_type"]:
                summary["by_fuel_type"][fuel_type] = {"count": 0, "co2_kg": 0.0}
            summary["by_fuel_type"][fuel_type]["count"] += 1
            summary["by_fuel_type"][fuel_type]["co2_kg"] += equipment.calculate_co2_emission()
        
        return summary
    
    def update_equipment_position(self, placed_equipment: PlacedEquipment, new_x: float, new_y: float):
        """Update equipment position with validation"""
        bounds = self.get_canvas_bounds()
        
        # Validate position bounds
        new_x = max(0, min(new_x, bounds[0]))
        new_y = max(0, min(new_y, bounds[1]))
        
        # Update position
        placed_equipment.x_position = new_x
        placed_equipment.y_position = new_y
        
        # Add to undo stack if not already recording
        if self.placed_equipment and placed_equipment in self.placed_equipment:
            self.add_to_undo_stack()