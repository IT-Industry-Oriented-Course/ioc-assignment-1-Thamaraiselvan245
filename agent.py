"""
LangChain Function-Calling Agent for Clinical Workflow Automation
This agent uses HuggingFace models with function calling capabilities.
"""

import os
import json
import re
from typing import Optional, List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
try:
    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
except ImportError:
    try:
        from langchain_community.chat_models import ChatHuggingFace
        HuggingFaceEndpoint = None
    except ImportError:
        ChatHuggingFace = None
        HuggingFaceEndpoint = None

from functions import HEALTHCARE_TOOLS, set_dry_run_mode


class ClinicalWorkflowAgent:
    """
    Function-calling LLM agent for clinical workflow automation.
    Acts as an intelligent orchestrator, not a medical advisor.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "meta-llama/Meta-Llama-3.1-8B-Instruct", dry_run: bool = False):
        """
        Initialize the clinical workflow agent.
        
        Args:
            api_key: HuggingFace API key (if None, reads from environment)
            model_name: HuggingFace model name
            dry_run: Enable dry-run mode (no actual API calls)
        """
        self.dry_run = dry_run
        
        # Set dry-run mode in functions module
        set_dry_run_mode(dry_run)
        
        # Get API key from parameter, config, or environment
        if api_key is None:
            try:
                from config import Config
                api_key = Config.get_huggingface_key()
            except ImportError:
                api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        if not api_key:
            try:
                from config import Config
                Config.print_setup_instructions()
            except ImportError:
                pass
            raise ValueError(
                "HuggingFace API key is required.\n"
                "Set HUGGINGFACE_API_KEY environment variable or pass api_key parameter.\n"
                "Get your API key from: https://huggingface.co/settings/tokens"
            )
        
        # Initialize HuggingFace LLM
        # Try multiple initialization methods for compatibility
        self.llm = None
        last_error = None
        
        # Method 1: Try HuggingFaceEndpoint (Inference API) - most reliable
        if HuggingFaceEndpoint is not None:
            try:
                self.llm = HuggingFaceEndpoint(
                    repo_id=model_name,
                    huggingfacehub_api_token=api_key,
                    task="text-generation",
                    temperature=0.1,
                    max_new_tokens=512,
                )
            except Exception as e:
                last_error = e
        
        # Method 2: Try ChatHuggingFace with different parameter combinations
        if self.llm is None and ChatHuggingFace is not None:
            for params in [
                {"model": model_name, "huggingfacehub_api_token": api_key, "temperature": 0.1, "max_tokens": 512},
                {"model_name": model_name, "huggingfacehub_api_token": api_key, "temperature": 0.1},
                {"model": model_name, "api_key": api_key, "temperature": 0.1},
                {"model_name": model_name, "api_key": api_key},
            ]:
                try:
                    self.llm = ChatHuggingFace(**params)
                    break
                except Exception as e:
                    last_error = e
                    continue
        
        if self.llm is None:
            raise ValueError(
                f"Could not initialize HuggingFace model '{model_name}'. "
                f"Please check your API key and model name.\n"
                f"Last error: {last_error}\n\n"
                f"Note: Make sure you have set HUGGINGFACE_API_KEY environment variable.\n"
                f"Alternative: Use demo_cli.py which works without HuggingFace API key.\n"
                f"Example: python demo_cli.py --dry-run \"your query\""
            )
        
        # Create system prompt that enforces safety and workflow focus
        system_prompt = """You are a Clinical Workflow Automation Agent. Your role is to help clinicians and administrators coordinate appointments, check patient eligibility, and manage care workflows.

CRITICAL RULES:
1. You MUST NOT provide medical advice, diagnoses, or treatment recommendations
2. You MUST only use the provided tools/functions to interact with healthcare systems
3. You MUST validate all inputs before calling functions
4. You MUST return structured, auditable outputs
5. If you cannot safely complete a request, you MUST refuse with a clear explanation

AVAILABLE FUNCTIONS:
- search_patient: Search for patients by name, ID, or date of birth
- check_insurance_eligibility: Check patient insurance coverage
- find_available_slots: Find available appointment slots for a specialty
- book_appointment: Book an appointment (requires patient_id and slot_id)

