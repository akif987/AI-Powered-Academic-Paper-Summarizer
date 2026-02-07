"""Tests for the compression service."""

import pytest
from unittest.mock import Mock, patch
import httpx

from app.services.compression_service import CompressionService


class TestCompressionService:
    """Tests for CompressionService."""

    @pytest.fixture
    def compression_service(self):
        """Create a compression service with test credentials."""
        with patch("app.services.compression_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                scaledown_api_key="test-api-key",
                scaledown_api_url="https://api.scaledown.ai/v1/compress",
            )
            return CompressionService()

    def test_compress_empty_chunks(self, compression_service):
        """Empty chunks should return empty string."""
        result = compression_service.compress_context([], "query")
        assert result == ""

    def test_compress_combines_chunks(self, compression_service):
        """Chunks should be combined with separators."""
        chunks = ["First chunk", "Second chunk", "Third chunk"]

        with patch.object(
            compression_service, "_call_scaledown_api"
        ) as mock_api:
            mock_api.return_value = "compressed text"

            compression_service.compress_context(chunks, "test query")

            # Check that chunks were combined
            call_args = mock_api.call_args[0]
            context = call_args[0]
            assert "First chunk" in context
            assert "Second chunk" in context
            assert "Third chunk" in context
            assert "---" in context  # Separator

    def test_compress_fallback_on_api_error(self, compression_service):
        """Should return uncompressed text if API fails."""
        chunks = ["Chunk one", "Chunk two"]

        with patch.object(
            compression_service, "_call_scaledown_api"
        ) as mock_api:
            mock_api.side_effect = Exception("API Error")

            result = compression_service.compress_context(chunks, "query")

            # Should return combined chunks as fallback
            assert "Chunk one" in result
            assert "Chunk two" in result

    @patch("httpx.Client")
    def test_api_call_headers(self, mock_client_class, compression_service):
        """API call should include correct headers."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"compressed_context": "compressed"}
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        compression_service._call_scaledown_api("context", "query", 0.5)

        # Check headers were passed
        call_kwargs = mock_client.post.call_args[1]
        headers = call_kwargs["headers"]
        assert "Authorization" in headers
        assert "Bearer" in headers["Authorization"]

    @patch("httpx.Client")
    def test_api_call_payload(self, mock_client_class, compression_service):
        """API call should include correct payload."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"compressed_context": "compressed"}
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        compression_service._call_scaledown_api("test context", "test query", 0.5)

        call_kwargs = mock_client.post.call_args[1]
        payload = call_kwargs["json"]
        
        assert payload["context"] == "test context"
        assert payload["query"] == "test query"
        assert payload["target_ratio"] == 0.5


class TestEstimateCompression:
    """Tests for compression estimation."""

    @pytest.fixture
    def compression_service(self):
        """Create compression service."""
        with patch("app.services.compression_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                scaledown_api_key="test-key",
                scaledown_api_url="https://api.test.com",
            )
            return CompressionService()

    def test_estimate_returns_dict(self, compression_service):
        """Estimate should return dict with required keys."""
        result = compression_service.estimate_compression("Some text here")
        
        assert "original_length" in result
        assert "estimated_compressed_length" in result
        assert "estimated_ratio" in result

    def test_estimate_original_length(self, compression_service):
        """Original length should match input."""
        text = "This is a test string"
        result = compression_service.estimate_compression(text)
        
        assert result["original_length"] == len(text)

    def test_estimate_ratio_reasonable(self, compression_service):
        """Estimated ratio should be between 0 and 1."""
        result = compression_service.estimate_compression("Some text")
        
        assert 0 < result["estimated_ratio"] < 1
