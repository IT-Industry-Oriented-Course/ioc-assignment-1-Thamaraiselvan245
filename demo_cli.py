"""
Demo CLI for Clinical Workflow Agent
Works without HuggingFace API key for basic function testing
"""

import sys
import os
from functions import HEALTHCARE_TOOLS, set_dry_run_mode
from logger import audit_logger

# Set dry-run mode
set_dry_run_mode(True)


def demo_search_patient(name: str = None, patient_id: str = None, date_of_birth: str = None):
    """Demo patient search - accepts name, ID, or DOB dynamically"""
    search_params = {}
    if name:
        search_params["name"] = name
        print(f"\n[DEMO] Searching for patient: {name}")
    elif patient_id:
        search_params["patient_id"] = patient_id
        print(f"\n[DEMO] Searching for patient ID: {patient_id}")
    elif date_of_birth:
        search_params["date_of_birth"] = date_of_birth
        print(f"\n[DEMO] Searching for patient with DOB: {date_of_birth}")
    else:
        print("\n[DEMO] No search parameters provided")
        return None
    
    tool = HEALTHCARE_TOOLS[0]  # search_patient
    result = tool.invoke(search_params)
    print(f"[RESULT] {result}\n")
    return result


def demo_check_insurance(patient_id: str):
    """Demo insurance check"""
    print(f"\n[DEMO] Checking insurance for patient ID: {patient_id}")
    tool = HEALTHCARE_TOOLS[1]  # check_insurance_eligibility
    result = tool.invoke({"patient_id": patient_id})
    print(f"[RESULT] {result}\n")
    return result


def demo_find_slots(specialty: str):
    """Demo find available slots"""
    print(f"\n[DEMO] Finding available slots for: {specialty}")
    tool = HEALTHCARE_TOOLS[2]  # find_available_slots
    result = tool.invoke({"specialty": specialty})
    
    # Parse and format the result more readably
    try:
        import json
        from datetime import datetime
        result_dict = eval(result) if isinstance(result, str) else result
        if isinstance(result_dict, dict) and "slots" in result_dict:
            count = result_dict.get('count', 0)
            slots = result_dict.get('slots', [])
            print(f"[RESULT] Found {count} available slots\n")
            
            print("  " + "=" * 65)
            print("  Available Appointment Slots:")
            print("  " + "=" * 65)
            
            # Group by provider for better readability
            providers = {}
            for slot in slots:
                provider = slot.get('provider_name', 'Unknown')
                if provider not in providers:
                    providers[provider] = []
                providers[provider].append(slot)
            
            slot_num = 1
            for provider_name, provider_slots in providers.items():
                print(f"\n  Provider: {provider_name}")
                print(f"  Specialty: {provider_slots[0].get('specialty', 'N/A')}")
                print(f"  Location: {provider_slots[0].get('location', 'N/A')}")
                print("  Available Times:")
                
                for slot in provider_slots[:5]:  # Show first 5 per provider
                    start_time = slot.get('start_time', '')
                    try:
                        dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        time_str = dt.strftime("%A, %B %d, %Y at %I:%M %p")
                    except:
                        time_str = start_time[:16] if start_time else 'N/A'
                    
                    print(f"    {slot_num}. {time_str}")
                    print(f"       Slot ID: {slot.get('slot_id', 'N/A')}")
                    slot_num += 1
                
                if len(provider_slots) > 5:
                    print(f"    ... and {len(provider_slots) - 5} more slots for this provider")
            
            if count > len(slots):
                print(f"\n  ... and {count - len(slots)} more slots available")
            
            print("\n  " + "=" * 65)
            print(f"  Total: {count} slots available")
            print("  " + "=" * 65 + "\n")
        else:
            print(f"[RESULT] {result}\n")
    except Exception as e:
        print(f"[RESULT] {result}\n")
    
    return result


