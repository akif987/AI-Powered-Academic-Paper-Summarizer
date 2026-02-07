"""Context compression service using ScaleDown API."""

import logging
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class CompressionService:
    """Service for compressing context using ScaleDown API.
    
    ScaleDown is a context engineering platform that intelligently compresses
    prompts while preserving semantic integrity, reducing tokens by up to 80%.
    
    API Documentation: https://scaledown.ai/
    Endpoint: https://api.scaledown.xyz/compress/raw/
    """

    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self._api_key = (api_key or settings.scaledown_api_key or "").strip()
        # Correct ScaleDown API endpoint
        self._api_url = "https://api.scaledown.xyz/compress/raw/"
        self._timeout = 30.0  # seconds

    def compress_context(
        self,
        chunks: list[str],
        query: str,
        target_ratio: float = 0.5,
    ) -> str:
        """
        Compress chunks using ScaleDown API.

        Args:
            chunks: List of text chunks to compress.
            query: The query to preserve relevance for.
            target_ratio: Target compression ratio (0.5 = 50% of original).

        Returns:
            Compressed context string.

        Note:
            If the API call fails, returns the uncompressed concatenation
            of chunks as a fallback.
        """
        if not chunks:
            return ""

        # Combine chunks into single context
        context = "\n\n---\n\n".join(chunks)

        try:
            compressed = self._call_scaledown_api(context, query, target_ratio)
            logger.info(
                f"Compressed context from {len(context)} to {len(compressed)} chars "
                f"({len(compressed)/len(context)*100:.1f}%)"
            )
            return compressed

        except httpx.ConnectError as e:
            logger.warning(f"Could not connect to ScaleDown (compression skipped): {e}")
            return context
        except httpx.HTTPStatusError as e:
            error_body = e.response.text
            logger.warning(f"ScaleDown API returned error {e.response.status_code}: {error_body}")
            return context
        except Exception as e:
            logger.error(f"ScaleDown API call failed: {e}")
            logger.warning("Falling back to uncompressed context")
            return context

    def _call_scaledown_api(
        self,
        context: str,
        query: str,
        target_ratio: float,
    ) -> str:
        """Make the actual API call to ScaleDown.
        
        ScaleDown API expects:
        - prompt: The context/prompt to compress
        - instruction: The query/instruction to preserve relevance for
        - rate: Compression rate ("auto" for automatic optimization)
        
        Returns:
        - compressed_prompt: The optimized context
        """
        headers = {
            "x-api-key": self._api_key,
            "Content-Type": "application/json",
        }

        # ScaleDown API payload format (from official documentation)
        payload = {
            "context": context,
            "prompt": query,
            "model": "gemini-2.0-flash",  # Supported model
            "scaledown": {
                "rate": "auto"  # Automatic compression rate optimization
            }
        }
        # Add this debug line to see what is actually being sent
        logger.info(f"Sending payload to ScaleDown with model: {payload['model']}")

        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(
                self._api_url,
                json=payload,
                headers=headers,
            )

            response.raise_for_status()
            result = response.json()

            # Check for API errors
            if "detail" in result:
                raise ValueError(f"ScaleDown API Error: {result['detail']}")

            if result.get("successful") is False and not result.get("partially_successful"):
                raise ValueError(f"ScaleDown API returned unsuccessful: {result}")
            
            # 1. Get the JSON result (already done above)
            # result = response.json()

            # 1. Handle "results" as a dictionary (Current API format)
            if "results" in result and isinstance(result["results"], dict):
                res_dict = result["results"]
                if "compressed_prompt" in res_dict:
                    return res_dict["compressed_prompt"]
                if "content" in res_dict:
                    return res_dict["content"]

            # 2. Handle "results" as a list (Batch format)
            elif "results" in result and isinstance(result["results"], list) and len(result["results"]) > 0:
                first_item = result["results"][0]
                if isinstance(first_item, dict):
                    # Check keys
                    val = first_item.get("compressed_prompt") or first_item.get("content")
                    if val:
                        return val
                elif isinstance(first_item, str):
                    return first_item

            # 3. Fallback to root level
            if result.get("compressed_prompt"):
                return result["compressed_prompt"]
            if result.get("content"):
                return result["content"]

            # 4. Final failure mode
            logger.error(f"DEBUG - Full ScaleDown Response: {result}")
            raise ValueError(f"Could not find text in ScaleDown response. Root keys: {list(result.keys())}")

    def estimate_compression(self, text: str) -> dict:
        """
        Estimate the compression that would be applied.

        Returns dict with original_length, estimated_compressed_length, ratio.
        """
        original_length = len(text)
        # ScaleDown typically achieves 40-80% compression
        estimated_ratio = 0.4
        estimated_length = int(original_length * estimated_ratio)

        return {
            "original_length": original_length,
            "estimated_compressed_length": estimated_length,
            "estimated_ratio": estimated_ratio,
        }
