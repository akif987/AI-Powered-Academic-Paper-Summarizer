"""PDF extraction service using PyMuPDF."""

import logging
from dataclasses import dataclass
from typing import Optional

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


@dataclass
class Section:
    """Represents a section extracted from a PDF."""

    title: Optional[str]
    content: str
    page_start: int
    page_end: int


class PDFService:
    """Service for extracting text and structure from PDF files."""

    def extract_text(self, pdf_bytes: bytes) -> str:
        """
        Extract all text from a PDF document.

        Args:
            pdf_bytes: Raw bytes of the PDF file.

        Returns:
            Full text content of the PDF.

        Raises:
            ValueError: If the PDF is encrypted or corrupted.
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            raise ValueError(f"Could not open PDF file: {e}") from e

        if doc.is_encrypted:
            doc.close()
            raise ValueError("PDF is encrypted and cannot be processed")

        text_parts: list[str] = []
        for page_num, page in enumerate(doc):
            try:
                text = page.get_text("text")
                text_parts.append(text)
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num}: {e}")
                continue

        doc.close()

        full_text = "\n\n".join(text_parts)
        logger.info(f"Extracted {len(full_text)} characters from PDF")
        return full_text

    def extract_sections(self, pdf_bytes: bytes) -> list[Section]:
        """
        Extract sections from a PDF based on outline/bookmarks or heading detection.

        Args:
            pdf_bytes: Raw bytes of the PDF file.

        Returns:
            List of Section objects with titles and content.
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            raise ValueError(f"Could not open PDF file: {e}") from e

        sections: list[Section] = []

        # Try to use the PDF outline (table of contents)
        toc = doc.get_toc()
        if toc:
            sections = self._extract_from_toc(doc, toc)
        else:
            # Fallback: treat each page as a section
            sections = self._extract_by_pages(doc)

        doc.close()
        logger.info(f"Extracted {len(sections)} sections from PDF")
        return sections

    def _extract_from_toc(self, doc: fitz.Document, toc: list) -> list[Section]:
        """Extract sections based on PDF table of contents."""
        sections: list[Section] = []

        for i, (level, title, page_num) in enumerate(toc):
            # Only use top-level sections (level 1)
            if level > 2:
                continue

            # Determine end page
            end_page = len(doc) - 1
            for j in range(i + 1, len(toc)):
                next_level, _, next_page = toc[j]
                if next_level <= level:
                    end_page = next_page - 1
                    break

            # Extract text from page range
            text_parts = []
            for page_idx in range(page_num - 1, min(end_page + 1, len(doc))):
                if 0 <= page_idx < len(doc):
                    text_parts.append(doc[page_idx].get_text("text"))

            content = "\n".join(text_parts).strip()
            if content:
                sections.append(
                    Section(
                        title=title.strip(),
                        content=content,
                        page_start=page_num,
                        page_end=end_page + 1,
                    )
                )

        return sections

    def _extract_by_pages(self, doc: fitz.Document) -> list[Section]:
        """Fallback: extract text treating each page as content."""
        # Combine all pages into a single section if no structure detected
        full_text = "\n\n".join(page.get_text("text") for page in doc)

        return [
            Section(
                title=None,
                content=full_text.strip(),
                page_start=1,
                page_end=len(doc),
            )
        ]

    def extract_metadata(self, pdf_bytes: bytes) -> dict:
        """
        Extract metadata from a PDF document.

        Args:
            pdf_bytes: Raw bytes of the PDF file.

        Returns:
            Dictionary containing PDF metadata.
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            metadata = doc.metadata or {}
            metadata["page_count"] = len(doc)
            doc.close()
            return metadata
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
            return {}
