"""
Example usage and test cases for the Clinical Workflow Automation Agent
"""

import os
from dotenv import load_dotenv
from agent import ClinicalWorkflowAgent

# Load environment variables
load_dotenv()


def run_examples():
    """Run example queries to demonstrate agent capabilities"""
    
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        print("❌ Error: HUGGINGFACE_API_KEY not found in environment")
        print("Please set it in .env file or environment variables")
        return
    
    print("=" * 70)
    print("Clinical Workflow Automation Agent - Example Queries")
    print("=" * 70)
    print()
    
    # Create agent
    agent = ClinicalWorkflowAgent(api_key=api_key, dry_run=False)
    
    # Example queries
    examples = [
        {
            "name": "Patient Search",
            "query": "Search for patient Ravi Kumar"
        },
        {
            "name": "Insurance Check",
            "query": "Check insurance eligibility for patient ID 12345"
        },
        {
            "name": "Find Appointment Slots",
            "query": "Find available slots for cardiology"
        },
        {
            "name": "Complete Workflow",
            "query": "Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{'='*70}")
        print(f"Example {i}: {example['name']}")
        print(f"{'='*70}")
        print(f"Query: {example['query']}")
        print("\nResponse:")
        print("-" * 70)
        
        try:
            response = agent.run(example['query'])
            if isinstance(response, dict):
                print(response.get('response', str(response)))
            else:
                print(response)
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n" + "-" * 70)
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    run_examples()

