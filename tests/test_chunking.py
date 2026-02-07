"""Tests for the chunking service."""

import pytest

from app.services.chunking_service import ChunkingService, ChunkData


@pytest.fixture
def chunking_service():
    """Create a chunking service instance."""
    return ChunkingService()


class TestTokenCounting:
    """Tests for token counting functionality."""

    def test_count_tokens_empty(self, chunking_service):
        """Empty string should have 0 tokens."""
        assert chunking_service.count_tokens("") == 0

    def test_count_tokens_simple(self, chunking_service):
        """Simple text should return reasonable token count."""
        text = "Hello, world!"
        tokens = chunking_service.count_tokens(text)
        assert tokens > 0
        assert tokens < 10  # Simple text shouldn't have many tokens

    def test_count_tokens_longer(self, chunking_service):
        """Longer text should have more tokens."""
        short_text = "Hello"
        long_text = "Hello, this is a much longer piece of text that should have more tokens."
        
        short_tokens = chunking_service.count_tokens(short_text)
        long_tokens = chunking_service.count_tokens(long_text)
        
        assert long_tokens > short_tokens


class TestChunking:
    """Tests for text chunking functionality."""

    def test_chunk_empty_text(self, chunking_service):
        """Empty text should return empty list."""
        chunks = chunking_service.chunk_text("")
        assert chunks == []

    def test_chunk_short_text(self, chunking_service):
        """Short text should return single chunk."""
        text = "This is a short piece of text."
        chunks = chunking_service.chunk_text(text)
        
        assert len(chunks) == 1
        assert chunks[0].content == text.strip()
        assert chunks[0].chunk_index == 0

    def test_chunk_preserves_content(self, chunking_service):
        """Chunking should preserve all content."""
        text = "First sentence. Second sentence. Third sentence."
        chunks = chunking_service.chunk_text(text)
        
        # All content should be present in chunks
        combined = " ".join(c.content for c in chunks)
        assert "First sentence" in combined
        assert "Second sentence" in combined
        assert "Third sentence" in combined

    def test_chunk_index_ordering(self, chunking_service):
        """Chunks should have sequential indices."""
        # Create text long enough to produce multiple chunks
        text = "This is a test sentence. " * 200
        chunks = chunking_service.chunk_text(text, chunk_size=100, chunk_overlap=10)
        
        if len(chunks) > 1:
            indices = [c.chunk_index for c in chunks]
            assert indices == list(range(len(chunks)))

    def test_chunk_has_token_count(self, chunking_service):
        """Each chunk should have a valid token count."""
        text = "This is some sample text for chunking."
        chunks = chunking_service.chunk_text(text)
        
        for chunk in chunks:
            assert chunk.token_count > 0
            # Token count should match actual count
            assert chunk.token_count == chunking_service.count_tokens(chunk.content)


class TestSectionDetection:
    """Tests for section detection in academic papers."""

    def test_detect_introduction_section(self, chunking_service):
        """Should detect Introduction as a section."""
        text = """Abstract
This is the abstract.

1. Introduction
This is the introduction section.

2. Methods
These are the methods."""
        
        chunks = chunking_service.chunk_text(text)
        section_titles = [c.section_title for c in chunks if c.section_title]
        
        # Should detect at least some sections
        assert len(section_titles) > 0

    def test_no_sections_returns_content(self, chunking_service):
        """Text without sections should still be chunked."""
        text = "Just some plain text without any section headers. It goes on and on."
        chunks = chunking_service.chunk_text(text)
        
        assert len(chunks) > 0
        assert chunks[0].content == text.strip()


class TestChunkData:
    """Tests for ChunkData dataclass."""

    def test_chunk_data_creation(self):
        """ChunkData should be creatable with all fields."""
        chunk = ChunkData(
            content="Test content",
            section_title="Introduction",
            chunk_index=0,
            token_count=5,
        )
        
        assert chunk.content == "Test content"
        assert chunk.section_title == "Introduction"
        assert chunk.chunk_index == 0
        assert chunk.token_count == 5

    def test_chunk_data_optional_section(self):
        """Section title should be optional."""
        chunk = ChunkData(
            content="Test content",
            section_title=None,
            chunk_index=0,
            token_count=5,
        )
        
        assert chunk.section_title is None
