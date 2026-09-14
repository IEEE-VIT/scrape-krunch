import json
from pathlib import Path

import pytest

import main


@pytest.fixture
def sample_articles():
    return [
        {
            "title": "Example article",
            "link": "https://example.com/article",
            "content": "This is article content.",
            "analysis": "This is article analysis.",
        }
    ]


def test_build_parser_accepts_export_flags():
    parser = main.build_parser()

    args = parser.parse_args(["--json", "--output", "exports/output.json"])
    assert args.json is True
    assert args.output == "exports/output.json"

    args = parser.parse_args(["--markdown", "--output", "exports/output.md"])
    assert args.markdown is True
    assert args.output == "exports/output.md"

    args = parser.parse_args(["--format", "json", "--output", "exports/custom.json"])
    assert args.format == "json"
    assert args.output == "exports/custom.json"


def test_export_articles_to_json(tmp_path, sample_articles):
    output = tmp_path / "articles.json"

    result = main.export_articles(sample_articles, format_name="json", output_path=str(output))

    assert result == str(output)
    assert output.exists()
    payload = json.loads(output.read_text())
    assert payload[0]["title"] == "Example article"
    assert payload[0]["analysis"] == "This is article analysis."


def test_export_articles_to_markdown(tmp_path, sample_articles):
    output = tmp_path / "articles.md"

    result = main.export_articles(sample_articles, format_name="markdown", output_path=str(output))

    assert result == str(output)
    assert output.exists()
    content = output.read_text()
    assert "# Example article" in content
    assert "This is article analysis." in content