WORKFLOW PATTERNS:
- To schedule an appointment: First search for the patient, check insurance eligibility, find available slots, then book
- Always validate patient exists before checking insurance or booking appointments
- Provide clear, structured responses with all relevant information

Remember: You are a workflow coordinator, not a medical advisor. Always use tools to get real data, never hallucinate or invent information."""

        # Store tools and system prompt for manual execution
        self.tools = HEALTHCARE_TOOLS
        self.system_prompt = system_prompt
        self.tool_map = {tool.name: tool for tool in HEALTHCARE_TOOLS}
    
    def _execute_tool(self, tool_name: str, args: dict) -> str:
        """Execute a tool function"""
        if tool_name not in self.tool_map:
            return f'{{"success": false, "error": "Unknown tool: {tool_name}"}}'
        
        try:
            tool = self.tool_map[tool_name]
            result = tool.invoke(args)
            return result
        except Exception as e:
            return f'{{"success": false, "error": "{str(e)}"}}'
    
    def _parse_and_execute(self, query: str) -> str:
        """Parse query and execute appropriate tools"""
        query_lower = query.lower()
        
        # Simple pattern matching for tool selection
        results = []
        found_patient_id = None  # Store patient ID from search results
        
        # Patient search
        if any(word in query_lower for word in ["search", "find", "look", "patient", "schedule", "appointment"]):
            # Extract patient name or ID - improved patterns to handle lowercase names
            name_patterns = [
                r'(?:patient|for)\s+patient\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+(?:next|this|week|and|with|has|needs|follow|follow-up|appointment|schedule))',
                r'(?:patient|for)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+(?:next|this|week|and|with|has|needs|follow|follow-up|appointment|schedule))',
                r'(?:patient|for)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
                r'schedule.*?patient\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            ]
            
            name = None
            for pattern in name_patterns:
                name_match = re.search(pattern, query, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1).strip()
                    # Remove "patient" if it was captured
                    if name.lower().startswith("patient "):
                        name = name[8:].strip()
                    # Skip common words that might be matched
                    if name.lower() not in ["a", "an", "the", "for", "next", "this", "week", "patient"]:
                        break
            
            id_match = re.search(r'(?:id|patient id)\s+(\d+)', query, re.IGNORECASE)
            
            if name:
                result = self._execute_tool("search_patient", {"name": name})
                results.append(f"Patient Search: {result}")
                # Extract patient ID from search result
                try:
                    import ast
                    result_dict = ast.literal_eval(result) if isinstance(result, str) else result
                    if isinstance(result_dict, dict) and result_dict.get("success") and result_dict.get("patients"):
                        patients = result_dict["patients"]
                        if patients and len(patients) > 0:
                            found_patient_id = patients[0].get("id")
                except:
                    pass
            elif id_match:
                found_patient_id = id_match.group(1)
                result = self._execute_tool("search_patient", {"patient_id": found_patient_id})
                results.append(f"Patient Search: {result}")
            else:
                # Try to extract any name-like pattern (fallback)
                words = query.split()
                for i, word in enumerate(words):
                    if word.lower() in ["patient", "for"] and i + 1 < len(words):
                        name = words[i + 1]
                        # Accept any word that looks like a name (not just capitalized)
                        if len(name) > 2 and name.isalpha():
                            result = self._execute_tool("search_patient", {"name": name})
                            results.append(f"Patient Search: {result}")
                            # Extract patient ID from search result
                            try:
                                import ast
                                result_dict = ast.literal_eval(result) if isinstance(result, str) else result
                                if isinstance(result_dict, dict) and result_dict.get("success") and result_dict.get("patients"):
                                    patients = result_dict["patients"]
                                    if patients and len(patients) > 0:
                                        found_patient_id = patients[0].get("id")
                            except:
                                pass
                            break
        
        # Insurance check - Use patient ID from search results or query
        if any(word in query_lower for word in ["insurance", "eligibility", "coverage", "check insurance"]):
            patient_id_for_insurance = None
            patient_name_for_insurance = None
            
            # Try to extract patient ID from query
            id_match = re.search(r'(?:patient\s+id|id|patient)\s+(\d+)', query, re.IGNORECASE)
            if id_match:
                patient_id_for_insurance = id_match.group(1)
            elif found_patient_id:
                # Use patient ID from search results
                patient_id_for_insurance = found_patient_id
            else:
                # Try to extract patient name from query for insurance check
                # Patterns like "deepan insurance check", "insurance check for deepan", "check insurance for patient deepan"
                insurance_name_patterns = [
                    r'^([A-Za-z]+)\s+insurance',  # "deepan insurance"
                    r'([A-Za-z]+)\s+insurance\s+check',  # "deepan insurance check"
                    r'insurance\s+check\s+for\s+([A-Za-z]+)',  # "insurance check for deepan"
                    r'check\s+insurance\s+for\s+([A-Za-z]+)',  # "check insurance for deepan"
                    r'check\s+insurance\s+for\s+patient\s+([A-Za-z]+)',  # "check insurance for patient deepan"
                    r'for\s+([A-Za-z]+)\s+insurance',  # "for deepan insurance"
                ]
                
                for pattern in insurance_name_patterns:
                    name_match = re.search(pattern, query, re.IGNORECASE)
                    if name_match:
                        potential_name = name_match.group(1).strip()
                        # Make sure it's not a common word
                        if potential_name.lower() not in ["check", "insurance", "eligibility", "coverage", "for", "patient"]:
                            patient_name_for_insurance = potential_name
                            break
                
                # If we found a patient name, search for them first
                if patient_name_for_insurance:
                    search_result = self._execute_tool("search_patient", {"name": patient_name_for_insurance})
                    # Extract patient ID from search result
                    try:
                        import ast
                        search_dict = ast.literal_eval(search_result) if isinstance(search_result, str) else search_result
                        if isinstance(search_dict, dict) and search_dict.get("success") and search_dict.get("patients"):
                            patients = search_dict["patients"]
                            if patients and len(patients) > 0:
                                patient_id_for_insurance = patients[0].get("id")
                                # Add patient search result if patients found
                                results.append(f"Patient Search: {search_result}")
                            # Don't add empty patient search - it clutters output
                    except:
                        pass
            
            if patient_id_for_insurance:
                result = self._execute_tool("check_insurance_eligibility", {"patient_id": patient_id_for_insurance})
                results.append(f"Insurance Check: {result}")
            elif patient_name_for_insurance:
                # Patient not found - could create them or show error
                results.append(f"Patient Search: {{'success': True, 'count': 0, 'patients': []}}")
                results.append(f"Insurance Check: {{'success': False, 'error': 'Patient {patient_name_for_insurance} not found. Please create patient first or use patient ID.'}}")
        
        # Find slots - also check for booking requests with typos
        found_slots_result = None
        booking_keywords = ["slot", "appointment", "appoinitment", "appoitment", "available", "schedule", "book"]
        if any(word in query_lower for word in booking_keywords):
            # Expanded specialty detection with variations
            specialty_patterns = {
                r'(cardiology|cardiac)': "Cardiology",
                r'(neurology|neurological)': "Neurology",
                r'(orthology|orthopedics|orthopedic|ortho)': "Orthopedics",
                r'(general medicine|general|primary care|family medicine)': "General Medicine",
                r'(dermatology|dermatologist)': "Dermatology",
                r'(pediatrics|pediatric)': "Pediatrics",
                r'(oncology|cancer)': "Oncology",
                r'(psychiatry|psychiatric|mental health)': "Psychiatry",
            }
            
            specialty = None
            for pattern, specialty_name in specialty_patterns.items():
                if re.search(pattern, query_lower):
                    specialty = specialty_name
                    break
            
            # Default to Cardiology if no specialty found
            if not specialty:
                specialty = "Cardiology"
            
            result = self._execute_tool("find_available_slots", {"specialty": specialty})
            results.append(f"Available Slots: {result}")
            found_slots_result = result
        
        # Book appointment if slots are available and booking is requested
        # Also handle common typos in "appointment"
        booking_words = ["schedule", "book", "appointment", "appoinitment", "appoitment", "appoinment"]
        if found_slots_result and any(word in query_lower for word in booking_words):
            try:
                import ast
                slots_dict = ast.literal_eval(found_slots_result) if isinstance(found_slots_result, str) else found_slots_result
                if isinstance(slots_dict, dict) and slots_dict.get("success") and slots_dict.get("slots"):
                    slots = slots_dict["slots"]
                    if slots and len(slots) > 0:
                        # Use first available slot
                        slot_id = slots[0].get("slot_id")
                        if slot_id:
                            # If patient not found but booking requested, create new patient
                            patient_id_to_use = found_patient_id
                            patient_created = False
                            if not patient_id_to_use:
                                # Extract patient name from query - improved patterns
                                # Handle "book appointment for X for Y" where X is patient, Y is specialty
                                name_patterns = [
                                    r'(?:book|schedule).*?(?:appointment|appoinitment|appoitment).*?for\s+([A-Za-z]+)\s+for\s+',  # "book appointment for shakthi for oncology"
                                    r'for\s+patient\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+(?:next|this|week|and|with|has|needs|follow|follow-up|appointment|schedule|$))',
                                    r'patient\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+(?:next|this|week|and|with|has|needs|follow|follow-up|appointment|schedule|$))',
                                    r'(?:book|schedule).*?for\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+(?:next|this|week|and|with|has|needs|follow|follow-up|appointment|schedule|$))',
                                    r'for\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+(?:next|this|week|and|with|has|needs|follow|follow-up|appointment|schedule|$))',
                                ]
                                
                                patient_name = None
                                for pattern in name_patterns:
                                    name_match = re.search(pattern, query, re.IGNORECASE)
                                    if name_match:
                                        patient_name = name_match.group(1).strip()
                                        # Clean up common prefixes
                                        if patient_name.lower().startswith("patient "):
                                            patient_name = patient_name[8:].strip()
                                        # Filter out common words that aren't names
                                        if patient_name.lower() not in ["a", "an", "the", "for", "next", "this", "week", "patient", "appointment", "schedule", "appoinitment", "appoitment"]:
                                            # Make sure it's not a specialty name
                                            specialties = ["cardiology", "neurology", "orthopedics", "dermatology", "pediatrics", "oncology", "psychiatry", "general medicine"]
                                            if patient_name.lower() not in specialties:
                                                break
                                
                                # Fallback: extract from words - look for name after "for" or "patient"
                                # Handle "for X for Y" pattern - take X (first for), ignore Y (second for is specialty)
                                if not patient_name:
                                    words = query.split()
                                    for i, word in enumerate(words):
                                        if word.lower() in ["patient", "for"] and i + 1 < len(words):
                                            potential_name = words[i + 1]
                                            # Check if it's not a specialty
                                            specialties = ["cardiology", "neurology", "orthopedics", "dermatology", "pediatrics", "oncology", "psychiatry", "general", "medicine"]
                                            if len(potential_name) > 2 and potential_name.lower() not in specialties:
                                                # Check if next word is "for" followed by a specialty - if so, this is the patient name
                                                if i + 2 < len(words) and words[i + 2].lower() == "for":
                                                    patient_name = potential_name
                                                    break
                                                elif potential_name.lower() not in specialties:
                                                    patient_name = potential_name
                                                    break
                                
                                # Additional fallback: if query has "for X for Y" pattern, extract X
                                if not patient_name:
                                    # Match "for X for Y" where X is patient name, Y is specialty
                                    for_pattern = re.search(r'for\s+([A-Za-z]+)\s+for\s+([A-Za-z]+)', query, re.IGNORECASE)
                                    if for_pattern:
                                        potential = for_pattern.group(1).strip()
                                        second_for = for_pattern.group(2).strip()
                                        specialties = ["cardiology", "neurology", "orthopedics", "dermatology", "pediatrics", "oncology", "psychiatry", "general"]
                                        # If second "for" is a specialty, then first is the patient
                                        if second_for.lower() in specialties and potential.lower() not in specialties and len(potential) > 2:
                                            patient_name = potential
                                    else:
                                        # Single "for X" pattern
                                        for_match = re.search(r'for\s+([A-Za-z]+)', query, re.IGNORECASE)
                                        if for_match:
                                            potential = for_match.group(1).strip()
                                            specialties = ["cardiology", "neurology", "orthopedics", "dermatology", "pediatrics", "oncology", "psychiatry", "general"]
                                            if potential.lower() not in specialties and len(potential) > 2:
                                                patient_name = potential
                                
                                # Create new patient if name found
                                if patient_name:
                                    from api_services import MockPatientService
                                    new_patient = MockPatientService.create_patient(name=patient_name.title())
                                    patient_id_to_use = new_patient.id
                                    patient_created = True
                                    # Only add patient creation message if patient was actually created
                                    results.append(f"Created New Patient: {new_patient.name} (ID: {new_patient.id})")
                            
                            if patient_id_to_use:
                                # Extract reason from query if available
                                reason_match = re.search(r'(?:for|reason|because)\s+([^and]+)', query, re.IGNORECASE)
                                reason = reason_match.group(1).strip() if reason_match else "Follow-up appointment"
                                
                                result = self._execute_tool("book_appointment", {
                                    "patient_id": patient_id_to_use,
                                    "slot_id": slot_id,
                                    "reason": reason
                                })
                                results.append(f"Booked Appointment: {result}")
                                
                                # If booking was successful and patient was created, remove empty patient search
                                if patient_created:
                                    # Remove empty patient search results
                                    results = [r for r in results if not (r.startswith("Patient Search:") and '"count": 0' in r)]
            except Exception as e:
                # If booking fails, continue without error
                pass
        
        # Clean up results - remove empty or unnecessary messages
        cleaned_results = []
        for r in results:
            # Skip empty patient searches
            if r.startswith("Patient Search:") and '"count": 0' in r:
                continue
            # Skip duplicate slot listings if booking was successful
            if r.startswith("Available Slots:") and any("Booked Appointment:" in res for res in results):
                # Keep slots but we'll simplify display in UI
                cleaned_results.append(r)
            else:
                cleaned_results.append(r)
        
        if cleaned_results:
            return "\n".join(cleaned_results)
        else:
            # Fallback to LLM for complex queries
            return self._llm_fallback(query)
    
    def _llm_fallback(self, query: str) -> str:
        """Use LLM to process query when pattern matching fails"""
        system_msg = """You are a Clinical Workflow Automation Agent. 
