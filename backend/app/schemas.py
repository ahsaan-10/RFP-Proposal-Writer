from pydantic import BaseModel, Field

class DocMetadata(BaseModel):
    doc_id: str
    filename: str
    industry: str = "unknown"
    service_type: str = "unknown"
    year: int | None = None
    outcome: str = "unknown"          # won | lost | unknown

class Chunk(BaseModel):
    doc_id: str
    heading: str = ""
    text: str
    token_count: int = 0

class Requirement(BaseModel):
    id: str
    text: str
    category: str = "general"         # scope | technical | commercial | compliance | general

class Evidence(BaseModel):
    chunk_id: int
    doc_id: str
    filename: str
    heading: str = ""
    text: str
    score: float = 0.0

class PricingLine(BaseModel):
    item: str
    amount: float
    basis: str                        # rule | precedent:<doc_id>
    note: str = ""

class ProposalSection(BaseModel):
    title: str
    body: str
    citations: list[int] = Field(default_factory=list)  # chunk ids referenced

class ProposalDraft(BaseModel):
    title: str = ""
    sections: list[ProposalSection] = Field(default_factory=list)
    pricing: list[PricingLine] = Field(default_factory=list)
    citation_audit: dict = Field(default_factory=dict)
