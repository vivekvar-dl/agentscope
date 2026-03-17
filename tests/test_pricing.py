"""Tests for pricing calculator."""

import pytest

from agentscope.core.pricing import PricingCalculator


def test_gpt4_pricing():
    """Test GPT-4 cost calculation."""
    calc = PricingCalculator()
    
    # 1000 prompt + 500 completion tokens
    cost = calc.calculate("gpt-4", 1000, 500)
    
    # Expected: (1000/1M)*30 + (500/1M)*60 = 0.03 + 0.03 = 0.06
    assert cost == pytest.approx(0.06)


def test_gpt35_pricing():
    """Test GPT-3.5-turbo cost calculation."""
    calc = PricingCalculator()
    
    cost = calc.calculate("gpt-3.5-turbo", 1000, 500)
    
    # Expected: (1000/1M)*0.5 + (500/1M)*1.5 = 0.0005 + 0.00075 = 0.00125
    assert cost == pytest.approx(0.00125)


def test_claude_pricing():
    """Test Claude cost calculation."""
    calc = PricingCalculator()
    
    cost = calc.calculate("claude-3-sonnet-20240229", 1000, 500)
    
    # Should normalize to "claude-3-sonnet"
    # Expected: (1000/1M)*3 + (500/1M)*15 = 0.003 + 0.0075 = 0.0105
    assert cost == pytest.approx(0.0105)


def test_unknown_model_defaults():
    """Test that unknown models use default pricing."""
    calc = PricingCalculator()
    
    # Unknown model should default to gpt-3.5-turbo
    cost = calc.calculate("unknown-model-123", 1000, 500)
    
    expected_cost = calc.calculate("gpt-3.5-turbo", 1000, 500)
    assert cost == pytest.approx(expected_cost)


def test_custom_pricing():
    """Test custom model pricing."""
    custom = {
        "my-custom-model": {
            "prompt": 5.0,
            "completion": 10.0,
        }
    }
    
    calc = PricingCalculator(custom_pricing=custom)
    cost = calc.calculate("my-custom-model", 1000, 500)
    
    # Expected: (1000/1M)*5 + (500/1M)*10 = 0.005 + 0.005 = 0.01
    assert cost == pytest.approx(0.01)


def test_add_model_pricing():
    """Test adding model pricing dynamically."""
    calc = PricingCalculator()
    calc.add_model_pricing("new-model", 2.0, 4.0)
    
    cost = calc.calculate("new-model", 1000, 500)
    
    # Expected: (1000/1M)*2 + (500/1M)*4 = 0.002 + 0.002 = 0.004
    assert cost == pytest.approx(0.004)


def test_model_name_normalization():
    """Test model name normalization."""
    calc = PricingCalculator()
    
    # These should all resolve to the same pricing
    models = [
        "gpt-4",
        "gpt-4-0613",
        "gpt-4-32k",
        "GPT-4",
    ]
    
    costs = [calc.calculate(m, 1000, 500) for m in models]
    
    # All should be equal
    assert all(c == costs[0] for c in costs)
