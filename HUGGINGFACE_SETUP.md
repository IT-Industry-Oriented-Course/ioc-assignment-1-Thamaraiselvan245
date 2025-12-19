# HuggingFace LLM Setup Guide

## Current Implementation Status

The project has **two modes**:

1. **Demo Mode** (`demo_cli.py`) - Uses pattern matching, **no HuggingFace needed**
2. **Full Agent Mode** (`main.py`) - Uses HuggingFace LLM, **requires API key**

---

## Why HuggingFace is Recommended

The assignment recommends HuggingFace because:
- ✅ True function-calling LLM agent (not just pattern matching)
- ✅ Better natural language understanding
- ✅ Can handle complex, varied queries
- ✅ More intelligent function selection
- ✅ Better for production use

---

## Step 1: Get HuggingFace API Key

1. Go to: https://huggingface.co/settings/tokens
2. Sign up or log in (free account works)
3. Click "New token"
4. Name it (e.g., "Clinical Agent")
5. Select "Read" permission (sufficient for API access)
6. Click "Generate token"
7. **Copy the token immediately** (you won't see it again!)

---

## Step 2: Set Up API Key

### Option A: Environment Variable (Recommended)

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

### Option B: .env File (Persistent)

Create a `.env` file in the project root:
```
HUGGINGFACE_API_KEY=hf_your_token_here
```

The `python-dotenv` package will automatically load it.

### Option C: Command Line Argument

```bash
python main.py --api-key "hf_your_token_here" --query "your query"
```

---

## Step 3: Run with HuggingFace LLM

### Interactive Mode:
```bash
python main.py
```

### Single Query:
```bash
python main.py --query "Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility"
```

### With Dry-Run:
```bash
python main.py --dry-run --query "Find available neurology appointments"
```

### Custom Model:
```bash
python main.py --model "mistralai/Mistral-7B-Instruct-v0.2" --query "your query"
```

---

## Step 4: Verify It's Working

When HuggingFace is properly configured, you'll see:
```
[INIT] Initializing agent with model: meta-llama/Meta-Llama-3.1-8B-Instruct
[SUCCESS] Agent initialized successfully!
```

If there's an error, you'll see:
```
[ERROR] HuggingFace API key is required!
```

---

## Comparison: Demo Mode vs Full LLM Mode

| Feature | Demo Mode (`demo_cli.py`) | Full LLM Mode (`main.py`) |
|---------|---------------------------|---------------------------|
| **HuggingFace Required** | ❌ No | ✅ Yes |
| **API Key Needed** | ❌ No | ✅ Yes |
| **Natural Language** | ✅ Basic (pattern matching) | ✅ Advanced (LLM understanding) |
| **Function Selection** | Pattern-based | LLM-based (intelligent) |
| **Complex Queries** | Limited | ✅ Handles complex queries |
| **Production Ready** | ❌ Demo only | ✅ Yes |

---

## Recommended Models

The default model is: `meta-llama/Meta-Llama-3.1-8B-Instruct`

Other good options:
- `mistralai/Mistral-7B-Instruct-v0.2` - Fast, good function calling
- `google/gemma-7b-it` - Good for structured outputs
- `meta-llama/Llama-2-7b-chat-hf` - Alternative Llama model

---

## Troubleshooting

### "HuggingFace API key is required"
- Make sure you've set the environment variable
- Check that `.env` file exists and has the correct key
- Verify the key starts with `hf_`

### "Could not initialize HuggingFace model"
- Check your internet connection
- Verify the API key is correct
- Try a different model: `--model "mistralai/Mistral-7B-Instruct-v0.2"`

### Model not available
- Some models require special access
- Try the default model first
- Check model availability at: https://huggingface.co/models

---

## Cost Information

- **Free tier**: Limited requests per month
- **Paid tier**: More requests, faster responses
- For assignment/demo: Free tier is usually sufficient

---

## Current Status

✅ **HuggingFace integration is complete** in `agent.py`
✅ **All code is ready** - just needs API key
✅ **Works with or without HuggingFace** (demo mode available)

---

## Quick Start

1. Get API key from https://huggingface.co/settings/tokens
2. Set environment variable: `$env:HUGGINGFACE_API_KEY="your_key"`
3. Run: `python main.py --query "your query"`
4. Done! 🎉

---

**Note:** The demo mode (`demo_cli.py`) works without HuggingFace for basic testing, but for the full LLM agent experience as recommended in the assignment, use `main.py` with a HuggingFace API key.

