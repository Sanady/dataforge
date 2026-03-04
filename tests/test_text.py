"""Tests for the TextProvider."""

from dataforge import DataForge


class TestQuote:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        quote = self.forge.text.quote()
        assert isinstance(quote, str)
        assert len(quote) > 0

    def test_contains_dash(self) -> None:
        # Quotes have format: "quote" — author
        quote = self.forge.text.quote()
        assert "\u2014" in quote  # em dash

    def test_batch(self) -> None:
        results = self.forge.text.quote(count=10)
        assert isinstance(results, list)
        assert len(results) == 10


class TestHeadline:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        headline = self.forge.text.headline()
        assert isinstance(headline, str)
        assert len(headline) > 0

    def test_batch(self) -> None:
        results = self.forge.text.headline(count=10)
        assert len(results) == 10


class TestBuzzword:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        bw = self.forge.text.buzzword()
        assert isinstance(bw, str)

    def test_batch(self) -> None:
        results = self.forge.text.buzzword(count=50)
        assert len(results) == 50


class TestParagraph:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        para = self.forge.text.paragraph()
        assert isinstance(para, str)
        assert len(para) > 10

    def test_contains_sentences(self) -> None:
        para = self.forge.text.paragraph()
        # Should contain at least one period
        assert "." in para

    def test_batch(self) -> None:
        results = self.forge.text.paragraph(count=5)
        assert len(results) == 5


class TestTextBlock:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_returns_str(self) -> None:
        block = self.forge.text.text_block()
        assert isinstance(block, str)
        assert len(block) > 20

    def test_contains_paragraphs(self) -> None:
        block = self.forge.text.text_block()
        # Multiple paragraphs separated by double newlines
        assert "\n\n" in block

    def test_batch(self) -> None:
        results = self.forge.text.text_block(count=3)
        assert len(results) == 3


class TestTextInSchema:
    def setup_method(self) -> None:
        self.forge = DataForge(locale="en_US", seed=42)

    def test_schema_fields(self) -> None:
        rows = self.forge.to_dict(
            fields=["headline", "buzzword"],
            count=5,
        )
        assert len(rows) == 5
        for row in rows:
            assert "headline" in row
            assert "buzzword" in row
