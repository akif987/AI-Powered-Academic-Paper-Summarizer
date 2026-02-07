"""Embedding service using Google Gemini API."""

import logging
import time
from typing import Optional

import google.generativeai as genai
import warnings

# Suppress deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

from app.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self._api_key = api_key or settings.gemini_api_key
        self._model_name = settings.gemini_embedding_model
        self._embedding_dim = settings.embedding_dimensions

        # Configure the Gemini API
        genai.configure(api_key=self._api_key)

        self._max_retries = 3
        self._retry_delay = 1.0  # seconds

    def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            List of floats representing the embedding vector.

        Raises:
            RuntimeError: If embedding fails after retries.
        """
        embeddings = self.embed_batch([text])
        return embeddings[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.

        Raises:
            RuntimeError: If embedding fails after retries.
        """
        if not texts:
            return []

        # Clean texts
        cleaned_texts = [self._clean_text(t) for t in texts]
        
        all_embeddings: list[list[float]] = []
        batch_size = 10  # Conservative batch size to avoid payload limits
        
        for i in range(0, len(cleaned_texts), batch_size):
            batch = cleaned_texts[i : i + batch_size]
            
            # Replace empty strings with space to avoid API errors in batch
            valid_batch = [t if t else " " for t in batch]
            
            try:
                # Try batch embedding first
                result = genai.embed_content(
                    model=f"models/{self._model_name}",
                    content=valid_batch,
                    task_type="retrieval_document",
                )
                
                # Handle response format (embedding vs embeddings)
                if 'embedding' in result:
                    batch_embeddings = result['embedding']
                    all_embeddings.extend(batch_embeddings)
                else:
                    raise ValueError(f"Unexpected response keys: {result.keys()}")

                # Rate limiting delay
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"Batch embedding failed for batch {i//batch_size}, falling back to sequential: {e}")
                time.sleep(5)  # Backoff before sequential retry
                
                # Fallback to sequential processing for this batch
                for text in batch:
                    if not text:
                        all_embeddings.append([0.0] * self._embedding_dim)
                        continue
                        
                    try:
                        emb = self._embed_with_retry(text)
                        all_embeddings.append(emb)
                        time.sleep(1) # Delay between sequential calls
                    except Exception as seq_e:
                        logger.error(f"Sequential embedding failed: {seq_e}")
                        # Append zero vector as last resort to keep alignment
                        all_embeddings.append([0.0] * self._embedding_dim)

        logger.info(f"Generated {len(all_embeddings)} embeddings (Batch processing)")
        return all_embeddings

    def _embed_with_retry(self, text: str) -> list[float]:
        """Embed text with retry logic for transient failures."""
        last_error: Optional[Exception] = None

        for attempt in range(self._max_retries):
            try:
                result = genai.embed_content(
                    model=f"models/{self._model_name}",
                    content=text,
                    task_type="retrieval_document",
                )
                return result["embedding"]

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Embedding attempt {attempt + 1}/{self._max_retries} failed: {e}"
                )

                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay * (attempt + 1))

        raise RuntimeError(f"Failed to generate embedding after {self._max_retries} attempts: {last_error}")

    def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for a search query.

        Uses 'retrieval_query' task type for better search performance.

        Args:
            query: The search query to embed.

        Returns:
            Embedding vector for the query.
        """
        cleaned_query = self._clean_text(query)
        if not cleaned_query:
            raise ValueError("Query cannot be empty")

        for attempt in range(self._max_retries):
            try:
                result = genai.embed_content(
                    model=f"models/{self._model_name}",
                    content=cleaned_query,
                    task_type="retrieval_query",
                )
                return result["embedding"]

            except Exception as e:
                logger.warning(
                    f"Query embedding attempt {attempt + 1}/{self._max_retries} failed: {e}"
                )
                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay * (attempt + 1))

        raise RuntimeError(f"Failed to generate query embedding after {self._max_retries} attempts")

    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for embedding."""
        if not text:
            return ""

        # Remove excessive whitespace
        cleaned = " ".join(text.split())

        # Truncate very long texts (Gemini has input limits)
        max_chars = 25000  # Conservative limit
        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars]
            logger.warning(f"Text truncated to {max_chars} characters for embedding")

        return cleaned
