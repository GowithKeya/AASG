import urllib.parse
import yaml
from shared.config import POLICY_PATH

_cached_policy = None

def get_policy() -> dict:
    global _cached_policy
    if _cached_policy is None:
        with open(POLICY_PATH, "r") as f:
            _cached_policy = yaml.safe_load(f)
    return _cached_policy

def is_tool_allowed(tool: str) -> bool:
    policy = get_policy()
    return tool in policy.get("allowed_tools", [])

def is_always_approve(tool: str) -> bool:
    policy = get_policy()
    return tool in policy.get("always_approve", [])

def is_sink(tool: str) -> bool:
    policy = get_policy()
    sinks = policy.get("sinks", {})
    if isinstance(sinks, dict):
        return tool in sinks
    if isinstance(sinks, list):
        return tool in sinks
    return False

def get_sink_destination(tool: str, args: dict) -> str | None:
    policy = get_policy()
    sinks = policy.get("sinks", {})
    if isinstance(sinks, dict) and tool in sinks:
        dest_key = sinks[tool].get("dest_arg", "to")
        return args.get(dest_key)
    if tool == "send_email":
        return args.get("to")
    if tool == "http_post":
        return args.get("url")
    return None

def extract_domain(destination: str | None) -> str | None:
    if not destination:
        return None
    dest = destination.strip()
    if "@" in dest:
        return dest.split("@")[-1].lower()
    if "://" in dest:
        parsed = urllib.parse.urlparse(dest)
        host = parsed.netloc.split(":")[0].lower()
        return host
    if "/" in dest:
        dest = dest.split("/")[0]
    return dest.lower()

def is_domain_allowed(destination: str | None) -> bool:
    if not destination:
        return False
    domain = extract_domain(destination)
    if not domain:
        return False
    policy = get_policy()
    allowed = policy.get("allowed_domains", [])
    for d in allowed:
        d = d.lower()
        if domain == d or domain.endswith("." + d):
            return True
    return False
