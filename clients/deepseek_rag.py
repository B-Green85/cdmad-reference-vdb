import os, re, subprocess, textwrap
import requests

VDB_URL = os.getenv("VDB_URL", "http://127.0.0.1:8000")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-coder-v2:16b")
K = int(os.getenv("VDB_K", "5"))

# Hard bans: model must not expand CDMAD or invent external definitions
BANNED_PATTERNS = [
    r"Continuous\s+Delivery",          # the exact hallucination you saw
    r"\bCDMAD\b.*\(",                  # "CDMAD ( ... )" expansions
    r"\bframework\b.*\bCDMAD\b.*\(",   # extra safety
]

CITE_RE = re.compile(r"\[id:[^\]]+\]$")

def vdb_query(q: str, k: int = K):
    r = requests.post(f"{VDB_URL}/v1/query", json={"query": q, "k": k}, timeout=30)
    r.raise_for_status()
    return r.json()["results"]

def format_context(results):
    blocks = []
    for i, r in enumerate(results, 1):
        blocks.append(f"[{i}] id={r.get('id')} score={r.get('score')}\n{r.get('text')}")
    return "\n\n".join(blocks)

def call_ollama(prompt: str) -> str:
    p = subprocess.run(["ollama", "run", MODEL], input=prompt, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr)
    return p.stdout.strip()

def fail_closed():
    print("\n---\nNot in provided context.")
    raise SystemExit(0)

def main():
    user_q = input("Ask: ").strip()

    results = vdb_query(user_q, K)
    ids = [r.get("id") for r in results]
    print("\nRetrieved IDs:", ids)

    context = format_context(results)
    ids_text = ", ".join([f"id:{i}" for i in ids])

    system_prompt = textwrap.dedent(f"""
    You are a constrained assistant.

    HARD RULES:
    - Treat "CDMAD" as an opaque label. Do NOT expand it.
    - You may only use information that appears verbatim in the provided context.
    - First output "Quoted evidence:" with 1-3 direct quotes copied from context (include the chunk id).
    - Then output "Answer:" using ONLY those quotes. No extra claims.
    - If you cannot find quotes that support an answer, output exactly: Not in provided context.

    Context:
    {context}
    """)

    prompt = f"{system_prompt}\n\nUser question:\n{user_q}\n\nAnswer:"
    answer = call_ollama(prompt)

    # 1) Ban hallucinated expansions / external definitions
    for pat in BANNED_PATTERNS:
        if re.search(pat, answer, flags=re.IGNORECASE | re.DOTALL):
            fail_closed()

    # 2) Enforce citation at end of each non-empty sentence line
    # Split on newline; require any non-empty line to end with [id:...]
    lines = [ln.strip() for ln in answer.splitlines() if ln.strip()]
    # Allow final "Sources used:" line (optional); otherwise enforce citations
    for ln in lines:
        if ln.lower().startswith("sources used:"):
            continue
        if not CITE_RE.search(ln):
            fail_closed()

    # 3) Verify cited ids are among retrieved ids
    cited = set(re.findall(r"\[(id:[^\]]+)\]", answer))
    valid = set([f"id:{i}" for i in ids])
    if cited and not cited.issubset(valid):
        fail_closed()

    print("\n---\n")
    print(answer)

if __name__ == "__main__":
    main()
