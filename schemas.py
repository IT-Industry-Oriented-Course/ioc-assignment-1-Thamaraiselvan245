"""
FHIR-style Pydantic schemas for healthcare data validation.
These schemas ensure type safety and validation for all API interactions.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class PatientIdentifier(BaseModel):
    """FHIR Patient Identifier"""
    system: str = Field(..., description="Identifier system (e.g., 'MRN', 'SSN')")
    value: str = Field(..., description="Identifier value")


class Patient(BaseModel):
    """FHIR Patient Resource"""
    id: Optional[str] = Field(None, description="Patient ID")
    name: str = Field(..., description="Patient full name")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    identifiers: List[PatientIdentifier] = Field(default_factory=list, description="Patient identifiers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "12345",
                "name": "Ravi Kumar",
                "date_of_birth": "1985-05-15",
                "identifiers": [{"system": "MRN", "value": "MRN-12345"}]
            }
        }


class InsuranceEligibility(BaseModel):
    """Insurance Eligibility Response"""
    patient_id: str = Field(..., description="Patient ID")
    insurance_provider: str = Field(..., description="Insurance provider name")
    policy_number: str = Field(..., description="Policy number")
    is_active: bool = Field(..., description="Whether insurance is active")
    coverage_type: str = Field(..., description="Type of coverage (e.g., 'Primary', 'Secondary')")
    effective_date: Optional[str] = Field(None, description="Effective date")
    expiration_date: Optional[str] = Field(None, description="Expiration date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "12345",
                "insurance_provider": "BlueCross BlueShield",
                "policy_number": "BCBS-987654",
                "is_active": True,
                "coverage_type": "Primary",
                "effective_date": "2024-01-01",
                "expiration_date": "2024-12-31"
            }
        }


class AppointmentSlot(BaseModel):
    """Available Appointment Slot"""
    slot_id: str = Field(..., description="Unique slot identifier")
    provider_name: str = Field(..., description="Healthcare provider name")
    provider_id: str = Field(..., description="Provider ID")
    specialty: str = Field(..., description="Medical specialty")
    start_time: str = Field(..., description="Start time (ISO 8601 format)")
    end_time: str = Field(..., description="End time (ISO 8601 format)")
    location: str = Field(..., description="Appointment location")
    
    class Config:
        json_schema_extra = {
            "example": {
                "slot_id": "SLOT-001",
                "provider_name": "Dr. Sarah Johnson",
                "provider_id": "PROV-001",
                "specialty": "Cardiology",
                "start_time": "2024-03-15T10:00:00Z",
                "end_time": "2024-03-15T10:30:00Z",
                "location": "Main Hospital, Floor 3"
            }
        }


class AppointmentRequest(BaseModel):
    """Appointment Booking Request"""
    patient_id: str = Field(..., description="Patient ID")
    slot_id: str = Field(..., description="Appointment slot ID")
    reason: Optional[str] = Field(None, description="Reason for visit")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @validator('patient_id', 'slot_id')
    def validate_ids(cls, v):
        if not v or not v.strip():
            raise ValueError("ID cannot be empty")
        return v.strip()


class Appointment(BaseModel):
    """Confirmed Appointment"""
    appointment_id: str = Field(..., description="Unique appointment identifier")
    patient_id: str = Field(..., description="Patient ID")
    patient_name: str = Field(..., description="Patient name")
    provider_name: str = Field(..., description="Provider name")
    provider_id: str = Field(..., description="Provider ID")
    specialty: str = Field(..., description="Specialty")
    start_time: str = Field(..., description="Start time")
    end_time: str = Field(..., description="End time")
    location: str = Field(..., description="Location")
    slot_id: str = Field(..., description="Slot ID that was booked")
    status: str = Field(default="confirmed", description="Appointment status")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "appointment_id": "APT-001",
                "patient_id": "12345",
                "patient_name": "Ravi Kumar",
                "provider_name": "Dr. Sarah Johnson",
                "provider_id": "PROV-001",
                "specialty": "Cardiology",
                "start_time": "2024-03-15T10:00:00Z",
                "end_time": "2024-03-15T10:30:00Z",
                "location": "Main Hospital, Floor 3",
                "status": "confirmed"
            }
        }


class SearchPatientRequest(BaseModel):
    """Patient Search Request"""
    name: Optional[str] = Field(None, description="Patient name (partial or full)")
    patient_id: Optional[str] = Field(None, description="Patient ID")
    date_of_birth: Optional[str] = Field(None, description="Date of birth")
    
    @validator('*', pre=True, always=True)
    def validate_at_least_one(cls, v, values):
        # This runs after all fields are set, so we check in model_validator instead
        return v
    
    @classmethod
    def validate_at_least_one_field(cls, values):
        if not values.get('name') and not values.get('patient_id') and not values.get('date_of_birth'):
            raise ValueError("At least one search parameter must be provided")
        return values


class AuditLog(BaseModel):
    """Audit Log Entry"""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    action: str = Field(..., description="Action performed")
    function_name: str = Field(..., description="Function called")
    input_data: dict = Field(..., description="Input parameters")
    output_data: Optional[dict] = Field(None, description="Output/result")
    success: bool = Field(..., description="Whether action succeeded")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    dry_run: bool = Field(default=False, description="Whether this was a dry run")

