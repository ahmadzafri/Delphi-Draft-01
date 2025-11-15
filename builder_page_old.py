import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from src.models.equipment_model import EQUIPMENT_CATEGORIES, create_equipment_defaults, EquipmentModel
from src.models.placed_equipment import PlacedEquipment, CanvasManager
from src.models.draggable_canvas import DraggableCanvasManager, create_enhanced_canvas_interface, display_selected_equipment_info

def initialize_builder_session():
    """Initialize session state for builder page"""
    if 'enhanced_canvas_manager' not in st.session_state:
        if st.session_state.current_project:
            width = st.session_state.current_project.get('canvas_width_m', 200)
            height = st.session_state.current_project.get('canvas_height_m', 200)
            st.session_state.enhanced_canvas_manager = DraggableCanvasManager(width, height)
        else:
            st.session_state.enhanced_canvas_manager = DraggableCanvasManager(200, 200)
    
    # Keep the legacy canvas manager for compatibility
    if 'canvas_manager' not in st.session_state:
        if st.session_state.current_project:
            width = st.session_state.current_project.get('canvas_width_m', 200)
            height = st.session_state.current_project.get('canvas_height_m', 200)
            st.session_state.canvas_manager = CanvasManager(width, height)
    
    if 'equipment_library_open' not in st.session_state:
        st.session_state.equipment_library_open = False
    
    if 'selected_equipment_for_config' not in st.session_state:
        st.session_state.selected_equipment_for_config = None
    
    if 'show_config_panel' not in st.session_state:
        st.session_state.show_config_panel = False

def equipment_library_panel():
    """Professional equipment library panel with enhanced styling"""
    
    st.markdown("""
    <div class="section-container">
        <div class="section-title">Equipment Library</div>
        <p style="color: #718096; margin-bottom: 1.5rem;">Select equipment to add to your facility layout</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Category selection with enhanced design
    equipment_defaults = create_equipment_defaults()
    
    for category, equipment_list in EQUIPMENT_CATEGORIES.items():
        with st.expander(f"📂 {category}", expanded=False):
            for equipment_name in equipment_list:
                equipment = equipment_defaults[equipment_name]
                
                # Professional equipment card display
                st.markdown(f"""
                <div class="equipment-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #2c5530;">{equipment.icon} {equipment_name}</h4>
                            <p style="margin: 0.3rem 0 0 0; color: #6c757d; font-size: 0.9rem;">
                                {f"{equipment.power_rate_kw}kW • {equipment.fuel_type}" if equipment.has_combustion and equipment.requires_power_config else "Non-combustion equipment"}
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"➕ Add {equipment_name}", key=f"add_{equipment_name}", 
                           help=f"Add {equipment_name} to facility layout", use_container_width=True):
                    add_equipment_to_canvas(equipment)
                    st.success(f"✅ {equipment_name} added to facility!")
                    st.rerun()

