"""Pytest configuration and fixtures."""

import pytest
from datetime import datetime
from typing import Any, Dict


class MockAgent:
    """Mock agent for testing."""

    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.call_count = 0

    def run(self, input_text: str) -> str:
        """Mock run method."""
        self.call_count += 1
        if self.should_fail:
            raise ValueError("Mock agent failed")
        return f"Processed: {input_text}"

    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Mock invoke method (LangChain style)."""
        self.call_count += 1
        input_text = inputs.get("input", "")
        if self.should_fail:
            raise ValueError("Mock agent failed")
        return {"output": f"Processed: {input_text}"}

    def __call__(self, *args: Any, **kwargs: Any) -> str:
        """Mock __call__ method."""
        return self.run(str(args))


@pytest.fixture
def mock_agent():
    """Provide a mock agent for testing."""
    return MockAgent()


@pytest.fixture
def failing_agent():
    """Provide a failing mock agent for testing."""
    return MockAgent(should_fail=True)


@pytest.fixture
def sample_input():
    """Provide sample input text."""
    return "Analyze this data and provide insights"


@pytest.fixture
def sample_metadata():
    """Provide sample metadata."""
    return {
        "project": "test-project",
        "tags": ["unit-test", "mock"],
        "environment": "test",
    }
