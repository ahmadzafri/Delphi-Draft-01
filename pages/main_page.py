import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, List

def load_existing_projects() -> List[Dict]:
    """Load existing projects from the projects directory"""
    projects = []
    projects_dir = "projects"
    
    if os.path.exists(projects_dir):
        for filename in os.listdir(projects_dir):
            if filename.endswith('.json') and not filename.endswith('_report.json'):
                try:
                    with open(os.path.join(projects_dir, filename), 'r') as f:
                        project_data = json.load(f)
                        # Validate that required fields exist
                        if isinstance(project_data, dict) and 'name' in project_data:
                            projects.append(project_data)
                        else:
                            st.warning(f"⚠️ Skipping invalid project file: {filename}")
                except Exception as e:
                    st.error(f"Error loading project {filename}: {e}")
    
    return sorted(projects, key=lambda x: x.get('last_modified', ''), reverse=True)

def save_project(project_name: str, facility_acres: float, facility_area_m2: float, facility_width_m: float, facility_height_m: float, description: str = "") -> bool:
    """Save a new project with flexible facility size options"""
    try:
        project_data = {
            "name": project_name,
            "description": description,
            "facility_size_acres": facility_acres,
            "facility_size_meters": facility_area_m2,
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "equipment": [],
            "canvas_config": {
                "width_m": facility_width_m,
                "height_m": facility_height_m
            }
        }
        
        # Ensure projects directory exists
        os.makedirs("projects", exist_ok=True)
        
        # Save project file
        filename = f"projects/{project_name.replace(' ', '_').lower()}.json"
        with open(filename, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error saving project: {e}")
        return False

def delete_project(project_name: str) -> bool:
    """Delete a project"""
    try:
        filename = f"projects/{project_name.replace(' ', '_').lower()}.json"
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False
    except Exception as e:
        st.error(f"Error deleting project: {e}")
        return False

def main_page():
    """Main page for project management"""
    
    # Professional enterprise-grade header with sophisticated CSS styling and background
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
            padding: 4rem 2rem 3rem 2rem;
            margin: -1rem -1rem 3rem -1rem;
            text-align: center;
            color: white;
            border-radius: 0;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        .enterprise-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" fill="white" opacity="0.05"><polygon points="0,0 1000,0 1000,100 0,80"/></svg>');
            pointer-events: none;
        }
        .enterprise-header h1 {
            font-size: 3.2rem;
            margin-bottom: 0.8rem;
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
            font-size: 1.1rem;
            opacity: 0.9;
            margin: 1rem auto;
            font-weight: 400;
            max-width: 700px;
            line-height: 1.5;
            position: relative;
            z-index: 1;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        .enterprise-header .developer-credit {
            font-size: 0.9rem;
            opacity: 0.7;
            margin-top: 1.5rem;
            font-style: italic;
            position: relative;
            z-index: 1;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        .enterprise-header .co2-formula {
            color: #81e6d9;
            font-weight: 600;
        }
        .section-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 8px;
            padding: 2.5rem;
            margin: 2rem 0;
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
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid #4fd1c7;
            padding-bottom: 0.8rem;
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
        .project-card {
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(247, 250, 252, 0.95) 100%);
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            backdrop-filter: blur(5px);
        }
        .project-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            border-color: #4fd1c7;
            background: rgba(255, 255, 255, 0.98);
        }
        .project-card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: #4fd1c7;
            border-radius: 4px 0 0 4px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .project-card:hover::before {
            opacity: 1;
        }
        .project-card h4 {
            color: #1a365d;
            margin-bottom: 0.8rem;
            font-weight: 600;
            font-size: 1.2rem;
        }
        .project-meta {
            color: #718096;
            font-size: 0.9rem;
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .project-meta span {
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        .info-metric {
            background: linear-gradient(145deg, rgba(237, 242, 247, 0.95) 0%, rgba(247, 250, 252, 0.95) 100%);
            padding: 1.2rem;
            border-radius: 6px;
            border-left: 4px solid #4fd1c7;
            margin: 1rem 0;
            font-size: 0.95rem;
            backdrop-filter: blur(5px);
        }
        .new-project-form {
            background: linear-gradient(145deg, rgba(247, 250, 252, 0.95) 0%, rgba(237, 242, 247, 0.95) 100%);
            border-radius: 8px;
            padding: 2rem;
            border: 1px solid #e2e8f0;
            backdrop-filter: blur(10px);
        }
        .stats-overview {
            background: linear-gradient(135deg, rgba(26, 54, 93, 0.95) 0%, rgba(45, 55, 72, 0.95) 100%);
            color: white;
            padding: 2rem;
            border-radius: 8px;
            margin: 2rem 0;
            text-align: center;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }
        .stat-item {
            background: rgba(255,255,255,0.15);
            padding: 1rem;
            border-radius: 6px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .stat-number {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
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
        .enterprise-footer {
            background: rgba(247, 250, 252, 0.95);
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 1.5rem;
            text-align: center;
            color: #4a5568;
            font-size: 0.9rem;
            margin-top: 3rem;
            backdrop-filter: blur(10px);
        }
    </style>
    
    <div class="enterprise-background"></div>
    <div class="enterprise-container">
        <div class="enterprise-header">
            <h1><span class="brand-name">Delphi</span>: <span class="co2-formula">CO₂</span> Emission Simulator</h1>
            <div class="subtitle">
                CO₂ Emission Prediction in Scope 1 Monitoring for Small-Scale Facility Planning <br>
            </div>
            <div class="developer-credit">
                Developed by Ahmad Zafri
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div class="section-container">
            <div class="section-title">Create New Project</div>
        """, unsafe_allow_html=True)
        
        # Facility Size Input Options (outside form for immediate updates)
        st.markdown("**Facility Size**")
        size_option = st.selectbox(
            "Select measurement unit:",
            ["Acres", "Square Meters (m²)", "Length × Width (m)"],
            help="Choose how you want to specify your facility size",
            key="facility_size_option"
        )
        
        # Initialize variables
        facility_area_m2 = 0
        facility_width_m = 0
        facility_height_m = 0
        facility_acres = 0
        
        if size_option == "Acres":
            facility_acres = st.number_input(
                "Facility Size (acres)",
                min_value=0.1,
                max_value=10000.0,
                value=1.0,
                step=0.1,
                help="Total area of your industrial facility in acres",
                key="facility_acres_input"
            )
            facility_area_m2 = facility_acres * 4047
            facility_width_m = facility_height_m = (facility_area_m2 ** 0.5)
            
        elif size_option == "Square Meters (m²)":
            facility_area_m2 = st.number_input(
                "Facility Area (m²)",
                min_value=100.0,
                max_value=40470000.0,  # ~10,000 acres max
                value=4047.0,
                step=100.0,
                help="Total area of your industrial facility in square meters",
                key="facility_m2_input"
            )
            facility_acres = facility_area_m2 / 4047
            facility_width_m = facility_height_m = (facility_area_m2 ** 0.5)
            
        else:  # Length × Width
            col_w, col_h = st.columns(2)
            with col_w:
                facility_width_m = st.number_input(
                    "Width (m)",
                    min_value=10.0,
                    max_value=10000.0,
                    value=64.0,
                    step=1.0,
                    help="Facility width in meters",
                    key="facility_width_input"
                )
            with col_h:
                facility_height_m = st.number_input(
                    "Length (m)",
                    min_value=10.0,
                    max_value=10000.0,
                    value=64.0,
                    step=1.0,
                    help="Facility length in meters",
                    key="facility_height_input"
                )
            facility_area_m2 = facility_width_m * facility_height_m
            facility_acres = facility_area_m2 / 4047
        
        with st.form("new_project_form"):
            project_name = st.text_input(
                "Project Name",
                placeholder="e.g., Melaka Refinery CO₂ Analysis",
                help="Enter a descriptive name for your industrial facility project"
            )
            
            project_description = st.text_area(
                "Project Description (Optional)",
                placeholder="Detailed description of the facility, emission sources, and analysis objectives...",
                height=100
            )
            
            create_button = st.form_submit_button("Create Project", use_container_width=True, type="primary")
            
            if create_button:
                if project_name.strip():
                    # Check if project already exists
                    existing_projects = load_existing_projects()
                    if any(p.get('name', '').lower() == project_name.lower() for p in existing_projects if 'name' in p):
                        st.error("A project with this name already exists. Please choose a different name.")
                    else:
                        if save_project(project_name.strip(), facility_acres, facility_area_m2, facility_width_m, facility_height_m, project_description.strip()):
                            st.success(f"Project '{project_name}' created successfully!")
                            
                            # Set session state and navigate to builder
                            st.session_state.current_project = {
                                "name": project_name.strip(),
                                "facility_size_acres": facility_acres,
                                "facility_size_meters": facility_area_m2,
                                "description": project_description.strip(),
                                "canvas_width_m": facility_width_m,
                                "canvas_height_m": facility_height_m
                            }
                            # Ensure facility_scale has consistent structure
                            st.session_state.facility_scale = {
                                "acres": facility_acres,
                                "meters": facility_area_m2,
                                "canvas_width_m": facility_width_m,
                                "canvas_height_m": facility_height_m
                            }
                            # Set flag to show production popup automatically
                            st.session_state.show_production_popup = True
                            st.session_state.current_page = 'builder'
                            st.rerun()
                else:
                    st.error("Please enter a project name.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="section-container">
            <div class="section-title">Existing Projects</div>
        """, unsafe_allow_html=True)
        
        existing_projects = load_existing_projects()
        
        if existing_projects:
            # Search/filter projects
            search_term = st.text_input(
                "Search Projects", 
                placeholder="Filter by project name or description...",
                help="Search through existing projects"
            )
            
            filtered_projects = existing_projects
            if search_term:
                filtered_projects = [p for p in existing_projects 
                                   if search_term.lower() in p.get('name', '').lower() or 
                                      search_term.lower() in p.get('description', '').lower()]
            
            st.markdown(f"**{len(filtered_projects)} project(s) available**")
            
            for project in filtered_projects[:10]:  # Show max 10 projects
                project_name = project.get('name', 'Unnamed Project')
                facility_size = project.get('facility_size_acres', 'Unknown')
                last_modified = project.get('last_modified', 'Unknown')[:10] if project.get('last_modified') else 'Unknown'
                description = project.get('description', 'No description available')
                
                st.markdown(f"""
                <div class="project-card">
                    <h4>{project_name}</h4>
                    <div class="project-meta">
                        <span>Facility: {facility_size} acres</span>
                        <span>Modified: {last_modified}</span>
                    </div>
                    {f'<p style="margin: 0.5rem 0 0 0; color: #718096; font-size: 0.9rem; line-height: 1.4;">{description}</p>' if description != 'No description available' else ''}
                </div>
                """, unsafe_allow_html=True)
                
                col_open, col_delete = st.columns([4, 1])
                
                with col_open:
                    if st.button("Open Project", key=f"open_{project_name}", use_container_width=True, type="primary"):
                        # Load project and navigate to builder
                        st.session_state.current_project = project
                        st.session_state.canvas_equipment = project.get('equipment', [])
                        
                        # Fix: Use canvas_config dimensions instead of facility_size_meters
                        canvas_config = project.get('canvas_config', {})
                        canvas_width = canvas_config.get('width_m', (project.get('facility_size_acres', 1.0) * 4047) ** 0.5)
                        canvas_height = canvas_config.get('height_m', (project.get('facility_size_acres', 1.0) * 4047) ** 0.5)
                        
                        st.session_state.facility_scale = {
                            "acres": project.get('facility_size_acres', 1.0),
                            "meters": project.get('facility_size_meters', 4047),
                            "canvas_width_m": canvas_width,
                            "canvas_height_m": canvas_height
                        }
                        st.session_state.current_page = 'builder'
                        st.rerun()
                
                with col_delete:
                    if st.button("Delete", key=f"delete_{project_name}", help="Delete project permanently"):
                        if delete_project(project_name):
                            st.success(f"Project '{project_name}' deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete project.")
            
            if len(filtered_projects) > 10:
                st.info(f"Showing first 10 of {len(filtered_projects)} projects. Use search to find specific projects.")
        
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #718096;">
                <h4 style="color: #4a5568;">No Projects Available</h4>
                <p>Create your first industrial facility project to begin CO₂ emission analysis</p>
                <div style="margin: 1.5rem 0; padding: 1rem; background: #f7fafc; border-radius: 6px; border-left: 4px solid #4fd1c7;">
                    <strong>Getting Started:</strong><br>
                    1. Enter a descriptive project name<br>
                    2. Specify your facility size in acres<br>
                    3. Add equipment and configure parameters<br>
                    4. Generate comprehensive emission reports
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Well-organized standards compliance section
    st.markdown("""
    <div style="background: rgba(247, 250, 252, 0.95); border-radius: 8px; padding: 1.8rem; margin: 2rem 0; border: 1px solid #e2e8f0;">
        <h4 style="margin-bottom: 1.2rem; color: #1a365d; font-size: 1.1rem; font-weight: 600; text-align: center;">Standards Compliance</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.5rem;">
            <div style="text-align: center; padding: 1rem; background: white; border-radius: 6px; border: 1px solid #e2e8f0;">
                <div style="font-weight: 600; color: #1a365d; font-size: 1rem; margin-bottom: 0.4rem;">IPCC Guidelines</div>
                <div style="color: #718096; font-size: 0.85rem;">National GHG Inventories</div>
            </div>
            <div style="text-align: center; padding: 1rem; background: white; border-radius: 6px; border: 1px solid #e2e8f0;">
                <div style="font-weight: 600; color: #1a365d; font-size: 1rem; margin-bottom: 0.4rem;">API Compendium</div>
                <div style="color: #718096; font-size: 0.85rem;">Petroleum Operations</div>
            </div>
            <div style="text-align: center; padding: 1rem; background: white; border-radius: 6px; border: 1px solid #e2e8f0;">
                <div style="font-weight: 600; color: #1a365d; font-size: 1rem; margin-bottom: 0.4rem;">ISO 14064</div>
                <div style="color: #718096; font-size: 0.85rem;">GHG Quantification</div>
            </div>
            <div style="text-align: center; padding: 1rem; background: white; border-radius: 6px; border: 1px solid #e2e8f0;">
                <div style="font-weight: 600; color: #1a365d; font-size: 1rem; margin-bottom: 0.4rem;">IOGP Report 446</div>
                <div style="color: #718096; font-size: 0.85rem;">Reporting GHG Emissions</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    
    # Simple footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #718096; font-size: 0.9rem; padding: 1rem;'>"
        "<strong>Delphi CO₂ Emission Simulator</strong><br>"
        "Supporting sustainable oil & gas industrial development through emission quantification and facilities planning"
        "</div>", 
        unsafe_allow_html=True
    )