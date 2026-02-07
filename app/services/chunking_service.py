"""Text chunking service with hybrid section-aware and token-based strategies."""

import logging
import re
from dataclasses import dataclass
from typing import Optional

import tiktoken

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class ChunkData:
    """Represents a text chunk ready for embedding."""

    content: str
    section_title: Optional[str]
    chunk_index: int
    token_count: int


class ChunkingService:
    """Service for splitting text into chunks for embedding."""

    def __init__(self):
        self.settings = get_settings()
        # Use cl100k_base encoding (GPT-4/text-embedding-ada-002 compatible)
        self._encoder = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string."""
        return len(self._encoder.encode(text))

    def chunk_text(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> list[ChunkData]:
        """
        Split text into chunks using hybrid strategy.

        First attempts to detect sections, then splits large sections
        by token count while keeping small sections together.

        Args:
            text: The full text to chunk.
            chunk_size: Target tokens per chunk (default from settings).
            chunk_overlap: Overlap tokens between chunks (default from settings).

        Returns:
            List of ChunkData objects.
        """
        chunk_size = chunk_size or self.settings.chunk_size
        chunk_overlap = chunk_overlap or self.settings.chunk_overlap

        # Try to detect sections first
        sections = self._detect_sections(text)

        chunks: list[ChunkData] = []
        chunk_index = 0

        for section_title, section_content in sections:
            section_tokens = self.count_tokens(section_content)

            if section_tokens <= chunk_size:
                # Section fits in one chunk
                chunks.append(
                    ChunkData(
                        content=section_content.strip(),
                        section_title=section_title,
                        chunk_index=chunk_index,
                        token_count=section_tokens,
                    )
                )
                chunk_index += 1
            else:
                # Split large section by token count with overlap
                section_chunks = self._split_by_tokens(
                    section_content,
                    section_title,
                    chunk_size,
                    chunk_overlap,
                    chunk_index,
                )
                chunks.extend(section_chunks)
                chunk_index += len(section_chunks)

        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks

    def _detect_sections(self, text: str) -> list[tuple[Optional[str], str]]:
        """
        Detect sections in text based on common academic paper patterns.

        Returns list of (section_title, section_content) tuples.
        """
        # Common section headers in academic papers
        section_patterns = [
            r"^(Abstract|ABSTRACT)\s*$",
            r"^(\d+\.?\s+)?Introduction\s*$",
            r"^(\d+\.?\s+)?Background\s*$",
            r"^(\d+\.?\s+)?Related Work\s*$",
            r"^(\d+\.?\s+)?Methodology|Methods?\s*$",
            r"^(\d+\.?\s+)?Experiments?\s*$",
            r"^(\d+\.?\s+)?Results?\s*$",
            r"^(\d+\.?\s+)?Discussion\s*$",
            r"^(\d+\.?\s+)?Conclusion\s*$",
            r"^(\d+\.?\s+)?References?\s*$",
            r"^(\d+\.?\s+)?Appendix\s*$",
            r"^[A-Z][A-Z\s]{2,}$",  # ALL CAPS headers
            r"^\d+\.\s+[A-Z]",  # Numbered sections like "1. Introduction"
        ]

        combined_pattern = "|".join(f"({p})" for p in section_patterns)
        header_regex = re.compile(combined_pattern, re.MULTILINE | re.IGNORECASE)

        # Find all section headers
        matches = list(header_regex.finditer(text))

        if not matches:
            # No sections detected, return text as single section
            return [(None, text)]

        sections: list[tuple[Optional[str], str]] = []

        # Add content before first header if any
        if matches[0].start() > 0:
            pre_content = text[: matches[0].start()].strip()
            if pre_content:
                sections.append((None, pre_content))

        # Extract each section
        for i, match in enumerate(matches):
            title = match.group().strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

            content = text[start:end].strip()
            if content:
                sections.append((title, content))

        return sections

    def _split_by_tokens(
        self,
        text: str,
        section_title: Optional[str],
        chunk_size: int,
        chunk_overlap: int,
        start_index: int,
    ) -> list[ChunkData]:
        """Split text by token count with sentence boundary awareness."""
        # Split into sentences first
        sentences = self._split_sentences(text)

        chunks: list[ChunkData] = []
        current_chunk: list[str] = []
        current_tokens = 0
        chunk_index = start_index

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)

            # If single sentence exceeds chunk size, split it
            if sentence_tokens > chunk_size:
                # Flush current chunk first
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunks.append(
                        ChunkData(
                            content=chunk_text.strip(),
                            section_title=section_title,
                            chunk_index=chunk_index,
                            token_count=self.count_tokens(chunk_text),
                        )
                    )
                    chunk_index += 1
                    current_chunk = []
                    current_tokens = 0

                # Split long sentence by words
                words = sentence.split()
                word_chunk: list[str] = []
                word_tokens = 0

                for word in words:
                    word_token_count = self.count_tokens(word + " ")
                    if word_tokens + word_token_count > chunk_size and word_chunk:
                        chunk_text = " ".join(word_chunk)
                        chunks.append(
                            ChunkData(
                                content=chunk_text.strip(),
                                section_title=section_title,
                                chunk_index=chunk_index,
                                token_count=self.count_tokens(chunk_text),
                            )
                        )
                        chunk_index += 1
                        word_chunk = []
                        word_tokens = 0

                    word_chunk.append(word)
                    word_tokens += word_token_count

                if word_chunk:
                    current_chunk = word_chunk
                    current_tokens = word_tokens
                continue

            # Check if adding sentence exceeds chunk size
            if current_tokens + sentence_tokens > chunk_size and current_chunk:
                # Create chunk and start new one with overlap
                chunk_text = " ".join(current_chunk)
                chunks.append(
                    ChunkData(
                        content=chunk_text.strip(),
                        section_title=section_title,
                        chunk_index=chunk_index,
                        token_count=self.count_tokens(chunk_text),
                    )
                )
                chunk_index += 1

                # Keep last sentences for overlap
                overlap_chunk: list[str] = []
                overlap_tokens = 0

                for s in reversed(current_chunk):
                    s_tokens = self.count_tokens(s)
                    if overlap_tokens + s_tokens <= chunk_overlap:
                        overlap_chunk.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break

                current_chunk = overlap_chunk
                current_tokens = overlap_tokens

            current_chunk.append(sentence)
            current_tokens += sentence_tokens

        # Don't forget the last chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(
                ChunkData(
                    content=chunk_text.strip(),
                    section_title=section_title,
                    chunk_index=chunk_index,
                    token_count=self.count_tokens(chunk_text),
                )
            )

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting on common punctuation
        sentence_endings = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
        sentences = sentence_endings.split(text)
        return [s.strip() for s in sentences if s.strip()]
