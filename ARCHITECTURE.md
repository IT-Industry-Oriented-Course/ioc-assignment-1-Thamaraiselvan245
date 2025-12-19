# Architecture Documentation

## System Overview

The Clinical Workflow Automation Agent is a function-calling LLM agent built with LangChain that interprets natural language clinical requests and safely interacts with healthcare APIs. It acts as an intelligent workflow orchestrator, not a medical advisor.

## Core Components

### 1. **schemas.py** - FHIR-Style Data Models
- Defines Pydantic models aligned with FHIR standards
- Ensures type safety and validation
- Models include:
  - `Patient`: Patient resource with identifiers
  - `InsuranceEligibility`: Insurance coverage information
  - `AppointmentSlot`: Available appointment time slots
  - `Appointment`: Confirmed appointment details
  - `AuditLog`: Compliance logging structure

### 2. **api_services.py** - Mock Healthcare APIs
- `MockPatientService`: Patient search functionality
- `MockInsuranceService`: Insurance eligibility checking
- `MockAppointmentService`: Appointment slot finding and booking
- All services include validation and error handling
- Simulates real healthcare API behavior

### 3. **functions.py** - LangChain Tool Definitions
- Exposes healthcare functions as LangChain tools
- Functions:
  - `search_patient`: Search patients by name/ID/DOB
  - `check_insurance_eligibility`: Verify insurance coverage
  - `find_available_slots`: Find appointment availability
  - `book_appointment`: Schedule appointments
- Each function includes:
  - Input schema validation
  - Error handling
  - Audit logging integration
  - Dry-run mode support

### 4. **agent.py** - LangChain Agent Implementation
- `ClinicalWorkflowAgent`: Main agent class
- Uses HuggingFace models via LangChain
- Implements safety checks (refuses medical advice)
- Supports dry-run mode
- Handles function calling and tool execution
- Provides structured responses

### 5. **logger.py** - Audit Logging System
- `AuditLogger`: Centralized logging
- Logs all agent actions with:
  - Timestamps
  - Function names
  - Input/output data
  - Success/failure status
  - Dry-run indicators
- Stores logs in JSONL format for compliance

### 6. **main.py** - CLI Interface
- Command-line interface for the agent
- Supports:
  - Interactive mode
  - Single query execution
  - Dry-run mode
  - Audit log viewing
  - Custom model selection

## Data Flow

```
User Query (Natural Language)
    ↓
main.py (CLI)
    ↓
agent.py (ClinicalWorkflowAgent)
    ↓
Safety Check (Medical Advice Filter)
    ↓
LangChain Agent Executor
    ↓
Function Selection & Execution
    ↓
functions.py (Tool Functions)
    ↓
api_services.py (Mock APIs)
    ↓
Response Processing
    ↓
Audit Logging (logger.py)
    ↓
Structured Output to User
```

## Safety Mechanisms

1. **Medical Advice Filter**: Refuses queries containing medical keywords
2. **Input Validation**: All inputs validated against FHIR schemas
3. **Error Handling**: Graceful failures with clear error messages
4. **Audit Trail**: Complete logging of all actions
5. **Dry-Run Mode**: Safe testing without actual API calls

## Function Calling Flow

1. User submits natural language query
2. Agent analyzes query and determines required functions
3. Agent calls functions in sequence (if needed)
4. Each function:
   - Validates inputs
   - Calls API service
   - Logs action
   - Returns structured result
5. Agent aggregates results and provides final response

## Example Workflow: Appointment Scheduling

```
Query: "Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility"

Agent Execution:
1. search_patient(name="Ravi Kumar")
   → Returns: Patient ID 12345

2. check_insurance_eligibility(patient_id="12345")
   → Returns: Active insurance coverage

3. find_available_slots(specialty="Cardiology")
   → Returns: List of available slots

4. book_appointment(patient_id="12345", slot_id="SLOT-...")
   → Returns: Confirmed appointment

Final Response: Structured appointment confirmation with all details
```

## Technology Stack

- **LangChain**: Agent framework and function calling
- **HuggingFace**: LLM provider (via API)
- **Pydantic**: Data validation and schemas
- **Python**: Core language (3.9+)

## Extensibility

The system is designed for easy extension:

1. **Add New Functions**: Define in `functions.py` with proper schemas
2. **Add New APIs**: Implement in `api_services.py` following existing patterns
3. **Custom Models**: Change model in `agent.py` initialization
4. **Additional Safety**: Add checks in `agent.py` safety filter

## Compliance & Auditability

- All actions logged with timestamps
- Input/output data preserved
- Success/failure tracking
- Dry-run mode clearly marked
- JSONL log format for easy parsing
- No medical advice or diagnoses logged

## Future Enhancements

Potential improvements:
- Real FHIR server integration
- Multi-turn conversation support
- User authentication and authorization
- Rate limiting and throttling
- Advanced error recovery
- Integration with EMR systems
- Support for additional healthcare workflows

