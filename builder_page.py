import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from src.models.equipment_model import EQUIPMENT_CATEGORIES, create_equipment_defaults, EquipmentModel
from src.models.placed_equipment import PlacedEquipment, CanvasManager
from src.models.draggable_canvas import DraggableCanvasManager, create_enhanced_canvas_interface, display_selected_equipment_info

def builder_page():
    """Professional facility builder with organized UI hierarchy"""
    
    # Professional enterprise-grade styling
    st.markdown("""
    <style>
        .enterprise-container {
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            color: #2c3e50;
            position: relative;
        }
        .enterprise-background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(45deg, 
                    rgba(26, 54, 93, 0.02) 0%, 
                    rgba(79, 209, 199, 0.01) 50%,
                    rgba(26, 54, 93, 0.02) 100%
                ),
                radial-gradient(circle at 20% 80%, rgba(79, 209, 199, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(26, 54, 93, 0.05) 0%, transparent 50%),
                url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><defs><pattern id="factory" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse"><rect width="40" height="40" fill="none"/><rect x="5" y="25" width="8" height="12" fill="%234fd1c7" opacity="0.03"/><rect x="15" y="20" width="6" height="17" fill="%231a365d" opacity="0.02"/><rect x="25" y="22" width="10" height="15" fill="%234fd1c7" opacity="0.02"/><circle cx="10" cy="10" r="1" fill="%234fd1c7" opacity="0.04"/><circle cx="30" cy="15" r="1.5" fill="%231a365d" opacity="0.03"/></pattern></defs><rect width="100%" height="100%" fill="url(%23factory)"/></svg>');
            background-size: auto, 400px 400px, 300px 300px, 80px 80px;
            background-position: center, top left, bottom right, center;
            background-repeat: repeat, no-repeat, no-repeat, repeat;
            z-index: -1;
            pointer-events: none;
        }
        .enterprise-header {
            background: linear-gradient(135deg, rgba(26, 54, 93, 0.95) 0%, rgba(45, 55, 72, 0.95) 50%, rgba(26, 32, 44, 0.95) 100%);
            padding: 2rem 2rem 1.5rem 2rem;
            margin: -1rem -1rem 2rem -1rem;
            text-align: center;
            color: white;
            border-radius: 0;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        .enterprise-header h1 {
            font-size: 2.2rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
            letter-spacing: -1px;
            position: relative;
            z-index: 1;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .enterprise-header .brand-name {
            color: #4fd1c7;
            font-weight: 800;
        }
        .enterprise-header .subtitle {
            font-size: 1rem;
            opacity: 0.9;
            margin: 0.5rem auto;
            font-weight: 400;
            max-width: 600px;
            line-height: 1.4;
            position: relative;
            z-index: 1;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        .section-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            transition: box-shadow 0.3s ease;
            backdrop-filter: blur(10px);
            position: relative;
        }
        .section-container:hover {
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        }
        .section-title {
            color: #1a365d;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            border-bottom: 2px solid #4fd1c7;
            padding-bottom: 0.5rem;
            position: relative;
        }
        .section-title::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 40px;
            height: 2px;
            background: #1a365d;
        }
        .control-panel {
            background: linear-gradient(145deg, rgba(247, 250, 252, 0.95) 0%, rgba(237, 242, 247, 0.95) 100%);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #e2e8f0;
            backdrop-filter: blur(5px);
        }
        .equipment-category {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 6px;
            padding: 1rem;
            margin: 0.8rem 0;
            border: 1px solid #e2e8f0;
            backdrop-filter: blur(5px);
        }
        .equipment-category h4 {
            color: #1a365d;
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 0.5rem;
        }
        .equipment-item {
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(247, 250, 252, 0.95) 100%);
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            padding: 0.8rem;
            margin: 0.4rem 0;
            transition: all 0.2s ease;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .equipment-item:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-color: #4fd1c7;
            background: rgba(79, 209, 199, 0.05);
        }
        .equipment-name {
            font-weight: 500;
            color: #1a365d;
            font-size: 0.9rem;
        }
        .equipment-specs {
            font-size: 0.75rem;
            color: #718096;
            margin-top: 0.2rem;
        }
        .canvas-section {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            backdrop-filter: blur(10px);
        }
        .facility-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 0.8rem;
            margin: 1rem 0;
        }
        .stat-card {
            background: rgba(255,255,255,0.9);
            padding: 0.8rem;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            text-align: center;
            backdrop-filter: blur(5px);
        }
        .stat-number {
            font-size: 1.2rem;
            font-weight: 700;
            color: #1a365d;
            margin-bottom: 0.2rem;
        }
        .stat-label {
            font-size: 0.7rem;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .project-header {
            background: linear-gradient(135deg, rgba(26, 54, 93, 0.08) 0%, rgba(79, 209, 199, 0.08) 100%);
            border-radius: 8px;
            padding: 1.2rem;
            margin: 1rem 0;
            border: 1px solid rgba(79, 209, 199, 0.2);
            text-align: center;
        }
        .project-name {
            color: #1a365d;
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .project-details {
            color: #718096;
            font-size: 0.9rem;
        }
        .action-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 0.8rem;
            margin: 1rem 0;
        }
    </style>
    
    <div class="enterprise-background"></div>
    <div class="enterprise-container">
        <div class="enterprise-header">
            <h1><span class="brand-name">Delphi</span>: <span style="color: #81e6d9;">CO₂</span> Builder</h1>
            <div class="subtitle">
                Professional Facility Equipment Configuration & Layout Design
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if project is loaded
    if not st.session_state.current_project:
        st.markdown("""
        <div class="section-container">
            <h4 style="color: #dc3545; margin: 0;">No Project Loaded</h4>
            <p style="margin: 0.5rem 0 0 0;">Please return to the main page and select a project to access the builder.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Return to Main Page", type="primary"):
            st.session_state.current_page = 'main'
            st.rerun()
        return
    
    # Initialize builder session
    initialize_builder_session()
    
    # PROJECT HEADER SECTION
    project = st.session_state.current_project
    st.markdown(f"""
    <div class="project-header">
        <div class="project-name">{project['name']}</div>
        <div class="project-details">
            Facility Size: {project['facility_size_acres']} acres ({project['facility_size_meters']:,.0f} m²)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # NAVIGATION SECTION
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
    
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    with nav_col1:
        if st.button("Home", help="Return to main page", use_container_width=True):
            if not st.session_state.get('project_saved', True):
                st.warning("You have unsaved changes!")
            else:
                st.session_state.current_page = 'main'
                st.rerun()
    
    with nav_col2:
        if st.button("Production Targets", help="Configure production capacity and targets", use_container_width=True):
            st.session_state.show_production_popup = True
            st.rerun()
    
    with nav_col3:
        if st.button("Save Project", help="Save current project", use_container_width=True, type="primary"):
            if save_current_project():
                st.success("Project saved successfully!")
            else:
                st.error("Failed to save project")
    
    with nav_col4:
        if st.button("View Report", help="Generate CO₂ analysis report", use_container_width=True):
            st.session_state.current_page = 'reporting'
            st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # MAIN WORKSPACE - Two Column Layout
    equipment_col, canvas_col = st.columns([1, 2.5], gap="medium")
    
    # LEFT COLUMN: EQUIPMENT LIBRARY
    with equipment_col:
        render_equipment_library()
    
    # RIGHT COLUMN: FACILITY STATISTICS, CANVAS & EQUIPMENT CONFIGURATION
    with canvas_col:
        render_facility_statistics()
        render_facility_canvas()
        if st.session_state.get('show_config_panel', False):
            render_equipment_configuration_panel()
    
    # Handle conditional popups/dialogs only when triggered
    handle_popup_dialogs()

def handle_popup_dialogs():
    """Handle all popup dialogs in a centralized location to prevent unwanted triggers"""
    
    # Production target popup - only show when explicitly requested
    if st.session_state.get('show_production_popup', False):
        production_config_dialog()
        # Note: Flag is reset inside the dialog's button handlers, not here
    
    # Position picker popup - only show when equipment is being placed
    render_position_picker()

@st.dialog("Refinery Production Target Configuration")
def production_config_dialog():
    """Modal dialog for production target configuration"""
    
    # Get current project and existing configuration
    current_project = st.session_state.get('current_project', {})
    existing_config = current_project.get('production_config', {})
    is_configured = bool(existing_config)
    
    if is_configured:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(79, 209, 199, 0.95) 0%, rgba(26, 54, 93, 0.95) 100%); 
                    color: white; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1.5rem;">
            <h4 style="margin: 0; color: white;">Current Production Configuration</h4>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">Review your configured production targets (Read-Only)</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(26, 54, 93, 0.95) 0%, rgba(45, 55, 72, 0.95) 100%); 
                    color: white; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1.5rem;">
            <h4 style="margin: 0; color: white;">Configure Production Capacity & Targets</h4>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">Define crude oil processing and power generation capacity for accurate CO₂ intensity analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Operating Hours Configuration
    st.markdown("### Operating Hours")
    
    operating_hours = st.number_input(
        "Operating Hours per Day",
        min_value=8,
        max_value=24,
        value=existing_config.get('operating_hours_day', 20),
        step=1,
        help="Number of operational hours per day for the facility",
        disabled=is_configured
    )
    
    st.markdown("---")
    
    # Crude Oil Processing Configuration
    st.markdown("### Crude Oil Processing")
    
    crude_throughput_bbl = st.number_input(
        "Crude Oil Throughput (bbl/day)",
        min_value=1000,
        max_value=1000000,
        value=existing_config.get('crude_throughput_bbl_day', 50000),
        step=1000,
        help="Daily crude oil processing capacity in barrels per day",
        disabled=is_configured
    )
    
    st.markdown("---")
    
    # Power Generation Configuration
    st.markdown("### Integrated Power Generation")
    col3, col4 = st.columns(2)
    
    with col3:
        power_capacity_kw = st.number_input(
            "Total Power Capacity (kW)",
            min_value=1000,
            max_value=500000,
            value=existing_config.get('power_capacity_kw', 25000),
            step=1000,
            help="Total electrical generation capacity from gas turbines and generators",
            disabled=is_configured
        )
        
    with col4:
        load_factor = st.slider(
            "Load Factor (%)",
            min_value=40,
            max_value=95,
            value=existing_config.get('load_factor_pct', 75),
            step=1,
            help="Average power capacity utilization",
            disabled=is_configured
        )
    
    # Action buttons
    if is_configured:
        # Show only Close button for read-only view
        col_spacer, col_close, col_spacer2 = st.columns([1, 1, 1])
        with col_close:
            if st.button("Close", use_container_width=True, type="primary"):
                st.session_state.show_production_popup = False
                st.rerun()
    else:
        # Show Cancel and Save buttons for initial configuration
        col_cancel, col_save = st.columns([1, 1])
        
        with col_cancel:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_production_popup = False
                st.rerun()
        
        with col_save:
            if st.button("Save Configuration", use_container_width=True, type="primary"):
                # Save production configuration to project
                production_config = {
                    "facility_type": "Oil & Gas Refinery",
                    "crude_throughput_bbl_day": crude_throughput_bbl,
                    "power_capacity_kw": power_capacity_kw,
                    "load_factor_pct": load_factor,
                    "operating_hours_day": operating_hours
                }
                
                # Update project with production configuration
                st.session_state.current_project["production_config"] = production_config
                st.session_state.current_project["production_configured"] = True
                
                # Update saved project file
                project_name = st.session_state.current_project["name"]
                try:
                    filename = f"projects/{project_name.replace(' ', '_').lower()}.json"
                    if os.path.exists(filename):
                        with open(filename, 'r') as f:
                            project_data = json.load(f)
                        project_data["production_config"] = production_config
                        project_data["last_modified"] = datetime.now().isoformat()
                        with open(filename, 'w') as f:
                            json.dump(project_data, f, indent=2)
                except Exception as e:
                    st.error(f"Error saving production configuration: {e}")
                    return
                
                st.session_state.show_production_popup = False
                st.success("Production targets configured successfully!")
                st.rerun()
    
def initialize_builder_session():
    
    # Force recreation of canvas managers to apply grid fixes (version 2.0)
    if st.session_state.get('canvas_manager_version', 1.0) < 2.0:
        if 'canvas_manager' in st.session_state:
            del st.session_state.canvas_manager
        if 'enhanced_canvas_manager' in st.session_state:
            del st.session_state.enhanced_canvas_manager
        st.session_state.canvas_manager_version = 2.0
    
    # Check if we need to reset canvas managers for a different project
    current_project_id = st.session_state.current_project.get('name', '') if st.session_state.current_project else ''
    last_loaded_project = st.session_state.get('last_loaded_project_id', '')
    
    if current_project_id != last_loaded_project:
        # Different project loaded, reset canvas managers
        if 'canvas_manager' in st.session_state:
            del st.session_state.canvas_manager
        if 'enhanced_canvas_manager' in st.session_state:
            del st.session_state.enhanced_canvas_manager
        # Update the last loaded project ID
        st.session_state.last_loaded_project_id = current_project_id
    
    if 'enhanced_canvas_manager' not in st.session_state:
        if st.session_state.current_project:
            # Get exact dimensions from project
            width = st.session_state.current_project.get('canvas_width_m', 200)
            height = st.session_state.current_project.get('canvas_height_m', 200)
            
            # Create temporary canvas manager to get rounded bounds
            temp_manager = DraggableCanvasManager(width, height)
            rounded_bounds = temp_manager.get_canvas_bounds()
            
            # Initialize with rounded bounds for clean grid
            st.session_state.enhanced_canvas_manager = DraggableCanvasManager(rounded_bounds[0], rounded_bounds[1])
        else:
            st.session_state.enhanced_canvas_manager = DraggableCanvasManager(200, 200)
    
    # Keep the legacy canvas manager for compatibility
    if 'canvas_manager' not in st.session_state:
        if st.session_state.current_project:
            # Get exact dimensions from project
            width = st.session_state.current_project.get('canvas_width_m', 200)
            height = st.session_state.current_project.get('canvas_height_m', 200)
            
            # Create temporary canvas manager to get rounded bounds
            temp_manager = CanvasManager(width, height)
            rounded_bounds = temp_manager.get_canvas_bounds()
            
            # Initialize with rounded bounds for clean grid
            st.session_state.canvas_manager = CanvasManager(rounded_bounds[0], rounded_bounds[1])
            
            # Load existing equipment from project
            project_equipment = st.session_state.current_project.get('equipment', [])
            if project_equipment:
                from src.models.placed_equipment import PlacedEquipment
                for eq_data in project_equipment:
                    # Recreate equipment from saved data
                    equipment = EquipmentModel.from_dict(eq_data['equipment'])
                    placed_eq = PlacedEquipment(
                        equipment=equipment,
                        x_position=eq_data['x_position'],
                        y_position=eq_data['y_position']
                    )
                    st.session_state.canvas_manager.placed_equipment.append(placed_eq)
        else:
            st.session_state.canvas_manager = CanvasManager(200, 200)
    
    if 'equipment_library_open' not in st.session_state:
        st.session_state.equipment_library_open = False
    
    if 'selected_equipment_for_config' not in st.session_state:
        st.session_state.selected_equipment_for_config = None
    if 'show_position_picker' not in st.session_state:
        st.session_state.show_position_picker = False
    if 'equipment_to_place' not in st.session_state:
        st.session_state.equipment_to_place = None
    
    if 'show_config_panel' not in st.session_state:
        st.session_state.show_config_panel = False
    
    # Initialize undo/redo history
    if 'canvas_history' not in st.session_state:
        st.session_state.canvas_history = []
    
    if 'canvas_history_index' not in st.session_state:
        st.session_state.canvas_history_index = -1

def production_target_popup():
    """Professional production target configuration popup for refinery facilities - LEGACY REDIRECT"""
    # DISABLED: This function was causing unwanted popups during page interactions
    # The popup is now only triggered by the centralized dialog system
    return  # Do nothing

def render_equipment_library():
    """Render organized equipment library"""
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.95); border-radius: 4px; padding: 0.8rem; margin: 0.3rem 0; border: 1px solid #e2e8f0; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
        <div style="color: #1a365d; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.4rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.3rem;">
            Equipment Library
        </div>
        <p style="color: #718096; margin-bottom: 0.6rem; font-size: 0.75rem;">
            Select equipment for facility
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    equipment_defaults = create_equipment_defaults()
    
    for category, equipment_list in EQUIPMENT_CATEGORIES.items():
        with st.expander(f"▶ {category}", expanded=True):
            for equipment_name in equipment_list:
                if equipment_name in equipment_defaults:
                    equipment = equipment_defaults[equipment_name]
                    
                    # Equipment card with professional styling
                    specs = f"{equipment.power_rate_kw}kW • {equipment.fuel_type}" if equipment.has_combustion and equipment.requires_power_config else "Non-combustion equipment"
                    
                    col1, col2 = st.columns([2.5, 1])
                    with col1:
                        st.markdown(f"""
                        <div style="font-weight: 500; color: #1a365d; font-size: 0.8rem;">
                            {equipment.icon} {equipment.name}
                        </div>
                        <div style="font-size: 0.7rem; color: #718096; margin-top: 0.1rem;">
                            {specs}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("Add", key=f"add_{equipment_name}", use_container_width=True, help=f"Add {equipment_name} to canvas"):
                            add_equipment_to_canvas(equipment)
                            st.rerun()

def render_facility_statistics():
    """Render compact facility statistics panel"""
    if 'canvas_manager' not in st.session_state:
        return
    
    canvas_manager = st.session_state.canvas_manager
    equipment_count = len(canvas_manager.placed_equipment)
    
    # Calculate basic statistics
    total_co2_daily = sum(eq.equipment.calculate_co2_emission() for eq in canvas_manager.placed_equipment)  # Already daily values
    combustion_equipment = sum(1 for eq in canvas_manager.placed_equipment if eq.equipment.has_combustion)
    
    # CO₂ time period selection
    if 'co2_time_period' not in st.session_state:
        st.session_state.co2_time_period = "Year"
    
    time_period = st.selectbox(
        "CO₂ Time Period",
        options=["Day", "Month", "Year"],
        index=["Day", "Month", "Year"].index(st.session_state.co2_time_period),
        key="co2_period_select",
        label_visibility="collapsed"
    )
    st.session_state.co2_time_period = time_period
    
    # Convert CO₂ based on selected period (scale UP from daily values)
    if time_period == "Day":
        total_co2 = total_co2_daily  # Already daily
        co2_label = "CO₂ (kg/day)"
        avg_co2 = total_co2 / equipment_count if equipment_count > 0 else 0
    elif time_period == "Month":
        total_co2 = total_co2_daily * 30.44  # Scale daily to monthly
        co2_label = "CO₂ (kg/month)"
        avg_co2 = total_co2 / equipment_count if equipment_count > 0 else 0
    else:  # Year
        total_co2 = total_co2_daily * 365.25  # Scale daily to annual
        co2_label = "CO₂ (kg/yr)"
        avg_co2 = total_co2 / equipment_count if equipment_count > 0 else 0
    
    # Minimal statistics display
    st.markdown("""
    <div style="background: rgba(247, 250, 252, 0.95); border-radius: 4px; padding: 0.6rem; margin: 0.3rem 0; border: 1px solid #e2e8f0;">
        <h4 style="color: #1a365d; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; text-align: center;">
            Facility Statistics
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Ultra-compact 2x2 grid layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Equipment", f"{equipment_count}", delta=None)
        st.metric(co2_label, f"{total_co2:,.0f}", delta=None)
    
    with col2:
        st.metric("Combustion", f"{combustion_equipment}", delta=None)
        if equipment_count > 0:
            st.metric("Avg/Unit", f"{avg_co2:,.0f}", delta=None)
        else:
            st.metric("Avg/Unit", "0", delta=None)

def render_facility_canvas():
    """Render the main facility canvas"""
    # Get production configuration for display
    production_config = st.session_state.current_project.get("production_config", {})
    has_production_config = bool(production_config)
    
    # Calculate real-time production from placed equipment
    canvas_manager = st.session_state.get('canvas_manager')
    actual_power_production = 0.0
    actual_crude_processing = 0.0
    
    if canvas_manager and canvas_manager.placed_equipment:
        # Calculate total power production from all equipment
        actual_power_production = sum(eq.equipment.calculate_power_production() for eq in canvas_manager.placed_equipment)
        # Calculate total crude processing capacity from all equipment
        actual_crude_processing = sum(eq.equipment.calculate_crude_processing_capacity() for eq in canvas_manager.placed_equipment)
    
    if has_production_config:
        target_crude_throughput = production_config.get("crude_throughput_bbl_day", 0)
        target_power_capacity = production_config.get("power_capacity_kw", 0)
        
        # Calculate progress percentages
        crude_progress = (actual_crude_processing / target_crude_throughput * 100) if target_crude_throughput > 0 else 0
        power_progress = (actual_power_production / target_power_capacity * 100) if target_power_capacity > 0 else 0
        
        # Determine progress bar colors based on completion
        crude_color = "#10b981" if crude_progress >= 100 else "#f59e0b" if crude_progress >= 50 else "#ef4444"
        power_color = "#10b981" if power_progress >= 100 else "#f59e0b" if power_progress >= 50 else "#ef4444"
        
        # Generate detailed breakdown for tooltips
        crude_breakdown = []
        power_breakdown = []
        
        if canvas_manager and canvas_manager.placed_equipment:
            for eq in canvas_manager.placed_equipment:
                crude_contribution = eq.equipment.calculate_crude_processing_capacity()
                power_contribution = eq.equipment.calculate_power_production()
                
                if crude_contribution > 0:
                    crude_breakdown.append(f"• {eq.equipment.name}: {crude_contribution:,.0f} bbl/day")
                
                if power_contribution > 0:
                    power_breakdown.append(f"• {eq.equipment.name}: {power_contribution:,.0f} kW")
        
        # Create tooltip content as HTML lists
        crude_tooltip_html = "<br>".join(crude_breakdown) if crude_breakdown else "No equipment contributing to crude processing"
        power_tooltip_html = "<br>".join(power_breakdown) if power_breakdown else "No equipment contributing to power generation"
        
        st.markdown(f"""
        <style>
        .tooltip-container {{
            position: relative;
            display: inline-block;
        }}
        .tooltip-container .tooltip-text {{
            visibility: hidden;
            background-color: #2d3748;
            color: #fff;
            text-align: left;
            border-radius: 6px;
            padding: 8px 12px;
            position: absolute;
            z-index: 1000;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
            white-space: nowrap;
            font-size: 0.7rem;
            line-height: 1.4;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 300px;
            white-space: normal;
        }}
        .tooltip-container .tooltip-text::after {{
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #2d3748 transparent transparent transparent;
        }}
        .tooltip-container:hover .tooltip-text {{
            visibility: visible;
            opacity: 1;
        }}
        </style>
        <div style="background: rgba(255, 255, 255, 0.98); border-radius: 4px; padding: 0.6rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
            <div style="color: #1a365d; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.6rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.3rem;">
                Simulation Parameters
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; font-size: 0.7rem;">
                <div style="color: #4a5568;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.2rem;">
                        <div class="tooltip-container">
                            <strong style="color: #2d3748; cursor: help;">Crude Oil Processing ⓘ</strong>
                            <div class="tooltip-text">{crude_tooltip_html}</div>
                        </div>
                        <span style="color: {crude_color}; font-weight: 600;">{crude_progress:.0f}%</span>
                    </div>
                    <div style="color: #718096; font-size: 0.65rem; margin-bottom: 0.3rem;">
                        {actual_crude_processing:,.0f} / {target_crude_throughput:,.0f} bbl/day
                    </div>
                    <div style="background: #e2e8f0; height: 4px; border-radius: 2px; overflow: hidden;">
                        <div style="background: {crude_color}; height: 100%; width: {min(crude_progress, 100):.1f}%; transition: width 0.3s ease;"></div>
                    </div>
                </div>
                <div style="color: #4a5568;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.2rem;">
                        <div class="tooltip-container">
                            <strong style="color: #2d3748; cursor: help;">Power Generation ⓘ</strong>
                            <div class="tooltip-text">{power_tooltip_html}</div>
                        </div>
                        <span style="color: {power_color}; font-weight: 600;">{power_progress:.0f}%</span>
                    </div>
                    <div style="color: #718096; font-size: 0.65rem; margin-bottom: 0.3rem;">
                        {actual_power_production:,.0f} / {target_power_capacity:,.0f} kW
                    </div>
                    <div style="background: #e2e8f0; height: 4px; border-radius: 2px; overflow: hidden;">
                        <div style="background: {power_color}; height: 100%; width: {min(power_progress, 100):.1f}%; transition: width 0.3s ease;"></div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.98); border-radius: 4px; padding: 0.6rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
            <div style="color: #1a365d; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.4rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.3rem;">
                Simulation Parameters
            </div>
            <p style="color: #718096; margin-bottom: 0.6rem; font-size: 0.75rem;">
                Configure production targets to view parameters
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Ultra-compact canvas control buttons
    st.markdown('<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.4rem; margin: 0.3rem 0;">', unsafe_allow_html=True)
    canvas_col1, canvas_col2, canvas_col3 = st.columns(3)
    
    with canvas_col1:
        if st.button("Reset", help="Clear all equipment", use_container_width=True):
            if st.session_state.get('canvas_manager'):
                # Save current state before reset
                save_canvas_state("Reset Canvas")
                st.session_state.canvas_manager.placed_equipment = []
                if st.session_state.get('enhanced_canvas_manager'):
                    st.session_state.enhanced_canvas_manager.placed_equipment = []
                st.session_state.project_saved = False
                st.success("Reset complete")
                st.rerun()
    
    with canvas_col2:
        can_undo = len(st.session_state.canvas_history) > 0 and st.session_state.canvas_history_index >= 0
        if st.button("Undo", help="Undo last action", use_container_width=True, disabled=not can_undo):
            if undo_canvas_action():
                st.success("Undone")
                st.rerun()
    
    with canvas_col3:
        can_redo = (len(st.session_state.canvas_history) > 0 and 
                   st.session_state.canvas_history_index < len(st.session_state.canvas_history) - 1)
        if st.button("Redo", help="Redo last undone action", use_container_width=True, disabled=not can_redo):
            if redo_canvas_action():
                st.success("Redone")
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if 'canvas_manager' not in st.session_state:
        st.error("Canvas not initialized. Please return to main page and reload the project.")
        return
    
    # Render the actual canvas
    render_canvas()
    
    # Canvas information
    canvas_manager = st.session_state.canvas_manager
    canvas_bounds = canvas_manager.get_canvas_bounds()
    
    if len(canvas_manager.placed_equipment) == 0:
        st.info("No equipment placed. Use equipment library to add.")
    else:
        st.success(f"{len(canvas_manager.placed_equipment)} units | {canvas_bounds[0]}×{canvas_bounds[1]}m")
    
    # Render Equipment Summary Table
    render_equipment_summary_table()

def render_equipment_configuration_panel():
    """Render equipment configuration in a professional panel with 3D movement controls"""
    if not st.session_state.get('show_config_panel', False) or not st.session_state.get('selected_equipment_for_config'):
        return
    
    selected = st.session_state.selected_equipment_for_config
    equipment = selected.equipment
    
    st.markdown("""
    <div class="section-container" style="border: 2px solid #4fd1c7; background: rgba(79, 209, 199, 0.02);">
        <div class="section-title">Equipment Configuration & 3D Controls</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Equipment header
    config_col1, config_col2 = st.columns([2, 1])
    
    with config_col1:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.9); padding: 1rem; border-radius: 6px; margin-bottom: 1rem;">
            <h3 style="color: #1a365d; margin-bottom: 0.5rem;">{equipment.icon} {equipment.name}</h3>
            <p style="color: #718096; margin: 0; font-size: 0.9rem;">Category: {equipment.category}</p>
            <p style="color: #4fd1c7; margin: 0; font-size: 0.8rem;">Position: ({selected.x_position:.1f}m, {selected.y_position:.1f}m)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with config_col2:
        st.markdown("#### 3D Movement Controls")
        
        # Movement controls
        move_increment = st.selectbox("Move Step (m)", [0.5, 1, 2, 5, 10], index=2, key="move_increment")
        
        # Direction buttons in grid layout
        col_nw, col_n, col_ne = st.columns(3)
        col_w, col_center, col_e = st.columns(3)
        col_sw, col_s, col_se = st.columns(3)
        
        canvas_bounds = st.session_state.canvas_manager.get_canvas_bounds()
        
        with col_n:
            if st.button("⬆️", key="move_north", use_container_width=True, help="Move North"):
                old_pos = (selected.x_position, selected.y_position)
                new_y = max(0, selected.y_position - move_increment)
                st.session_state.canvas_manager.update_equipment_position(selected, selected.x_position, new_y)
                st.success(f"✅ Moved North: ({old_pos[0]:.1f}, {old_pos[1]:.1f}) → ({selected.x_position:.1f}, {new_y:.1f})")
                st.rerun()
        
        with col_w:
            if st.button("⬅️", key="move_west", use_container_width=True, help="Move West"):
                new_x = max(0, selected.x_position - move_increment)
                st.session_state.canvas_manager.update_equipment_position(selected, new_x, selected.y_position)
                st.rerun()
        
        with col_center:
            if st.button("🎯", key="center_equipment", use_container_width=True, help="Center"):
                center_x, center_y = canvas_bounds[0] / 2, canvas_bounds[1] / 2
                st.session_state.canvas_manager.update_equipment_position(selected, center_x, center_y)
                st.rerun()
        
        with col_e:
            if st.button("➡️", key="move_east", use_container_width=True, help="Move East"):
                new_x = min(canvas_bounds[0], selected.x_position + move_increment)
                st.session_state.canvas_manager.update_equipment_position(selected, new_x, selected.y_position)
                st.rerun()
        
        with col_s:
            if st.button("⬇️", key="move_south", use_container_width=True, help="Move South"):
                new_y = min(canvas_bounds[1], selected.y_position + move_increment)
                st.session_state.canvas_manager.update_equipment_position(selected, selected.x_position, new_y)
                st.rerun()
        
        # Precise positioning
        precise_col1, precise_col2 = st.columns(2)
        with precise_col1:
            new_x = st.number_input("X (m)", min_value=0.0, max_value=float(canvas_bounds[0]), 
                                  value=float(selected.x_position), step=0.5, key="precise_x")
        with precise_col2:
            new_y = st.number_input("Y (m)", min_value=0.0, max_value=float(canvas_bounds[1]),
                                  value=float(selected.y_position), step=0.5, key="precise_y")
        
        if st.button("📐 Update Position", key="update_precise_position", use_container_width=True):
            st.session_state.canvas_manager.update_equipment_position(selected, new_x, new_y)
            st.success(f"✅ Updated position to ({new_x:.1f}, {new_y:.1f})")
            st.rerun()
            
        # Test button to force canvas refresh
        if st.button("🔄 Force Refresh Canvas", key="force_refresh", use_container_width=True):
            st.success("🔄 Canvas refreshed!")
            st.rerun()
    
    st.markdown("---")
        
    # Configuration form
    with st.form("equipment_config", clear_on_submit=False):
        config_form_col1, config_form_col2 = st.columns([3, 2])
        
        with config_form_col1:
            if equipment.requires_power_config:
                power_rate = st.number_input(
                    "Power Rate (kW)",
                    min_value=0.0,
                    value=equipment.power_rate_kw,
                    step=10.0,
                    help="Operating power consumption in kilowatts"
                )
                
                operation_time = st.number_input(
                    "Operation Time (hours/year)",
                    min_value=0.0,
                    max_value=8760.0,
                    value=equipment.operation_time_hours,
                    step=100.0,
                    help="Annual operating hours (max 8760)"
                )
                
                fuel_type = st.selectbox(
                    "Fuel Type",
                    options=["LPG", "Diesel", "Gasoline", "Natural Gas", "None", "Gas", "Electric"],
                    index=["LPG", "Diesel", "Gasoline", "Natural Gas", "None", "Gas", "Electric"].index(equipment.fuel_type),
                    help="Primary fuel or energy source"
                )
            else:
                st.info("ℹ️ This equipment type doesn't require power or fuel configuration.")
                power_rate = 0.0
                operation_time = 0.0
                fuel_type = "None"
            
            # Action buttons
            button_col1, button_col2, button_col3 = st.columns(3)
            
            with button_col1:
                save_clicked = st.form_submit_button("Save Changes", use_container_width=True, type="primary")
            
            with button_col2:
                delete_clicked = st.form_submit_button("Delete Equipment", use_container_width=True)
            
            with button_col3:
                close_clicked = st.form_submit_button("Close Panel", use_container_width=True)
            
            if save_clicked:
                # Update equipment
                equipment.power_rate_kw = power_rate
                equipment.operation_time_hours = operation_time
                equipment.fuel_type = fuel_type
                st.success("✅ Equipment configuration updated successfully!")
                st.session_state.project_saved = False  # Mark as unsaved
                st.rerun()
            
            if delete_clicked:
                # Remove equipment
                if 'canvas_manager' in st.session_state:
                    st.session_state.canvas_manager.remove_equipment(equipment.id)
                    st.success("🗑️ Equipment removed from facility!")
                    st.session_state.show_config_panel = False
                    st.session_state.project_saved = False  # Mark as unsaved
                    st.rerun()
            
            if close_clicked:
                st.session_state.show_config_panel = False
                st.rerun()
    
    with config_col2:
        # Equipment information panel
        st.markdown("""
        <div style="background: rgba(247, 250, 252, 0.95); padding: 1rem; border-radius: 6px;">
            <h4 style="color: #1a365d; margin-bottom: 0.8rem; font-size: 1rem;">Equipment Information</h4>
        </div>
        """, unsafe_allow_html=True)
        
        info = equipment.get_equipment_info()
        
        # Basic information
        st.markdown("**Basic Properties:**")
        st.write(f"• **Type:** {info['basic_info']['name']}")
        st.write(f"• **Category:** {info['basic_info']['category']}")
        st.write(f"• **Combustion:** {'Yes' if info['basic_info']['has_combustion'] else 'No'}")
        
        if equipment.requires_power_config:
            st.markdown("**Operational Data:**")
            for key, value in info['operational_data'].items():
                formatted_key = key.replace('_', ' ').title()
                st.write(f"• **{formatted_key}:** {value}")
        
        # Environmental impact
        st.markdown("**Environmental Impact:**")
        st.write(f"• **CO₂ Emission:** {info['environmental_impact']['co2_emission_kg']:,.1f} kg/year")
        
        # Position information
        st.markdown("**Position:**")
        st.write(f"• **X:** {selected.x_position:.1f} m")
        st.write(f"• **Y:** {selected.y_position:.1f} m")

def add_equipment_to_canvas(equipment_template: EquipmentModel):
    """Show position picker for adding equipment to canvas"""
    # Set up the equipment to be placed
    st.session_state.equipment_to_place = equipment_template
    st.session_state.show_position_picker = True
    st.rerun()

def render_position_picker():
    """Render position picker as a popup dialog"""
    if not st.session_state.get('show_position_picker', False) or not st.session_state.get('equipment_to_place'):
        return
    
    equipment = st.session_state.equipment_to_place
    canvas_bounds = st.session_state.canvas_manager.get_canvas_bounds()
    
    @st.dialog(f"Equipment Positioning: {equipment.name}")
    def position_picker_dialog():
        # Single column layout
        st.markdown("### Coordinates")
        
        # Coordinates in one row
        coord_col1, coord_col2 = st.columns(2)
        
        with coord_col1:
            x_pos = st.number_input(
                "X-Position", 
                min_value=0.0, 
                max_value=float(canvas_bounds[0]), 
                value=float(canvas_bounds[0] / 2), 
                step=5.0, 
                key="place_x",
                help="Horizontal distance from origin (meters)",
                format="%.0f"
            )
        
        with coord_col2:
            y_pos = st.number_input(
                "Y-Position", 
                min_value=0.0, 
                max_value=float(canvas_bounds[1]), 
                value=float(canvas_bounds[1] / 2), 
                step=5.0, 
                key="place_y",
                help="Vertical distance from origin (meters)",
                format="%.0f"
            )
        
        # Layout Preview - using full width space
        st.markdown("### Layout Preview")
        
        # Create professional facility layout preview
        import plotly.graph_objects as go
        
        preview_fig = go.Figure()
        
        # Facility boundary with professional styling
        preview_fig.add_trace(go.Scatter(
            x=[0, canvas_bounds[0], canvas_bounds[0], 0, 0],
            y=[0, 0, canvas_bounds[1], canvas_bounds[1], 0],
            mode='lines',
            line=dict(color='#2d3748', width=3),
            fill='none',
            name='Facility Boundary',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Adaptive grid system based on facility size
        max_dimension = max(canvas_bounds[0], canvas_bounds[1])
        
        # Calculate appropriate grid spacing for better precision
        if max_dimension <= 100:      # Small facilities (≤100m) - 5m grid
            grid_spacing = 5
        elif max_dimension <= 200:    # Medium facilities (≤200m) - 10m grid  
            grid_spacing = 10
        elif max_dimension <= 500:    # Large facilities (≤500m) - 20m grid
            grid_spacing = 20
        else:                         # Very large facilities (>500m) - 50m grid
            grid_spacing = 50
        
        # Major grid lines
        for x in range(0, int(canvas_bounds[0]) + 1, grid_spacing):
            preview_fig.add_trace(go.Scatter(
                x=[x, x], y=[0, canvas_bounds[1]],
                mode='lines',
                line=dict(color='#cbd5e0', width=1, dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        for y in range(0, int(canvas_bounds[1]) + 1, grid_spacing):
            preview_fig.add_trace(go.Scatter(
                x=[0, canvas_bounds[0]], y=[y, y],
                mode='lines',
                line=dict(color='#cbd5e0', width=1, dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Existing equipment with professional markers
        if st.session_state.canvas_manager.placed_equipment:
            existing_x = [eq.x_position for eq in st.session_state.canvas_manager.placed_equipment]
            existing_y = [eq.y_position for eq in st.session_state.canvas_manager.placed_equipment]
            existing_names = [eq.equipment.name for eq in st.session_state.canvas_manager.placed_equipment]
            
            preview_fig.add_trace(go.Scatter(
                x=existing_x, y=existing_y,
                mode='markers',
                marker=dict(color='#718096', size=12, symbol='square'),
                name='Existing Equipment',
                showlegend=False,
                text=existing_names,
                hovertemplate="<b>%{text}</b><br>X: %{x:.0f}m<br>Y: %{y:.0f}m<extra></extra>"
            ))
        
        # New equipment position with distinctive marker
        preview_fig.add_trace(go.Scatter(
            x=[x_pos], y=[y_pos],
            mode='markers',
            marker=dict(
                color='#e53e3e', 
                size=16, 
                symbol='diamond',
                line=dict(color='#ffffff', width=2)
            ),
            name='New Equipment',
            showlegend=False,
            hovertemplate=f"<b>New: {equipment.name}</b><br>X: {x_pos:.0f}m<br>Y: {y_pos:.0f}m<extra></extra>"
        ))
        
        # Professional layout configuration
        preview_fig.update_layout(
            title=dict(
                text="Facility Layout",
                font=dict(size=16, color='#2d3748'),
                x=0.5
            ),
            xaxis=dict(
                title="X-Position (m)",
                range=[0, canvas_bounds[0]],
                dtick=grid_spacing,
                showgrid=False,
                zeroline=False,
                tickfont=dict(size=10)
            ),
            yaxis=dict(
                title="Y-Position (m)",
                range=[0, canvas_bounds[1]],
                dtick=grid_spacing,
                scaleanchor="x",
                scaleratio=1,
                showgrid=False,
                zeroline=False,
                tickfont=dict(size=10)
            ),
            height=400,
            margin=dict(l=50, r=20, t=50, b=50),
            showlegend=False,
            plot_bgcolor='rgba(247, 250, 252, 0.8)',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(preview_fig, use_container_width=True, key="facility_preview")
        
        # Position Analysis
        st.markdown("### Position Analysis")
        distance_from_center = ((x_pos - canvas_bounds[0]/2)**2 + (y_pos - canvas_bounds[1]/2)**2)**0.5
        
        # Position zone classification
        x_percent = x_pos / canvas_bounds[0]
        y_percent = y_pos / canvas_bounds[1]
        
        if x_percent < 0.33:
            x_zone = "Western"
        elif x_percent > 0.67:
            x_zone = "Eastern"
        else:
            x_zone = "Central"
            
        if y_percent < 0.33:
            y_zone = "Southern"
        elif y_percent > 0.67:
            y_zone = "Northern"
        else:
            y_zone = "Central"
        
        zone_description = f"{y_zone} {x_zone}" if y_zone != "Central" or x_zone != "Central" else "Central"
        
        analysis_col1, analysis_col2 = st.columns(2)
        with analysis_col1:
            st.metric("Distance from Center", f"{distance_from_center:.0f}m")
        with analysis_col2:
            st.metric("Facility Zone", zone_description)
        
        # Equipment Variable Configuration Section
        st.markdown("### Equipment Variable Configuration")
        
        config_col1, config_col2 = st.columns(2)
        
        # Initialize configuration variables
        configured_power_rate = equipment.power_rate_kw
        configured_operation_hours = equipment.operation_time_hours
        configured_fuel_type = equipment.fuel_type
        configured_fuel_consumption = equipment.fuel_consumption_rate
        load_factor = 1.0
        efficiency = 0.85
        
        # Get emission factor from EMISSION_FACTORS
        from src.models.equipment_model import EMISSION_FACTORS
        
        with config_col1:
            # Rated Capacity (Power Rate)
            if equipment.requires_power_config:
                configured_power_rate = st.number_input(
                    "Rated Capacity (kW)",
                    min_value=0.0,
                    value=float(equipment.power_rate_kw),
                    step=10.0,
                    help="Equipment's rated power capacity in kilowatts",
                    key="config_power_rate"
                )
            else:
                st.text_input("Rated Capacity", value="N/A", disabled=True)
            
            # Operating Hours
            if equipment.requires_power_config:
                # Convert annual hours to daily for display, with reasonable default
                default_daily_hours = min(24, equipment.operation_time_hours / 365) if equipment.operation_time_hours > 0 else 8
                configured_operation_hours = st.number_input(
                    "Operating Hours (hours/day)",
                    min_value=0.0,
                    max_value=24.0,
                    value=float(default_daily_hours),
                    step=0.5,
                    help="Daily operating hours (max 24 hours/day)",
                    key="config_operation_hours"
                )
            else:
                st.text_input("Operating Hours", value="N/A", disabled=True)
            
            # Load Factor
            if equipment.requires_power_config and equipment.has_combustion:
                load_factor = st.number_input(
                    "Load Factor",
                    min_value=0.1,
                    max_value=1.0,
                    value=1.0,
                    step=0.05,
                    help="Operating load as fraction of rated capacity (0.1 to 1.0)",
                    key="config_load_factor"
                )
            else:
                st.text_input("Load Factor", value="N/A", disabled=True)
            
            # Efficiency
            if equipment.has_combustion:
                if equipment.category == "Power Generation":
                    efficiency = st.number_input(
                        "Efficiency",
                        min_value=0.2,
                        max_value=0.95,
                        value=0.85,
                        step=0.05,
                        help="Equipment efficiency (0.2 to 0.95)",
                        key="config_efficiency"
                    )
                elif equipment.category in ["Process Heating & Steam", "Utility"]:
                    efficiency = st.number_input(
                        "Thermal Efficiency",
                        min_value=0.6,
                        max_value=0.95,
                        value=0.85,
                        step=0.05,
                        help="Thermal efficiency (0.6 to 0.95)",
                        key="config_efficiency"
                    )
                else:
                    efficiency = st.number_input(
                        "Efficiency",
                        min_value=0.5,
                        max_value=0.95,
                        value=0.80,
                        step=0.05,
                        help="Equipment efficiency (0.5 to 0.95)",
                        key="config_efficiency"
                    )
            else:
                st.text_input("Efficiency", value="N/A", disabled=True)
        
        with config_col2:
            # Fuel Type
            if equipment.has_combustion or equipment.fuel_type == "Electric":
                available_fuels = ["Natural Gas", "Gas", "Diesel", "LPG", "Gasoline", "Electric"]
                if equipment.fuel_type in available_fuels:
                    fuel_index = available_fuels.index(equipment.fuel_type)
                else:
                    fuel_index = 0
                
                configured_fuel_type = st.selectbox(
                    "Fuel Type",
                    options=available_fuels,
                    index=fuel_index,
                    help="Type of fuel used by equipment",
                    key="config_fuel_type"
                )
            else:
                st.text_input("Fuel Type", value="N/A", disabled=True)
            
            # Fuel Consumption Rate
            if equipment.has_combustion:
                if configured_fuel_type in ["Diesel", "LPG", "Gasoline"]:
                    configured_fuel_consumption = st.number_input(
                        "Fuel Consumption (L/hr)",
                        min_value=0.0,
                        value=float(equipment.fuel_consumption_rate) if equipment.fuel_consumption_rate > 0 else 10.0,
                        step=1.0,
                        help="Fuel consumption rate in liters per hour",
                        key="config_fuel_consumption"
                    )
                elif configured_fuel_type in ["Natural Gas", "Gas"]:
                    configured_fuel_consumption = st.number_input(
                        "Gas Consumption (kWh/hr)",
                        min_value=0.0,
                        value=float(equipment.fuel_consumption_rate) if equipment.fuel_consumption_rate > 0 else 100.0,
                        step=10.0,
                        help="Gas consumption rate in kWh per hour",
                        key="config_fuel_consumption"
                    )
                else:
                    configured_fuel_consumption = st.number_input(
                        "Fuel Consumption",
                        min_value=0.0,
                        value=float(equipment.fuel_consumption_rate) if equipment.fuel_consumption_rate > 0 else 10.0,
                        step=1.0,
                        help="Fuel consumption rate",
                        key="config_fuel_consumption"
                    )
            else:
                st.text_input("Fuel Consumption", value="N/A", disabled=True)
            
            # Get updated emission factor based on current fuel type selection
            emission_factor_data = EMISSION_FACTORS.get(configured_fuel_type, {"factor": 0.0, "unit": "N/A"})
            emission_factor = emission_factor_data["factor"]
            emission_unit = emission_factor_data["unit"]
            
            # Emission Factor (Read-only)
            st.text_input(
                "Emission Factor (International Standard)",
                value=f"{emission_factor} {emission_unit}",
                disabled=True,
                help="CO2 emission factor based on international standards (EPA). Updates automatically with fuel type."
            )
        
        # Real-time calculations outside the form for immediate updates
        st.markdown("### Real-time Calculations")
        calc_col1, calc_col2 = st.columns(2)
        
        # Update equipment parameters automatically with current input values
        equipment.power_rate_kw = configured_power_rate
        equipment.operation_time_hours = configured_operation_hours * 365  # Convert daily back to annual for storage
        equipment.fuel_type = configured_fuel_type
        equipment.fuel_consumption_rate = configured_fuel_consumption
        
        with calc_col1:
            # CO2 Emissions Calculation (Daily) - Using same method as equipment model
            if equipment.has_combustion:
                # Calculate fuel consumption using same method as equipment_model.py
                if equipment.category == "Power Generation":
                    if equipment.name == "Gas Turbine" and configured_fuel_type in ["Natural Gas", "Gas"]:
                        # Gas turbine: heat rate approach (11.0 kWh thermal per kWh electrical)
                        heat_rate = 11.0
                        daily_thermal_consumption = configured_power_rate * heat_rate * configured_operation_hours
                        daily_co2_emissions = daily_thermal_consumption * emission_factor * load_factor
                    elif equipment.name == "Gas Engine Generator" and configured_fuel_type in ["Natural Gas", "Gas"]:
                        # Gas engine: heat rate approach (10.0 kWh thermal per kWh electrical)
                        heat_rate = 10.0
                        daily_thermal_consumption = configured_power_rate * heat_rate * configured_operation_hours
                        daily_co2_emissions = daily_thermal_consumption * emission_factor * load_factor
                    elif equipment.name == "Diesel Gen-set" and configured_fuel_type == "Diesel":
                        # Diesel generator: fuel rate approach (0.28 L/kWh)
                        fuel_rate = 0.28
                        daily_fuel_consumption = configured_power_rate * fuel_rate * configured_operation_hours
                        daily_co2_emissions = daily_fuel_consumption * emission_factor * load_factor
                    else:
                        daily_co2_emissions = 0.0
                elif equipment.category in ["Process Heating & Steam", "Utility"]:
                    if configured_fuel_type in ["Natural Gas", "Gas"]:
                        # Thermal efficiency approach (85% for process, 80% for utility heaters)
                        thermal_efficiency = 0.85 if equipment.category == "Process Heating & Steam" else 0.80
                        daily_thermal_consumption = configured_power_rate * (1/thermal_efficiency) * configured_operation_hours
                        daily_co2_emissions = daily_thermal_consumption * emission_factor * load_factor
                    elif configured_fuel_type == "Diesel":
                        # Diesel thermal equipment
                        fuel_rate = 0.30  # L/kWh thermal
                        daily_fuel_consumption = configured_power_rate * fuel_rate * configured_operation_hours
                        daily_co2_emissions = daily_fuel_consumption * emission_factor * load_factor
                    else:
                        daily_co2_emissions = 0.0
                else:
                    # Other categories: use direct fuel consumption rate
                    daily_fuel_consumption = configured_fuel_consumption * configured_operation_hours
                    daily_co2_emissions = daily_fuel_consumption * emission_factor * load_factor
                
                # Custom metric with smaller font
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 0.75rem; border-radius: 0.5rem; border-left: 4px solid #1f77b4;">
                    <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 0.25rem;">Daily CO2 Emissions</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #1f77b4;">{daily_co2_emissions:.2f} kg/day</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Non-combustion equipment
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 0.75rem; border-radius: 0.5rem; border-left: 4px solid #28a745;">
                    <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 0.25rem;">Daily CO2 Emissions</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #28a745;">0.00 kg/day</div>
                </div>
                """, unsafe_allow_html=True)
        
        with calc_col2:
            # Determine if this equipment processes crude oil or generates power
            oil_processing_equipment = [
                "Boiler", "Process Heater", "Furnace", "Atmospheric Distillation Column", 
                "Column Reboiler", "Overhead Condenser", "Preheat Train", "Desalter", "Dehydrator",
                "Crude Tank", "Storage Tank", "Feed Pump", "Product Pump"
            ]
            
            if equipment.name in oil_processing_equipment:
                # Crude Processing Capacity Calculation (Daily)
                if configured_power_rate > 0:
                    # Engineering calculation: thermal capacity to barrel processing
                    # Using thermodynamic principles for crude oil processing
                    # Crude oil density: ~136 kg/bbl, specific heat: ~2.0 kJ/kg·K, temp delta: ~290K
                    # Energy per barrel: 136 kg/bbl × 2.0 kJ/kg·K × 290K = 78,880 kJ/bbl
                    energy_per_barrel_kj = 78880  # kJ/bbl
                    
                    # Convert power from kW to kJ/day: kW × 3600 s/hr × 24 hr/day = kJ/day
                    daily_energy_available_kj = configured_power_rate * 3600 * configured_operation_hours
                    
                    # Apply thermal efficiency and load factor
                    processing_efficiency = efficiency * load_factor
                    effective_energy_kj = daily_energy_available_kj * processing_efficiency
                    
                    # Calculate processing capacity
                    daily_processing_capacity = effective_energy_kj / energy_per_barrel_kj
                    
                    # Custom metric with smaller font
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 0.75rem; border-radius: 0.5rem; border-left: 4px solid #8B4513;">
                        <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 0.25rem;">Daily Crude Processing</div>
                        <div style="font-size: 1.2rem; font-weight: 600; color: #8B4513;">{daily_processing_capacity:.0f} bbl/day</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 0.75rem; border-radius: 0.5rem; border-left: 4px solid #6c757d;">
                        <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 0.25rem;">Daily Crude Processing</div>
                        <div style="font-size: 1.2rem; font-weight: 600; color: #6c757d;">N/A</div>
                    </div>
                    """, unsafe_allow_html=True)
            elif equipment.category == "Power Generation":
                # Power Generation Calculation (Daily)
                capacity_factors = {
                    "Gas Turbine": 0.95,
                    "Gas Engine Generator": 0.92,
                    "Diesel Gen-set": 0.90,
                    "Motor Control Centre (MCC)": 1.0,
                    "SCADA Control System": 1.0
                }
                capacity_factor = capacity_factors.get(equipment.name, 0.85)
                daily_power = configured_power_rate * configured_operation_hours * capacity_factor * efficiency * load_factor
                # Custom metric with smaller font
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 0.75rem; border-radius: 0.5rem; border-left: 4px solid #ff7f0e;">
                    <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 0.25rem;">Daily Power Generation</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #ff7f0e;">{daily_power:.0f} kWh/day</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Other equipment types - no specific output
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 0.75rem; border-radius: 0.5rem; border-left: 4px solid #6c757d;">
                    <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 0.25rem;">Production Output</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #6c757d;">N/A</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Confirm Placement and Cancel in one row
        st.markdown("### Confirm Placement")
        
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if st.button(
                "Place Equipment", 
                use_container_width=True, 
                type="primary", 
                key="place_equipment_confirm",
                help=f"Place {equipment.name} at coordinates ({x_pos:.0f}, {y_pos:.0f})"
            ):
                place_equipment_at_position(equipment, x_pos, y_pos)
        
        with action_col2:
            if st.button("Cancel", use_container_width=True, key="cancel_placement", help="Cancel equipment placement"):
                st.session_state.show_position_picker = False
                st.session_state.equipment_to_place = None
                st.rerun()
    
    # Open the dialog
    position_picker_dialog()

def place_equipment_at_position(equipment_template: EquipmentModel, x_pos: float, y_pos: float):
    """Actually place the equipment at the specified position"""
    
    # Save current state before making changes
    save_canvas_state(f"Add {equipment_template.name}")
    
    # Add to enhanced canvas manager
    if 'enhanced_canvas_manager' in st.session_state:
        canvas_manager = st.session_state.enhanced_canvas_manager
        
        # Create new equipment instance with unique ID
        new_equipment = EquipmentModel(
            id="",  # Will generate new ID
            name=equipment_template.name,
            category=equipment_template.category,
            power_rate_kw=equipment_template.power_rate_kw,
            operation_time_hours=equipment_template.operation_time_hours,
            fuel_type=equipment_template.fuel_type,
            fuel_consumption_rate=equipment_template.fuel_consumption_rate,
            description=equipment_template.description,
            icon=equipment_template.icon
        )
        
        # Add equipment to enhanced canvas
        placed_equipment = canvas_manager.add_equipment(new_equipment, x_pos, y_pos)
    
    # Add to legacy canvas manager for compatibility
    if 'canvas_manager' in st.session_state:
        legacy_canvas = st.session_state.canvas_manager
        
        # Create new equipment instance for legacy canvas
        legacy_equipment = EquipmentModel(
            id="",  # Will generate new ID
            name=equipment_template.name,
            category=equipment_template.category,
            power_rate_kw=equipment_template.power_rate_kw,
            operation_time_hours=equipment_template.operation_time_hours,
            fuel_type=equipment_template.fuel_type,
            fuel_consumption_rate=equipment_template.fuel_consumption_rate,
            description=equipment_template.description,
            icon=equipment_template.icon
        )
        
        # Use the specified positioning
        legacy_canvas.add_equipment(legacy_equipment, x_pos, y_pos)
    
    # Mark project as unsaved
    st.session_state.project_saved = False
    
    # Close position picker
    st.session_state.show_position_picker = False
    st.session_state.equipment_to_place = None
    
    st.success(f"✅ {equipment_template.name} placed at ({x_pos:.1f}, {y_pos:.1f})")
    st.rerun()

def render_canvas():
    """Render the facility canvas in 3D"""
    if 'canvas_manager' not in st.session_state:
        st.error("Canvas not initialized properly.")
        return
    
    canvas_manager = st.session_state.canvas_manager
    
    # Create 3D plotly figure
    fig = go.Figure()
    
    # Get canvas bounds and facility area
    canvas_bounds = canvas_manager.get_canvas_bounds()
    project = st.session_state.current_project
    facility_acres = project.get('facility_size_acres', 1.0)
    
    # Add 3D ground plane with grid based on actual facility size
    ground_x = [0, canvas_bounds[0], canvas_bounds[0], 0, 0]
    ground_y = [0, 0, canvas_bounds[1], canvas_bounds[1], 0]
    ground_z = [0, 0, 0, 0, 0]
    
    fig.add_trace(go.Scatter3d(
        x=ground_x, y=ground_y, z=ground_z,
        mode='lines',
        line=dict(color='#e2e8f0', width=2),
        name='Facility Boundary',
        hovertemplate=f"Facility Area: {facility_acres} acres ({canvas_bounds[0]}m × {canvas_bounds[1]}m)<extra></extra>",
        showlegend=False
    ))
    
    # Add grid lines for scale reference - using adaptive spacing
    max_dimension = max(canvas_bounds[0], canvas_bounds[1])
    
    # Calculate appropriate grid spacing for better precision (same as 2D canvas)
    if max_dimension <= 100:      # Small facilities (≤100m) - 5m grid
        grid_spacing = 5
    elif max_dimension <= 200:    # Medium facilities (≤200m) - 10m grid  
        grid_spacing = 10
    elif max_dimension <= 500:    # Large facilities (≤500m) - 20m grid
        grid_spacing = 20
    else:                         # Very large facilities (>500m) - 50m grid
        grid_spacing = 50
    
    # Vertical grid lines
    for x in range(0, int(canvas_bounds[0]) + 1, int(grid_spacing)):
        fig.add_trace(go.Scatter3d(
            x=[x, x], y=[0, canvas_bounds[1]], z=[0, 0],
            mode='lines',
            line=dict(color='#000000', width=1),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Horizontal grid lines  
    for y in range(0, int(canvas_bounds[1]) + 1, int(grid_spacing)):
        fig.add_trace(go.Scatter3d(
            x=[0, canvas_bounds[0]], y=[y, y], z=[0, 0],
            mode='lines',
            line=dict(color='#000000', width=1),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add directional arrows and labels to mark X and Y axes
    arrow_length = min(canvas_bounds[0], canvas_bounds[1]) * 0.15
    
    # X-axis arrow (red) - pointing right
    fig.add_trace(go.Scatter3d(
        x=[0, arrow_length], y=[0, 0], z=[0, 0],
        mode='lines+text',
        line=dict(color='#e53e3e', width=6),
        text=['', 'X'],
        textposition='middle right',
        textfont=dict(size=16, color='#e53e3e'),
        name='X-Axis',
        showlegend=False,
        hovertemplate="X-Axis Direction<extra></extra>"
    ))
    
    # Y-axis arrow (green) - pointing forward
    fig.add_trace(go.Scatter3d(
        x=[0, 0], y=[0, arrow_length], z=[0, 0],
        mode='lines+text',
        line=dict(color='#38a169', width=6),
        text=['', 'Y'],
        textposition='middle right',
        textfont=dict(size=16, color='#38a169'),
        name='Y-Axis',
        showlegend=False,
        hovertemplate="Y-Axis Direction<extra></extra>"
    ))
    
    # Add origin marker
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers+text',
        marker=dict(
            symbol='circle',
            size=8,
            color='#2d3748',
            line=dict(color='#ffffff', width=2)
        ),
        text=['Origin (0,0)'],
        textposition='top center',
        textfont=dict(size=12, color='#2d3748'),
        showlegend=False,
        hovertemplate="Origin Point (0,0)<extra></extra>"
    ))
    
    # Add 3D equipment to canvas
    if canvas_manager.placed_equipment:
        for placed_eq in canvas_manager.placed_equipment:
            equipment = placed_eq.equipment
            
            # Get 3D equipment representation
            equipment_3d = get_equipment_3d_model(equipment, placed_eq.x_position, placed_eq.y_position)
            
            # Add equipment to figure
            for trace in equipment_3d:
                trace.update(customdata=[equipment.id])
                fig.add_trace(trace)
    
    # Configure 3D layout with turntable rotation
    fig.update_layout(
        title="",
        scene=dict(
            xaxis=dict(
                title="X-Axis Distance (m) →",
                range=[0, canvas_bounds[0]],
                showgrid=True,
                gridcolor="#e2e8f0",
                gridwidth=1,
                title_font=dict(size=12, color='#e53e3e'),
                dtick=grid_spacing  # Use adaptive grid spacing for clean axis labels
            ),
            yaxis=dict(
                title="Y-Axis Distance (m) ↑", 
                range=[0, canvas_bounds[1]],
                showgrid=True,
                gridcolor="#e2e8f0",
                gridwidth=1,
                title_font=dict(size=12, color='#38a169'),
                dtick=grid_spacing  # Use adaptive grid spacing for clean axis labels
            ),
            zaxis=dict(
                title="Height (m)",
                range=[0, max(50, canvas_bounds[0] * 0.3)],  # Dynamic height based on facility size
                showgrid=True,
                gridcolor="#e2e8f0",
                gridwidth=1,
                title_font=dict(size=9),
                dtick=20  # Fewer numbers on Z-axis
            ),
            bgcolor="rgba(247, 250, 252, 0.9)",
            camera=dict(
                eye=dict(x=0.8, y=0.8, z=1.0),  # Closer view focused on origin area
                center=dict(x=0, y=0, z=0),  # Lock rotation center at origin (0,0,0)
                up=dict(x=0, y=0, z=1)
            ),
            aspectmode='manual',
            aspectratio=dict(
                x=1, 
                y=canvas_bounds[1]/canvas_bounds[0],  # Dynamic Y ratio based on actual facility dimensions
                z=0.5
            ),  # Proper proportions for rectangular facilities
            # Enable turntable rotation by default
            dragmode='turntable'  # This enables smooth 3D rotation
        ),
        height=600,  # Increased from 500 to 600 for more bottom space during rotation
        showlegend=False,
        margin=dict(l=35, r=15, t=5, b=50),  # Increased bottom margin from 35 to 50
        # Additional 3D interaction configuration
        scene_dragmode='turntable'  # Ensure turntable mode is default
    )
    
    # Display the 3D canvas with turntable rotation and border
    # Add dynamic key to force refresh when equipment moves
    canvas_key = f"facility_canvas_3d_{len(canvas_manager.placed_equipment)}_{sum([eq.x_position + eq.y_position for eq in canvas_manager.placed_equipment]) if canvas_manager.placed_equipment else 0}"
    
    # Add border around canvas area
    st.markdown("""
    <style>
    .canvas-container {
        border: 1px solid #cbd5e0;
        border-radius: 8px;
        padding: 0px;
        background: transparent;
        overflow: hidden;
        margin-bottom: 10px;
    }
    .canvas-container > div {
        margin: 0 !important;
    }
    .canvas-container > div > div {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create container with border class
    with st.container():
        st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
        
        selected_points = st.plotly_chart(
            fig, 
            use_container_width=True, 
            key=canvas_key,  # Dynamic key forces refresh
            on_select="rerun",
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'autoScale2d'],
                'modeBarButtonsToAdd': ['orbitRotation', 'tableRotation'],
                'scrollZoom': True,
                'doubleClick': 'reset',
                'showTips': False
            }
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Handle equipment selection
    if selected_points and hasattr(selected_points, 'selection') and selected_points.selection.points:
        point = selected_points.selection.points[0]
        if hasattr(point, 'customdata') and point.customdata:
            equipment_id = point.customdata
            
            # Find selected equipment
            for placed_eq in canvas_manager.placed_equipment:
                if placed_eq.equipment.id == equipment_id:
                    st.session_state.selected_equipment_for_config = placed_eq
                    st.session_state.show_config_panel = True
                    st.rerun()
    
    # Add debug information when equipment is selected
    if st.session_state.get('selected_equipment_for_config'):
        selected_eq = st.session_state.selected_equipment_for_config
        st.sidebar.success(f"✅ Selected: {selected_eq.equipment.name}")
        st.sidebar.write(f"Position: ({selected_eq.x_position:.1f}, {selected_eq.y_position:.1f})")
        
        # Quick action buttons for selected equipment
        st.sidebar.markdown("**Quick Actions:**")
        remove_col, config_col = st.sidebar.columns(2)
        
        with remove_col:
            if st.button("🗑️ Remove", key="quick_remove", use_container_width=True, help="Remove equipment from canvas"):
                if 'canvas_manager' in st.session_state:
                    st.session_state.canvas_manager.remove_equipment(selected_eq.equipment.id)
                    st.sidebar.success("Equipment removed!")
                    st.session_state.selected_equipment_for_config = None
                    st.session_state.show_config_panel = False
                    st.session_state.project_saved = False
                    st.rerun()
        
        with config_col:
            if st.button("⚙️ Configure", key="quick_config", use_container_width=True, help="Open configuration panel"):
                st.session_state.show_config_panel = True
                st.rerun()
    else:
        st.sidebar.info("ℹ️ Click on equipment to select and remove it")

def get_equipment_3d_model(equipment, x_pos, y_pos):
    """Generate 3D model traces for equipment based on type"""
    traces = []
    
    # Base height and scaling factors
    base_height = 2.0
    
    if equipment.category == "Power Generation":
        if "Turbine" in equipment.name:
            # Gas Turbine - cylindrical with exhaust stack
            traces.extend(create_turbine_3d(x_pos, y_pos, equipment))
        elif "Diesel" in equipment.name:
            # Diesel Generator - rectangular housing
            traces.extend(create_generator_3d(x_pos, y_pos, equipment, "diesel"))
        else:
            # Gas Engine Generator
            traces.extend(create_generator_3d(x_pos, y_pos, equipment, "gas"))
            
    elif equipment.category == "Process Heating & Steam":
        if "Boiler" in equipment.name:
            # Boiler - vertical cylindrical
            traces.extend(create_boiler_3d(x_pos, y_pos, equipment))
        elif "Furnace" in equipment.name:
            # Furnace - box-shaped with stack
            traces.extend(create_furnace_3d(x_pos, y_pos, equipment))
        else:
            # Process Heater
            traces.extend(create_heater_3d(x_pos, y_pos, equipment))
            
    elif equipment.category == "Flaring & Destructor":
        if "Flare" in equipment.name:
            # Flare Stack - tall vertical tower
            traces.extend(create_flare_stack_3d(x_pos, y_pos, equipment))
        else:
            # Thermal Oxidizer/Incinerator
            traces.extend(create_oxidizer_3d(x_pos, y_pos, equipment))
            
    elif equipment.category == "Utility":
        if "Chiller" in equipment.name:
            # Chiller - horizontal rectangular
            traces.extend(create_chiller_3d(x_pos, y_pos, equipment))
        else:
            # Heater/Reboiler
            traces.extend(create_utility_3d(x_pos, y_pos, equipment))
            
    elif equipment.category == "Drivers & Machinery":
        if "Compressor" in equipment.name:
            # Compressor - cylindrical horizontal
            traces.extend(create_compressor_3d(x_pos, y_pos, equipment))
        else:
            # Pump - smaller cylindrical
            traces.extend(create_pump_3d(x_pos, y_pos, equipment))
            
    elif equipment.category == "Non-Combustion":
        if "Tank" in equipment.name:
            # Storage tanks - large cylinders
            traces.extend(create_tank_3d(x_pos, y_pos, equipment))
        elif "Pipeline" in equipment.name:
            # Pipeline - horizontal cylinder
            traces.extend(create_pipeline_3d(x_pos, y_pos, equipment))
        elif "Building" in equipment.name:
            # Control building - rectangular structure
            traces.extend(create_building_3d(x_pos, y_pos, equipment))
        elif "Fence" in equipment.name:
            # Fence - linear structure
            traces.extend(create_fence_3d(x_pos, y_pos, equipment))
        else:
            # Entrance - gate structure
            traces.extend(create_entrance_3d(x_pos, y_pos, equipment))
    
    return traces

def create_turbine_3d(x, y, equipment):
    """Create 3D gas turbine model"""
    traces = []
    
    # Scale based on power rating
    scale = min(3.0, max(1.0, equipment.power_rate_kw / 2000))
    width = 8 * scale
    length = 12 * scale
    height = 6 * scale
    
    # Main turbine housing (cylinder)
    theta = np.linspace(0, 2*np.pi, 20)
    z_cyl = np.linspace(2, 2 + height, 10)
    theta_mesh, z_mesh = np.meshgrid(theta, z_cyl)
    x_cyl = x + (width/2) * np.cos(theta_mesh)
    y_cyl = y + (width/2) * np.sin(theta_mesh)
    
    traces.append(go.Surface(
        x=x_cyl, y=y_cyl, z=z_mesh,
        colorscale=[[0, '#4a5568'], [1, '#2d3748']],
        showscale=False,
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Power: {equipment.power_rate_kw}kW<br>Fuel: {equipment.fuel_type}<extra></extra>"
    ))
    
    # Exhaust stack
    stack_height = height + 15
    z_stack = np.linspace(2 + height, 2 + stack_height, 15)
    theta_stack, z_stack_mesh = np.meshgrid(theta, z_stack)
    x_stack = x + 2 + (width/6) * np.cos(theta_stack)
    y_stack = y + 2 + (width/6) * np.sin(theta_stack)
    
    traces.append(go.Surface(
        x=x_stack, y=y_stack, z=z_stack_mesh,
        colorscale=[[0, '#e2e8f0'], [1, '#cbd5e0']],
        showscale=False,
        showlegend=False,
        hoverinfo='skip'
    ))
    
    return traces

def create_generator_3d(x, y, equipment, gen_type):
    """Create 3D generator model"""
    traces = []
    
    # Scale based on power rating
    scale = min(2.5, max(0.8, equipment.power_rate_kw / 1500))
    width = 6 * scale
    length = 8 * scale
    height = 4 * scale
    
    # Generator housing (rectangular)
    x_box = [x, x+length, x+length, x, x, x, x+length, x+length, x, x, x, x+length, x+length, x+length, x+length, x]
    y_box = [y, y, y+width, y+width, y, y, y, y+width, y+width, y+width, y, y, y+width, y+width, y, y]
    z_box = [0, 0, 0, 0, 0, height, height, height, height, 0, height, height, height, 0, 0, height]
    
    traces.append(go.Scatter3d(
        x=x_box, y=y_box, z=z_box,
        mode='lines',
        line=dict(color='#2d3748', width=3),
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Type: {gen_type.title()}<br>Power: {equipment.power_rate_kw}kW<br>Fuel: {equipment.fuel_type}<extra></extra>"
    ))
    
    # Add exhaust pipe for diesel
    if gen_type == "diesel":
        pipe_x = [x + length/2, x + length/2]
        pipe_y = [y + width/2, y + width/2]
        pipe_z = [height, height + 8]
        
        traces.append(go.Scatter3d(
            x=pipe_x, y=pipe_y, z=pipe_z,
            mode='lines',
            line=dict(color='#4a5568', width=5),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    return traces

def create_boiler_3d(x, y, equipment):
    """Create 3D boiler model"""
    traces = []
    
    scale = min(2.0, max(1.0, equipment.power_rate_kw / 2000))
    radius = 4 * scale
    height = 12 * scale
    
    # Vertical cylindrical boiler
    theta = np.linspace(0, 2*np.pi, 20)
    z_cyl = np.linspace(0, height, 15)
    theta_mesh, z_mesh = np.meshgrid(theta, z_cyl)
    x_cyl = x + radius * np.cos(theta_mesh)
    y_cyl = y + radius * np.sin(theta_mesh)
    
    traces.append(go.Surface(
        x=x_cyl, y=y_cyl, z=z_mesh,
        colorscale=[[0, '#4a5568'], [1, '#2d3748']],
        showscale=False,
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Power: {equipment.power_rate_kw}kW<br>Fuel: {equipment.fuel_type}<extra></extra>"
    ))
    
    return traces

def create_furnace_3d(x, y, equipment):
    """Create 3D furnace model"""
    traces = []
    
    scale = min(2.0, max(1.0, equipment.power_rate_kw / 2500))
    width = 8 * scale
    length = 10 * scale
    height = 8 * scale
    
    # Furnace body
    x_box = [x, x+length, x+length, x, x, x, x+length, x+length, x, x, x, x+length, x+length, x+length, x+length, x]
    y_box = [y, y, y+width, y+width, y, y, y, y+width, y+width, y+width, y, y, y+width, y+width, y, y]
    z_box = [0, 0, 0, 0, 0, height, height, height, height, 0, height, height, height, 0, 0, height]
    
    traces.append(go.Scatter3d(
        x=x_box, y=y_box, z=z_box,
        mode='lines',
        line=dict(color='#744210', width=3),
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Power: {equipment.power_rate_kw}kW<br>Fuel: {equipment.fuel_type}<extra></extra>"
    ))
    
    # Stack
    stack_x = [x + length/2, x + length/2]
    stack_y = [y + width/2, y + width/2]
    stack_z = [height, height + 15]
    
    traces.append(go.Scatter3d(
        x=stack_x, y=stack_y, z=stack_z,
        mode='lines',
        line=dict(color='#4a5568', width=6),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    return traces

def create_heater_3d(x, y, equipment):
    """Create 3D heater model"""
    traces = []
    
    scale = min(1.5, max(0.8, equipment.power_rate_kw / 1000))
    radius = 3 * scale
    length = 8 * scale
    
    # Horizontal cylindrical heater
    theta = np.linspace(0, 2*np.pi, 16)
    x_cyl = np.linspace(x, x + length, 10)
    theta_mesh, x_mesh = np.meshgrid(theta, x_cyl)
    y_cyl = y + radius * np.cos(theta_mesh)
    z_cyl = 2 + radius * np.sin(theta_mesh)
    
    traces.append(go.Surface(
        x=x_mesh, y=y_cyl, z=z_cyl,
        colorscale=[[0, '#e53e3e'], [1, '#c53030']],
        showscale=False,
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Power: {equipment.power_rate_kw}kW<br>Fuel: {equipment.fuel_type}<extra></extra>"
    ))
    
    return traces

def create_flare_stack_3d(x, y, equipment):
    """Create 3D flare stack model"""
    traces = []
    
    # Tall vertical structure
    height = 35
    radius = 0.8
    
    # Stack tower
    theta = np.linspace(0, 2*np.pi, 12)
    z_stack = np.linspace(0, height, 20)
    theta_mesh, z_mesh = np.meshgrid(theta, z_stack)
    x_stack = x + radius * np.cos(theta_mesh)
    y_stack = y + radius * np.sin(theta_mesh)
    
    traces.append(go.Surface(
        x=x_stack, y=y_stack, z=z_mesh,
        colorscale=[[0, '#4a5568'], [1, '#2d3748']],
        showscale=False,
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Height: {height}m<br>Fuel: {equipment.fuel_type}<extra></extra>"
    ))
    
    # Flare tip (flame effect)
    flame_x = [x, x]
    flame_y = [y, y]
    flame_z = [height, height + 5]
    
    traces.append(go.Scatter3d(
        x=flame_x, y=flame_y, z=flame_z,
        mode='markers',
        marker=dict(size=8, color='#ff6b35'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    return traces

def create_oxidizer_3d(x, y, equipment):
    """Create 3D thermal oxidizer model"""
    traces = []
    
    scale = min(2.0, max(1.0, equipment.power_rate_kw / 1500))
    width = 6 * scale
    height = 8 * scale
    
    # Cylindrical oxidizer
    theta = np.linspace(0, 2*np.pi, 16)
    z_cyl = np.linspace(0, height, 10)
    theta_mesh, z_mesh = np.meshgrid(theta, z_cyl)
    x_cyl = x + width/2 * np.cos(theta_mesh)
    y_cyl = y + width/2 * np.sin(theta_mesh)
    
    traces.append(go.Surface(
        x=x_cyl, y=y_cyl, z=z_mesh,
        colorscale=[[0, '#e53e3e'], [1, '#c53030']],
        showscale=False,
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Power: {equipment.power_rate_kw}kW<br>Fuel: {equipment.fuel_type}<extra></extra>"
    ))
    
    return traces

def create_chiller_3d(x, y, equipment):
    """Create 3D chiller model"""
    traces = []
    
    scale = min(2.0, max(1.0, equipment.power_rate_kw / 1000))
    width = 8 * scale
    length = 12 * scale
    height = 6 * scale
    
    # Chiller unit (rectangular)
    x_box = [x, x+length, x+length, x, x, x, x+length, x+length, x, x, x, x+length, x+length, x+length, x+length, x]
    y_box = [y, y, y+width, y+width, y, y, y, y+width, y+width, y+width, y, y, y+width, y+width, y, y]
    z_box = [0, 0, 0, 0, 0, height, height, height, height, 0, height, height, height, 0, 0, height]
    
    traces.append(go.Scatter3d(
        x=x_box, y=y_box, z=z_box,
        mode='lines',
        line=dict(color='#3182ce', width=3),
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Power: {equipment.power_rate_kw}kW<br>Type: Cooling System<extra></extra>"
    ))
    
    return traces

def create_utility_3d(x, y, equipment):
    """Create 3D utility equipment model"""
    traces = []
    
    scale = min(1.5, max(0.8, equipment.power_rate_kw / 800))
    width = 4 * scale
    length = 6 * scale
    height = 4 * scale
    
    # Utility box
    x_box = [x, x+length, x+length, x, x, x, x+length, x+length, x, x, x, x+length, x+length, x+length, x+length, x]
    y_box = [y, y, y+width, y+width, y, y, y, y+width, y+width, y+width, y, y, y+width, y+width, y, y]
    z_box = [0, 0, 0, 0, 0, height, height, height, height, 0, height, height, height, 0, 0, height]
    
    traces.append(go.Scatter3d(
        x=x_box, y=y_box, z=z_box,
        mode='lines',
        line=dict(color='#38a169', width=3),
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Power: {equipment.power_rate_kw}kW<br>Fuel: {equipment.fuel_type}<extra></extra>"
    ))
    
    return traces

def create_compressor_3d(x, y, equipment):
    """Create 3D compressor model"""
    traces = []
    
    scale = min(2.0, max(1.0, equipment.power_rate_kw / 2000))
    radius = 3 * scale
    length = 10 * scale
    
    # Horizontal cylindrical compressor
    theta = np.linspace(0, 2*np.pi, 16)
    x_cyl = np.linspace(x, x + length, 10)
    theta_mesh, x_mesh = np.meshgrid(theta, x_cyl)
    y_cyl = y + radius * np.cos(theta_mesh)
    z_cyl = 2 + radius * np.sin(theta_mesh)
    
    traces.append(go.Surface(
        x=x_mesh, y=y_cyl, z=z_cyl,
        colorscale=[[0, '#805ad5'], [1, '#6b46c1']],
        showscale=False,
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Power: {equipment.power_rate_kw}kW<br>Fuel: {equipment.fuel_type}<extra></extra>"
    ))
    
    return traces

def create_pump_3d(x, y, equipment):
    """Create 3D pump model"""
    traces = []
    
    scale = min(1.5, max(0.6, equipment.power_rate_kw / 500))
    radius = 2 * scale
    height = 3 * scale
    
    # Pump housing (small cylinder)
    theta = np.linspace(0, 2*np.pi, 12)
    z_cyl = np.linspace(0, height, 8)
    theta_mesh, z_mesh = np.meshgrid(theta, z_cyl)
    x_cyl = x + radius * np.cos(theta_mesh)
    y_cyl = y + radius * np.sin(theta_mesh)
    
    traces.append(go.Surface(
        x=x_cyl, y=y_cyl, z=z_mesh,
        colorscale=[[0, '#3182ce'], [1, '#2c5aa0']],
        showscale=False,
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Power: {equipment.power_rate_kw}kW<br>Fuel: {equipment.fuel_type}<extra></extra>"
    ))
    
    return traces

def create_tank_3d(x, y, equipment):
    """Create 3D storage tank model"""
    traces = []
    
    # Large cylindrical tank
    radius = 8
    height = 15
    
    if "Crude" in equipment.name:
        radius = 12
        height = 10
    
    theta = np.linspace(0, 2*np.pi, 20)
    z_cyl = np.linspace(0, height, 15)
    theta_mesh, z_mesh = np.meshgrid(theta, z_cyl)
    x_cyl = x + radius * np.cos(theta_mesh)
    y_cyl = y + radius * np.sin(theta_mesh)
    
    color = '#e2e8f0' if "Storage" in equipment.name else '#805ad5'
    
    traces.append(go.Surface(
        x=x_cyl, y=y_cyl, z=z_mesh,
        colorscale=[[0, color], [1, '#a0aec0']],
        showscale=False,
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Radius: {radius}m<br>Height: {height}m<extra></extra>"
    ))
    
    return traces

def create_pipeline_3d(x, y, equipment):
    """Create 3D pipeline model - centered at coordinates (x,y)"""
    traces = []
    
    # Horizontal pipe centered at the given coordinates
    length = 20
    radius = 0.5
    
    # Create pipeline running along X-axis, centered at (x,y)
    # X coordinates: from (x-10) to (x+10)
    x_start = x - length/2
    x_end = x + length/2
    x_pipe = np.linspace(x_start, x_end, 15)
    
    # Create circular cross-section at each point
    theta = np.linspace(0, 2*np.pi, 16)
    
    # Create meshgrid for surface
    x_mesh = np.repeat(x_pipe[:, np.newaxis], len(theta), axis=1)
    theta_mesh = np.repeat(theta[np.newaxis, :], len(x_pipe), axis=0)
    
    # Pipeline centered at Y coordinate
    y_mesh = y + radius * np.cos(theta_mesh)
    z_mesh = 1 + radius * np.sin(theta_mesh)
    
    traces.append(go.Surface(
        x=x_mesh, y=y_mesh, z=z_mesh,
        colorscale=[[0, '#4a5568'], [1, '#2d3748']],
        showscale=False,
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Length: {length}m<br>Center: ({x:.1f}m, {y:.1f}m)<br>X Range: {x_start:.1f} to {x_end:.1f}<extra></extra>"
    ))
    
    # Add center marker for debugging
    traces.append(go.Scatter3d(
        x=[x], y=[y], z=[2],
        mode='markers',
        marker=dict(size=8, color='red', symbol='cross'),
        name=f"{equipment.name} Center",
        hovertemplate=f"<b>Pipeline Center</b><br>X: {x:.1f}m<br>Y: {y:.1f}m<extra></extra>",
        showlegend=False
    ))
    
    return traces

def create_building_3d(x, y, equipment):
    """Create 3D control building model"""
    traces = []
    
    width = 8
    length = 12
    height = 6
    
    # Building structure - centered at given coordinates
    x_offset = length / 2
    y_offset = width / 2
    x_box = [x-x_offset, x+x_offset, x+x_offset, x-x_offset, x-x_offset, x-x_offset, x+x_offset, x+x_offset, x-x_offset, x-x_offset, x-x_offset, x+x_offset, x+x_offset, x+x_offset, x+x_offset, x-x_offset]
    y_box = [y-y_offset, y-y_offset, y+y_offset, y+y_offset, y-y_offset, y-y_offset, y-y_offset, y+y_offset, y+y_offset, y+y_offset, y-y_offset, y-y_offset, y+y_offset, y+y_offset, y-y_offset, y-y_offset]
    z_box = [0, 0, 0, 0, 0, height, height, height, height, 0, height, height, height, 0, 0, height]
    
    traces.append(go.Scatter3d(
        x=x_box, y=y_box, z=z_box,
        mode='lines',
        line=dict(color='#4a5568', width=3),
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Size: {length}m × {width}m × {height}m<extra></extra>"
    ))
    
    return traces

def create_fence_3d(x, y, equipment):
    """Create 3D fence model"""
    traces = []
    
    length = 15
    height = 3
    
    # Fence line - centered at given coordinates
    fence_x = [x - length/2, x + length/2]
    fence_y = [y, y]
    fence_z = [0, 0]
    
    traces.append(go.Scatter3d(
        x=fence_x, y=fence_y, z=fence_z,
        mode='lines',
        line=dict(color='#4a5568', width=4),
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Length: {length}m<br>Height: {height}m<extra></extra>"
    ))
    
    # Fence posts - centered along the fence
    for i in range(0, length + 1, 3):
        post_x = [x - length/2 + i, x - length/2 + i]
        post_y = [y, y]
        post_z = [0, height]
        
        traces.append(go.Scatter3d(
            x=post_x, y=post_y, z=post_z,
            mode='lines',
            line=dict(color='#4a5568', width=3),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    return traces

def create_entrance_3d(x, y, equipment):
    """Create 3D entrance gate model"""
    traces = []
    
    width = 8
    height = 4
    
    # Gate posts - centered at given coordinates
    post1_x = [x - width/2, x - width/2]
    post1_y = [y, y]
    post1_z = [0, height]
    
    post2_x = [x + width/2, x + width/2]
    post2_y = [y, y]
    post2_z = [0, height]
    
    traces.append(go.Scatter3d(
        x=post1_x, y=post1_y, z=post1_z,
        mode='lines',
        line=dict(color='#4a5568', width=5),
        name=equipment.name,
        hovertemplate=f"<b>{equipment.name}</b><br>Width: {width}m<br>Height: {height}m<extra></extra>"
    ))
    
    traces.append(go.Scatter3d(
        x=post2_x, y=post2_y, z=post2_z,
        mode='lines',
        line=dict(color='#4a5568', width=5),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Gate bar - centered between posts
    gate_x = [x - width/2, x + width/2]
    gate_y = [y, y]
    gate_z = [height/2, height/2]
    
    traces.append(go.Scatter3d(
        x=gate_x, y=gate_y, z=gate_z,
        mode='lines',
        line=dict(color='#e2e8f0', width=3),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    return traces

def save_current_project():
    """Save the current project state"""
    try:
        if not st.session_state.current_project:
            return False
        
        project_name = st.session_state.current_project['name']
        project_file = f"projects/{project_name.lower().replace(' ', '_')}.json"
        
        # Update project with current canvas state
        if 'canvas_manager' in st.session_state:
            canvas_manager = st.session_state.canvas_manager
            
            # Save equipment data
            equipment_data = []
            for placed_eq in canvas_manager.placed_equipment:
                equipment_data.append({
                    'equipment': placed_eq.equipment.to_dict(),
                    'x_position': placed_eq.x_position,
                    'y_position': placed_eq.y_position
                })
            
            # Calculate and save summary data including facilities efficiency
            summary = canvas_manager.get_equipment_summary()
            
            st.session_state.current_project['equipment'] = equipment_data
            st.session_state.current_project['summary'] = summary  # Save the calculated summary
            st.session_state.current_project['last_modified'] = datetime.now().isoformat()
        
        # Save to file
        with open(project_file, 'w') as f:
            json.dump(st.session_state.current_project, f, indent=2)
        
        st.session_state.project_saved = True
        return True
        
    except Exception as e:
        st.error(f"Error saving project: {str(e)}")
        return False

def auto_arrange_equipment():
    """Automatically arrange equipment in a grid layout"""
    try:
        if 'canvas_manager' not in st.session_state:
            return False
        
        canvas_manager = st.session_state.canvas_manager
        if not canvas_manager.placed_equipment:
            return False
        
        # Save current state before making changes
        save_canvas_state("Auto Arrange Equipment")
        
        canvas_bounds = canvas_manager.get_canvas_bounds()
        equipment_count = len(canvas_manager.placed_equipment)
        
        # Calculate grid dimensions
        cols = min(5, equipment_count)  # Max 5 columns
        rows = (equipment_count + cols - 1) // cols  # Ceiling division
        
        # Calculate spacing
        x_spacing = canvas_bounds[0] / (cols + 1)
        y_spacing = canvas_bounds[1] / (rows + 1)
        
        # Rearrange equipment
        for i, placed_eq in enumerate(canvas_manager.placed_equipment):
            row = i // cols
            col = i % cols
            
            new_x = x_spacing * (col + 1)
            new_y = y_spacing * (row + 1)
            
            placed_eq.x_position = new_x
            placed_eq.y_position = new_y
        
        st.session_state.project_saved = False
        return True
        
    except Exception as e:
        st.error(f"Error auto-arranging equipment: {str(e)}")
        return False

def save_canvas_state(action_description: str = "Canvas Action"):
    """Save current canvas state to history for undo/redo functionality"""
    try:
        if 'canvas_manager' not in st.session_state:
            return
        
        canvas_manager = st.session_state.canvas_manager
        
        # Create a deep copy of current equipment state
        current_state = {
            "action": action_description,
            "timestamp": datetime.now().isoformat(),
            "equipment": []
        }
        
        for placed_eq in canvas_manager.placed_equipment:
            equipment_state = {
                "equipment_dict": placed_eq.equipment.to_dict(),
                "x_position": placed_eq.x_position,
                "y_position": placed_eq.y_position
            }
            current_state["equipment"].append(equipment_state)
        
        # Add to history
        history = st.session_state.canvas_history
        current_index = st.session_state.canvas_history_index
        
        # Remove any redo history if we're not at the end
        if current_index < len(history) - 1:
            st.session_state.canvas_history = history[:current_index + 1]
        
        # Add new state
        st.session_state.canvas_history.append(current_state)
        st.session_state.canvas_history_index = len(st.session_state.canvas_history) - 1
        
        # Limit history size to prevent memory issues
        max_history = 20
        if len(st.session_state.canvas_history) > max_history:
            st.session_state.canvas_history = st.session_state.canvas_history[-max_history:]
            st.session_state.canvas_history_index = len(st.session_state.canvas_history) - 1
            
    except Exception as e:
        st.error(f"Error saving canvas state: {str(e)}")

def restore_canvas_state(state_data: Dict):
    """Restore canvas to a specific state"""
    try:
        if 'canvas_manager' not in st.session_state:
            return False
        
        canvas_manager = st.session_state.canvas_manager
        
        # Clear current equipment
        canvas_manager.placed_equipment = []
        
        # Restore equipment from state
        for eq_state in state_data["equipment"]:
            # Recreate equipment from dictionary
            equipment = EquipmentModel.from_dict(eq_state["equipment_dict"])
            
            # Create placed equipment
            from src.models.placed_equipment import PlacedEquipment
            placed_eq = PlacedEquipment(
                equipment=equipment,
                x_position=eq_state["x_position"],
                y_position=eq_state["y_position"]
            )
            
            canvas_manager.placed_equipment.append(placed_eq)
        
        return True
        
    except Exception as e:
        st.error(f"Error restoring canvas state: {str(e)}")
        return False

def undo_canvas_action():
    """Undo the last canvas action"""
    try:
        history = st.session_state.canvas_history
        current_index = st.session_state.canvas_history_index
        
        if current_index < 0 or len(history) == 0:
            return False
        
        # Move to previous state
        if current_index > 0:
            previous_state = history[current_index - 1]
            if restore_canvas_state(previous_state):
                st.session_state.canvas_history_index = current_index - 1
                st.session_state.project_saved = False
                return True
        else:
            # If we're at the first state, clear everything
            if 'canvas_manager' in st.session_state:
                st.session_state.canvas_manager.placed_equipment = []
                st.session_state.canvas_history_index = -1
                st.session_state.project_saved = False
                return True
        
        return False
        
    except Exception as e:
        st.error(f"Error during undo: {str(e)}")
        return False

def redo_canvas_action():
    """Redo the last undone canvas action"""
    try:
        history = st.session_state.canvas_history
        current_index = st.session_state.canvas_history_index
        
        if current_index >= len(history) - 1:
            return False
        
        # Move to next state
        next_state = history[current_index + 1]
        if restore_canvas_state(next_state):
            st.session_state.canvas_history_index = current_index + 1
            st.session_state.project_saved = False
            return True
        
        return False
    except Exception as e:
        st.error(f"Error during redo: {str(e)}")
        return False

def render_equipment_summary_table():
    """Render professional equipment summary table with production metrics and CO2 emissions"""
    canvas_manager = st.session_state.get('canvas_manager')
    
    # Time period selector - always show
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        time_period = st.selectbox(
            "Reporting Period",
            ["Day", "Month", "Year"],
            index=0,
            key="equipment_table_period"
        )
    
    # Calculate time multiplier
    time_multipliers = {
        "Day": 1,
        "Month": 30.44,  # Average days per month
        "Year": 365.25   # Accounting for leap years
    }
    multiplier = time_multipliers[time_period]
    
    # Check if we have equipment
    has_equipment = canvas_manager and canvas_manager.placed_equipment
    
    if has_equipment:
        # Prepare table data
        table_data = []
        
        for placed_eq in canvas_manager.placed_equipment:
            equipment = placed_eq.equipment
            
            # Calculate production metrics
            crude_processing = equipment.calculate_crude_processing_capacity()
            power_generation = equipment.calculate_power_production()
            co2_emission_daily = equipment.calculate_co2_emission()  # Already daily kg CO2
            
            # Apply time period multiplier and determine units
            crude_processing_period = crude_processing * multiplier if crude_processing > 0 else None
            
            # Power generation: kW for Day, kWh for Month/Year
            if time_period == "Day":
                power_generation_period = power_generation if power_generation > 0 else None  # kW instantaneous
                power_unit = "kW"
            else:
                # For month/year, convert to energy (kWh) = power (kW) × hours in period × capacity factor
                if power_generation > 0:
                    hours_in_period = 24 * multiplier  # 24 hours/day × days in period
                    capacity_factor = 0.85  # Typical capacity factor for continuous operation
                    power_generation_period = power_generation * hours_in_period * capacity_factor
                    power_unit = "kWh"
                else:
                    power_generation_period = None
                    power_unit = "kWh"
            
            co2_emission_period = co2_emission_daily * multiplier if co2_emission_daily > 0 else None  # Scale daily CO2 to period
            
            # Determine time period abbreviations
            period_abbrev = {"Day": "d", "Month": "m", "Year": "y"}[time_period]
            
            # Format values for display
            crude_display = f"{crude_processing_period:,.0f}" if crude_processing_period else "N/A"
            power_display = f"{power_generation_period:,.0f}" if power_generation_period else "N/A"
            co2_display = f"{co2_emission_period:,.0f}" if co2_emission_period else "N/A"
            
            table_data.append({
                "Equipment": equipment.name,
                "Category": equipment.category,
                "Fuel": equipment.fuel_type if equipment.fuel_type != "None" else "N/A",
                f"Crude (bbl/{period_abbrev})": crude_display,
                f"Power ({power_unit})": power_display,
                f"CO2 (kg/{period_abbrev})": co2_display
            })
    else:
        table_data = []
    
    # Always show table header and content
    period_abbrev = {"Day": "d", "Month": "m", "Year": "y"}[time_period]
    power_unit = "kW" if time_period == "Day" else "kWh"
    
    # Simple table header
    st.markdown(f"""
    <div style="margin-top: 1.5rem; margin-bottom: 0.5rem;">
        <h4 style="color: #374151; margin: 0; font-size: 1.0rem; font-weight: 500;">
            Equipment Summary - {time_period}ly Production & Emissions
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    if table_data:
        # Create DataFrame
        import pandas as pd
        df = pd.DataFrame(table_data)
        
        # Get dynamic column names for configuration
        period_abbrev = {"Day": "d", "Month": "m", "Year": "y"}[time_period]
        power_unit = "kW" if time_period == "Day" else "kWh"
        
        # Simple table header
        st.markdown(f"""
        <div style="margin-top: 1.5rem; margin-bottom: 0.5rem;">
            <h4 style="color: #374151; margin: 0; font-size: 1.0rem; font-weight: 500;">
                Equipment Summary - {time_period}ly Production & Emissions
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Display simple table using Streamlit's native dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Equipment": st.column_config.TextColumn("Equipment", width="small"),
                "Category": st.column_config.TextColumn("Category", width="small"),
                "Fuel": st.column_config.TextColumn("Fuel", width="small"),
                f"Crude (bbl/{period_abbrev})": st.column_config.TextColumn(
                    f"Crude (bbl/{period_abbrev})", width="small"
                ),
                f"Power ({power_unit})": st.column_config.TextColumn(f"Power ({power_unit})", width="small"),
                f"CO2 (kg/{period_abbrev})": st.column_config.TextColumn(
                    f"CO2 (kg/{period_abbrev})", width="small"
                )
            }
        )
    else:
        # Show empty state message
        st.info("No equipment placed yet. Add equipment from the library to see summary data.")
        
    # Summary statistics - always show
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    if has_equipment:
        with col1:
            total_crude = sum(equipment.calculate_crude_processing_capacity() for equipment in 
                            [eq.equipment for eq in canvas_manager.placed_equipment]) * multiplier
            st.metric(
                f"Total Crude Processing ({time_period.lower()})",
                f"{total_crude:,.0f} bbl" if total_crude > 0 else "0 bbl"
            )
        
        with col2:
            total_power_kw = sum(equipment.calculate_power_production() for equipment in 
                               [eq.equipment for eq in canvas_manager.placed_equipment])
            
            if time_period == "Day":
                power_metric = total_power_kw
                power_label = "Total Power Generation"
                power_unit_summary = "kW"
            else:
                # For month/year, convert to energy (kWh)
                hours_in_period = 24 * multiplier
                capacity_factor = 0.85
                power_metric = total_power_kw * hours_in_period * capacity_factor
                power_label = "Total Energy Generation"
                power_unit_summary = "kWh"
                
            st.metric(
                power_label,
                f"{power_metric:,.0f} {power_unit_summary}" if power_metric > 0 else f"0 {power_unit_summary}"
            )
        
        with col3:
            total_co2_daily = sum(equipment.calculate_co2_emission() for equipment in 
                                [eq.equipment for eq in canvas_manager.placed_equipment])
            total_co2_period = total_co2_daily * multiplier  # Scale daily CO2 to selected period
            st.metric(
                f"Total CO2 Emissions ({time_period.lower()})",
                f"{total_co2_period:,.0f} kg" if total_co2_period > 0 else "0 kg"
            )
    else:
        # Show zero metrics when no equipment
        with col1:
            st.metric(f"Total Crude Processing ({time_period.lower()})", "0 bbl")
        with col2:
            power_unit_summary = "kW" if time_period == "Day" else "kWh"
            power_label = "Total Power Generation" if time_period == "Day" else "Total Energy Generation"
            st.metric(power_label, f"0 {power_unit_summary}")
        with col3:
            st.metric(f"Total CO2 Emissions ({time_period.lower()})", "0 kg")
        
    # Facilities Efficiency Section - always show
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-bottom: 0.5rem;">
        <h4 style="color: #374151; margin: 0; font-size: 1.0rem; font-weight: 500;">
            Facilities Efficiency (Annual Basis)
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    eff_col1, eff_col2 = st.columns(2)
    
    if has_equipment:
        with eff_col1:
            # Calculate annual values for efficiency metrics
            total_crude_annual = sum(equipment.calculate_crude_processing_capacity() for equipment in 
                                   [eq.equipment for eq in canvas_manager.placed_equipment]) * 365.25  # Annual crude processing
            total_co2_daily = sum(equipment.calculate_co2_emission() for equipment in 
                                [eq.equipment for eq in canvas_manager.placed_equipment])
            total_co2_annual = total_co2_daily * 365.25  # Annual CO2 emissions
            
            # CO2 intensity per crude oil processed (t CO₂/tonne crude)
            if total_crude_annual > 0:
                # Convert: bbl to tonnes (1 bbl crude ≈ 0.136 tonnes), kg CO2 to tonnes CO2
                crude_annual_tonnes = total_crude_annual * 0.136  # Convert bbl to tonnes
                co2_annual_tonnes = total_co2_annual / 1000  # Convert kg to tonnes
                co2_per_crude = co2_annual_tonnes / crude_annual_tonnes  # t CO₂/tonne crude
                co2_crude_display = f"{co2_per_crude:.3f}"
            else:
                co2_crude_display = "N/A"
            
            st.metric(
                "CO₂ Intensity (Crude)",
                f"{co2_crude_display} t CO₂/tonne crude" if co2_crude_display != "N/A" else "N/A"
            )
        
        with eff_col2:
            # Calculate annual energy generation for efficiency metric
            total_energy_annual_kwh = 0
            for equipment in [eq.equipment for eq in canvas_manager.placed_equipment]:
                power_kw = equipment.calculate_power_production()
                if power_kw > 0:
                    # Use actual operation hours from equipment configuration
                    annual_operation_hours = equipment.operation_time_hours
                    capacity_factor = 0.85  # Typical capacity factor
                    energy_kwh = power_kw * annual_operation_hours * capacity_factor
                    total_energy_annual_kwh += energy_kwh
            
            # CO2 intensity per energy generated (kg CO₂/kWh)
            if total_energy_annual_kwh > 0:
                co2_per_kwh = total_co2_annual / total_energy_annual_kwh  # kg CO₂/kWh
                co2_energy_display = f"{co2_per_kwh:.3f}"
            else:
                co2_energy_display = "N/A"
            
            st.metric(
                "CO₂ Intensity (Energy)",
                f"{co2_energy_display} kg CO₂/kWh" if co2_energy_display != "N/A" else "N/A"
            )
    else:
        # Show N/A metrics when no equipment
        with eff_col1:
            st.metric("CO₂ Intensity (Crude)", "N/A")
        with eff_col2:
            st.metric("CO₂ Intensity (Energy)", "N/A")