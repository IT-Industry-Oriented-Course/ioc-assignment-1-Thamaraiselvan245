# HuggingFace API Key Integration Guide

## Quick Setup

### Step 1: Get Your HuggingFace API Key

1. Go to: **https://huggingface.co/settings/tokens**
2. Sign up or log in (free account works)
3. Click **"New token"**
4. Name it (e.g., "Clinical Agent")
5. Select **"Read"** permission
6. Click **"Generate token"**
7. **Copy the token** (starts with `hf_`)

### Step 2: Set the API Key

Choose one method:

#### Method A: Environment Variable (Recommended)

**Windows PowerShell:**
```powershell
$env:HUGGINGFACE_API_KEY="hf_your_token_here"
```

**Windows Command Prompt:**
```cmd
set HUGGINGFACE_API_KEY=hf_your_token_here
```

**Linux/Mac:**
```bash
export HUGGINGFACE_API_KEY="hf_your_token_here"
```

#### Method B: .env File (Persistent)

Create a `.env` file in the project root:
```
HUGGINGFACE_API_KEY=hf_your_token_here
```

The `python-dotenv` package will automatically load it.

#### Method C: Command Line Argument

```bash
python main.py --api-key "hf_your_token_here" --query "your query"
```

### Step 3: Verify Setup

```bash
python -c "from config import Config; print('API Key:', Config.HUGGINGFACE_API_KEY[:10] + '...' if Config.HUGGINGFACE_API_KEY else 'Not set')"
```

### Step 4: Run with HuggingFace

```bash
python main.py --query "Schedule a cardiology follow-up for patient Ravi Kumar"
```

## Configuration System

The project now uses `config.py` for centralized configuration:

```python
from config import Config

# Get API key
api_key = Config.get_huggingface_key()

# Validate setup
is_valid, error = Config.validate_huggingface_setup()
if not is_valid:
    print(error)
```

## Troubleshooting

### "HUGGINGFACE_API_KEY not set"
- Make sure you've set the environment variable
- Check that `.env` file exists and has the correct key
- Verify the key starts with `hf_`

### "Invalid API key format"
- HuggingFace keys should start with `hf_`
- Make sure you copied the full token

### Still having issues?
- Use `demo_cli.py` which works without HuggingFace
- Check `HUGGINGFACE_TROUBLESHOOTING.md` for more help

## No Hardcoded Values

The system now:
- ✅ Extracts patient names dynamically from queries
- ✅ Extracts patient IDs from queries
- ✅ Extracts specialties from queries
- ✅ Uses configuration system instead of hardcoded values
- ✅ All data comes from API responses or query parsing

