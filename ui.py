"""
Healthcare Workflow UI - Streamlit Application
Clean, modern UI for all healthcare workflow functions
"""

import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

# Import healthcare functions and services
from functions import (
    search_patient,
    check_insurance_eligibility,
    find_available_slots,
    book_appointment
)
from api_services import MockPatientService, MockInsuranceService, MockAppointmentService
from schemas import SearchPatientRequest

# Import agent for chat interface
try:
    from agent import ClinicalWorkflowAgent
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    ClinicalWorkflowAgent = None

# Helper function to call LangChain tools
# LangChain @tool decorator wraps functions, so we need to use .invoke() method
def call_tool(tool_func, **kwargs):
    """Call a LangChain tool with the given arguments"""
    if hasattr(tool_func, 'invoke'):
        # It's a LangChain tool, use invoke method
        return tool_func.invoke(kwargs)
    else:
        # It's a regular function, call it directly
        return tool_func(**kwargs)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Healthcare Workflow System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .patient-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .slot-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)


def format_datetime(dt_str: str) -> str:
    """Format ISO datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%A, %B %d, %Y at %I:%M %p")
    except:
        return dt_str


def display_patient_search_results(result: str):
    """Display patient search results in a clean format"""
    try:
        data = eval(result) if isinstance(result, str) else result
        
        if not data.get("success"):
            st.error(f"❌ Error: {data.get('error', 'Unknown error')}")
            return
        
        count = data.get("count", 0)
        patients = data.get("patients", [])
        
        if count == 0:
            st.info("No patients found matching your search criteria.")
            return
        
        st.success(f"✅ Found {count} patient(s)")
        
        for patient in patients:
            with st.container():
                st.markdown(f"""
                <div class="patient-card">
                    <h4>👤 {patient.get('name', 'N/A')}</h4>
                    <p><strong>Patient ID:</strong> {patient.get('id', 'N/A')}</p>
                    <p><strong>Date of Birth:</strong> {patient.get('date_of_birth', 'N/A')}</p>
                    {f"<p><strong>MRN:</strong> {patient.get('identifiers', [{}])[0].get('value', 'N/A')}</p>" if patient.get('identifiers') else ""}
                </div>
                """, unsafe_allow_html=True)
                st.markdown("---")
    
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")
        st.json(result)


def display_insurance_results(result: str):
    """Display insurance eligibility results"""
    try:
        data = eval(result) if isinstance(result, str) else result
        
        if not data.get("success"):
            st.error(f"❌ {data.get('error', 'No insurance information found')}")
            return
        
        eligibility = data.get("eligibility", {})
        
        st.success("✅ Insurance Eligibility Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="info-box">
                <h4>📋 Insurance Details</h4>
                <p><strong>Provider:</strong> {eligibility.get('insurance_provider', 'N/A')}</p>
                <p><strong>Policy Number:</strong> {eligibility.get('policy_number', 'N/A')}</p>
                <p><strong>Coverage Type:</strong> {eligibility.get('coverage_type', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            status_color = "#28a745" if eligibility.get('is_active') else "#dc3545"
            status_text = "✅ Active" if eligibility.get('is_active') else "❌ Inactive"
            st.markdown(f"""
            <div class="info-box">
                <h4>📊 Status</h4>
                <p><strong>Status:</strong> <span style="color: {status_color};">{status_text}</span></p>
                <p><strong>Effective Date:</strong> {eligibility.get('effective_date', 'N/A')}</p>
                <p><strong>Expiration Date:</strong> {eligibility.get('expiration_date', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")
        st.json(result)


def display_slots_results(result: str):
    """Display available appointment slots in a simplified, clean format"""
    try:
        data = eval(result) if isinstance(result, str) else result
        
        if not data.get("success"):
            st.error(f"❌ Error: {data.get('error', 'Unknown error')}")
            return
        
        count = data.get("count", 0)
        slots = data.get("slots", [])
        
        if count == 0:
            st.info("No available slots found for the selected specialty.")
            return
        
        st.success(f"✅ Found {count} available appointment slot(s)")
        
        # Group by provider
        providers = {}
        for slot in slots:
            provider = slot.get('provider_name', 'Unknown')
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(slot)
        
        # Simplified, compact display
        for provider_name, provider_slots in providers.items():
            specialty = provider_slots[0].get('specialty', 'N/A')
            location = provider_slots[0].get('location', 'N/A')
            
            with st.expander(f"👨‍⚕️ {provider_name} - {specialty} ({len(provider_slots)} slots)", expanded=True):
                # Simple list format
                for slot in provider_slots[:15]:  # Show max 15 slots
                    time_str = format_datetime(slot.get('start_time', ''))
                    slot_id = slot.get('slot_id', 'N/A')
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"📅 {time_str}")
                    with col2:
                        st.code(slot_id, language=None)
                
                if len(provider_slots) > 15:
                    st.caption(f"*... and {len(provider_slots) - 15} more slots*")
                
                st.caption(f"📍 {location}")
    
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")
        st.json(result)


def display_appointment_results(result: str):
    """Display appointment booking results"""
    try:
        data = eval(result) if isinstance(result, str) else result
        
        if not data.get("success"):
            st.error(f"❌ Error: {data.get('error', 'Booking failed')}")
            return
        
        if data.get("dry_run"):
            st.warning("⚠️ DRY RUN MODE - No actual appointment was booked")
            st.info(f"✅ Validation successful: {data.get('message', 'Appointment validated')}")
            st.info(f"Patient: {data.get('patient_name', 'N/A')}")
            return
        
        appointment = data.get("appointment", {})
        
        st.success("✅ Appointment Booked Successfully!")
        
        st.markdown(f"""
        <div class="success-box">
            <h3>📅 Appointment Confirmed</h3>
            <p><strong>Appointment ID:</strong> {appointment.get('appointment_id', 'N/A')}</p>
            <p><strong>Patient:</strong> {appointment.get('patient_name', 'N/A')} (ID: {appointment.get('patient_id', 'N/A')})</p>
            <p><strong>Provider:</strong> {appointment.get('provider_name', 'N/A')}</p>
            <p><strong>Specialty:</strong> {appointment.get('specialty', 'N/A')}</p>
            <p><strong>Date & Time:</strong> {format_datetime(appointment.get('start_time', ''))}</p>
            <p><strong>Location:</strong> {appointment.get('location', 'N/A')}</p>
            <p><strong>Status:</strong> {appointment.get('status', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")
        st.json(result)


def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Healthcare Workflow System</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        dry_run = st.checkbox("Dry Run Mode", value=False, help="Enable dry-run mode to validate without making actual changes")
        
        st.markdown("---")
        st.header("📊 Quick Stats")
        
        # Get stats from mock services
        total_patients = len(MockPatientService._patients)
        total_providers = len(MockAppointmentService._providers)
        booked_appointments = len(MockAppointmentService._appointments)
        
        st.metric("Total Patients", total_patients)
        st.metric("Available Providers", total_providers)
        st.metric("Booked Appointments", booked_appointments)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This system provides a clean interface for:
        - Patient search
        - Insurance eligibility checks
        - Appointment slot finding
        - Appointment booking
        """)
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Chat Assistant",
        "🔍 Search Patient",
        "💳 Check Insurance",
        "📅 Find Appointments",
        "📋 Booked Appointments"
    ])
    
    # Tab 0: Chat Assistant
    with tab1:
        st.markdown('<h2 class="sub-header">💬 Chat with Healthcare Assistant</h2>', unsafe_allow_html=True)
        st.markdown("Ask me anything about patient search, insurance checks, or appointment scheduling!")
        
        # Initialize agent if available
        if AGENT_AVAILABLE:
            # Initialize session state for chat
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []
            
            if "agent" not in st.session_state:
                try:
                    with st.spinner("Initializing AI agent..."):
                        api_key = os.getenv("HUGGINGFACE_API_KEY")
                        if not api_key:
                            try:
                                from config import Config
                                api_key = Config.get_huggingface_key()
                            except:
                                pass
                        
                        if api_key:
                            st.session_state.agent = ClinicalWorkflowAgent(
                                api_key=api_key,
                                dry_run=dry_run
                            )
                            st.session_state.agent_ready = True
                        else:
                            st.session_state.agent = None
                            st.session_state.agent_ready = False
                except Exception as e:
                    st.error(f"Failed to initialize agent: {str(e)}")
                    st.session_state.agent = None
                    st.session_state.agent_ready = False
            
            # Display chat messages
            chat_container = st.container()
            with chat_container:
                for idx, message in enumerate(st.session_state.chat_messages):
                    if message["role"] == "user":
                        with st.chat_message("user"):
                            st.write(message["content"])
                    else:
                        with st.chat_message("assistant"):
                            # Display the text response
                            response_text = message["content"]
                            
                            # Check if we have structured data to display nicely
                            if message.get("data") and isinstance(message["data"], dict):
                                data = message["data"]
                                
                                # Try to parse and display structured results
                                if data.get("success") and data.get("response"):
                                    response_str = data.get("response", "")
                                    
                                    # Try to extract and display patient search results (only if patients found)
                                    if "Patient Search:" in response_str:
                                        try:
                                            # Extract patient data from response
                                            import re
                                            patient_match = re.search(r'Patient Search:\s*(\{.*?"patients".*?\})', response_str, re.DOTALL)
                                            if patient_match:
                                                patient_data = eval(patient_match.group(1))
                                                if patient_data.get("success") and patient_data.get("patients"):
                                                    patients = patient_data.get("patients", [])
                                                    if patients:  # Only show if patients found
                                                        st.success(f"✅ Found {len(patients)} patient(s)")
                                                        for patient in patients[:5]:
                                                            st.markdown(f"""
                                                            <div class="patient-card">
                                                                <strong>👤 {patient.get('name', 'N/A')}</strong><br>
                                                                Patient ID: {patient.get('id', 'N/A')} | DOB: {patient.get('date_of_birth', 'N/A')}
                                                            </div>
                                                            """, unsafe_allow_html=True)
                                                        # Remove from response text
                                                        response_text = response_str.replace(patient_match.group(0), "").strip()
                                                else:
                                                    # Hide empty patient search results
                                                    response_text = response_str.replace(patient_match.group(0), "").strip()
                                        except:
                                            pass
                                    
                                    # Try to extract and display insurance results
                                    elif "Insurance Check:" in response_str or "eligibility" in response_str.lower():
                                        try:
                                            import re
                                            ins_match = re.search(r'\{.*"eligibility".*\}', response_str, re.DOTALL)
                                            if ins_match:
                                                ins_data = eval(ins_match.group())
                                                if ins_data.get("success") and ins_data.get("eligibility"):
                                                    elig = ins_data["eligibility"]
                                                    st.success("✅ Insurance Eligibility Information")
                                                    col1, col2 = st.columns(2)
                                                    with col1:
                                                        st.markdown(f"""
                                                        **Provider:** {elig.get('insurance_provider', 'N/A')}<br>
                                                        **Policy:** {elig.get('policy_number', 'N/A')}<br>
                                                        **Coverage:** {elig.get('coverage_type', 'N/A')}
                                                        """)
                                                    with col2:
                                                        status = "✅ Active" if elig.get('is_active') else "❌ Inactive"
                                                        st.markdown(f"**Status:** {status}")
                                                    response_text = response_str.replace(ins_match.group(), "").strip()
                                        except:
                                            pass
                                    
                                    # Try to extract and display appointment slots (only if not booking)
                                    if "Available Slots:" in response_str and "Booked Appointment:" not in response_str:
                                        try:
                                            import re
                                            slots_match = re.search(r'Available Slots:\s*(\{.*?"slots".*?\})', response_str, re.DOTALL)
                                            if slots_match:
                                                slots_data = eval(slots_match.group(1))
                                                if slots_data.get("success") and slots_data.get("slots"):
                                                    st.success(f"✅ Found {slots_data.get('count', 0)} available slot(s)")
                                                    display_slots_results(str(slots_data))
                                                    # Remove from response text
                                                    response_text = response_str.replace(slots_match.group(0), "").strip()
                                        except:
                                            pass
                                    
                                    # Try to extract and display patient creation
                                    if "Created New Patient:" in response_str:
                                        try:
                                            import re
                                            # Extract "Created New Patient: Name (ID: xxxxx)"
                                            created_match = re.search(r'Created New Patient:\s*([^(]+)\s*\(ID:\s*([^)]+)\)', response_str)
                                            if created_match:
                                                patient_name = created_match.group(1).strip()
                                                patient_id = created_match.group(2).strip()
                                                st.success(f"✅ **New Patient Created:** {patient_name} (ID: {patient_id})")
                                                response_text = response_str.replace(created_match.group(0), "").strip()
                                        except:
                                            pass
                                    
                                    # Try to extract and display appointment booking
                                    if "Booked Appointment:" in response_str:
                                        try:
                                            import re
                                            # Try to find the appointment data
                                            appt_match = re.search(r'Booked Appointment:\s*(\{.*?\})', response_str, re.DOTALL)
                                            if appt_match:
                                                appt_data_str = appt_match.group(1)
                                                appt_data = eval(appt_data_str)
                                                display_appointment_results(str(appt_data))
                                                response_text = response_str.replace(appt_match.group(0), "").strip()
                                            # Also check for appointment in the response
                                            elif '"appointment"' in response_str:
                                                appt_match = re.search(r'\{.*"appointment".*?\}', response_str, re.DOTALL)
                                                if appt_match:
                                                    appt_data = eval(appt_match.group())
                                                    display_appointment_results(str(appt_data))
                                                    response_text = response_str.replace(appt_match.group(), "").strip()
                                        except Exception as e:
                                            # If parsing fails, try to show the raw booking message
                                            if "Booked Appointment:" in response_str:
                                                booking_msg = response_str.split("Booked Appointment:")[-1].split("\n")[0]
                                                st.success(f"✅ **Appointment Booked:** {booking_msg[:100]}")
                                                response_text = response_str.replace("Booked Appointment:", "").strip()
                                            pass
                            
                            # Display the response text
                            if response_text and response_text.strip():
                                st.markdown(response_text)
            
            # Chat input
            if st.session_state.agent_ready:
                user_query = st.chat_input("Type your question here... (e.g., 'Find patient Ravi Kumar' or 'Check insurance for patient 12345')")
                
                if user_query:
                    # Add user message to chat
                    st.session_state.chat_messages.append({
                        "role": "user",
                        "content": user_query
                    })
                    
                    # Get agent response
                    with st.spinner("Processing your request..."):
                        try:
                            response = st.session_state.agent.run(user_query)
                            
                            # Format response
                            if response.get("error") == "REFUSED":
                                response_text = f"❌ {response.get('message', 'Request refused')}\n\n💡 {response.get('suggestion', '')}"
                            elif not response.get("success"):
                                response_text = f"❌ Error: {response.get('message', 'Unknown error')}\n\n💡 {response.get('suggestion', '')}"
                            else:
                                response_text = response.get("response", "No response")
                                if response.get("dry_run"):
                                    response_text += "\n\n⚠️ **DRY RUN MODE** - No actual changes were made"
                            
                            # Add assistant response to chat
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "content": response_text,
                                "data": response
                            })
                            
                            # Rerun to show new messages
                            st.rerun()
                            
                        except Exception as e:
                            error_msg = f"Error processing request: {str(e)}"
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "content": f"❌ {error_msg}"
                            })
                            st.rerun()
            else:
                st.warning("⚠️ AI Agent not available. Please set HUGGINGFACE_API_KEY environment variable.")
                st.info("""
                **To enable the chat assistant:**
                1. Get your HuggingFace API key from: https://huggingface.co/settings/tokens
                2. Set it as an environment variable: `HUGGINGFACE_API_KEY=your_key`
                3. Or create a `.env` file with: `HUGGINGFACE_API_KEY=your_key`
                4. Refresh this page
                """)
            
            # Example queries
            st.markdown("---")
            with st.expander("💡 Example Queries"):
                st.markdown("""
                **Try asking:**
                - "Search for patient Ravi Kumar"
                - "Find patient with ID 12345"
                - "Check insurance eligibility for patient 12345"
                - "Find available cardiology appointments"
                - "Show me neurology slots for next week"
                - "Schedule a cardiology follow-up for patient Ravi Kumar and check insurance"
                """)
        else:
            st.warning("⚠️ Agent module not available. Using form-based interface only.")
            st.info("The chat assistant requires the agent module. Use the other tabs for form-based interactions.")
    
    # Tab 2: Search Patient
    with tab2:
        st.markdown('<h2 class="sub-header">Search for Patients</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            patient_name = st.text_input("Patient Name", placeholder="e.g., Ravi Kumar")
        
        with col2:
            patient_id = st.text_input("Patient ID", placeholder="e.g., 12345")
        
        with col3:
            date_of_birth = st.date_input(
                "Date of Birth",
                value=None,
                min_value=datetime(1900, 1, 1),
                max_value=datetime.now()
            )
            dob_str = date_of_birth.strftime("%Y-%m-%d") if date_of_birth else None
        
        if st.button("🔍 Search Patient", type="primary", use_container_width=True):
            if not patient_name and not patient_id and not dob_str:
                st.warning("⚠️ Please provide at least one search parameter")
            else:
                with st.spinner("Searching for patients..."):
                    try:
                        result = call_tool(
                            search_patient,
                            name=patient_name if patient_name else None,
                            patient_id=patient_id if patient_id else None,
                            date_of_birth=dob_str
                        )
                        display_patient_search_results(result)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Show example patients
        with st.expander("📋 Example Patient IDs"):
            example_patients = list(MockPatientService._patients.values())[:5]
            for patient in example_patients:
                st.text(f"ID: {patient.id} | Name: {patient.name} | DOB: {patient.date_of_birth}")
    
    # Tab 3: Check Insurance
    with tab3:
        st.markdown('<h2 class="sub-header">Check Insurance Eligibility</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            insurance_patient_id = st.text_input(
                "Patient ID",
                placeholder="Enter patient ID to check insurance",
                key="insurance_patient_id"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
        
        if st.button("💳 Check Insurance", type="primary", use_container_width=True):
            if not insurance_patient_id:
                st.warning("⚠️ Please enter a patient ID")
            else:
                with st.spinner("Checking insurance eligibility..."):
                    try:
                        result = call_tool(check_insurance_eligibility, patient_id=insurance_patient_id)
                        display_insurance_results(result)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Show example
        with st.expander("💡 Example Patient IDs with Insurance"):
            st.text("12345 - BlueCross BlueShield (Active)")
            st.text("67890 - Aetna (Active)")
            st.text("22222 - Cigna (Active)")
    
    # Tab 4: Find Appointments
    with tab4:
        st.markdown('<h2 class="sub-header">Find Available Appointment Slots</h2>', unsafe_allow_html=True)
        
        # Define specialties list
        specialties = [
            "Cardiology",
            "Neurology",
            "General Medicine",
            "Orthopedics",
            "Dermatology",
            "Pediatrics",
            "Oncology",
            "Psychiatry"
        ]
        
        # Specialty input section - both dropdown and text input
        st.markdown("### 📋 Select or Enter Medical Specialty")
        col_spec1, col_spec2 = st.columns([1, 1])
        
        with col_spec1:
            specialty_dropdown = st.selectbox(
                "Choose from List",
                ["Select a specialty..."] + specialties,
                key="specialty_dropdown"
            )
        
        with col_spec2:
            specialty_text = st.text_input(
                "Or Type Specialty Name",
                placeholder="e.g., Cardiology, Neurology, etc.",
                key="specialty_text"
            )
        
        # Determine which specialty to use
        if specialty_text and specialty_text.strip():
            specialty = specialty_text.strip()
        elif specialty_dropdown and specialty_dropdown != "Select a specialty...":
            specialty = specialty_dropdown
        else:
            specialty = None
        
        # Show selected specialty
        if specialty:
            st.info(f"🔍 Selected Specialty: **{specialty}**")
        
        # Date filters
        st.markdown("### 📅 Filter by Date Range (Optional)")
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date (Optional)",
                value=None,
                min_value=datetime.now().date(),
                help="Leave empty to search from today"
            )
            start_date_str = start_date.strftime("%Y-%m-%d") if start_date else None
        
        with col2:
            end_date = st.date_input(
                "End Date (Optional)",
                value=None,
                min_value=start_date if start_date else datetime.now().date(),
                help="Leave empty to search up to 7 days ahead"
            )
            end_date_str = end_date.strftime("%Y-%m-%d") if end_date else None
        
        # Search button
        search_disabled = not specialty
        if st.button("📅 Find Available Slots", type="primary", use_container_width=True, disabled=search_disabled):
            with st.spinner(f"Searching for available {specialty} slots..."):
                try:
                    result = call_tool(
                        find_available_slots,
                        specialty=specialty,
                        start_date=start_date_str,
                        end_date=end_date_str
                    )
                    display_slots_results(result)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        if not specialty:
            st.warning("⚠️ Please select or enter a medical specialty to search for slots")
        
        # Quick examples
        with st.expander("💡 Quick Examples"):
            st.markdown("""
            **Try these specialties:**
            - Cardiology
            - Neurology  
            - General Medicine
            - Orthopedics
            - Dermatology
            - Pediatrics
            - Oncology
            - Psychiatry
            """)
    
    # Tab 5: Booked Appointments List
    with tab5:
        st.markdown('<h2 class="sub-header">📋 Booked Appointments</h2>', unsafe_allow_html=True)
        
        # Get all appointments
        appointments = MockAppointmentService.get_all_appointments()
        
        if not appointments:
            st.info("📭 No appointments booked yet. Use the Chat Assistant or Find Appointments tab to book appointments.")
        else:
            st.success(f"✅ Found {len(appointments)} booked appointment(s)")
            
            # Display each appointment in a compact format
            for appointment in appointments:
                status = appointment.status
                status_color = {
                    "confirmed": "#28a745",
                    "cancelled": "#dc3545",
                    "completed": "#17a2b8"
                }.get(status, "#6c757d")
                
                status_bg_color = {
                    "confirmed": "#d4edda",
                    "cancelled": "#f8d7da",
                    "completed": "#d1ecf1"
                }.get(status, "#f8f9fa")
                
                status_emoji = {
                    "confirmed": "✅",
                    "cancelled": "❌",
                    "completed": "✓"
                }.get(status, "📅")
                
                with st.container():
                    col1, col2, col3 = st.columns([4, 1, 1])
                    
                    with col1:
                        # Compact card design with clearer name display
                        st.markdown(f"""
                        <div style="padding: 0.75rem; border-radius: 0.5rem; background-color: {status_bg_color}; border-left: 4px solid {status_color}; margin: 0.5rem 0;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong style="font-size: 1.1rem; color: #212529;">👤 {appointment.patient_name}</strong> | 
                                    <span style="color: {status_color}; font-weight: bold; font-size: 0.95rem;">{status.upper()}</span> | 
                                    <span style="color: #6c757d; font-size: 0.9rem;">ID: {appointment.appointment_id}</span>
                                </div>
                            </div>
                            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #495057;">
                                👨‍⚕️ {appointment.provider_name} • {appointment.specialty} • 
                                📅 {format_datetime(appointment.start_time)} • 
                                📍 {appointment.location}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if status == "confirmed":
                            if st.button("🗑️ Remove", key=f"remove_{appointment.appointment_id}", use_container_width=True):
                                try:
                                    success = MockAppointmentService.cancel_appointment(appointment.appointment_id)
                                    if success:
                                        st.success("✅ Cancelled & slot freed!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                    
                    with col3:
                        if status == "confirmed":
                            if st.button("✓ Complete", key=f"complete_{appointment.appointment_id}", use_container_width=True):
                                try:
                                    success = MockAppointmentService.complete_appointment(appointment.appointment_id)
                                    if success:
                                        st.success("✅ Completed & slot freed!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
    
    


if __name__ == "__main__":
    main()

