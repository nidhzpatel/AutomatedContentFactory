from backend.tools.source_validator import validate_source
from backend.tools.article_exporter import export_article_to_markdown


def test_validate_source():
    assert validate_source("https://example.com") is True
    assert validate_source("http://insecure.com") is False


def test_export_article_to_markdown():
    output = export_article_to_markdown("Test Title", "Test Content Body")
    assert "# Test Title" in output
    assert "Test Content Body" in output
