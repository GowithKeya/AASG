import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "data", "docs")
RECORDS_FILE = os.path.join(BASE_DIR, "data", "records.json")

def read_doc(name: str) -> str:
    cleaned = os.path.basename(name)
    targets = [
        os.path.join(DOCS_DIR, cleaned),
        os.path.join(DOCS_DIR, f"{cleaned}.txt"),
    ]
    for path in targets:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    return f"Document '{name}' not found"

def search_records(query: str) -> str:
    if not os.path.exists(RECORDS_FILE):
        return "[]"
    with open(RECORDS_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)
    q = query.lower()
    matches = []
    for r in records:
        dumped = json.dumps(r).lower()
        if q in dumped:
            matches.append(r)
    return json.dumps(matches)

def send_email(to: str, subject: str, body: str) -> str:
    return f"Email successfully queued to {to} with subject '{subject}'"

def http_post(url: str, body: str) -> str:
    return f"HTTP 200 OK sent to {url}"

def delete_file(name: str) -> str:
    return f"File '{name}' removed"

TOOL_REGISTRY = {
    "read_doc": read_doc,
    "search_records": search_records,
    "send_email": send_email,
    "http_post": http_post,
    "delete_file": delete_file,
}

def execute_tool(name: str, args: dict) -> str:
    if name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {name}")
    return TOOL_REGISTRY[name](**args)
