"""Provider-abstracted LLM + embedding client. Swap providers via .env, not code."""
import hashlib, json, re
from .config import settings

def chat(system: str, user: str, temperature: float = 0.2, max_tokens: int = 4096) -> str:
    if settings.llm_provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        msg = client.messages.create(
            model=settings.anthropic_model, max_tokens=max_tokens, temperature=temperature,
            system=system, messages=[{"role": "user", "content": user}])
        return "".join(b.text for b in msg.content if b.type == "text")
    if settings.llm_provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model=settings.openai_model, temperature=temperature,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}])
        return resp.choices[0].message.content
    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")

def chat_json(system: str, user: str, **kw) -> dict:
    """Ask for JSON; strip fences; fail loudly if the model didn't comply."""
    raw = chat(system, user + "\n\nRespond with valid JSON only. No markdown fences.", **kw)
    m = re.search(r"\{.*\}|\[.*\]", raw, re.S)
    return json.loads(m.group(0)) if m else json.loads(raw)

def embed(texts: list[str]) -> list[list[float]]:
    if settings.embedding_provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        out = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
        return [d.embedding for d in out.data]
    return [stub_embed(t) for t in texts]

def stub_embed(text: str, dim: int = 1536) -> list[float]:
    """Deterministic local embedding for tests/dev without API keys. NOT semantic."""
    vec = [0.0] * dim
    for token in re.findall(r"\w+", text.lower()):
        h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = sum(v * v for v in vec) ** 0.5 or 1.0
    return [v / norm for v in vec]
