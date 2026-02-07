"""Chunk and Embedding models for storing paper sections and their vectors."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.paper import Paper


class Chunk(Base, UUIDMixin, TimestampMixin):
    """Model representing a chunk/section of a paper."""

    __tablename__ = "chunks"

    paper_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    section_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    paper: Mapped["Paper"] = relationship("Paper", back_populates="chunks")
    embedding: Mapped[Optional["Embedding"]] = relationship(
        "Embedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Chunk(id={self.id}, paper_id={self.paper_id}, index={self.chunk_index})>"


class Embedding(Base, UUIDMixin):
    """Model storing vector embeddings for chunks."""

    __tablename__ = "embeddings"

    chunk_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("chunks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    embedding: Mapped[list] = mapped_column(ARRAY(Float), nullable=False)

    # Relationships
    chunk: Mapped["Chunk"] = relationship("Chunk", back_populates="embedding")

    def __repr__(self) -> str:
        return f"<Embedding(id={self.id}, chunk_id={self.chunk_id})>"