def add_equipment_to_canvas(equipment_template: EquipmentModel):
    """Add equipment to both canvas managers"""
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
            description=equipment_template.description,
            icon=equipment_template.icon
        )
        
        # Add to canvas with smart positioning
        canvas_bounds = canvas_manager.get_canvas_bounds()
        
        # Calculate next position in a grid layout
        existing_count = len(canvas_manager.placed_equipment)
        grid_cols = int(canvas_bounds[0] // 50)  # 50m spacing
        if grid_cols < 1:
            grid_cols = 1
        
        col = existing_count % grid_cols
        row = existing_count // grid_cols
        
        x_pos = 25 + (col * 50)  # Start 25m from edge with 50m spacing
        y_pos = 25 + (row * 50)
        
        # Ensure within bounds
        x_pos = min(x_pos, canvas_bounds[0] - 25)
        y_pos = min(y_pos, canvas_bounds[1] - 25)
        
        placed_equipment = canvas_manager.add_equipment(new_equipment, x_pos, y_pos)
        
        # Also add to legacy canvas manager for compatibility
        if 'canvas_manager' in st.session_state:
            st.session_state.canvas_manager.add_equipment(new_equipment, x_pos, y_pos)
        
        st.success(f"✅ {equipment_template.icon} {equipment_template.name} added to canvas at ({x_pos:.0f}m, {y_pos:.0f}m)")
        
        # Mark project as unsaved
        st.session_state.project_saved = False

def render_canvas():
    """Render the main canvas with equipment"""
    if 'canvas_manager' not in st.session_state:
        st.error("Canvas not initialized")
        return
    
    canvas_manager = st.session_state.canvas_manager
    canvas_bounds = canvas_manager.get_canvas_bounds()
    
    # Create plotly figure for canvas
    fig = go.Figure()
    
    # Add grid
    grid_size = canvas_manager.grid_size
    
    # Vertical grid lines
    for x in range(0, int(canvas_bounds[0]) + 1, int(grid_size)):
        fig.add_shape(
            type="line",
            x0=x, y0=0,
            x1=x, y1=canvas_bounds[1],
            line=dict(color="lightgray", width=0.5, dash="dot")
        )
    
    # Horizontal grid lines
    for y in range(0, int(canvas_bounds[1]) + 1, int(grid_size)):
        fig.add_shape(
            type="line",
            x0=0, y0=y,
            x1=canvas_bounds[0], y1=y,
            line=dict(color="lightgray", width=0.5, dash="dot")
        )
    
    # Add facility boundary
    fig.add_shape(
        type="rect",
        x0=0, y0=0,
        x1=canvas_bounds[0], y1=canvas_bounds[1],
        line=dict(color="darkgreen", width=3),
        fillcolor="rgba(46, 139, 87, 0.1)"
    )
    
    # Add placed equipment as interactive elements
    equipment_x = []
    equipment_y = []
    equipment_text = []
    equipment_colors = []
    equipment_ids = []
    
    for i, placed_equipment in enumerate(canvas_manager.placed_equipment):
        equipment = placed_equipment.equipment
        width, height = placed_equipment.get_equipment_size()
        
        # Add equipment as scatter point for interactivity
        equipment_x.append(placed_equipment.x_position)
        equipment_y.append(placed_equipment.y_position)
        equipment_text.append(f"{equipment.icon} {equipment.name}<br>CO2: {equipment.calculate_co2_emission():.1f} kg/year")
        equipment_colors.append("red" if placed_equipment.is_selected else "blue")
        equipment_ids.append(equipment.id)
        
        # Equipment rectangle background
        color = "red" if placed_equipment.is_selected else "blue"
        
        fig.add_shape(
            type="rect",
            x0=placed_equipment.x_position - width/2,
            y0=placed_equipment.y_position - height/2,
            x1=placed_equipment.x_position + width/2,
            y1=placed_equipment.y_position + height/2,
            line=dict(color=color, width=2),
            fillcolor=f"rgba(255, 0, 0, 0.3)" if placed_equipment.is_selected else "rgba(0, 100, 255, 0.3)"
        )
        
        # Equipment label
        fig.add_annotation(
            x=placed_equipment.x_position,
            y=placed_equipment.y_position - height/2 - 8,
            text=f"{equipment.icon}<br><b>{equipment.name}</b>",
            showarrow=False,
            font=dict(size=10, color="black"),
            bgcolor="white",
            bordercolor="gray",
            borderwidth=1,
            borderpad=2
        )
    
    # Add interactive scatter plot for equipment selection
    if equipment_x:
        fig.add_trace(go.Scatter(
            x=equipment_x,
            y=equipment_y,
            mode='markers',
            marker=dict(
                size=20,
                color=equipment_colors,
                symbol='square',
                opacity=0.7,
                line=dict(width=2, color='black')
            ),
            text=equipment_text,
            hoverinfo='text',
            name='Equipment',
            customdata=equipment_ids
        ))
    
    # Configure layout
    fig.update_layout(
        title=dict(
            text="Facility Layout Canvas - Click equipment to configure",
            x=0.5,
            font=dict(size=16)
        ),
        xaxis=dict(
            title="Distance (meters)",
            range=[0, canvas_bounds[0]],
            scaleanchor="y",
            scaleratio=1,
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray"
        ),
        yaxis=dict(
            title="Distance (meters)",
            range=[0, canvas_bounds[1]],
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray"
        ),
        width=None,
        height=600,
        showlegend=False,
        dragmode="pan",
        hovermode='closest'
    )
    
    # Display canvas with click event handling
    canvas_container = st.container()
    with canvas_container:
        selected_points = st.plotly_chart(
            fig, 
            use_container_width=True, 
            key="canvas",
            on_select="rerun"
        )
        
        # Handle equipment selection
        if selected_points and 'selection' in selected_points:
            if 'points' in selected_points['selection'] and selected_points['selection']['points']:
                point_indices = [p['point_index'] for p in selected_points['selection']['points']]
                if point_indices and len(canvas_manager.placed_equipment) > point_indices[0]:
                    selected_equipment = canvas_manager.placed_equipment[point_indices[0]]
                    st.session_state.selected_equipment_for_config = selected_equipment
                    st.session_state.show_config_panel = True
                    canvas_manager.select_equipment(selected_equipment.equipment.id)
                    st.rerun()

def equipment_config_panel():
    """Render equipment configuration panel"""
    if not st.session_state.show_config_panel or not st.session_state.selected_equipment_for_config:
        return
    
    selected = st.session_state.selected_equipment_for_config
    equipment = selected.equipment
    
    # Modal-like panel
    with st.container():
        st.markdown("### Equipment Configuration")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Equipment header
            st.markdown(f"## {equipment.icon} {equipment.name}")
            st.caption(f"Category: {equipment.category}")
            
            # Configuration form
            with st.form("equipment_config"):
                if equipment.requires_power_config:
                    power_rate = st.number_input(
                        "Power Rate (kW)",
                        min_value=0.0,
                        value=equipment.power_rate_kw,
                        step=10.0
                    )
                    
                    operation_time = st.number_input(
                        "Operation Time (hours/year)",
                        min_value=0.0,
                        max_value=8760.0,
                        value=equipment.operation_time_hours,
                        step=100.0
                    )
                    
                    fuel_type = st.selectbox(
                        "Fuel Type",
                        options=["LPG", "Diesel", "Gasoline", "Natural Gas", "None", "Gas", "Electric"],
                        index=["LPG", "Diesel", "Gasoline", "Natural Gas", "None", "Gas", "Electric"].index(equipment.fuel_type)
                    )
                else:
                    st.info("This equipment type doesn't require power or fuel configuration.")
                    power_rate = 0.0
                    operation_time = 0.0
                    fuel_type = "None"
                
                col_save, col_delete, col_close = st.columns([1, 1, 1])
                
                with col_save:
                    save_clicked = st.form_submit_button("💾 Save", use_container_width=True)
                
                with col_delete:
                    delete_clicked = st.form_submit_button("Delete", use_container_width=True)
                
                with col_close:
                    close_clicked = st.form_submit_button("❌ Close", use_container_width=True)
                
                if save_clicked:
                    # Update equipment
                    equipment.power_rate_kw = power_rate
                    equipment.operation_time_hours = operation_time
                    equipment.fuel_type = fuel_type
                    st.success("Equipment updated!")
                    st.session_state.show_config_panel = False
                    st.rerun()
                
                if delete_clicked:
                    # Remove equipment
                    if 'canvas_manager' in st.session_state:
                        st.session_state.canvas_manager.remove_equipment(equipment.id)
                        st.success("Equipment deleted!")
                        st.session_state.show_config_panel = False
                        st.rerun()
                
                if close_clicked:
                    st.session_state.show_config_panel = False
                    st.rerun()
        
        with col2:
            # Equipment info panel
            st.markdown("### Equipment Info")
            
            info = equipment.get_equipment_info()
            
            # Basic info
            st.markdown("**Basic Information:**")
            st.write(f"• **Type:** {info['basic_info']['name']}")
            st.write(f"• **Category:** {info['basic_info']['category']}")
            st.write(f"• **Combustion:** {'Yes' if info['basic_info']['has_combustion'] else 'No'}")
            
            if equipment.requires_power_config:
                st.markdown("**Operational Data:**")
                for key, value in info['operational_data'].items():
                    st.write(f"• **{key.replace('_', ' ').title()}:** {value}")
            
            # Environmental impact
            st.markdown("**Environmental Impact:**")
            st.write(f"• **CO2 Emission:** {info['environmental_impact']['co2_emission_kg']} kg/year")
            st.write(f"• **Emission Factor:** {info['environmental_impact']['emission_factor']['factor']} {info['environmental_impact']['emission_factor']['unit']}")

def top_navigation():
    """Professional top navigation bar with enhanced styling"""
    
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("Home", help="Return to main page", use_container_width=True):
            if not st.session_state.project_saved:
                st.warning("You have unsaved changes!")
                col_save, col_cancel = st.columns([1, 1])
                with col_save:
                    if st.button("Save & Go Home"):
                        save_current_project()
                        st.session_state.current_page = 'main'
                        st.rerun()
                with col_cancel:
                    if st.button("Discard Changes"):
                        st.session_state.current_page = 'main'
                        st.rerun()
            else:
                st.session_state.current_page = 'main'
                st.rerun()
    
    with col2:
        if st.button("Refresh", help="Refresh canvas", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.session_state.current_project:
            st.markdown(f'<div class="project-title">{st.session_state.current_project["name"]}</div>', unsafe_allow_html=True)
    
    with col4:
        if st.button("Save", help="Save current project", use_container_width=True, type="primary"):
            save_current_project()
            st.success("Project saved!")
    
    with col5:
        if st.button("Report", help="Generate CO2 analysis report", use_container_width=True):
            st.session_state.current_page = 'reporting'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def save_current_project():
    """Save the current project state"""
    if not st.session_state.current_project or 'canvas_manager' not in st.session_state:
        return False
    
    try:
        project = st.session_state.current_project
        canvas_manager = st.session_state.canvas_manager
        
        # Update project data
        project_data = {
            "name": project['name'],
            "description": project.get('description', ''),
            "facility_size_acres": project['facility_size_acres'],
            "facility_size_meters": project['facility_size_meters'],
            "created_date": project.get('created_date', datetime.now().isoformat()),
            "last_modified": datetime.now().isoformat(),
            "equipment": [placed.to_dict() for placed in canvas_manager.placed_equipment],
            "canvas_config": {
                "width_m": canvas_manager.facility_width_m,
                "height_m": canvas_manager.facility_height_m
            }
        }
        
        # Save to file
        filename = f"projects/{project['name'].replace(' ', '_').lower()}.json"
        with open(filename, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        st.session_state.project_saved = True
        return True
        
    except Exception as e:
        st.error(f"Error saving project: {e}")
        return False

def builder_page():
    """Main builder page function"""
    
    # Professional enterprise-grade styling (same as main page)
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
            padding: 2rem;
            margin: 1.5rem 0;
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
            font-size: 1.3rem;
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
        .project-title {
            color: #1a365d;
            font-size: 1.5rem;
            font-weight: 600;
            margin: 1rem 0;
            text-align: center;
        }
        .btn-primary {
            background: linear-gradient(135deg, #4fd1c7 0%, #38b2ac 100%);
            border: none;
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(79, 209, 199, 0.3);
        }
        .equipment-card {
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(247, 250, 252, 0.95) 100%);
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 1rem;
            margin: 0.5rem 0;
            transition: all 0.2s ease;
            cursor: pointer;
            backdrop-filter: blur(5px);
        }
        .equipment-card:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: #4fd1c7;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        .stat-item {
            background: rgba(255,255,255,0.9);
            padding: 1rem;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            text-align: center;
            backdrop-filter: blur(5px);
        }
        .stat-number {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1a365d;
            margin-bottom: 0.3rem;
        }
        .stat-label {
            font-size: 0.8rem;
            color: #718096;
        }
    </style>
    
    <div class="enterprise-background"></div>
    <div class="enterprise-container">
        <div class="enterprise-header">
            <h1><span class="brand-name">Delphi</span>: <span style="color: #81e6d9;">Facilities</span> Builder</h1>
            <div class="subtitle">
                Facility Equipment Configuration & Layout Design
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if project is loaded
    if not st.session_state.current_project:
        st.error("No project loaded. Please return to main page and select a project.")
        if st.button("Return to Main Page"):
            st.session_state.current_page = 'main'
            st.rerun()
        return
    
    # Initialize builder session
    initialize_builder_session()
    
    # Add equipment library to sidebar as well for easy access
    with st.sidebar:
        st.markdown("### Quick Equipment Access")
        st.markdown("*Common equipment shortcuts*")
        
        # Quick add buttons for most common equipment
        equipment_defaults = create_equipment_defaults()
        
        st.markdown("**Frequently Used:**")
        common_equipment = ["Gas Turbine", "Boiler", "Storage Tank", "Control Building"]
        
        for equipment_name in common_equipment:
            if equipment_name in equipment_defaults:
                equipment = equipment_defaults[equipment_name]
                if st.button(f"{equipment.icon} {equipment_name}", key=f"quick_{equipment_name}", use_container_width=True):
                    add_equipment_to_canvas(equipment)
                    st.rerun()
        
        st.markdown("---")
        st.markdown("Access complete equipment library in the main panel.")
    
    # Top navigation
    top_navigation()
    
    st.markdown("---")
    
    # Main layout
    col_sidebar, col_canvas = st.columns([1, 3])
    
    with col_sidebar:
        equipment_library_panel()
    
    with col_canvas:
        st.markdown("""
        <div class="section-container">
            <div class="section-header">
                🎨 Facility Layout Designer
            </div>
        """, unsafe_allow_html=True)
        
        # Use the enhanced draggable canvas
        create_enhanced_canvas_interface()
        
        # Equipment management section
        if 'enhanced_canvas_manager' in st.session_state and st.session_state.enhanced_canvas_manager.placed_equipment:
            st.markdown("### � Facility Summary")
            
            canvas_manager = st.session_state.enhanced_canvas_manager
            bounds = canvas_manager.get_canvas_bounds()
            equipment_count = len(canvas_manager.placed_equipment)
            total_co2 = canvas_manager.calculate_total_co2_emissions()
            
            # Summary stats
            col_stats1, col_stats2, col_stats3 = st.columns([1, 1, 1])
            with col_stats1:
                st.metric("Equipment Count", equipment_count)
            with col_stats2:
                st.metric("Facility Size", f"{bounds[0]:.0f}m × {bounds[1]:.0f}m")
            with col_stats3:
                st.metric("Total CO2", f"{total_co2:,.1f} kg/year")
        else:
            st.info("No equipment placed yet. Use the equipment library on the left to add equipment to your facility.")
    
    # Configuration panel (shown as overlay)
    if st.session_state.show_config_panel:
        st.markdown("---")
        equipment_config_panel()