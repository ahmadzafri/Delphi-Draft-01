"""
Interactive drag and drop interface for equipment placement
"""
import streamlit as st
import streamlit.components.v1 as components
import json
from typing import Dict, List, Optional, Tuple

def create_drag_drop_canvas(canvas_width: int = 800, canvas_height: int = 600):
    """Create an interactive drag and drop canvas using HTML5 Canvas and JavaScript"""
    
    # Equipment data for the JavaScript component
    equipment_data = []
    if 'enhanced_canvas_manager' in st.session_state:
        canvas_manager = st.session_state.enhanced_canvas_manager
        for placed in canvas_manager.placed_equipment:
            equipment = placed.equipment
            equipment_data.append({
                'id': equipment.id,
                'name': equipment.name,
                'icon': equipment.icon,
                'x': placed.x_position,
                'y': placed.y_position,
                'category': equipment.category,
                'co2': equipment.calculate_co2_emission(),
                'selected': placed.is_selected
            })
    
    # HTML and JavaScript for drag and drop canvas
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .canvas-container {{
                border: 2px solid #2E8B57;
                border-radius: 10px;
                background: linear-gradient(45deg, #f0f8f0 25%, transparent 25%), 
                           linear-gradient(-45deg, #f0f8f0 25%, transparent 25%), 
                           linear-gradient(45deg, transparent 75%, #f0f8f0 75%), 
                           linear-gradient(-45deg, transparent 75%, #f0f8f0 75%);
                background-size: 20px 20px;
                background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
                position: relative;
                overflow: hidden;
                margin: 10px 0;
            }}
            .equipment-item {{
                position: absolute;
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #4ECDC4, #44A08D);
                border: 3px solid white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                cursor: move;
                user-select: none;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                transition: all 0.2s ease;
                z-index: 10;
            }}
            .equipment-item:hover {{
                transform: scale(1.1);
                box-shadow: 0 6px 12px rgba(0,0,0,0.3);
                z-index: 20;
            }}
            .equipment-item.selected {{
                background: linear-gradient(135deg, #FF6B6B, #EE5A52);
                border-color: #FFD93D;
                box-shadow: 0 0 20px rgba(255, 107, 107, 0.5);
            }}
            .equipment-item.dragging {{
                opacity: 0.8;
                transform: scale(1.15);
                z-index: 30;
            }}
            .equipment-label {{
                position: absolute;
                top: 65px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(255, 255, 255, 0.95);
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
                color: #2c3e50;
                white-space: nowrap;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border: 1px solid #ddd;
            }}
            .grid-overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                opacity: 0.3;
            }}
            .facility-info {{
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(255, 255, 255, 0.9);
                padding: 10px;
                border-radius: 8px;
                font-size: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <div class="canvas-container" id="canvas" style="width: {canvas_width}px; height: {canvas_height}px;">
            <div class="facility-info">
                <div><strong>🏭 Facility Layout Canvas</strong></div>
                <div>Drag equipment to reposition</div>
                <div>Click to select equipment</div>
            </div>
            <div class="grid-overlay"></div>
        </div>
        
        <script>
            let equipmentData = {json.dumps(equipment_data)};
            let selectedEquipment = null;
            let isDragging = false;
            let dragOffset = {{x: 0, y: 0}};
            
            const canvas = document.getElementById('canvas');
            const canvasRect = canvas.getBoundingClientRect();
            
            // Create equipment elements
            function createEquipmentElements() {{
                // Clear existing equipment
                const existingEquipment = canvas.querySelectorAll('.equipment-item');
                existingEquipment.forEach(el => el.remove());
                
                equipmentData.forEach(equipment => {{
                    const equipmentEl = document.createElement('div');
                    equipmentEl.className = 'equipment-item';
                    if (equipment.selected) equipmentEl.classList.add('selected');
                    equipmentEl.id = `equipment-${{equipment.id}}`;
                    equipmentEl.innerHTML = `
                        ${{equipment.icon}}
                        <div class="equipment-label">${{equipment.name}}</div>
                    `;
                    
                    // Position equipment (scale from meters to pixels)
                    const scale = Math.min({canvas_width}/200, {canvas_height}/200); // Assume 200m = canvas size
                    equipmentEl.style.left = `${{equipment.x * scale - 30}}px`;
                    equipmentEl.style.top = `${{equipment.y * scale - 30}}px`;
                    
                    // Add event listeners
                    equipmentEl.addEventListener('mousedown', handleMouseDown);
                    equipmentEl.addEventListener('click', handleClick);
                    
                    canvas.appendChild(equipmentEl);
                }});
            }}
            
            function handleMouseDown(e) {{
                e.preventDefault();
                isDragging = true;
                const equipment = e.target.closest('.equipment-item');
                equipment.classList.add('dragging');
                
                const rect = equipment.getBoundingClientRect();
                const canvasRect = canvas.getBoundingClientRect();
                dragOffset.x = e.clientX - rect.left - rect.width/2;
                dragOffset.y = e.clientY - rect.top - rect.height/2;
                
                document.addEventListener('mousemove', handleMouseMove);
                document.addEventListener('mouseup', handleMouseUp);
            }}
            
            function handleMouseMove(e) {{
                if (!isDragging) return;
                
                const equipment = document.querySelector('.dragging');
                if (!equipment) return;
                
                const canvasRect = canvas.getBoundingClientRect();
                const x = e.clientX - canvasRect.left - dragOffset.x - 30;
                const y = e.clientY - canvasRect.top - dragOffset.y - 30;
                
                // Constrain to canvas bounds
                const constrainedX = Math.max(0, Math.min(x, {canvas_width} - 60));
                const constrainedY = Math.max(0, Math.min(y, {canvas_height} - 60));
                
                equipment.style.left = `${{constrainedX}}px`;
                equipment.style.top = `${{constrainedY}}px`;
            }}
            
            function handleMouseUp(e) {{
                if (!isDragging) return;
                
                const equipment = document.querySelector('.dragging');
                if (equipment) {{
                    equipment.classList.remove('dragging');
                    
                    // Convert back to meters and send to Streamlit
                    const rect = equipment.getBoundingClientRect();
                    const canvasRect = canvas.getBoundingClientRect();
                    const scale = Math.min({canvas_width}/200, {canvas_height}/200);
                    
                    const centerX = (rect.left - canvasRect.left + 30) / scale;
                    const centerY = (rect.top - canvasRect.top + 30) / scale;
                    
                    // Send position update to Streamlit
                    window.parent.postMessage({{
                        type: 'equipment_moved',
                        equipment_id: equipment.id.replace('equipment-', ''),
                        x: Math.round(centerX),
                        y: Math.round(centerY)
                    }}, '*');
                }}
                
                isDragging = false;
                document.removeEventListener('mousemove', handleMouseMove);
                document.removeEventListener('mouseup', handleMouseUp);
            }}
            
            function handleClick(e) {{
                e.stopPropagation();
                const equipment = e.target.closest('.equipment-item');
                
                // Clear previous selection
                document.querySelectorAll('.equipment-item').forEach(el => el.classList.remove('selected'));
                
                // Select clicked equipment
                equipment.classList.add('selected');
                
                // Send selection to Streamlit
                window.parent.postMessage({{
                    type: 'equipment_selected',
                    equipment_id: equipment.id.replace('equipment-', '')
                }}, '*');
            }}
            
            // Initialize
            createEquipmentElements();
            
            // Handle canvas click (deselect)
            canvas.addEventListener('click', (e) => {{
                if (e.target === canvas || e.target.classList.contains('grid-overlay')) {{
                    document.querySelectorAll('.equipment-item').forEach(el => el.classList.remove('selected'));
                    window.parent.postMessage({{
                        type: 'equipment_deselected'
                    }}, '*');
                }}
            }});
            
            // Listen for equipment updates from Streamlit
            window.addEventListener('message', (event) => {{
                if (event.data.type === 'update_equipment') {{
                    equipmentData = event.data.equipment_data;
                    createEquipmentElements();
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    # Render the HTML component
    component_value = components.html(html_code, height=canvas_height + 50, scrolling=False)
    
    return component_value

def handle_canvas_events():
    """Handle events from the drag and drop canvas"""
    # This would typically be handled through Streamlit's component communication
    # For now, we'll use session state to track changes
    pass