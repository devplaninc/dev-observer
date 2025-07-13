# dev-observer
Standalone context building application that performs in-depth 
github repository analysis and website crawl. Output is a summary 
that can be used for context in AI applications like Devplan or 
for input into other process (or simply for better understanding of 
code or website content).

# Quick Start:

## Pre-requisites

### System Requirements
- **Python 3.12+** - Required for the server backend
- **Node.js 18+** - Required for the web frontend

### Installation Instructions

#### 1. Python 3.12+
**macOS (using Homebrew):**
```bash
brew install python
```

#### 2. uv (Python Package Manager)
**All platforms:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 3. Node.js 18+ and npm
**macOS (using Homebrew):**
```bash
brew install node
```

### Verification
After installation, verify all tools are available:
```bash
python --version      # Should show python version
uv --version          # Should show uv version
node --version        # Should show Node.js 18+
npm --version         # Should show npm version
```

## Get your Google API Key:
1. Visit https://aistudio.google.com/prompts/new_chat
2. Click "Get API key"
3. Create an API key and copy it

## Run quick start:

```bash
GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY> ./examples/quick-start/start.sh
```

Then open http://localhost:5173.

Add your repository or website, then navigate to it and click Rescan. After
a few seconds repo/site analysis should appear.
