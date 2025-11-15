"""
Enhanced draggable canvas for equipment placement with icons
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict

from .equipment_model import EquipmentModel
from .placed_equipment import PlacedEquipment, CanvasManager
from .interactive_canvas import create_drag_drop_canvas

class DraggableCanvasManager(CanvasManager):
    """Enhanced canvas manager with drag functionality and better visualization"""
    
    def __init__(self, width_m: float, height_m: float):
        super().__init__(width_m, height_m)
        self.dragging_equipment_id: Optional[str] = None
        self.last_click_position: Optional[Tuple[float, float]] = None
    
    def create_equipment_visualization(self) -> go.Figure:
        """Create enhanced plotly figure with draggable equipment icons"""
        fig = go.Figure()
        
        # Add grid background
        self._add_grid_to_figure(fig)
        
        # Add facility boundary
        self._add_facility_boundary(fig)
        
        # Add equipment as interactive scatter points with custom icons
        if self.placed_equipment:
            self._add_equipment_to_figure(fig)
        
        # Configure layout for interactivity
        self._configure_figure_layout(fig)
        
        return fig
    
    def _add_grid_to_figure(self, fig: go.Figure):
        """Add grid lines to the figure"""
        bounds = self.get_canvas_bounds()
        
        # Vertical grid lines
        for x in range(0, int(bounds[0]) + 1, int(self.grid_size)):
            fig.add_shape(
                type="line",
                x0=x, y0=0, x1=x, y1=bounds[1],
                line=dict(color="rgba(200, 200, 200, 0.3)", width=1, dash="dot")
            )
        
        # Horizontal grid lines  
        for y in range(0, int(bounds[1]) + 1, int(self.grid_size)):
            fig.add_shape(
                type="line",
                x0=0, y0=y, x1=bounds[0], y1=y,
                line=dict(color="rgba(200, 200, 200, 0.3)", width=1, dash="dot")
            )
    
    def _add_facility_boundary(self, fig: go.Figure):
        """Add facility boundary rectangle"""
        bounds = self.get_canvas_bounds()
        fig.add_shape(
            type="rect",
            x0=0, y0=0, x1=bounds[0], y1=bounds[1],
            line=dict(color="darkgreen", width=3),
            fillcolor="rgba(46, 139, 87, 0.05)"
        )
    
    def _add_equipment_to_figure(self, fig: go.Figure):
        """Add equipment as interactive points with enhanced visualization"""
        equipment_data = {
            'x': [], 'y': [], 'text': [], 'ids': [], 'colors': [],
            'icons': [], 'names': [], 'hover_text': []
        }
        
        for placed in self.placed_equipment:
            equipment = placed.equipment
            
            # Basic position data
            equipment_data['x'].append(placed.x_position)
            equipment_data['y'].append(placed.y_position)
            equipment_data['ids'].append(equipment.id)
            equipment_data['names'].append(equipment.name)
            equipment_data['icons'].append(equipment.icon)
            
            # Styling based on selection state
            color = "#FF6B6B" if placed.is_selected else "#4ECDC4"
            equipment_data['colors'].append(color)
            
            # Enhanced hover information
            co2_emission = equipment.calculate_co2_emission()
            hover_info = [
                f"<b>{equipment.icon} {equipment.name}</b>",
                f"Category: {equipment.category}",
                f"Position: ({placed.x_position:.0f}m, {placed.y_position:.0f}m)"
            ]
            
            if equipment.requires_power_config:
                hover_info.extend([
                    f"Power: {equipment.power_rate_kw:.0f} kW",
                    f"Fuel: {equipment.fuel_type}",
                    f"CO2: {co2_emission:.1f} kg/year"
                ])
            
            equipment_data['hover_text'].append("<br>".join(hover_info))
            equipment_data['text'].append(f"{equipment.icon}")
        
        # Add equipment scatter plot
        fig.add_trace(go.Scatter(
            x=equipment_data['x'],
            y=equipment_data['y'],
            mode='markers+text',
            marker=dict(
                size=30,
                color=equipment_data['colors'],
                symbol='circle',
                opacity=0.8,
                line=dict(width=3, color='white')
            ),
            text=equipment_data['icons'],
            textfont=dict(size=20),
            textposition="middle center",
            hovertext=equipment_data['hover_text'],
            hoverinfo='text',
            name='Equipment',
            customdata=equipment_data['ids']
        ))
        
        # Add equipment labels below icons
        fig.add_trace(go.Scatter(
            x=equipment_data['x'],
            y=[y - 15 for y in equipment_data['y']],  # Offset labels below icons
            mode='text',
            text=[f"<b>{name}</b>" for name in equipment_data['names']],
            textfont=dict(size=10, color='black'),
            textposition="middle center",
            showlegend=False,
            hoverinfo='skip'
        ))
    
    def _configure_figure_layout(self, fig: go.Figure):
        """Configure figure layout for optimal interaction"""
        bounds = self.get_canvas_bounds()
        
        fig.update_layout(
            title=dict(
                text="Industrial Facility Layout",
                x=0.5,
                font=dict(size=18, color='#2c3e50')
            ),
            xaxis=dict(
                title="Distance (meters)",
                range=[-10, bounds[0] + 10],
                scaleanchor="y",
                scaleratio=1,
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(200, 200, 200, 0.2)",
                zeroline=False
            ),
            yaxis=dict(
                title="Distance (meters)",  
                range=[-20, bounds[1] + 10],
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(200, 200, 200, 0.2)",
                zeroline=False
            ),
            width=None,
            height=700,
            showlegend=False,
            dragmode="select",  # Enable selection/dragging
            hovermode='closest',
            plot_bgcolor='rgba(248, 249, 250, 1)',
            paper_bgcolor='white'
        )
    
    def handle_canvas_click(self, click_data: Dict) -> bool:
        """Handle canvas click events for equipment selection and movement"""
        if not click_data or 'points' not in click_data:
            return False
        
        points = click_data['points']
        if not points:
            return False
        
        point = points[0]
        
        # Handle equipment selection
        if 'customdata' in point and point['customdata']:
            equipment_id = point['customdata']
            self.select_equipment(equipment_id)
            return True
        
        return False
    
    def handle_drag_event(self, relayout_data: Dict) -> bool:
        """Handle drag events to move equipment"""
        if not relayout_data:
            return False
        
        # Check for selection events that indicate dragging
        if 'selections' in relayout_data:
            selections = relayout_data['selections']
            if selections and len(selections) > 0:
                selection = selections[0]
                if 'x0' in selection and 'x1' in selection:
                    # Calculate new position from selection bounds
                    new_x = (selection['x0'] + selection['x1']) / 2
                    new_y = (selection['y0'] + selection['y1']) / 2
                    
                    # Find selected equipment and update position
                    selected_equipment = self.get_selected_equipment()
                    if selected_equipment:
                        return self.move_equipment(selected_equipment.equipment.id, new_x, new_y)
        
        return False
    
    def get_equipment_at_position(self, x: float, y: float, tolerance: float = 15) -> Optional[PlacedEquipment]:
        """Find equipment at given position within tolerance"""
        for placed in self.placed_equipment:
            distance = ((placed.x_position - x) ** 2 + (placed.y_position - y) ** 2) ** 0.5
            if distance <= tolerance:
                return placed
        return None

def create_enhanced_canvas_interface():
    """Create the enhanced canvas interface with drag and drop functionality"""
    st.markdown("### Facility Layout Canvas")
    
    if 'enhanced_canvas_manager' not in st.session_state:
        if st.session_state.current_project:
            width = st.session_state.current_project.get('canvas_width_m', 200)
            height = st.session_state.current_project.get('canvas_height_m', 200)
            st.session_state.enhanced_canvas_manager = DraggableCanvasManager(width, height)
        else:
            st.session_state.enhanced_canvas_manager = DraggableCanvasManager(200, 200)
    
    canvas_manager = st.session_state.enhanced_canvas_manager
    
    # Canvas mode selection
    canvas_mode = st.radio(
        "Visualization Mode:",
        ["Interactive Layout", "Technical Diagram"],
        horizontal=True,
        help="Choose between interactive layout or technical diagram view"
    )
    
    # Canvas controls
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("Clear All", help="Remove all equipment from canvas"):
            canvas_manager.clear_all_equipment()
            st.session_state.project_saved = False
            st.rerun()
    
    with col2:
        if st.button("Reset View", help="Reset canvas view"):
            st.rerun()
    
    with col3:
        equipment_count = len(canvas_manager.placed_equipment)
        st.metric("Equipment Count", equipment_count)
    
    with col4:
        total_co2 = sum(eq.equipment.calculate_co2_emission() for eq in canvas_manager.placed_equipment)
        st.metric("Total CO2 (kg/year)", f"{total_co2:.1f}")
    
    # Main canvas display
    if canvas_mode == "Interactive Layout":
        st.markdown("#### Interactive Equipment Layout")
        st.info("Click and drag equipment icons to reposition. Select equipment for detailed configuration.")
        
        # Interactive HTML5 canvas
        canvas_component = create_drag_drop_canvas(
            canvas_width=800, 
            canvas_height=500
        )
        
        # Handle component events (would need custom component for full functionality)
        if canvas_component:
            # This is where we'd handle position updates from the JavaScript component
            pass
            
    else:
        st.markdown("#### Technical Facility Diagram")
        
        # Original plotly implementation
        fig = canvas_manager.create_equipment_visualization()
        
        # Display canvas with event handling
        canvas_events = st.plotly_chart(
            fig,
            use_container_width=True,
            key="enhanced_canvas_plotly",
            on_select="rerun",
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'facility_layout',
                    'height': 700,
                    'width': 1200,
                    'scale': 1
                }
            }
        )
        
        # Handle canvas interaction events
        if canvas_events and 'selection' in canvas_events:
            if canvas_manager.handle_canvas_click(canvas_events['selection']):
                st.rerun()
    
    # Equipment information panel
    selected_equipment = canvas_manager.get_selected_equipment()
    if selected_equipment:
        st.markdown("---")
        display_selected_equipment_info(selected_equipment)

def display_selected_equipment_info(placed_equipment: PlacedEquipment):
    """Display information about selected equipment"""
    equipment = placed_equipment.equipment
    
    st.markdown(f"### Selected Equipment: {equipment.name}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Category:** {equipment.category}")
        st.markdown(f"**Position:** ({placed_equipment.x_position:.0f}m, {placed_equipment.y_position:.0f}m)")
        
        if equipment.requires_power_config:
            st.markdown(f"**Power Rating:** {equipment.power_rate_kw:.0f} kW")
            st.markdown(f"**Fuel Type:** {equipment.fuel_type}")
            st.markdown(f"**CO2 Emission:** {equipment.calculate_co2_emission():.1f} kg/year")
    
    with col2:
        if st.button("Configure", key="config_selected"):
            st.session_state.selected_equipment_for_config = placed_equipment
            st.session_state.show_config_panel = True
            st.rerun()
        
        if st.button("Remove", key="remove_selected"):
            canvas_manager = st.session_state.enhanced_canvas_manager
            if canvas_manager.remove_equipment(equipment.id):
                st.session_state.project_saved = False
                st.success(f"Removed {equipment.name}")
                st.rerun()