"""
Configuration management for the Clinical Workflow Agent
Handles environment variables and API keys
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Centralized configuration management"""
    
    # HuggingFace Configuration
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")
    
    # API Configuration
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # Logging Configuration
    LOG_FILE: str = os.getenv("LOG_FILE", "audit_log.jsonl")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_huggingface_key(cls) -> Optional[str]:
        """Get HuggingFace API key with validation"""
        key = cls.HUGGINGFACE_API_KEY
        if not key:
            return None
        # Validate format (should start with hf_)
        if not key.startswith("hf_"):
            print(f"[WARNING] HuggingFace API key should start with 'hf_'. Got: {key[:5]}...")
        return key
    
    @classmethod
    def validate_huggingface_setup(cls) -> tuple[bool, str]:
        """
        Validate HuggingFace configuration
        
        Returns:
            (is_valid, error_message)
        """
        if not cls.HUGGINGFACE_API_KEY:
            return False, "HUGGINGFACE_API_KEY not set. Get one from https://huggingface.co/settings/tokens"
        
        if not cls.HUGGINGFACE_API_KEY.startswith("hf_"):
            return False, f"Invalid API key format. Should start with 'hf_'. Got: {cls.HUGGINGFACE_API_KEY[:10]}..."
        
        return True, ""
    
    @classmethod
    def print_setup_instructions(cls):
        """Print instructions for setting up HuggingFace"""
        print("\n" + "=" * 70)
        print("HuggingFace API Key Setup")
        print("=" * 70)
        print("\n1. Get your API key:")
        print("   https://huggingface.co/settings/tokens")
        print("\n2. Set it in one of these ways:")
        print("\n   Option A: Environment Variable (PowerShell)")
        print("   $env:HUGGINGFACE_API_KEY=\"hf_your_token_here\"")
        print("\n   Option B: Environment Variable (Linux/Mac)")
        print("   export HUGGINGFACE_API_KEY=\"hf_your_token_here\"")
        print("\n   Option C: .env file (create in project root)")
        print("   HUGGINGFACE_API_KEY=hf_your_token_here")
        print("\n3. Verify it's set:")
        print("   python -c \"from config import Config; print(Config.HUGGINGFACE_API_KEY)\"")
        print("\n" + "=" * 70 + "\n")

