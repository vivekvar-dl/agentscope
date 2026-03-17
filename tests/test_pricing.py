"""Tests for pricing calculator."""

import pytest

from agentscope.core.pricing import PricingCalculator, MODEL_PRICING


class TestPricingCalculatorBasic:
    """Test basic pricing calculations."""

    def test_gpt4_pricing(self):
        """Test GPT-4 cost calculation."""
        calc = PricingCalculator()
        
        # 1000 prompt + 500 completion tokens
        cost = calc.calculate("gpt-4", 1000, 500)
        
        # Expected: (1000/1M)*30 + (500/1M)*60 = 0.03 + 0.03 = 0.06
        assert cost == pytest.approx(0.06)

    def test_gpt35_pricing(self):
        """Test GPT-3.5-turbo cost calculation."""
        calc = PricingCalculator()
        
        cost = calc.calculate("gpt-3.5-turbo", 1000, 500)
        
        # Expected: (1000/1M)*0.5 + (500/1M)*1.5 = 0.0005 + 0.00075 = 0.00125
        assert cost == pytest.approx(0.00125)

    def test_zero_tokens(self):
        """Test calculation with zero tokens."""
        calc = PricingCalculator()
        
        cost = calc.calculate("gpt-4", 0, 0)
        assert cost == 0.0

    def test_large_token_count(self):
        """Test calculation with large token counts."""
        calc = PricingCalculator()
        
        # 1M prompt + 1M completion tokens
        cost = calc.calculate("gpt-4", 1_000_000, 1_000_000)
        
        # Expected: 30 + 60 = 90
        assert cost == pytest.approx(90.0)


class TestClaudePricing:
    """Test Claude model pricing."""

    def test_claude_pricing(self):
        """Test Claude cost calculation."""
        calc = PricingCalculator()
        
        cost = calc.calculate("claude-3-sonnet-20240229", 1000, 500)
        
        # Should normalize to "claude-3-sonnet"
        # Expected: (1000/1M)*3 + (500/1M)*15 = 0.003 + 0.0075 = 0.0105
        assert cost == pytest.approx(0.0105)

    def test_claude_opus_pricing(self):
        """Test Claude Opus pricing."""
        calc = PricingCalculator()
        
        cost = calc.calculate("claude-3-opus", 1000, 500)
        
        # Expected: (1000/1M)*15 + (500/1M)*75 = 0.015 + 0.0375 = 0.0525
        assert cost == pytest.approx(0.0525)

    def test_claude_haiku_pricing(self):
        """Test Claude Haiku pricing."""
        calc = PricingCalculator()
        
        cost = calc.calculate("claude-3-haiku", 1000, 500)
        
        # Expected: (1000/1M)*0.25 + (500/1M)*1.25 = 0.00025 + 0.000625 = 0.000875
        assert cost == pytest.approx(0.000875)


class TestModelNormalization:
    """Test model name normalization."""

    def test_unknown_model_defaults(self):
        """Test that unknown models use default pricing."""
        calc = PricingCalculator()
        
        # Unknown model should default to gpt-3.5-turbo
        cost = calc.calculate("unknown-model-123", 1000, 500)
        
        expected_cost = calc.calculate("gpt-3.5-turbo", 1000, 500)
        assert cost == pytest.approx(expected_cost)

    def test_model_name_normalization(self):
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

    def test_case_insensitive(self):
        """Test that model names are case-insensitive."""
        calc = PricingCalculator()
        
        cost_lower = calc.calculate("gpt-4", 1000, 500)
        cost_upper = calc.calculate("GPT-4", 1000, 500)
        cost_mixed = calc.calculate("Gpt-4", 1000, 500)
        
        assert cost_lower == cost_upper == cost_mixed


class TestCustomPricing:
    """Test custom pricing configuration."""

    def test_custom_pricing(self):
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

    def test_add_model_pricing(self):
        """Test adding model pricing dynamically."""
        calc = PricingCalculator()
        calc.add_model_pricing("new-model", 2.0, 4.0)
        
        cost = calc.calculate("new-model", 1000, 500)
        
        # Expected: (1000/1M)*2 + (500/1M)*4 = 0.002 + 0.002 = 0.004
        assert cost == pytest.approx(0.004)

    def test_get_model_pricing(self):
        """Test getting pricing for a model."""
        calc = PricingCalculator()
        
        pricing = calc.get_model_pricing("gpt-4")
        
        assert pricing is not None
        assert "prompt" in pricing
        assert "completion" in pricing
        assert pricing["prompt"] == 30.0
        assert pricing["completion"] == 60.0

    def test_get_unknown_model_pricing(self):
        """Test getting pricing for unknown model."""
        calc = PricingCalculator()
        
        pricing = calc.get_model_pricing("unknown-model")
        
        assert pricing is None


class TestAllSupportedModels:
    """Test all supported models have valid pricing."""

    def test_all_models_calculable(self):
        """Test that all models in MODEL_PRICING can calculate costs."""
        calc = PricingCalculator()
        
        for model_name in MODEL_PRICING.keys():
            cost = calc.calculate(model_name, 1000, 500)
            assert cost > 0, f"Model {model_name} should have positive cost"

    def test_model_pricing_structure(self):
        """Test that all models have required pricing structure."""
        for model_name, pricing in MODEL_PRICING.items():
            assert "prompt" in pricing, f"{model_name} missing prompt pricing"
            assert "completion" in pricing, f"{model_name} missing completion pricing"
            assert pricing["prompt"] > 0, f"{model_name} has invalid prompt price"
            assert pricing["completion"] > 0, f"{model_name} has invalid completion price"
