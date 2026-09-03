from app.ingestion.chunker import chunk_document, is_heading

DOC = """Executive Summary
We propose a full replacement of the reporting platform.

Scope of Work
Discovery workshops, migration design, and a handover programme.

3.1 Commercial Terms
Fixed price, invoiced monthly in arrears.
"""


def test_chunks_split_on_headings_including_short_sections():
    chunks = chunk_document("doc1", DOC)
    headings = [c.heading for c in chunks]
    assert headings == ["Executive Summary", "Scope of Work", "3.1 Commercial Terms"]
    assert "reporting platform" in chunks[0].text


def test_body_sentences_are_not_mistaken_for_headings():
    assert is_heading("Scope of Work")
    assert is_heading("## Pricing Summary")
    assert is_heading("SECTION 4 REQUIREMENTS")
    assert not is_heading("We propose a full replacement of the reporting platform.")
    assert not is_heading("The vendor shall provide named team members for the duration")


def test_oversized_sections_split_at_paragraph_boundaries_and_keep_heading():
    para = "word " * 200  # ~250 tokens per paragraph
    doc = "Approach\n" + "\n\n".join([para] * 4)
    chunks = chunk_document("doc2", doc, max_tokens=300)
    assert len(chunks) > 1
    assert all(c.heading.startswith("Approach") for c in chunks)
    assert all(c.token_count <= 400 for c in chunks)
