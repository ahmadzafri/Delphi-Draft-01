# DelphiGPT Setup Guide

## Overview

DelphiGPT is an AI-powered assistant integrated into the CO2 Simulation WebApp that provides intelligent recommendations for emissions optimization, equipment analysis, and regulatory compliance.

## Features

- **Real-time Analysis**: AI-powered insights based on your facility's actual data
- **Professional Recommendations**: Industry-grade optimization strategies
- **Equipment Analysis**: Detailed breakdown of high-emitting equipment
- **Fuel Strategy**: ROI calculations for fuel switching options
- **Compliance Guidance**: Regulatory requirements based on emission levels

## Setup Options

### Option 1: OpenAI GPT-4 (Recommended)

For the best AI experience with advanced language capabilities:

1. **Get an OpenAI API Key**:

   - Visit [OpenAI API](https://platform.openai.com/api-keys)
   - Create an account and generate an API key
   - Copy your API key

2. **Configure the API Key**:

   - Open `.streamlit/secrets.toml`
   - Add your API key:
     ```toml
     OPENAI_API_KEY = "your-openai-api-key-here"
     ```

3. **Alternative Environment Variable**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

### Option 2: Local AI Engine (Fallback)

If no OpenAI API key is provided, DelphiGPT automatically uses a built-in local AI engine that provides:

- Facility-specific analysis based on your data
- Equipment optimization recommendations
- Fuel switching strategies
- Compliance guidance

## Usage

1. Navigate to the **Reporting Page**
2. Scroll down to the **DelphiGPT AI Assistant** section
3. Either:
   - Type your question in the input field
   - Use the quick action buttons for common queries

## Sample Questions

- "How can I reduce emissions from my gas turbines?"
- "What's the ROI of switching to electric equipment?"
- "Analyze my highest emitting equipment"
- "What fuel switching options would provide the best emissions reduction?"
- "Help me understand regulatory compliance requirements"

## Quick Actions

- **💡 Optimization Tips**: Get immediate optimization strategies
- **🔍 Equipment Analysis**: Analyze highest emitting equipment
- **📊 Fuel Strategy**: Fuel switching recommendations
- **🎯 Compliance Help**: Regulatory guidance

## API Costs (OpenAI)

- Typical query: ~$0.01-0.03 per interaction
- Monthly usage (moderate): ~$5-15
- Costs depend on query complexity and response length

## Privacy & Security

- All facility data stays within your organization
- API calls include only aggregated emissions data, not sensitive information
- No facility-specific data is stored by OpenAI

## Troubleshooting

- **No API Key**: DelphiGPT automatically uses local engine
- **API Errors**: Fallback to local engine with warning message
- **Rate Limits**: Built-in error handling and retry logic

## Support

For technical support or feature requests related to DelphiGPT, please contact the development team.
