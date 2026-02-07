"""Summary and QueryCache models for caching generated content."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.paper import Paper


class Summary(Base, UUIDMixin, TimestampMixin):
    """Model for caching generated paper summaries."""

    __tablename__ = "summaries"

    paper_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False
    )
    summary_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'abstract', 'section', 'keypoints'
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    paper: Mapped["Paper"] = relationship("Paper", back_populates="summaries")

    def __repr__(self) -> str:
        return f"<Summary(id={self.id}, paper_id={self.paper_id}, type={self.summary_type})>"


class QueryCache(Base, UUIDMixin, TimestampMixin):
    """Model for caching Q&A responses to avoid redundant API calls."""

    __tablename__ = "query_cache"

    paper_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_refs: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, default=list
    )  # List of chunk IDs used

    # Relationships
    paper: Mapped["Paper"] = relationship("Paper", back_populates="query_cache")

    def __repr__(self) -> str:
        return f"<QueryCache(id={self.id}, paper_id={self.paper_id})>"
