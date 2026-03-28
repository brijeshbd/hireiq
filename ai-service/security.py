import re
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# ── PII DETECTION ─────────────────────────────────────────────
# Microsoft Presidio — detects and removes personal information
# Java equivalent: new PIIDetector()
analyzer  = AnalyzerEngine()
anonymizer = AnonymizerEngine()


def scrub_pii(text: str) -> dict:
    """
    Detect and remove PII from text before sending to LLM.

    Detects: emails, phone numbers, SSN, credit cards,
             names, addresses, passport numbers etc.

    Java equivalent:
    PIIResult result = piiDetector.scrub(text);

    Returns:
        scrubbed_text: text with PII replaced
        pii_found:     list of PII types detected
        was_modified:  whether any PII was found
    """
    # Analyze for PII
    results = analyzer.analyze(
        text=text,
        language="en",
        entities=[
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "CREDIT_CARD",
            "IBAN_CODE",
            "US_SSN",
            "US_PASSPORT",
            "PERSON",
            "LOCATION",
            "URL"
        ]
    )

    if not results:
        return {
            "scrubbed_text": text,
            "pii_found":     [],
            "was_modified":  False
        }

    # Anonymize — replace PII with placeholders
    # e.g. "My email is john@gmail.com" → "My email is <EMAIL_ADDRESS>"
    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=results
    )

    pii_types = list(set(r.entity_type for r in results))

    return {
        "scrubbed_text": anonymized.text,
        "pii_found":     pii_types,
        "was_modified":  True
    }


# ── PROMPT INJECTION DETECTION ────────────────────────────────
# Detect attempts to hijack the AI system prompt
INJECTION_PATTERNS = [
    # Classic injection attempts
    r"ignore (all |previous |above |your )?instructions",
    r"forget (everything|all instructions|your instructions)",
    r"you are now",
    r"pretend (you are|to be)",
    r"act as (if you are|a)?",
    r"your new instructions",
    r"system prompt",
    r"disregard (all |previous )?",

    # Role jailbreaks
    r"dan mode",
    r"jailbreak",
    r"developer mode",
    r"unrestricted mode",

    # Attempts to reveal internals
    r"reveal your (prompt|instructions|system)",
    r"show me your (prompt|instructions)",
    r"what are your instructions",

    # Manipulation attempts
    r"you must (now|always|never)",
    r"from now on you",
    r"override (your |all )?",
]

def detect_prompt_injection(text: str) -> dict:
    """
    Detect prompt injection attempts.

    Java equivalent:
    InjectionResult result = injectionDetector.analyze(text);

    Returns:
        is_injection: whether injection was detected
        patterns:     which patterns matched
        risk_level:   low/medium/high
    """
    text_lower = text.lower()
    matched_patterns = []

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            matched_patterns.append(pattern)

    if not matched_patterns:
        return {
            "is_injection": False,
            "patterns":     [],
            "risk_level":   "low"
        }

    risk_level = "high" if len(matched_patterns) > 2 else "medium"

    return {
        "is_injection": True,
        "patterns":     matched_patterns,
        "risk_level":   risk_level
    }


# ── INPUT VALIDATION ──────────────────────────────────────────
def validate_input(text: str, max_length: int = 5000) -> dict:
    """
    Validate and sanitize user input.

    Checks:
    - Not empty
    - Not too long
    - No null bytes or control characters
    - Not pure whitespace

    Java equivalent:
    ValidationResult result = inputValidator.validate(text, maxLength);
    """
    if not text or not text.strip():
        return {
            "valid":   False,
            "reason":  "Input cannot be empty"
        }

    if len(text) > max_length:
        return {
            "valid":   False,
            "reason":  f"Input too long. Maximum {max_length} characters allowed."
        }

    # Remove null bytes and control characters
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    if len(cleaned.strip()) == 0:
        return {
            "valid":   False,
            "reason":  "Input contains only invalid characters"
        }

    return {
        "valid":        True,
        "cleaned_text": cleaned.strip()
    }


# ── FULL SECURITY CHECK ───────────────────────────────────────
def security_check(text: str) -> dict:
    """
    Run all security checks on input text.

    Order:
    1. Validate input
    2. Detect prompt injection
    3. Scrub PII

    Java equivalent:
    SecurityResult result = securityService.check(text);
    """
    # Step 1: Validate
    validation = validate_input(text)
    if not validation["valid"]:
        return {
            "safe":    False,
            "reason":  validation["reason"],
            "text":    None
        }

    cleaned_text = validation["cleaned_text"]

    # Step 2: Check for injection
    injection = detect_prompt_injection(cleaned_text)
    if injection["is_injection"]:
        return {
            "safe":       False,
            "reason":     "Potential prompt injection detected",
            "risk_level": injection["risk_level"],
            "text":       None
        }

    # Step 3: Scrub PII
    pii_result = scrub_pii(cleaned_text)

    return {
        "safe":          True,
        "text":          pii_result["scrubbed_text"],
        "pii_found":     pii_result["pii_found"],
        "was_modified":  pii_result["was_modified"]
    }