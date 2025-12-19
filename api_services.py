"""
Mock Healthcare API Services
These simulate real healthcare APIs with proper validation and error handling.
In production, these would connect to actual FHIR servers or EMR systems.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
import json
import os
from schemas import (
    Patient, PatientIdentifier, InsuranceEligibility, 
    AppointmentSlot, Appointment, SearchPatientRequest
)


class MockPatientService:
    """Mock patient search service"""
    
    # Mock patient database
    _patients = {
        "12345": Patient(
            id="12345",
            name="Ravi Kumar",
            date_of_birth="1985-05-15",
            identifiers=[PatientIdentifier(system="MRN", value="MRN-12345")]
        ),
        "67890": Patient(
            id="67890",
            name="Jane Smith",
            date_of_birth="1990-08-22",
            identifiers=[PatientIdentifier(system="MRN", value="MRN-67890")]
        ),
        "11111": Patient(
            id="11111",
            name="John Doe",
            date_of_birth="1975-12-10",
            identifiers=[PatientIdentifier(system="MRN", value="MRN-11111")]
        ),
        "22222": Patient(
            id="22222",
            name="Thamaraiselvan Kumar",
            date_of_birth="1992-03-20",
            identifiers=[PatientIdentifier(system="MRN", value="MRN-22222")]
        ),
        "66666": Patient(
            id="66666",
            name="Thamu Selvan",
            date_of_birth="1992-03-20",
            identifiers=[PatientIdentifier(system="MRN", value="MRN-66666")]
        ),
        "33333": Patient(
            id="33333",
            name="Priya Sharma",
            date_of_birth="1988-07-14",
            identifiers=[PatientIdentifier(system="MRN", value="MRN-33333")]
        ),
        "44444": Patient(
            id="44444",
            name="Michael Brown",
            date_of_birth="1983-11-05",
            identifiers=[PatientIdentifier(system="MRN", value="MRN-44444")]
        ),
        "55555": Patient(
            id="55555",
            name="Sarah Williams",
            date_of_birth="1995-01-30",
            identifiers=[PatientIdentifier(system="MRN", value="MRN-55555")]
        ),
        "77777": Patient(
            id="77777",
            name="Deepan Raj",
            date_of_birth="1991-06-12",
            identifiers=[PatientIdentifier(system="MRN", value="MRN-77777")]
        ),
    }
    
    @classmethod
    def search_patient(cls, request: SearchPatientRequest) -> List[Patient]:
        """
        Search for patients by name, ID, or date of birth.
        
        Args:
            request: Search request with search parameters
            
        Returns:
            List of matching patients
        """
        results = []
        
        # Search by patient ID
        if request.patient_id:
            if request.patient_id in cls._patients:
                results.append(cls._patients[request.patient_id])
            return results
        
        # Search by name (case-insensitive partial match)
        if request.name:
            name_lower = request.name.lower()
            for patient in cls._patients.values():
                if name_lower in patient.name.lower():
                    results.append(patient)
        
        # Search by date of birth
        if request.date_of_birth:
            for patient in cls._patients.values():
                if patient.date_of_birth == request.date_of_birth:
                    if patient not in results:
                        results.append(patient)
        
        return results
    
    @classmethod
    def create_patient(cls, name: str, date_of_birth: Optional[str] = None) -> Patient:
        """
        Create a new patient if not found.
        
        Args:
            name: Patient name
            date_of_birth: Date of birth in YYYY-MM-DD format (optional)
            
        Returns:
            Created Patient object
        """
        import random
        # Generate a new patient ID
        patient_id = str(random.randint(10000, 99999))
        while patient_id in cls._patients:
            patient_id = str(random.randint(10000, 99999))
        
        # Use provided DOB or default to a reasonable date
        if not date_of_birth:
            date_of_birth = "1990-01-01"  # Default DOB
        
        # Create patient
        patient = Patient(
            id=patient_id,
            name=name,
            date_of_birth=date_of_birth,
            identifiers=[PatientIdentifier(system="MRN", value=f"MRN-{patient_id}")]
        )
        
        # Add to database
        cls._patients[patient_id] = patient
        
        # Save to JSON file
        cls._save_patients_to_json()
        
        return patient
    
    @classmethod
    def _save_patients_to_json(cls):
        """Save all patients to a JSON file"""
        try:
            patients_data = {}
            for patient_id, patient in cls._patients.items():
                patients_data[patient_id] = {
                    "id": patient.id,
                    "name": patient.name,
                    "date_of_birth": patient.date_of_birth,
                    "identifiers": [{"system": ident.system, "value": ident.value} for ident in patient.identifiers]
                }
            
            json_file = "patients.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(patients_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Don't fail if JSON save fails, just log it
            print(f"Warning: Could not save patients to JSON: {str(e)}")
    
    @classmethod
    def _load_patients_from_json(cls):
        """Load patients from JSON file if it exists"""
        try:
            json_file = "patients.json"
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    patients_data = json.load(f)
                
                for patient_id, patient_data in patients_data.items():
                    # Only add if not already in memory (don't overwrite existing)
                    if patient_id not in cls._patients:
                        identifiers = [
                            PatientIdentifier(system=ident["system"], value=ident["value"])
                            for ident in patient_data.get("identifiers", [])
                        ]
                        patient = Patient(
                            id=patient_data["id"],
                            name=patient_data["name"],
                            date_of_birth=patient_data.get("date_of_birth"),
                            identifiers=identifiers
                        )
                        cls._patients[patient_id] = patient
        except Exception as e:
            # Don't fail if JSON load fails
            print(f"Warning: Could not load patients from JSON: {str(e)}")


# Load patients from JSON when module is imported (after class is fully defined)
MockPatientService._load_patients_from_json()


class MockInsuranceService:
    """Mock insurance eligibility service"""
    
    # Mock insurance database
    _insurance_data = {
        "12345": InsuranceEligibility(
            patient_id="12345",
            insurance_provider="BlueCross BlueShield",
            policy_number="BCBS-987654",
            is_active=True,
            coverage_type="Primary",
            effective_date="2024-01-01",
            expiration_date="2024-12-31"
        ),
        "67890": InsuranceEligibility(
            patient_id="67890",
            insurance_provider="Aetna",
            policy_number="AET-456789",
            is_active=True,
            coverage_type="Primary",
            effective_date="2024-01-01",
            expiration_date="2024-12-31"
        ),
        "11111": InsuranceEligibility(
            patient_id="11111",
            insurance_provider="UnitedHealthcare",
            policy_number="UHC-123456",
            is_active=False,  # Inactive for testing
            coverage_type="Primary",
            effective_date="2023-01-01",
            expiration_date="2023-12-31"
        ),
        "22222": InsuranceEligibility(
            patient_id="22222",
            insurance_provider="Cigna",
            policy_number="CIG-789012",
            is_active=True,
            coverage_type="Primary",
            effective_date="2024-01-01",
            expiration_date="2024-12-31"
        ),
        "33333": InsuranceEligibility(
            patient_id="33333",
            insurance_provider="Humana",
            policy_number="HUM-345678",
            is_active=True,
            coverage_type="Primary",
            effective_date="2024-01-01",
            expiration_date="2024-12-31"
        ),
        "44444": InsuranceEligibility(
            patient_id="44444",
            insurance_provider="Kaiser Permanente",
            policy_number="KP-901234",
            is_active=True,
            coverage_type="Primary",
            effective_date="2024-01-01",
            expiration_date="2024-12-31"
        ),
        "55555": InsuranceEligibility(
            patient_id="55555",
            insurance_provider="Medicaid",
            policy_number="MED-567890",
            is_active=True,
            coverage_type="Primary",
            effective_date="2024-01-01",
            expiration_date="2024-12-31"
        ),
        "66666": InsuranceEligibility(
            patient_id="66666",
            insurance_provider="BlueCross BlueShield",
            policy_number="BCBS-111222",
            is_active=True,
            coverage_type="Primary",
            effective_date="2024-01-01",
            expiration_date="2024-12-31"
        ),
        "77777": InsuranceEligibility(
            patient_id="77777",
            insurance_provider="Aetna",
            policy_number="AET-777777",
            is_active=True,
            coverage_type="Primary",
            effective_date="2024-01-01",
            expiration_date="2024-12-31"
        ),
    }
    
    @classmethod
    def check_eligibility(cls, patient_id: str) -> Optional[InsuranceEligibility]:
        """
        Check insurance eligibility for a patient.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Insurance eligibility information or None if not found
        """
        return cls._insurance_data.get(patient_id)


class MockAppointmentService:
    """Mock appointment scheduling service"""
    
    # Mock providers database
    _providers = {
        "PROV-001": {"name": "Dr. Sarah Johnson", "specialty": "Cardiology"},
        "PROV-002": {"name": "Dr. Michael Chen", "specialty": "Neurology"},
        "PROV-003": {"name": "Dr. Emily Rodriguez", "specialty": "Cardiology"},
        "PROV-004": {"name": "Dr. David Kim", "specialty": "General Medicine"},
        "PROV-005": {"name": "Dr. James Wilson", "specialty": "Orthopedics"},
        "PROV-006": {"name": "Dr. Lisa Anderson", "specialty": "Orthopedics"},
        "PROV-007": {"name": "Dr. Robert Taylor", "specialty": "Dermatology"},
        "PROV-008": {"name": "Dr. Maria Garcia", "specialty": "Pediatrics"},
        "PROV-009": {"name": "Dr. Jennifer Martinez", "specialty": "Oncology"},
        "PROV-010": {"name": "Dr. Thomas Brown", "specialty": "Oncology"},
        "PROV-011": {"name": "Dr. Patricia White", "specialty": "Psychiatry"},
        "PROV-012": {"name": "Dr. Christopher Lee", "specialty": "Psychiatry"},
    }
    
    # Mock appointments database (to prevent double-booking)
    _appointments: Dict[str, Appointment] = {}
    
    @classmethod
    def find_available_slots(
        cls, 
        specialty: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[AppointmentSlot]:
        """
        Find available appointment slots for a specialty.
        
        Args:
            specialty: Medical specialty (e.g., "Cardiology", "Neurology")
            start_date: Start date for search (ISO format, optional)
            end_date: End date for search (ISO format, optional)
            
        Returns:
            List of available appointment slots
        """
        slots = []
        
        # Filter providers by specialty
        matching_providers = [
            (pid, pdata) for pid, pdata in cls._providers.items()
            if pdata["specialty"].lower() == specialty.lower()
        ]
        
        if not matching_providers:
            return slots
        
        # Generate slots for next week (default)
        base_date = datetime.now()
        if start_date:
            try:
                base_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                pass
        
        # Generate 3 slots per provider for the next 7 days
        for day_offset in range(7):
            slot_date = base_date + timedelta(days=day_offset)
            
            # Skip weekends for simplicity
            if slot_date.weekday() >= 5:
                continue
            
            for provider_id, provider_data in matching_providers:
                # Generate morning and afternoon slots
                for hour in [9, 10, 11, 14, 15, 16]:
                    slot_start = slot_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    slot_end = slot_start + timedelta(minutes=30)
                    
                    slot_id = f"SLOT-{provider_id}-{slot_start.strftime('%Y%m%d%H%M')}"
                    
                    # Check if slot is already booked
                    if slot_id not in [apt.slot_id for apt in cls._appointments.values()]:
                        slots.append(AppointmentSlot(
                            slot_id=slot_id,
                            provider_name=provider_data["name"],
                            provider_id=provider_id,
                            specialty=provider_data["specialty"],
                            start_time=slot_start.isoformat() + "Z",
                            end_time=slot_end.isoformat() + "Z",
                            location="Main Hospital, Floor 3"
                        ))
        
        return slots[:10]  # Return max 10 slots (can be reduced to 5 for shorter output)
    
    @classmethod
    def book_appointment(
        cls,
        patient_id: str,
        slot_id: str,
        reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Appointment:
        """
        Book an appointment.
        
        Args:
            patient_id: Patient ID
            slot_id: Slot ID to book
            reason: Reason for visit
            notes: Additional notes
            
        Returns:
            Confirmed appointment
            
        Raises:
            ValueError: If slot is invalid or already booked
        """
        # Find the slot details
        slot = None
        for provider_id, provider_data in cls._providers.items():
            if provider_id in slot_id:
                # Reconstruct slot info
                specialty = provider_data["specialty"]
                provider_name = provider_data["name"]
                # Extract datetime from slot_id
                try:
                    date_str = slot_id.split('-')[-1]
                    slot_start = datetime.strptime(date_str, '%Y%m%d%H%M')
                    slot_end = slot_start + timedelta(minutes=30)
                    slot = AppointmentSlot(
                        slot_id=slot_id,
                        provider_name=provider_name,
                        provider_id=provider_id,
                        specialty=specialty,
                        start_time=slot_start.isoformat() + "Z",
                        end_time=slot_end.isoformat() + "Z",
                        location="Main Hospital, Floor 3"
                    )
                except:
                    pass
                break
        
        if not slot:
            raise ValueError(f"Invalid slot ID: {slot_id}")
        
        # Check if already booked
        if slot_id in [apt.slot_id for apt in cls._appointments.values()]:
            raise ValueError(f"Slot {slot_id} is already booked")
        
        # Get patient info
        patient = MockPatientService._patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient not found: {patient_id}")
        
        # Create appointment
        appointment_id = f"APT-{random.randint(1000, 9999)}"
        appointment = Appointment(
            appointment_id=appointment_id,
            patient_id=patient_id,
            patient_name=patient.name,
            provider_name=slot.provider_name,
            provider_id=slot.provider_id,
            specialty=slot.specialty,
            start_time=slot.start_time,
            end_time=slot.end_time,
            location=slot.location,
            slot_id=slot_id,
            status="confirmed"
        )
        
        # Store appointment
        cls._appointments[appointment_id] = appointment
        
        return appointment
    
    @classmethod
    def get_all_appointments(cls) -> List[Appointment]:
        """
        Get all appointments.
        
        Returns:
            List of all appointments
        """
        return list(cls._appointments.values())
    
    @classmethod
    def cancel_appointment(cls, appointment_id: str) -> bool:
        """
        Cancel an appointment and free the slot.
        
        Args:
            appointment_id: Appointment ID to cancel
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        if appointment_id in cls._appointments:
            appointment = cls._appointments[appointment_id]
            appointment.status = "cancelled"
            # Remove from active appointments (slot is now free)
            del cls._appointments[appointment_id]
            return True
        return False
    
    @classmethod
    def complete_appointment(cls, appointment_id: str) -> bool:
        """
        Mark an appointment as completed and free the slot.
        
        Args:
            appointment_id: Appointment ID to complete
            
        Returns:
            True if completed successfully, False otherwise
        """
        if appointment_id in cls._appointments:
            appointment = cls._appointments[appointment_id]
            appointment.status = "completed"
            # Remove from active appointments (slot is now free)
            del cls._appointments[appointment_id]
            return True
        return False

