"""Structure-aware chunking.

Proposals, SOWs and RFPs are sectioned documents, so chunks follow headings rather
than a fixed token window. A section longer than the budget is split at paragraph
boundaries and keeps its heading, so no chunk ever loses its context.
"""
import re

from ..config import settings
from ..schemas import Chunk

MD_HEADING = re.compile(r"^#{1,6}\s+\S")
NUMBERED = re.compile(r"^(\d+(\.\d+)*)[.)]?\s+\S")
SENTENCE_END = (".", "!", "?", ",", ";")


def approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def is_heading(line: str) -> bool:
    """A heading is short, unpunctuated at the end, and either markdown, numbered,
    ALL CAPS, or Title Case. Body sentences fail at least one of those tests."""
    s = line.strip()
    if not s or len(s) > 90:
        return False
    if MD_HEADING.match(s):
        return True
    if s.endswith(SENTENCE_END):
        return False
    words = s.split()
    if len(words) > 12:
        return False
    if NUMBERED.match(s):
        return True
    letters = [c for c in s if c.isalpha()]
    if letters and all(c.isupper() for c in letters):
        return True
    return s[0].isupper() and sum(w[0].isupper() for w in words if w[:1].isalpha()) >= max(1, len(words) - 2)


def _split_oversized(text: str, max_tokens: int) -> list[str]:
    """Break a too-long section on blank lines, never mid-paragraph."""
    parts, buf = [], []
    for para in text.split("\n\n"):
        candidate = buf + [para]
        if buf and approx_tokens("\n\n".join(candidate)) > max_tokens:
            parts.append("\n\n".join(buf))
            buf = [para]
        else:
            buf = candidate
    if buf:
        parts.append("\n\n".join(buf))
    return parts


def chunk_document(doc_id: str, text: str, max_tokens: int | None = None) -> list[Chunk]:
    max_tokens = max_tokens or settings.chunk_max_tokens
    chunks: list[Chunk] = []
    heading, buf = "Preamble", []

    def flush(current_heading: str) -> None:
        body = "\n".join(buf).strip()
        if not body:
            return
        pieces = ([body] if approx_tokens(body) <= max_tokens
                  else _split_oversized(body, max_tokens))
        for i, piece in enumerate(pieces):
            label = current_heading if i == 0 else f"{current_heading} (cont. {i + 1})"
            chunks.append(Chunk(doc_id=doc_id, heading=label, text=piece,
                                token_count=approx_tokens(piece)))

    for line in text.splitlines():
        if is_heading(line):
            flush(heading)
            heading, buf = line.strip().lstrip("# ").rstrip(":"), []
        else:
            buf.append(line)
    flush(heading)
    return chunks