def demo_workflow(query: str):
    """Execute complete workflow based on query"""
    print("=" * 70)
    print("Clinical Workflow Automation Agent - DEMO MODE")
    print("=" * 70)
    print(f"\n[QUERY] {query}\n")
    print("[DRY RUN MODE] - No actual changes will be made\n")
    
    query_lower = query.lower()
    results = []
    
    # Step 1: Search for patient - Extract name dynamically from query
    patient_id = None
    patient_name = None
    
    # Extract patient name from query using regex (more precise patterns)
    import re
    name_patterns = [
        r'patient\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)(?:\s+(?:next|this|for|and|with|has|needs))',  # "patient John Doe next"
        r'for\s+patient\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)(?:\s+(?:next|this|and|with))',  # "for patient Jane Smith"
        r'patient\s+([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+(?:next|this|and|with|has|needs))',  # "patient Ravi Kumar next"
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+(?:next|this|week|and|with))',  # "Ravi Kumar next week"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            patient_name = match.group(1).strip()
            break
    
    # If patient name found, search for patient
    if patient_name:
        patient_result = demo_search_patient(name=patient_name)
        if patient_result:
            results.append(("Patient Search", patient_result))
            
            # Extract patient ID from search result dynamically
            try:
                patient_data = eval(patient_result) if isinstance(patient_result, str) else patient_result
                if isinstance(patient_data, dict) and "patients" in patient_data:
                    if patient_data["patients"] and len(patient_data["patients"]) > 0:
                        patient_id = patient_data["patients"][0].get("id")
            except:
                pass
    
    # Also check for patient ID in query (if not already found)
    if not patient_id:
        id_match = re.search(r'(?:patient\s+id|id)\s+(\d+)', query, re.IGNORECASE)
        if id_match:
            patient_id = id_match.group(1)
            if not patient_name:
                patient_result = demo_search_patient(patient_id=patient_id)
                if patient_result:
                    results.append(("Patient Search", patient_result))
    
    # Step 2: Check insurance - only if patient_id found
    if ("insurance" in query_lower or "eligibility" in query_lower) and patient_id:
        insurance_result = demo_check_insurance(patient_id)
        results.append(("Insurance Check", insurance_result))
    
    # Step 3: Find slots - Extract specialty dynamically
    if "appointment" in query_lower or "schedule" in query_lower or "slot" in query_lower:
        # Extract specialty from query
        specialty_keywords = {
            "cardiology": "Cardiology",
            "neurology": "Neurology",
            "general medicine": "General Medicine",
            "general": "General Medicine"
        }
        specialty = "Cardiology"  # Default
        for keyword, spec in specialty_keywords.items():
            if keyword in query_lower:
                specialty = spec
                break
        
        slots_result = demo_find_slots(specialty)
        results.append(("Available Slots", slots_result))
    
    # Summary
    print("\n" + "=" * 70)
    print("[WORKFLOW SUMMARY]")
    print("=" * 70)
    for step_name, result in results:
        print(f"\n{step_name}:")
        print(f"  {result[:200]}..." if len(str(result)) > 200 else f"  {result}")
    
    print("\n" + "=" * 70)
    print("[AUDIT LOGS]")
    print("=" * 70)
    logs = audit_logger.get_recent_logs(limit=10)
    for log in logs:
        status = "[OK]" if log.get("success") else "[FAIL]"
        print(f"  {status} [{log.get('timestamp', 'N/A')[:19]}] {log.get('action', 'N/A')}")
    
    print("\n[DEMO COMPLETE]\n")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python demo_cli.py --dry-run \"<query>\"")
        print("\nExample:")
        print('  python demo_cli.py --dry-run "Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility"')
        sys.exit(1)
    
    # Parse arguments
    query = None
    dry_run = False
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--dry-run":
            dry_run = True
            i += 1
        elif sys.argv[i].startswith("--"):
            i += 1
        else:
            query = sys.argv[i]
            i += 1
    
    if not query:
        # Try to get query from remaining args
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])
            if query.startswith("--dry-run"):
                query = query.replace("--dry-run", "").strip()
    
    if not query:
        print("[ERROR] No query provided")
        sys.exit(1)
    
    # Execute demo workflow
    demo_workflow(query)


if __name__ == "__main__":
    main()

