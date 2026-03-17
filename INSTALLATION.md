# Installation Guide

## Quick Install (PyPI)

```bash
pip install agentscope
```

## Development Install

### Prerequisites

- Python 3.9 or higher
- pip

### 1. Clone Repository

```bash
git clone https://github.com/vivekvar-dl/agentscope.git
cd agentscope
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create venv
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install

```bash
# Basic install
pip install -e "."

# With all optional dependencies
pip install -e ".[all]"

# For development (includes test tools)
pip install -e ".[dev]"
```

### 4. Verify Installation

```bash
python -c "import agentscope; print(agentscope.__version__)"
```

Should output: `0.1.0`

## Optional Dependencies

### LangChain Support

```bash
pip install "agentscope[langchain]"
```

### Dashboard (Web UI)

```bash
pip install "agentscope[dashboard]"
```

### Everything

```bash
pip install "agentscope[all]"
```

## Testing Installation

```bash
# Run example
python examples/basic_example.py

# Run tests (requires dev dependencies)
pytest tests/
```

## Troubleshooting

### Import Error

**Problem:** `ModuleNotFoundError: No module named 'agentscope'`

**Solution:**
```bash
# Make sure you're in the right directory
cd path/to/agentscope

# Reinstall in editable mode
pip install -e "."
```

### pytest Not Found

**Problem:** `python3 -m pytest: No module named pytest`

**Solution:**
```bash
pip install "agentscope[dev]"
```

### Permission Denied (Linux/Mac)

**Problem:** `ERROR: Could not install packages due to an EnvironmentError`

**Solution:**
```bash
# Use --user flag
pip install --user -e "."

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -e "."
```

## Platform-Specific Notes

### Windows

- Use `python` instead of `python3`
- Use backslashes in paths: `venv\Scripts\activate`

### macOS

- If `python3` not found, install from [python.org](https://python.org)
- Or use Homebrew: `brew install python@3.11`

### Linux (Ubuntu/Debian)

```bash
# Install Python if needed
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Then follow normal installation
```

## Next Steps

1. Read the [Quick Start](README.md#quick-start)
2. Try the [Examples](examples/)
3. Check the [API Documentation](docs/)
4. Join our [Discord](https://discord.gg/agentscope)
