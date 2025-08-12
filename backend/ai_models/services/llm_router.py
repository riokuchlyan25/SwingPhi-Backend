from typing import Dict, List, Optional


def generate(messages: List[Dict[str, str]], *, model: Optional[str] = None, temperature: Optional[float] = None) -> str:
    """Minimal stub router that raises if not configured.

    This satisfies imports if provider modules are not present.
    Replace with provider-backed impl when needed.
    """
    raise RuntimeError("LLM router not configured. Please implement providers or set up Azure/Anthropic providers.")