You help with:
1. Searching for patients
2. Checking insurance eligibility  
3. Finding appointment slots
4. Booking appointments

Provide helpful guidance on what information is needed. Never provide medical advice."""
        
        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=query)
        ]
        
        try:
            response = self.llm.invoke(messages)
            content = response.content if hasattr(response, 'content') else str(response)
            return content
        except Exception as e:
            return f"I understand you're asking about: {query}. Please be more specific about what you need (patient search, insurance check, appointment scheduling)."
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Execute a natural language query using the agent.
        
        Args:
            query: Natural language query from user
            
        Returns:
            Agent response with structured output
        """
        # Safety check: refuse medical advice requests
        medical_keywords = ["diagnose", "diagnosis", "treatment", "prescribe", "medicine", "medication", "symptom", "disease"]
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in medical_keywords):
            return {
                "error": "REFUSED",
                "message": "I cannot provide medical advice, diagnoses, or treatment recommendations. I am a workflow automation agent. Please use me for scheduling appointments, checking eligibility, or managing care coordination.",
                "suggestion": "Try asking me to schedule an appointment, check insurance eligibility, or find available appointment slots."
            }
        
        try:
            # Execute tools based on query
            output = self._parse_and_execute(query)
            
            return {
                "success": True,
                "query": query,
                "response": output,
                "dry_run": self.dry_run
            }
        
        except Exception as e:
            error_msg = f"Agent execution error: {str(e)}"
            print(f"Error: {error_msg}")
            return {
                "success": False,
                "error": "EXECUTION_ERROR",
                "message": error_msg,
                "suggestion": "Please check your query format and try again. Make sure you're asking about appointments, patient search, or insurance eligibility."
            }


def create_agent(api_key: Optional[str] = None, dry_run: bool = False) -> ClinicalWorkflowAgent:
    """
    Factory function to create a ClinicalWorkflowAgent instance.
    
    Args:
        api_key: HuggingFace API key (optional, reads from env if not provided)
        dry_run: Enable dry-run mode
        
    Returns:
        Configured ClinicalWorkflowAgent instance
    """
    return ClinicalWorkflowAgent(api_key=api_key, dry_run=dry_run)

