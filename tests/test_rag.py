"""Tests for Advanced RAG Pipeline (Ingestion, Chunking, and Search)."""

from src.rag.rag_pipeline import chunk_document_text, ingest_policy_document, search_rag_chunks


def test_chunk_document_text():
    """Text is split into semantic chunks based on section headers."""
    sample = """
    ## Section 1: Inpatient Hospitalization
    All room charges covered up to 1% of sum insured.
    
    ## Section 2: Exclusions
    Cosmetic surgery is strictly excluded.
    """
    chunks = chunk_document_text(sample)
    assert len(chunks) == 2
    assert "Section 1" in chunks[0]["section_title"]
    assert "Section 2" in chunks[1]["section_title"]


def test_ingest_and_search_rag_document():
    """Admin ingests a new document, which is indexed in FTS5 and immediately searchable."""
    content = """
    ## Section 1.1: Accidental Shield
    Immediate financial assistance in the event of accidental injury on public transport.
    
    ## Section 1.2: Ambulance Allowance
    Emergency ambulance expenses capped at Rs. 2,000 per incident.
    """
    ok, doc_id, chunk_count = ingest_policy_document(
        title="Accident Shield Plan Wording v1.0",
        raw_content=content,
        version="v1.0",
        effective_date="2026-05-01",
    )
    assert ok is True
    assert chunk_count == 2
    assert doc_id.startswith("DOC-")

    # Search for ambulance
    results = search_rag_chunks("ambulance", top_k=2)
    assert len(results) > 0
    assert any("ambulance" in r["chunk_text"].lower() for r in results)
