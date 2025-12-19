"""
Quick script to help set up HuggingFace API key
"""

import os
from pathlib import Path

def setup_api_key():
    """Interactive setup for HuggingFace API key"""
    print("\n" + "=" * 70)
    print("HuggingFace API Key Setup")
    print("=" * 70)
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("\n[OK] .env file already exists")
        with open(env_file, 'r') as f:
            content = f.read()
            if "HUGGINGFACE_API_KEY" in content:
                print("[OK] HUGGINGFACE_API_KEY found in .env file")
                # Check if it's set
                from dotenv import load_dotenv
                load_dotenv()
                key = os.getenv("HUGGINGFACE_API_KEY")
                if key:
                    print(f"[OK] API Key is loaded (starts with: {key[:10]}...)")
                    return True
                else:
                    print("[WARNING] API Key is in file but not loading properly")
            else:
                print("[WARNING] .env file exists but HUGGINGFACE_API_KEY not found")
    else:
        print("\n[INFO] .env file not found")
    
    # Get API key from user
    print("\nPlease enter your HuggingFace API key:")
    print("(Get it from: https://huggingface.co/settings/tokens)")
    api_key = input("\nAPI Key: ").strip()
    
    if not api_key:
        print("\n❌ No API key provided. Exiting.")
        return False
    
    # Validate format
    if not api_key.startswith("hf_"):
        print(f"\n[WARNING] API key should start with 'hf_'. Got: {api_key[:10]}...")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return False
    
    # Write to .env file
    try:
        with open(env_file, 'w') as f:
            f.write(f"HUGGINGFACE_API_KEY={api_key}\n")
        print(f"\n[OK] API key saved to .env file")
        
        # Verify
        from dotenv import load_dotenv
        load_dotenv(override=True)
        loaded_key = os.getenv("HUGGINGFACE_API_KEY")
        if loaded_key == api_key:
            print("[OK] API key verified and loaded successfully!")
            print("\nYou can now use the chat assistant in the UI.")
            print("Refresh your browser if the UI is already running.")
            return True
        else:
            print("[WARNING] API key saved but verification failed")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Error saving API key: {str(e)}")
        return False

if __name__ == "__main__":
    setup_api_key()

