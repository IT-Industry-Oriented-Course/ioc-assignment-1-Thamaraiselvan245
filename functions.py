"""
Healthcare API Function Definitions for LangChain
These functions are exposed as tools to the LLM agent.
"""

from typing import List, Optional, Dict, Any
from langchain.tools import tool
from pydantic import BaseModel, Field
from schemas import (
    Patient, InsuranceEligibility, AppointmentSlot, Appointment,
    SearchPatientRequest, AppointmentRequest
)
from api_services import (
    MockPatientService, MockInsuranceService, MockAppointmentService
)
from logger import audit_logger

# Global dry-run flag (set by agent)
_DRY_RUN_MODE = False


def set_dry_run_mode(enabled: bool):
    """Set global dry-run mode"""
    global _DRY_RUN_MODE
    _DRY_RUN_MODE = enabled


class SearchPatientInput(BaseModel):
    """Input schema for search_patient function"""
    name: Optional[str] = Field(None, description="Patient name (partial or full name)")
    patient_id: Optional[str] = Field(None, description="Patient ID")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD format)")


class CheckInsuranceInput(BaseModel):
    """Input schema for check_insurance_eligibility function"""
    patient_id: str = Field(..., description="Patient ID to check insurance for")


class FindSlotsInput(BaseModel):
    """Input schema for find_available_slots function"""
    specialty: str = Field(..., description="Medical specialty (e.g., Cardiology, Neurology, General Medicine)")
    start_date: Optional[str] = Field(None, description="Start date for search (YYYY-MM-DD format, optional)")
    end_date: Optional[str] = Field(None, description="End date for search (YYYY-MM-DD format, optional)")


class BookAppointmentInput(BaseModel):
    """Input schema for book_appointment function"""
    patient_id: str = Field(..., description="Patient ID")
    slot_id: str = Field(..., description="Appointment slot ID to book")
    reason: Optional[str] = Field(None, description="Reason for visit")
    notes: Optional[str] = Field(None, description="Additional notes")


@tool(args_schema=SearchPatientInput)
def search_patient(name: Optional[str] = None, patient_id: Optional[str] = None, date_of_birth: Optional[str] = None) -> str:
    """
    Search for patients by name, patient ID, or date of birth.
    At least one parameter must be provided.
    
    Args:
        name: Patient name (can be partial match)
        patient_id: Patient ID
        date_of_birth: Date of birth in YYYY-MM-DD format
        
    Returns:
        JSON string with list of matching patients
    """
    try:
        request = SearchPatientRequest(
            name=name,
            patient_id=patient_id,
            date_of_birth=date_of_birth
        )
        
        patients = MockPatientService.search_patient(request)
        
        result = {
            "success": True,
            "count": len(patients),
            "patients": [p.model_dump() for p in patients]
        }
        
        audit_logger.log_action(
            action=f"Search patient: {name or patient_id or date_of_birth}",
            function_name="search_patient",
            input_data=request.model_dump(),
            output_data=result,
            success=True
        )
        
        return str(result)
    
    except Exception as e:
        error_msg = f"Error searching patient: {str(e)}"
        audit_logger.log_action(
            action=f"Search patient failed: {name or patient_id or date_of_birth}",
            function_name="search_patient",
            input_data={"name": name, "patient_id": patient_id, "date_of_birth": date_of_birth},
            success=False,
            error_message=error_msg
        )
        return f'{{"success": false, "error": "{error_msg}"}}'


@tool(args_schema=CheckInsuranceInput)
def check_insurance_eligibility(patient_id: str) -> str:
    """
    Check insurance eligibility and coverage for a patient.
    
    Args:
        patient_id: Patient ID to check insurance for
        
    Returns:
        JSON string with insurance eligibility information
    """
    try:
        eligibility = MockInsuranceService.check_eligibility(patient_id)
        
        if eligibility:
            result = {
                "success": True,
                "eligibility": eligibility.model_dump()
            }
        else:
            result = {
                "success": False,
                "error": f"No insurance information found for patient {patient_id}"
            }
        
        audit_logger.log_action(
            action=f"Check insurance eligibility for patient {patient_id}",
            function_name="check_insurance_eligibility",
            input_data={"patient_id": patient_id},
            output_data=result,
            success=eligibility is not None
        )
        
        return str(result)
    
    except Exception as e:
        error_msg = f"Error checking insurance: {str(e)}"
        audit_logger.log_action(
            action=f"Check insurance failed for patient {patient_id}",
            function_name="check_insurance_eligibility",
            input_data={"patient_id": patient_id},
            success=False,
            error_message=error_msg
        )
        return f'{{"success": false, "error": "{error_msg}"}}'


