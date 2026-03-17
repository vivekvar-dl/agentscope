"""LLM pricing calculator."""

from typing import Dict, Optional


# Pricing per 1M tokens (as of March 2026)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    # OpenAI
    "gpt-4": {"prompt": 30.0, "completion": 60.0},
    "gpt-4-turbo": {"prompt": 10.0, "completion": 30.0},
    "gpt-3.5-turbo": {"prompt": 0.5, "completion": 1.5},
    "gpt-3.5-turbo-instruct": {"prompt": 1.5, "completion": 2.0},
    # Anthropic
    "claude-3-opus": {"prompt": 15.0, "completion": 75.0},
    "claude-3-sonnet": {"prompt": 3.0, "completion": 15.0},
    "claude-3-haiku": {"prompt": 0.25, "completion": 1.25},
    "claude-3.5-sonnet": {"prompt": 3.0, "completion": 15.0"},
    # Google
    "gemini-pro": {"prompt": 0.5, "completion": 1.5},
    "gemini-pro-vision": {"prompt": 0.5, "completion": 1.5},
    # Meta
    "llama-2-70b": {"prompt": 0.7, "completion": 0.9},
    "llama-3-70b": {"prompt": 0.7, "completion": 0.9},
    # Mistral
    "mistral-large": {"prompt": 4.0, "completion": 12.0},
    "mistral-medium": {"prompt": 2.7, "completion": 8.1},
    "mistral-small": {"prompt": 1.0, "completion": 3.0},
}


class PricingCalculator:
    """Calculate LLM API costs."""

    def __init__(self, custom_pricing: Optional[Dict[str, Dict[str, float]]] = None):
        """
        Initialize pricing calculator.
        
        Args:
            custom_pricing: Override default pricing
        """
        self.pricing = {**MODEL_PRICING}
        if custom_pricing:
            self.pricing.update(custom_pricing)

    def calculate(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """
        Calculate cost for a model call.
        
        Args:
            model: Model name (e.g., "gpt-4")
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
        
        Returns:
            Cost in USD
        """
        # Normalize model name
        model_key = self._normalize_model_name(model)

        if model_key not in self.pricing:
            # Unknown model - use GPT-3.5-turbo pricing as default
            model_key = "gpt-3.5-turbo"

        pricing = self.pricing[model_key]

        prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]

        return prompt_cost + completion_cost

    def _normalize_model_name(self, model: str) -> str:
        """Normalize model name for pricing lookup."""
        model = model.lower().strip()

        # Handle versioned models
        if model.startswith("gpt-4-") and "turbo" in model:
            return "gpt-4-turbo"
        elif model.startswith("gpt-4"):
            return "gpt-4"
        elif model.startswith("gpt-3.5") and "instruct" in model:
            return "gpt-3.5-turbo-instruct"
        elif model.startswith("gpt-3.5"):
            return "gpt-3.5-turbo"

        # Claude models
        if "claude-3.5-sonnet" in model:
            return "claude-3.5-sonnet"
        elif "claude-3-opus" in model:
            return "claude-3-opus"
        elif "claude-3-sonnet" in model:
            return "claude-3-sonnet"
        elif "claude-3-haiku" in model:
            return "claude-3-haiku"

        # Return as-is if no normalization needed
        return model

    def get_model_pricing(self, model: str) -> Optional[Dict[str, float]]:
        """Get pricing for a specific model."""
        model_key = self._normalize_model_name(model)
        return self.pricing.get(model_key)

    def add_model_pricing(self, model: str, prompt_price: float, completion_price: float) -> None:
        """
        Add or update pricing for a model.
        
        Args:
            model: Model name
            prompt_price: Price per 1M prompt tokens
            completion_price: Price per 1M completion tokens
        """
        self.pricing[model] = {
            "prompt": prompt_price,
            "completion": completion_price,
        }
