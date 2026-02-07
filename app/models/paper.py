"""Paper model for storing uploaded academic papers."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.chunk import Chunk
    from app.models.query_cache import QueryCache, Summary


class Paper(Base, UUIDMixin, TimestampMixin):
    """Model representing an uploaded academic paper."""

    __tablename__ = "papers"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[Optional[dict]] = mapped_column(
        "metadata", JSONB, nullable=True, default=dict
    )

    # Relationships
    chunks: Mapped[list["Chunk"]] = relationship(
        "Chunk", back_populates="paper", cascade="all, delete-orphan"
    )
    summaries: Mapped[list["Summary"]] = relationship(
        "Summary", back_populates="paper", cascade="all, delete-orphan"
    )
    query_cache: Mapped[list["QueryCache"]] = relationship(
        "QueryCache", back_populates="paper", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Paper(id={self.id}, title='{self.title[:50]}...')>"
