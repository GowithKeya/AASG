import os

DB_PATH = os.getenv("DB_PATH", "firewall.db")
POLICY_PATH = os.getenv("POLICY_PATH", "policy.yaml")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
INJECTION_THRESHOLD = float(os.getenv("INJECTION_THRESHOLD", "0.7"))
LAYERS = [x.strip() for x in os.getenv("LAYERS", "injection,taint,policy,leak").split(",") if x.strip()]
ALLOWED_DOMAINS = ["acme.com"]
QUARANTINE_PLACEHOLDER = "[QUARANTINED CONTENT - POTENTIAL PROMPT INJECTION DETECTED]"

def layer_active(name: str) -> bool:
    return name in LAYERS