@tool(args_schema=FindSlotsInput)
def find_available_slots(specialty: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """
    Find available appointment slots for a medical specialty.
    
    Args:
        specialty: Medical specialty (e.g., "Cardiology", "Neurology", "General Medicine")
        start_date: Start date for search (YYYY-MM-DD format, optional)
        end_date: End date for search (YYYY-MM-DD format, optional)
        
    Returns:
        JSON string with list of available appointment slots
    """
    try:
        slots = MockAppointmentService.find_available_slots(
            specialty=specialty,
            start_date=start_date,
            end_date=end_date
        )
        
        result = {
            "success": True,
            "count": len(slots),
            "slots": [s.model_dump() for s in slots]
        }
        
        audit_logger.log_action(
            action=f"Find available slots for {specialty}",
            function_name="find_available_slots",
            input_data={"specialty": specialty, "start_date": start_date, "end_date": end_date},
            output_data=result,
            success=True
        )
        
        # Return formatted result (can be made more concise if needed)
        return str(result)
    
    except Exception as e:
        error_msg = f"Error finding slots: {str(e)}"
        audit_logger.log_action(
            action=f"Find slots failed for {specialty}",
            function_name="find_available_slots",
            input_data={"specialty": specialty, "start_date": start_date, "end_date": end_date},
            success=False,
            error_message=error_msg
        )
        return f'{{"success": false, "error": "{error_msg}"}}'


@tool(args_schema=BookAppointmentInput)
def book_appointment(patient_id: str, slot_id: str, reason: Optional[str] = None, notes: Optional[str] = None) -> str:
    """
    Book an appointment for a patient.
    
    Args:
        patient_id: Patient ID
        slot_id: Appointment slot ID to book
        reason: Reason for visit (optional)
        notes: Additional notes (optional)
        
    Returns:
        JSON string with confirmed appointment details
    """
    global _DRY_RUN_MODE
    try:
        if _DRY_RUN_MODE:
            # In dry-run mode, validate but don't book
            # Check if patient exists
            patient = MockPatientService._patients.get(patient_id)
            if not patient:
                raise ValueError(f"Patient not found: {patient_id}")
            
            # Check if slot exists (simplified validation)
            if not slot_id.startswith("SLOT-"):
                raise ValueError(f"Invalid slot ID format: {slot_id}")
            
            result = {
                "success": True,
                "dry_run": True,
                "message": f"Dry-run: Would book appointment for patient {patient_id} in slot {slot_id}",
                "validated": True,
                "patient_name": patient.name
            }
        else:
            appointment = MockAppointmentService.book_appointment(
                patient_id=patient_id,
                slot_id=slot_id,
                reason=reason,
                notes=notes
            )
            
            result = {
                "success": True,
                "appointment": appointment.model_dump()
            }
        
        audit_logger.log_action(
            action=f"Book appointment for patient {patient_id}",
            function_name="book_appointment",
            input_data={"patient_id": patient_id, "slot_id": slot_id, "reason": reason, "notes": notes},
            output_data=result,
            success=True,
            dry_run=_DRY_RUN_MODE
        )
        
        return str(result)
    
    except Exception as e:
        error_msg = f"Error booking appointment: {str(e)}"
        audit_logger.log_action(
            action=f"Book appointment failed for patient {patient_id}",
            function_name="book_appointment",
            input_data={"patient_id": patient_id, "slot_id": slot_id, "reason": reason, "notes": notes},
            success=False,
            error_message=error_msg,
            dry_run=_DRY_RUN_MODE
        )
        return f'{{"success": false, "error": "{error_msg}"}}'


# List of all available tools
HEALTHCARE_TOOLS = [
    search_patient,
    check_insurance_eligibility,
    find_available_slots,
    book_appointment
]

