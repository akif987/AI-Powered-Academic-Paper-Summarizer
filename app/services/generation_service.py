"""Generation service using Google Gemini API for Q&A and summarization."""

import logging
from dataclasses import dataclass
from typing import Optional

import google.generativeai as genai
import warnings

# Suppress deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class Answer:
    """Structured answer with citations."""

    text: str
    chunk_ids: list[str]
    confidence: str  # 'high', 'medium', 'low', 'not_found'


class GenerationService:
    """Service for generating answers and summaries using Gemini."""

    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self._api_key = api_key or settings.gemini_api_key
        self._model_name = settings.gemini_generation_model

        # Configure and create model
        genai.configure(api_key=self._api_key)
        self._model = genai.GenerativeModel(self._model_name)

    def answer_question(
        self,
        context: str,
        question: str,
        chunk_ids: list[str],
    ) -> Answer:
        """
        Generate an answer to a question based on provided context.

        Args:
            context: The compressed/retrieved context.
            question: The user's question.
            chunk_ids: IDs of chunks used for citation.

        Returns:
            Answer object with text and confidence level.
        """
        prompt = self._build_qa_prompt(context, question)

        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1024,
                ),
            )

            answer_text = response.text.strip()

            # Determine confidence based on response content
            confidence = self._assess_confidence(answer_text)

            return Answer(
                text=answer_text,
                chunk_ids=chunk_ids,
                confidence=confidence,
            )

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return Answer(
                text=f"I apologize, but I encountered an error generating a response: {e}",
                chunk_ids=chunk_ids,
                confidence="not_found",
            )

    def _build_qa_prompt(self, context: str, question: str) -> str:
        """Build the prompt for question answering."""
        return f"""You are an expert academic paper analyst. Answer the following question based ONLY on the provided context from an academic paper.

IMPORTANT INSTRUCTIONS:
1. Only use information explicitly stated in the context
2. If the answer is not found in the context, clearly state "This information is not present in the provided paper sections."
3. Be precise and technically accurate
4. Cite specific parts of the context when relevant
5. Do not make up or hallucinate any information

CONTEXT FROM PAPER:
{context}

QUESTION: {question}

ANSWER:"""

    def _assess_confidence(self, answer: str) -> str:
        """Assess confidence level based on answer content."""
        lower_answer = answer.lower()

        not_found_phrases = [
            "not present",
            "not found",
            "not mentioned",
            "does not contain",
            "no information",
            "cannot find",
            "not explicitly",
            "not stated",
        ]

        uncertain_phrases = [
            "may",
            "might",
            "possibly",
            "it seems",
            "appears to",
            "unclear",
            "not certain",
        ]

        if any(phrase in lower_answer for phrase in not_found_phrases):
            return "not_found"
        elif any(phrase in lower_answer for phrase in uncertain_phrases):
            return "medium"
        else:
            return "high"

    def generate_summary(
        self,
        text: str,
        summary_type: str = "abstract",
    ) -> str:
        """
        Generate a summary of the paper.

        Args:
            text: The full paper text or relevant sections.
            summary_type: Type of summary - 'abstract', 'section', or 'keypoints'.

        Returns:
            Generated summary text.
        """
        prompt = self._build_summary_prompt(text, summary_type)

        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2048 if summary_type == "section" else 1024,
                ),
            )

            return response.text.strip()

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return f"Failed to generate summary: {e}"

    def _build_summary_prompt(self, text: str, summary_type: str) -> str:
        """Build prompt for summary generation."""
        if summary_type == "abstract":
            instruction = """Provide a concise 2-3 sentence summary of this academic paper that captures:
- The main research question or problem
- The key methodology or approach
- The primary findings or contributions

Keep it accessible but technically accurate."""

        elif summary_type == "section":
            instruction = """Provide a structured summary of this academic paper with the following sections:
- **Background**: Brief context and problem statement (2-3 sentences)
- **Methodology**: Key methods and approach (2-3 sentences)
- **Results**: Main findings (3-4 sentences)
- **Significance**: Why this matters and implications (1-2 sentences)

Use clear, precise language and maintain technical accuracy."""

        elif summary_type == "keypoints":
            instruction = """Extract the 5-7 most important key points from this academic paper.

Format as a bulleted list where each point:
- Captures a distinct and significant finding, claim, or contribution
- Is self-contained and understandable
- Uses precise technical language from the paper

Start each bullet with an action verb or key concept."""

        else:
            instruction = f"Summarize this paper ({summary_type} style)."

        return f"""You are an expert at summarizing academic papers accurately and concisely.

INSTRUCTIONS:
{instruction}

IMPORTANT:
- Only include information explicitly stated in the paper
- Do not add interpretations or outside knowledge
- If certain information is unclear or missing, acknowledge it

PAPER TEXT:
{text}

SUMMARY:"""

    def generate_section_summary(
        self,
        section_title: str,
        section_content: str,
    ) -> str:
        """Generate a summary for a specific paper section."""
        prompt = f"""Summarize this section from an academic paper in 2-3 sentences.
Capture the key information while remaining technically accurate.

SECTION: {section_title}

CONTENT:
{section_content}

SUMMARY:"""

        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=256,
                ),
            )
            return response.text.strip()

        except Exception as e:
            logger.error(f"Section summary failed: {e}")
            return f"Failed to summarize section: {e}"
