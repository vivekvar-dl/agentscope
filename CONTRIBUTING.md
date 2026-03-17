# Contributing to AgentScope

Thank you for your interest in contributing! 🎉

AgentScope is a community-driven project, and we welcome contributions of all kinds:
- 🐛 Bug reports and fixes
- ✨ New features
- 📚 Documentation improvements
- 🧪 Test coverage
- 💡 Ideas and suggestions

## Quick Start

### 1. Set Up Development Environment

```bash
# Clone the repository
git clone https://github.com/vivekvar-dl/agentscope
cd agentscope

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use prefixes:
- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation
- `test/` for test additions

### 3. Make Your Changes

Write clean, readable code that follows our style guide.

### 4. Run Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=agentscope --cov-report=html

# Run specific test file
pytest tests/test_metrics.py -v

# Run only tests matching a pattern
pytest -k "test_pricing"
```

### 5. Lint and Format

```bash
# Format code
black agentscope tests examples

# Check linting
ruff check agentscope tests examples

# Type checking
mypy agentscope
```

### 6. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add cost optimization suggestions"
```

Commit message prefixes:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub with:
- **Title:** Clear, descriptive title
- **Description:** What and why (not how)
- **Testing:** How you tested the changes
- **Screenshots:** If UI changes (dashboard, CLI output)

## Code Style

We follow PEP 8 with these specifics:

```python
# Good
def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    """
    Calculate LLM API cost.
    
    Args:
        model: Model name
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
    
    Returns:
        Cost in USD
    """
    return pricing.calculate(model, prompt_tokens, completion_tokens)


# Bad
def calc(m,p,c): return p*0.001+c*0.002  # No docstring, unclear names
```

**Key points:**
- 100 character line length
- Type hints for all public functions
- Docstrings for all public classes/functions
- Descriptive variable names (no `x`, `y`, `temp`)

## Testing Guidelines

### Writing Tests

```python
import pytest
from agentscope import AgentScope


def test_agent_scope_basic():
    """Test basic AgentScope functionality."""
    scope = AgentScope(mock_agent, project="test")
    
    # Arrange
    input_text = "test input"
    
    # Act
    with scope:
        result = mock_agent.run(input_text)
    
    # Assert
    assert scope.metrics.success is True
    assert scope.tokens > 0


@pytest.mark.parametrize("model,expected_cost", [
    ("gpt-4", 0.06),
    ("gpt-3.5-turbo", 0.00125),
])
def test_pricing_multiple_models(model, expected_cost):
    """Test pricing for multiple models."""
    calc = PricingCalculator()
    cost = calc.calculate(model, 1000, 500)
    assert cost == pytest.approx(expected_cost)
```

**Test coverage:** Aim for 80%+ coverage for new code.

### Running Tests Locally

```bash
# Fast: Run without coverage
pytest

# Full: With coverage
pytest --cov=agentscope --cov-report=html
open htmlcov/index.html  # View coverage report
```

## Adding New Features

### 1. Check Existing Issues

Search [existing issues](https://github.com/vivekvar-dl/agentscope/issues) first.

### 2. Discuss First (For Big Changes)

Open an issue to discuss:
- What problem does it solve?
- How will it work?
- Any breaking changes?

### 3. Implementation Checklist

- [ ] Code implements the feature
- [ ] Tests cover the feature (80%+ coverage)
- [ ] Documentation updated (README, docstrings)
- [ ] Example added (if applicable)
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or discussed first)

## Adding Adapters

Want to support a new agent framework?

1. **Create adapter file:** `agentscope/adapters/your_framework_adapter.py`

```python
from agentscope.adapters.base import BaseAdapter


class YourFrameworkAdapter(BaseAdapter):
    def wrap(self, agent, scope):
        # Monkey-patch agent to log to scope
        pass
    
    def unwrap(self, agent):
        # Restore original agent
        pass
    
    def supports(self, agent):
        # Check if agent is from your framework
        return "your_framework" in type(agent).__module__
```

2. **Add tests:** `tests/test_your_framework_adapter.py`
3. **Update docs:** Add to README and examples
4. **Add to dependencies:** Update `pyproject.toml` optional deps

## Documentation

### Docstring Format

```python
def function_name(arg1: str, arg2: int) -> bool:
    """
    One-line summary.
    
    Longer description if needed. Can span multiple paragraphs.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When something is invalid
    
    Example:
        >>> function_name("hello", 42)
        True
    """
```

### README Updates

- Keep examples simple and runnable
- Add screenshots/GIFs for visual features
- Update feature list if adding capabilities

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `__init__.py`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. GitHub Actions will build and publish to PyPI

## Getting Help

- 💬 [GitHub Discussions](https://github.com/vivekvar-dl/agentscope/discussions) - Ask questions
- 🐛 [GitHub Issues](https://github.com/vivekvar-dl/agentscope/issues) - Report bugs
- 💬 [Discord](https://discord.gg/agentscope) - Chat with community

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to build something cool together.

## Recognition

Contributors are recognized in:
- README.md contributors section
- GitHub contributors page
- CHANGELOG.md for significant contributions

---

**Thank you for contributing to AgentScope!** 🚀

Every contribution, no matter how small, makes this project better.
