"""
Main entry point for Clinical Workflow Automation Agent
Provides CLI interface for interacting with the agent.
"""

import os
import sys
import argparse
import json
from dotenv import load_dotenv
from agent import ClinicalWorkflowAgent
from logger import audit_logger

# Try to import config for better API key management
try:
    from config import Config
except ImportError:
    Config = None


def print_banner():
    """Print welcome banner"""
    banner = """
    ================================================================
      Clinical Workflow Automation Agent
      Function-Calling LLM Agent for Healthcare Workflows
    ================================================================
    """
    print(banner)


def print_help():
    """Print help information"""
    help_text = """
    Available Commands:
    - Type your query in natural language
    - Type 'exit' or 'quit' to exit
    - Type 'help' to show this message
    - Type 'examples' to see example queries
    
    Example Queries:
    - "Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility"
    - "Search for patient Ravi Kumar"
    - "Find available slots for cardiology next Monday"
    - "Check insurance eligibility for patient ID 12345"
    - "Book an appointment for patient Jane Smith with Dr. Johnson"
    """
    print(help_text)


def print_examples():
    """Print example queries"""
    examples = """
    Example Queries:
    
    1. Patient Search:
       "Search for patient Ravi Kumar"
       "Find patient with ID 12345"
       "Look up patient Jane Smith"
    
    2. Insurance Check:
       "Check insurance eligibility for patient 12345"
       "Verify insurance coverage for Ravi Kumar"
    
    3. Appointment Scheduling:
       "Find available cardiology appointments next week"
       "Show me neurology slots for Monday"
       "What cardiology appointments are available?"
    
    4. Complete Workflow:
       "Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility"
       "Book an appointment for Jane Smith with a cardiologist and verify her insurance"
    """
    print(examples)


