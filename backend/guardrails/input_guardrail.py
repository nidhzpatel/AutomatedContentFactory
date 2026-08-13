import re
from typing import Tuple


def validate_input_prompt(prompt: str) -> Tuple[bool, str]:
    """
    Comprehensive Input Guardrail checking for:
    - Prompt Injection attacks
    - System prompt / instruction overrides
    - Jailbreak patterns (DAN, Developer Mode, privilege escalation)
    - Malicious command injection
    """
    if not prompt or not prompt.strip():
        return False, "Prompt cannot be empty"

    lowered = prompt.lower()

    # Jailbreak & Instruction Override Patterns
    injection_patterns = [
        r"ignore\s+previous\s+instructions",
        r"disregard\s+all\s+prior",
        r"system\s+prompt\s+override",
        r"you\s+are\s+now\s+in\s+developer\s+mode",
        r"dan\s+mode",
        r"bypass\s+safety\s+filters",
        r"reveal\s+your\s+instructions",
        r"drop\s+table",
        r"eval\(",
        r"exec\(",
        r"rm\s+-rf",
    ]

    for pattern in injection_patterns:
        if re.search(pattern, lowered):
            return False, f"Prompt injection / jailbreak security violation detected (pattern: '{pattern}')"

    return True, "Input validation passed"
