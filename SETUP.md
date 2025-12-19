# Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get HuggingFace API Key

1. Go to https://huggingface.co/settings/tokens
2. Create a new token (read access is sufficient)
3. Copy the token

### 3. Configure Environment

Create a `.env` file in the project root:

```bash
HUGGINGFACE_API_KEY=your_token_here
```

Or set it as an environment variable:

**Windows (PowerShell):**
```powershell
$env:HUGGINGFACE_API_KEY="your_token_here"
```

**Linux/Mac:**
```bash
export HUGGINGFACE_API_KEY="your_token_here"
```

### 4. Run the Agent

**Interactive Mode:**
```bash
python main.py
```

**Single Query:**
```bash
python main.py --query "Search for patient Ravi Kumar"
```

**Dry-Run Mode (Safe Testing):**
```bash
python main.py --dry-run --query "Schedule appointment for John Doe"
```

**With Audit Logs:**
```bash
python main.py --query "Find cardiology slots" --show-logs
```

## Example Queries

### Patient Operations
- `"Search for patient Ravi Kumar"`
- `"Find patient with ID 12345"`
- `"Look up patient Jane Smith"`

### Insurance Operations
- `"Check insurance eligibility for patient 12345"`
- `"Verify insurance coverage for Ravi Kumar"`

### Appointment Operations
- `"Find available cardiology appointments next week"`
- `"Show me neurology slots for Monday"`
- `"What cardiology appointments are available?"`

### Complete Workflows
- `"Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility"`
- `"Book an appointment for Jane Smith with a cardiologist and verify her insurance"`

## Testing

Run the example script:
```bash
python examples.py
```

## Troubleshooting

### "HuggingFace API key is required"
- Make sure you've set the `HUGGINGFACE_API_KEY` environment variable
- Check that your `.env` file is in the project root
- Verify the API key is correct

### "Could not initialize HuggingFace model"
- Check your internet connection
- Verify the API key has proper permissions
- Try a different model: `python main.py --model "mistralai/Mistral-7B-Instruct-v0.2"`

### Agent not calling functions
- Some HuggingFace models may not support function calling natively
- The agent will fall back to providing instructions on what functions to call
- Consider using OpenAI or Anthropic models for better function calling support

## Project Structure

```
.
├── main.py              # CLI entry point
├── agent.py             # LangChain agent implementation
├── functions.py         # Healthcare API function definitions
├── schemas.py           # FHIR-style Pydantic schemas
├── api_services.py      # Mock healthcare API services
├── logger.py            # Audit logging system
├── examples.py          # Example usage script
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
└── SETUP.md            # This file
```

## Mock Data

The agent uses mock patient and appointment data for demonstration:

**Patients:**
- Ravi Kumar (ID: 12345)
- Jane Smith (ID: 67890)
- John Doe (ID: 11111)

**Specialties:**
- Cardiology
- Neurology
- General Medicine

## Safety Features

- ✅ No medical advice or diagnoses
- ✅ Input validation with FHIR-style schemas
- ✅ Complete audit logging
- ✅ Dry-run mode for safe testing
- ✅ Error handling and graceful failures