def format_response(response: dict) -> str:
    """Format agent response for display"""
    if isinstance(response, dict):
        if response.get("error") == "REFUSED":
            return f"\n[ERROR] {response.get('message', 'Request refused')}\n[INFO] {response.get('suggestion', '')}\n"
        elif not response.get("success"):
            return f"\n[ERROR] {response.get('message', 'Unknown error')}\n[INFO] {response.get('suggestion', '')}\n"
        else:
            # Format the response more readably
            response_text = response.get('response', 'No response')
            
            # Parse and format the response string
            try:
                import re
                formatted_parts = []
                
                # Split response by sections (Patient Search, Insurance Check, Available Slots)
                if isinstance(response_text, str):
                    # Extract each section
                    sections = re.split(r'(Created New Patient:|Patient Search:|Insurance Check:|Available Slots:|Booked Appointment:)', response_text)
                    
                    for i in range(1, len(sections), 2):
                        section_name = sections[i].rstrip(':')
                        section_data = sections[i+1] if i+1 < len(sections) else ""
                        
                        # Try to extract JSON from section
                        json_match = re.search(r'\{.*\}', section_data, re.DOTALL)
                        if json_match:
                            try:
                                data = eval(json_match.group())
                                
                                if section_name == "Available Slots" and isinstance(data, dict) and 'slots' in data:
                                    # Format slots nicely
                                    formatted_parts.append(f"\n{section_name}:\n{format_slots_output(data)}")
                                elif section_name == "Created New Patient":
                                    # Format new patient creation message
                                    formatted_parts.append(f"\n{section_name}: {section_data.strip()}")
                                elif section_name == "Patient Search" and isinstance(data, dict):
                                    # Format patient search
                                    if data.get('success') and data.get('count', 0) > 0:
                                        patients = data.get('patients', [])
                                        formatted_parts.append(f"\n{section_name}:")
                                        for p in patients:
                                            formatted_parts.append(f"  - {p.get('name', 'N/A')} (ID: {p.get('id', 'N/A')}, DOB: {p.get('date_of_birth', 'N/A')})")
                                    else:
                                        formatted_parts.append(f"\n{section_name}: No patients found")
                                elif section_name == "Insurance Check" and isinstance(data, dict):
                                    # Format insurance
                                    if data.get('success') and 'eligibility' in data:
                                        elig = data['eligibility']
                                        formatted_parts.append(f"\n{section_name}:")
                                        formatted_parts.append(f"  Provider: {elig.get('insurance_provider', 'N/A')}")
                                        formatted_parts.append(f"  Policy: {elig.get('policy_number', 'N/A')}")
                                        formatted_parts.append(f"  Status: {'Active' if elig.get('is_active') else 'Inactive'}")
                                        formatted_parts.append(f"  Coverage: {elig.get('coverage_type', 'N/A')}")
                                    else:
                                        formatted_parts.append(f"\n{section_name}: {data.get('error', 'No information available')}")
                                elif section_name == "Booked Appointment" and isinstance(data, dict):
                                    # Format appointment object
                                    if data.get('success'):
                                        if data.get('dry_run'):
                                            formatted_parts.append(f"\n{section_name}:")
                                            formatted_parts.append(f"  [DRY RUN] {data.get('message', 'Appointment validated')}")
                                            formatted_parts.append(f"  Patient: {data.get('patient_name', 'N/A')}")
                                        elif 'appointment' in data:
                                            appt = data['appointment']
                                            formatted_parts.append(f"\n{section_name}:")
                                            formatted_parts.append(f"  Appointment ID: {appt.get('appointment_id', 'N/A')}")
                                            formatted_parts.append(f"  Patient: {appt.get('patient_name', 'N/A')} (ID: {appt.get('patient_id', 'N/A')})")
                                            formatted_parts.append(f"  Provider: {appt.get('provider_name', 'N/A')}")
                                            formatted_parts.append(f"  Specialty: {appt.get('specialty', 'N/A')}")
                                            formatted_parts.append(f"  Date/Time: {appt.get('start_time', 'N/A')}")
                                            formatted_parts.append(f"  Location: {appt.get('location', 'N/A')}")
                                            formatted_parts.append(f"  Status: {appt.get('status', 'N/A')}")
                                        else:
                                            formatted_parts.append(f"\n{section_name}: {str(data)}")
                                    else:
                                        formatted_parts.append(f"\n{section_name}: {data.get('error', 'Booking failed')}")
                                else:
                                    formatted_parts.append(f"\n{section_name}: {section_data[:200]}...")
                            except:
                                formatted_parts.append(f"\n{section_name}: {section_data[:200]}...")
                        else:
                            formatted_parts.append(f"\n{section_name}: {section_data[:200]}...")
                    
                    if formatted_parts:
                        response_text = "\n".join(formatted_parts)
            except Exception as e:
                # If parsing fails, use original response
                pass
            
            output = f"\n[SUCCESS] Response:{response_text}\n"
            if response.get("dry_run"):
                output += "\n[DRY RUN MODE] - No actual changes were made\n"
            if response.get("note"):
                output += f"\n[NOTE] {response.get('note')}\n"
            return output
    else:
        return f"\n{str(response)}\n"


def format_slots_output(data: dict) -> str:
    """Format appointment slots output in a readable format"""
    from datetime import datetime
    
    if not isinstance(data, dict) or 'slots' not in data:
        return str(data)
    
    count = data.get('count', 0)
    slots = data.get('slots', [])
    
    output = f"\n{'='*70}\n"
    output += f"Available Appointment Slots: {count} found\n"
    output += f"{'='*70}\n\n"
    
    # Group by provider
    providers = {}
    for slot in slots:
        provider = slot.get('provider_name', 'Unknown')
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(slot)
    
    slot_num = 1
    for provider_name, provider_slots in providers.items():
        output += f"Provider: {provider_name}\n"
        output += f"Specialty: {provider_slots[0].get('specialty', 'N/A')}\n"
        output += f"Location: {provider_slots[0].get('location', 'N/A')}\n"
        output += "Available Times:\n"
        
        for slot in provider_slots[:5]:
            start_time = slot.get('start_time', '')
            try:
                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                time_str = dt.strftime("%A, %B %d, %Y at %I:%M %p")
            except:
                time_str = start_time[:16] if start_time else 'N/A'
            
            output += f"  {slot_num}. {time_str}\n"
            output += f"     Slot ID: {slot.get('slot_id', 'N/A')}\n"
            slot_num += 1
        
        if len(provider_slots) > 5:
            output += f"  ... and {len(provider_slots) - 5} more slots\n"
        output += "\n"
    
    output += f"{'='*70}\n"
    return output


