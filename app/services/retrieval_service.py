"""Retrieval service for vector similarity search."""

import logging
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Chunk, Embedding, Paper
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    """Chunk retrieved from vector search with similarity score."""

    chunk_id: str
    content: str
    section_title: Optional[str]
    chunk_index: int
    similarity_score: float
    paper_id: Optional[str] = None
    paper_filename: Optional[str] = None


class RetrievalService:
    """Service for retrieving relevant chunks using vector similarity search."""

    def __init__(self, db_session: Session, embedding_service: Optional[EmbeddingService] = None):
        self.db = db_session
        self.embedding_service = embedding_service or EmbeddingService()
        self.settings = get_settings()

    def retrieve_chunks(
        self,
        query: str,
        paper_id: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> list[RetrievedChunk]:
        """
        Retrieve the most relevant chunks for a query using vector similarity.
        
        Searches across ALL papers unless a specific paper_id is provided.

        Args:
            query: The search query.
            paper_id: Optional ID of specific paper to search within. If None, searches all papers.
            top_k: Number of chunks to retrieve (default from settings).

        Returns:
            List of RetrievedChunk objects sorted by relevance.
        """
        top_k = top_k or self.settings.top_k_chunks

        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)

        # Perform vector similarity search
        results = self._vector_search(query_embedding, top_k, paper_id)

        logger.info(f"Retrieved {len(results)} chunks for query: {query[:50]}...")
        return results

    def _vector_search(
        self,
        query_vector: list[float],
        top_k: int,
        paper_id: Optional[str] = None,
    ) -> list[RetrievedChunk]:
        """Execute vector similarity search using array-based cosine similarity.
        
        Searches across all papers unless paper_id is specified.
        """
        # Build SQL query - optionally filter by paper_id
        paper_filter = "WHERE c.paper_id = :paper_id" if paper_id else ""
        
        sql = text(f"""
            WITH query_vec AS (
                SELECT ARRAY[:query_vector]::float[] as vec
            ),
            similarities AS (
                SELECT 
                    c.id,
                    c.content,
                    c.section_title,
                    c.chunk_index,
                    c.paper_id,
                    p.filename as paper_filename,
                    (
                        -- Dot product
                        (SELECT SUM(a * b) 
                         FROM unnest(e.embedding, (SELECT vec FROM query_vec)) AS t(a, b))
                        /
                        -- Magnitude product
                        NULLIF(
                            sqrt((SELECT SUM(a * a) FROM unnest(e.embedding) AS t(a))) *
                            sqrt((SELECT SUM(b * b) FROM unnest((SELECT vec FROM query_vec)) AS t(b))),
                            0
                        )
                    ) as similarity
                FROM chunks c
                JOIN embeddings e ON e.chunk_id = c.id
                JOIN papers p ON p.id = c.paper_id
                {paper_filter}
            )
            SELECT id, content, section_title, chunk_index, paper_id, paper_filename, similarity
            FROM similarities
            WHERE similarity IS NOT NULL
            ORDER BY similarity DESC
            LIMIT :top_k
        """)

        params = {
            "query_vector": query_vector,
            "top_k": top_k,
        }
        if paper_id:
            params["paper_id"] = paper_id

        result = self.db.execute(sql, params)

        chunks = []
        for row in result:
            chunks.append(
                RetrievedChunk(
                    chunk_id=row.id,
                    content=row.content,
                    section_title=row.section_title,
                    chunk_index=row.chunk_index,
                    similarity_score=float(row.similarity),
                    paper_id=row.paper_id,
                    paper_filename=row.paper_filename,
                )
            )

        return chunks

    def retrieve_all_chunks(self, paper_id: str) -> list[Chunk]:
        """
        Retrieve all chunks for a paper in order.

        Args:
            paper_id: ID of the paper.

        Returns:
            List of Chunk objects ordered by chunk_index.
        """
        stmt = (
            select(Chunk)
            .where(Chunk.paper_id == paper_id)
            .order_by(Chunk.chunk_index)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Chunk]:
        """Get a single chunk by its ID."""
        stmt = select(Chunk).where(Chunk.id == chunk_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
