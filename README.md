# CO2 Simulation WebApp

A comprehensive Streamlit-based web application for simulating and analyzing CO2 emissions from industrial facilities.

## 🌍 Overview

This application provides an intuitive interface for creating facility layouts, configuring industrial equipment, and analyzing CO2 emissions. Perfect for environmental engineers, facility managers, and sustainability professionals.

## ✨ Features

### 🏠 Project Management

- Create new simulation projects
- Open and manage existing projects
- Project search and filtering
- Automatic project saving

### 🔧 Interactive Builder

- **Equipment Library**: 6 categories with 20+ equipment types

  - Power Generation (Gas Turbine, Diesel Gen-set, etc.)
  - Process Heating & Steam (Boiler, Furnace, etc.)
  - Flaring & Destructor (Flare Stack, Thermal Oxidizer, etc.)
  - Utility (Heater, Chiller, etc.)
  - Drivers & Machinery (Compressor, Pump Drive, etc.)
  - Non-Combustion (Storage Tank, Pipeline, etc.)

- **Visual Canvas**:

  - Grid-based layout system
  - Facility scaling (acres to meters)
  - Equipment snap functionality
  - Real-time equipment placement

- **Configuration Panel**:
  - Equipment properties (power, operation time, fuel type)
  - Real-time CO2 calculation
  - Equipment information panel

### 📈 Comprehensive Reporting

- Executive summary with key metrics
- Emissions analysis by category and fuel type
- Individual equipment breakdown
- Interactive charts and visualizations
- CO2 reduction recommendations
- Export capabilities (Excel, PDF planned)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone or download the project:

```bash
cd "C02 Sim WebApp"
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## 🏗️ Project Structure

```
C02 Sim WebApp/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── pages/                      # Application pages
│   ├── main_page.py           # Project management
│   ├── builder_page.py        # Equipment configuration
│   └── reporting_page.py      # CO2 analysis & reports
├── src/                       # Source code modules
│   ├── models/               # Data models
│   │   ├── equipment_model.py # Equipment definitions & CO2 logic
│   │   └── placed_equipment.py # Canvas placement logic
│   ├── utils/                # Utility functions
│   └── data/                 # Data processing
├── projects/                 # Saved project files
└── .github/
    └── copilot-instructions.md # AI coding guidelines
```

## 🎯 How to Use

### 1. Create a Project

- Enter project name and facility size in acres
- Add optional description
- Click "Create Project"

### 2. Build Your Facility

- Browse equipment library on the left sidebar
- Click "+" to add equipment to canvas
- Click on equipment to configure properties
- Adjust power rates, operation hours, and fuel types

### 3. Analyze Emissions

- Click "Generate Report" to view CO2 analysis
- Review emissions by category and fuel type
- Examine individual equipment performance
- Export reports for documentation

## 🔬 CO2 Calculation Methodology

The application uses industry-standard emission factors:

- **Natural Gas**: 0.0551 kg CO2/kWh
- **Diesel**: 2.68 kg CO2/liter
- **LPG**: 1.51 kg CO2/liter
- **Gasoline**: 2.31 kg CO2/liter
- **Electric**: 0.85 kg CO2/kWh (grid average)

Calculations consider:

- Equipment power ratings
- Annual operation hours
- Fuel consumption rates
- Equipment-specific efficiency factors

## 🛠️ Technical Features

### Equipment Management

- 20+ predefined equipment types with default configurations
- Realistic sizing and placement on canvas
- Snap-to-grid functionality for precise layouts
- Equipment connection tracking

### Data Persistence

- JSON-based project storage
- Automatic saving of canvas layouts
- Equipment configuration preservation
- Project modification tracking

### Visualization

- Interactive Plotly charts
- Real-time canvas updates
- Responsive design for different screen sizes
- Grid overlay for precise placement

## 🤝 Contributing

This project is designed to be easily extensible:

1. **Adding New Equipment**: Update `equipment_model.py` with new equipment types
2. **Custom Calculations**: Modify emission factors and calculation logic
3. **New Visualizations**: Add charts in `reporting_page.py`
4. **Enhanced UI**: Improve styling and interactions in page files

## 📋 Roadmap

### Upcoming Features

- [ ] Enhanced drag & drop with visual feedback
- [ ] Equipment connection lines and flow diagrams
- [ ] Multi-scenario comparison
- [ ] Temporal analysis (emissions over time)
- [ ] Integration with external emission databases
- [ ] Advanced optimization recommendations
- [ ] 3D facility visualization
- [ ] Mobile-responsive design improvements

### Export Enhancements

- [ ] PDF report generation
- [ ] Excel export with charts
- [ ] CAD file export for facility layouts
- [ ] Regulatory compliance reporting templates

## 🐛 Troubleshooting

### Common Issues

**"No module named 'plotly'"**

```bash
pip install plotly
```

**"Canvas not loading"**

- Ensure all dependencies are installed
- Check browser console for JavaScript errors
- Try refreshing the page

**"Project not saving"**

- Check write permissions in project directory
- Ensure sufficient disk space
- Verify project name doesn't contain special characters

## 📞 Support

For issues, feature requests, or questions:

- Check the `.github/copilot-instructions.md` for development guidelines
- Review the code comments for implementation details
- Use browser developer tools for debugging frontend issues

## 📄 License

This project is designed for educational and professional use in environmental engineering and sustainability analysis.

---

**🌍 Building a sustainable future, one simulation at a time.**
