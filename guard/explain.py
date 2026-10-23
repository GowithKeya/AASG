def explain_decision(rule_id: str, tool: str, destination: str | None,
                     leak_found: bool, matches: list[str],
                     tainted: bool, highest_sensitivity: str) -> str:
    matches_str = ", ".join(matches) if matches else "internal data"
    if rule_id == "permission_denied":
        return f"Tool call '{tool}' blocked: tool is not on the firewall's approved tools list."
    if rule_id == "always_approve":
        return f"Tool call '{tool}' held for human review: configured as an always-approve sensitive tool."
    if rule_id == "leak_to_external":
        return f"Blocked exfiltration to external target '{destination}': tool '{tool}' payload contains sensitive data ({matches_str})."
    if rule_id == "destination_not_allowed":
        return f"Blocked unapproved outbound destination '{destination}': destination domain is outside authorized domains."
    if rule_id == "leak_while_tainted":
        return f"Blocked transmission from tainted session: tool '{tool}' payload contains sensitive data ({matches_str}) after untrusted context was ingested."
    if rule_id == "untrusted_influence_on_sink":
        return f"Approval required for outbound sink '{tool}': session is tainted by untrusted data and context contains {highest_sensitivity} records."
    return f"Tool call '{tool}' permitted by default firewall policy."
