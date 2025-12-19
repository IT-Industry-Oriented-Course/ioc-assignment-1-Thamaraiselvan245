# Healthcare Workflow UI

A clean, modern web interface for the Healthcare Workflow System built with Streamlit.

## Features

The UI provides easy access to all healthcare workflow functions:

1. **🔍 Search Patient** - Search for patients by name, ID, or date of birth
2. **💳 Check Insurance** - Verify insurance eligibility and coverage
3. **📅 Find Appointments** - Search for available appointment slots by specialty
4. **✅ Book Appointment** - Book appointments for patients

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have your HuggingFace API key set up (see main README.md)

## Running the UI

Start the Streamlit application:

```bash
streamlit run ui.py
```

The UI will open automatically in your default web browser at `http://localhost:8501`

## Usage

### Search Patient
- Enter at least one of: Patient Name, Patient ID, or Date of Birth
- Click "Search Patient" to find matching patients
- Results show patient details including ID, name, DOB, and MRN

### Check Insurance
- Enter a Patient ID
- Click "Check Insurance" to view eligibility information
- Results show provider, policy number, coverage type, and status

### Find Appointments
- Select a medical specialty from the dropdown
- Optionally set start and end dates to filter results
- Click "Find Available Slots" to see available appointments
- Results are grouped by provider with date/time information

### Book Appointment
- Enter Patient ID and Slot ID (get Slot ID from "Find Appointments" tab)
- Optionally add reason for visit and notes
- Enable "Dry Run Mode" in the sidebar to validate without booking
- Click "Book Appointment" to confirm the booking

## Features

- **Clean, Modern UI** - Beautiful, responsive interface
- **Real-time Results** - Instant feedback on all operations
- **Dry Run Mode** - Test appointments without making actual bookings
- **Quick Stats** - View system statistics in the sidebar
- **Error Handling** - Clear error messages for invalid inputs
- **Example Data** - Quick access to example patient IDs and specialties

## Notes

- The UI uses mock data services (same as the CLI)
- All functions work exactly like the CLI version
- Dry Run Mode can be toggled from the sidebar
- Results are displayed in a clean, formatted manner

