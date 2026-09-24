import pytest

from backend.crews.content_crew import ContentCrew
from backend.crews.research_crew import ResearchCrew
from backend.models.research import ResearchOutput

SAMPLE_RESEARCH = (
    "SUMMARY: Quantum error correction protects fragile qubit states via surface codes.\n"
    "It enables fault-tolerant computation at scale.\n"
    "KEY FINDINGS:\n"
    "- Surface codes tolerate 1% physical error rates\n"
    "- Logical error rates drop exponentially with code distance\n"
    "SOURCES:\n"
    "- Nielsen & Chuang | https://example.edu/qec\n"
    "- arXiv:2301.00001 | https://arxiv.org/abs/2301.00001\n"
)

SAMPLE_ARTICLE = (
    "# Mastering Quantum Computing: A Comprehensive Overview\n\n"
    "## Introduction\n"
    "Quantum computing leverages superposition and entanglement to solve problems "
    "intractable for classical machines. " * 3
)


def test_research_crew_parses_structured_output():
    result = ResearchCrew("Quantum Computing")._parse_result(SAMPLE_RESEARCH)
    assert "Quantum error correction" in result.summary
    assert any("Surface codes" in f for f in result.key_findings)
    assert len(result.sources) == 2
    assert result.sources[0].url == "https://example.edu/qec"


def test_research_crew_garbage_falls_back_to_canned():
    result = ResearchCrew("AI Safety")._parse_result("I cannot fulfill this request.")
    assert result.summary == (
        "Comprehensive research summary analyzing key trends, safeguards, "
        "and system architecture for AI Safety."
    )
    assert len(result.sources) == 2


def test_content_crew_parses_article():
    research = ResearchOutput(topic="Quantum Computing", summary="s")
    result = ContentCrew("Quantum Computing", research)._parse_result(SAMPLE_ARTICLE)
    assert result.title == "Mastering Quantum Computing: A Comprehensive Overview"
    assert result.word_count == len(SAMPLE_ARTICLE.split())
    assert result.body.startswith("# Mastering Quantum")


def test_content_crew_short_output_raises():
    research = ResearchOutput(topic="AI Safety", summary="s")
    with pytest.raises(ValueError):
        ContentCrew("AI Safety", research)._parse_result("too short")