def interactive_mode(agent: ClinicalWorkflowAgent):
    """Run agent in interactive mode"""
    print("\n[READY] Agent ready! Type your query or 'help' for assistance.\n")
    
    while True:
        try:
            query = input("You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n[GOODBYE] Exiting...\n")
                break
            
            if query.lower() == 'help':
                print_help()
                continue
            
            if query.lower() == 'examples':
                print_examples()
                continue
            
            # Execute query
            print("\n[PROCESSING] Analyzing query...\n")
            response = agent.run(query)
            print(format_response(response))
            
        except KeyboardInterrupt:
            print("\n\n[GOODBYE] Exiting...\n")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {str(e)}\n")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Clinical Workflow Automation Agent - Function-Calling LLM Agent"
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Query to execute (non-interactive mode)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Enable dry-run mode (no actual API calls)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="HuggingFace API key (overrides environment variable)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="meta-llama/Meta-Llama-3.1-8B-Instruct",
        help="HuggingFace model name (default: meta-llama/Meta-Llama-3.1-8B-Instruct)"
    )
    parser.add_argument(
        "--show-logs",
        action="store_true",
        help="Show recent audit logs before exit"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Print banner
    print_banner()
    
    # Get API key from multiple sources
    api_key = None
    if args.api_key:
        api_key = args.api_key
    elif Config:
        api_key = Config.get_huggingface_key()
        if not api_key:
            is_valid, error_msg = Config.validate_huggingface_setup()
            if not is_valid:
                print(f"[ERROR] {error_msg}")
                Config.print_setup_instructions()
                sys.exit(1)
    else:
        api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    if not api_key:
        print("[ERROR] HuggingFace API key is required!")
        if Config:
            Config.print_setup_instructions()
        else:
            print("\nPlease provide it in one of these ways:")
            print("  1. Set HUGGINGFACE_API_KEY environment variable")
            print("  2. Create a .env file with: HUGGINGFACE_API_KEY=your_key")
            print("  3. Use --api-key command line argument")
            print("\nGet your API key from: https://huggingface.co/settings/tokens\n")
        sys.exit(1)
    
    # Create agent
    try:
        print(f"[INIT] Initializing agent with model: {args.model}")
        if args.dry_run:
            print("[DRY RUN] DRY RUN MODE ENABLED - No actual API calls will be made\n")
        
        agent = ClinicalWorkflowAgent(
            api_key=api_key,
            model_name=args.model,
            dry_run=args.dry_run
        )
        print("[SUCCESS] Agent initialized successfully!\n")
        
    except Exception as e:
        print(f"[ERROR] Failed to initialize agent: {str(e)}\n")
        sys.exit(1)
    
    # Execute query or start interactive mode
    if args.query:
        # Non-interactive mode
        print(f"[QUERY] {args.query}\n")
        response = agent.run(args.query)
        print(format_response(response))
        
        if args.show_logs:
            print("\n[AUDIT LOGS] Recent Audit Logs:")
            logs = audit_logger.get_recent_logs(limit=5)
            for log in logs:
                status = "[OK]" if log.get("success") else "[FAIL]"
                print(f"  {status} [{log.get('timestamp', 'N/A')}] {log.get('action', 'N/A')}")
    else:
        # Interactive mode
        interactive_mode(agent)
    
    # Show logs if requested
    if args.show_logs and not args.query:
        print("\n[AUDIT LOGS] Recent Audit Logs:")
        logs = audit_logger.get_recent_logs(limit=10)
        for log in logs:
            status = "[OK]" if log.get("success") else "[FAIL]"
            dry_run_indicator = "[DRY RUN] " if log.get("dry_run") else ""
            print(f"  {status} {dry_run_indicator}[{log.get('timestamp', 'N/A')}] {log.get('action', 'N/A')}")


if __name__ == "__main__":
    main()

