"""Tests for the generation service."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.generation_service import GenerationService, Answer


class TestAnswer:
    """Tests for Answer dataclass."""

    def test_answer_creation(self):
        """Answer should be creatable with all fields."""
        answer = Answer(
            text="This is the answer text.",
            chunk_ids=["chunk-1", "chunk-2"],
            confidence="high",
        )

        assert answer.text == "This is the answer text."
        assert answer.chunk_ids == ["chunk-1", "chunk-2"]
        assert answer.confidence == "high"

    def test_answer_empty_chunks(self):
        """Answer can have empty chunk list."""
        answer = Answer(
            text="Answer without chunks",
            chunk_ids=[],
            confidence="medium",
        )

        assert answer.chunk_ids == []


class TestGenerationService:
    """Tests for GenerationService."""

    @pytest.fixture
    def mock_genai(self):
        """Mock the google.generativeai module."""
        with patch("app.services.generation_service.genai") as mock:
            yield mock

    @pytest.fixture
    def generation_service(self, mock_genai):
        """Create a generation service with mocked API."""
        with patch("app.services.generation_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                gemini_api_key="test-api-key",
                gemini_generation_model="gemini-1.5-flash",
            )
            return GenerationService()

    def test_answer_question_returns_answer(self, generation_service, mock_genai):
        """answer_question should return Answer object."""
        mock_response = Mock()
        mock_response.text = "This is the generated answer."
        generation_service._model.generate_content.return_value = mock_response

        result = generation_service.answer_question(
            context="Test context",
            question="Test question?",
            chunk_ids=["chunk-1"],
        )

        assert isinstance(result, Answer)
        assert result.text == "This is the generated answer."
        assert result.chunk_ids == ["chunk-1"]

    def test_answer_question_handles_error(self, generation_service, mock_genai):
        """answer_question should handle API errors gracefully."""
        generation_service._model.generate_content.side_effect = Exception("API Error")

        result = generation_service.answer_question(
            context="Context",
            question="Question?",
            chunk_ids=[],
        )

        assert isinstance(result, Answer)
        assert "error" in result.text.lower()
        assert result.confidence == "not_found"


class TestConfidenceAssessment:
    """Tests for confidence assessment logic."""

    @pytest.fixture
    def generation_service(self):
        """Create service for testing."""
        with patch("app.services.generation_service.genai"):
            with patch("app.services.generation_service.get_settings") as mock_settings:
                mock_settings.return_value = Mock(
                    gemini_api_key="test-key",
                    gemini_generation_model="gemini-1.5-flash",
                )
                return GenerationService()

    def test_high_confidence(self, generation_service):
        """Clear answers should have high confidence."""
        answer = "The paper clearly states that X is the main finding."
        confidence = generation_service._assess_confidence(answer)
        assert confidence == "high"

    def test_not_found_confidence(self, generation_service):
        """Answers indicating missing info should have not_found confidence."""
        answers = [
            "This information is not present in the paper.",
            "The paper does not contain this information.",
            "I could not find this in the provided sections.",
        ]

        for answer in answers:
            confidence = generation_service._assess_confidence(answer)
            assert confidence == "not_found", f"Failed for: {answer}"

    def test_medium_confidence(self, generation_service):
        """Uncertain answers should have medium confidence."""
        answers = [
            "The results may suggest that...",
            "It appears to be the case that...",
            "This might indicate...",
        ]

        for answer in answers:
            confidence = generation_service._assess_confidence(answer)
            assert confidence == "medium", f"Failed for: {answer}"


class TestSummaryGeneration:
    """Tests for summary generation."""

    @pytest.fixture
    def generation_service(self):
        """Create service with mocked API."""
        with patch("app.services.generation_service.genai") as mock_genai:
            with patch("app.services.generation_service.get_settings") as mock_settings:
                mock_settings.return_value = Mock(
                    gemini_api_key="test-key",
                    gemini_generation_model="gemini-1.5-flash",
                )
                service = GenerationService()
                
                # Setup mock response
                mock_response = Mock()
                mock_response.text = "Generated summary text."
                service._model.generate_content.return_value = mock_response
                
                return service

    def test_generate_abstract_summary(self, generation_service):
        """Should generate abstract-level summary."""
        result = generation_service.generate_summary(
            "Paper text here...",
            summary_type="abstract",
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_section_summary(self, generation_service):
        """Should generate section-level summary."""
        result = generation_service.generate_summary(
            "Paper text here...",
            summary_type="section",
        )

        assert isinstance(result, str)

    def test_generate_keypoints(self, generation_service):
        """Should generate key points."""
        result = generation_service.generate_summary(
            "Paper text here...",
            summary_type="keypoints",
        )

        assert isinstance(result, str)

    def test_handles_generation_error(self, generation_service):
        """Should handle generation errors."""
        generation_service._model.generate_content.side_effect = Exception("Error")

        result = generation_service.generate_summary("Text", "abstract")

        assert "Failed" in result or "error" in result.lower()


class TestPromptBuilding:
    """Tests for prompt construction."""

    @pytest.fixture
    def generation_service(self):
        """Create service for testing."""
        with patch("app.services.generation_service.genai"):
            with patch("app.services.generation_service.get_settings") as mock_settings:
                mock_settings.return_value = Mock(
                    gemini_api_key="test-key",
                    gemini_generation_model="gemini-1.5-flash",
                )
                return GenerationService()

    def test_qa_prompt_includes_context(self, generation_service):
        """QA prompt should include the context."""
        prompt = generation_service._build_qa_prompt(
            context="This is the context.",
            question="What is the answer?",
        )

        assert "This is the context." in prompt
        assert "What is the answer?" in prompt

    def test_qa_prompt_includes_instructions(self, generation_service):
        """QA prompt should include anti-hallucination instructions."""
        prompt = generation_service._build_qa_prompt("context", "question")

        assert "ONLY" in prompt or "only" in prompt
        assert "not found" in prompt.lower() or "not present" in prompt.lower()

    def test_summary_prompts_differ_by_type(self, generation_service):
        """Different summary types should have different prompts."""
        abstract_prompt = generation_service._build_summary_prompt("text", "abstract")
        section_prompt = generation_service._build_summary_prompt("text", "section")
        keypoints_prompt = generation_service._build_summary_prompt("text", "keypoints")

        # Prompts should be different
        assert abstract_prompt != section_prompt
        assert section_prompt != keypoints_prompt
        assert abstract_prompt != keypoints_prompt
