# Clinical Workflow Automation Agent

A function-calling LLM agent designed for clinical appointment and care coordination workflows. This agent acts as an intelligent orchestrator that safely interacts with healthcare APIs without providing medical advice.

## 🎯 Core Features

- **Function Calling**: Uses LangChain with HuggingFace models for structured tool execution
- **FHIR-Style Schemas**: Validated input/output schemas aligned with healthcare standards
- **Safety First**: No medical advice, no hallucinations - only validated API interactions
- **Audit Logging**: Complete compliance logging for all actions
- **Dry-Run Mode**: Test workflows without executing actual API calls
- **External API Integration**: Mock healthcare APIs for demonstration

## 🏥 Supported Functions

1. **search_patient**: Search for patients by name, ID, or other identifiers
2. **check_insurance_eligibility**: Verify patient insurance coverage and eligibility
3. **find_available_slots**: Find available appointment slots for a specialty
4. **book_appointment**: Schedule appointments with validation

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- HuggingFace API key ([Get one here](https://huggingface.co/settings/tokens))

### Installation

```bash
# Clone or navigate to the project directory
cd "Ioc pro"

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file with:
# HUGGINGFACE_API_KEY=your_api_key_here
```

### Usage

```bash
# Run the agent in interactive mode
python main.py

# Or run with a specific query
python main.py --query "Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility"

# Enable dry-run mode (no actual API calls)
python main.py --dry-run --query "Schedule appointment for John Doe"
```

### Example Queries

```
"Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility"
"Find available slots for neurology next Monday"
"Check if patient ID 12345 has active insurance coverage"
"Book an appointment for patient Jane Smith with Dr. Johnson on March 15th"
```

## 📁 Project Structure

```
.
├── main.py                 # Main application entry point
├── agent.py                # LangChain agent implementation
├── functions.py            # Healthcare API function definitions
├── schemas.py              # FHIR-style Pydantic schemas
├── api_services.py         # Mock healthcare API services
├── logger.py               # Audit logging system
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔒 Safety & Compliance

- **No Medical Advice**: The agent explicitly refuses to provide diagnoses or medical recommendations
- **Input Validation**: All inputs are validated against FHIR-style schemas
- **Audit Trail**: Every action is logged with timestamps, user context, and outcomes
- **Dry-Run Mode**: Test workflows safely before execution
- **Error Handling**: Graceful failures with clear error messages

## 🧪 Testing

```bash
# Run example queries
python main.py --query "Search for patient Ravi Kumar"
python main.py --query "Check insurance for patient ID 12345"
python main.py --dry-run --query "Book appointment"
```

## 📝 Notes

- This is a POC (Proof of Concept) for demonstration purposes
- Uses mock APIs for safety - replace with real APIs in production
- Designed for local execution and in-person demonstration
- All function schemas follow FHIR resource patterns

## 🔧 Configuration

The agent uses HuggingFace models by default. To use a different provider, modify `agent.py`:

```python
# Currently uses HuggingFace
from langchain_huggingface import ChatHuggingFace

# Can be switched to OpenAI, Anthropic, etc.
```

## 📄 License

Educational/Assignment Project

