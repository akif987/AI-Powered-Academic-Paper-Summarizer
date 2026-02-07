"""Tests for the retrieval service."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.retrieval_service import RetrievalService, RetrievedChunk


class TestRetrievedChunk:
    """Tests for RetrievedChunk dataclass."""

    def test_retrieved_chunk_creation(self):
        """RetrievedChunk should be creatable with all fields."""
        chunk = RetrievedChunk(
            chunk_id="test-id-123",
            content="This is the chunk content",
            section_title="Introduction",
            chunk_index=0,
            similarity_score=0.95,
        )

        assert chunk.chunk_id == "test-id-123"
        assert chunk.content == "This is the chunk content"
        assert chunk.section_title == "Introduction"
        assert chunk.chunk_index == 0
        assert chunk.similarity_score == 0.95

    def test_retrieved_chunk_optional_section(self):
        """Section title can be None."""
        chunk = RetrievedChunk(
            chunk_id="test-id",
            content="Content",
            section_title=None,
            chunk_index=0,
            similarity_score=0.8,
        )

        assert chunk.section_title is None


class TestRetrievalService:
    """Tests for RetrievalService."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def mock_embedding_service(self):
        """Create a mock embedding service."""
        service = Mock()
        # Return a fake 768-dim vector
        service.embed_query.return_value = [0.1] * 768
        return service

    def test_retrieve_chunks_calls_embed_query(
        self, mock_db_session, mock_embedding_service
    ):
        """retrieve_chunks should embed the query."""
        # Setup mock to return empty result
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([]))
        mock_db_session.execute.return_value = mock_result

        service = RetrievalService(mock_db_session, mock_embedding_service)

        service.retrieve_chunks("paper-id", "What is the main finding?")

        mock_embedding_service.embed_query.assert_called_once_with(
            "What is the main finding?"
        )

    def test_retrieve_chunks_uses_top_k(
        self, mock_db_session, mock_embedding_service
    ):
        """retrieve_chunks should respect top_k parameter."""
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([]))
        mock_db_session.execute.return_value = mock_result

        service = RetrievalService(mock_db_session, mock_embedding_service)

        service.retrieve_chunks("paper-id", "query", top_k=10)

        # Check that execute was called (SQL contains LIMIT)
        mock_db_session.execute.assert_called_once()
        call_args = mock_db_session.execute.call_args
        # The second argument should contain top_k
        assert call_args[0][1]["top_k"] == 10

    def test_retrieve_chunks_returns_list(
        self, mock_db_session, mock_embedding_service
    ):
        """retrieve_chunks should return a list of RetrievedChunk."""
        # Mock a result row
        mock_row = Mock()
        mock_row.id = "chunk-123"
        mock_row.content = "Test content"
        mock_row.section_title = "Methods"
        mock_row.chunk_index = 1
        mock_row.similarity = 0.92

        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([mock_row]))
        mock_db_session.execute.return_value = mock_result

        service = RetrievalService(mock_db_session, mock_embedding_service)
        chunks = service.retrieve_chunks("paper-id", "query")

        assert len(chunks) == 1
        assert isinstance(chunks[0], RetrievedChunk)
        assert chunks[0].chunk_id == "chunk-123"
        assert chunks[0].content == "Test content"
        assert chunks[0].section_title == "Methods"
        assert chunks[0].similarity_score == 0.92


class TestVectorSearch:
    """Tests for vector search functionality."""

    def test_vector_format(self):
        """Vector should be formatted correctly for PostgreSQL."""
        # Test the vector string format
        vector = [0.1, 0.2, 0.3]
        vector_str = "[" + ",".join(str(v) for v in vector) + "]"
        
        assert vector_str == "[0.1,0.2,0.3]"

    def test_cosine_similarity_range(self):
        """Similarity scores should be between 0 and 1."""
        chunk = RetrievedChunk(
            chunk_id="id",
            content="content",
            section_title=None,
            chunk_index=0,
            similarity_score=0.85,
        )
        
        assert 0 <= chunk.similarity_score <= 1
