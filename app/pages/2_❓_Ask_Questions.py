"""Ask Questions Page - Query papers using RAG."""

import logging

import streamlit as st
from sqlalchemy import select, func

from app.database import get_db_session
from app.models import Paper, QueryCache
from app.services import (
    EmbeddingService,
    RetrievalService,
    CompressionService,
    GenerationService,
)
from app.styles import inject_css, page_header, confidence_badge, source_chunk, empty_state

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Ask Questions - Academic Summarizer",
    page_icon="🤖",
    layout="wide",
)

# Inject professional CSS
inject_css()


def get_paper_count():
    """Get count of uploaded papers."""
    with get_db_session() as db:
        count = db.execute(select(func.count()).select_from(Paper)).scalar()
        return count or 0


def get_cached_answer(question: str) -> dict | None:
    """Check if we have a cached answer for this question."""
    with get_db_session() as db:
        stmt = select(QueryCache).where(
            QueryCache.question == question,
        )
        result = db.execute(stmt)
        cached = result.scalar_one_or_none()
        if cached:
            return {
                "answer": cached.answer,
                "paper_id": cached.paper_id,
            }
    return None


def cache_answer(question: str, answer: str, chunk_ids: list[str], paper_ids: list[str]):
    """Cache the answer for future queries."""
    from uuid import uuid4

    with get_db_session() as db:
        # Ensure chunk_ids are strings (in case they're UUID objects)
        chunk_ids_str = [str(cid) for cid in chunk_ids]
        paper_ids_str = [str(pid) for pid in paper_ids]
        
        cache_entry = QueryCache(
            id=str(uuid4()),
            paper_id=paper_ids_str[0] if paper_ids_str else None,  # Primary paper
            question=question,
            answer=answer,
            chunk_refs={"chunk_ids": chunk_ids_str, "paper_ids": paper_ids_str},
        )
        db.add(cache_entry)
        db.commit()


def answer_question(question: str) -> dict:
    """Generate answer using RAG pipeline - searches ALL papers automatically."""
    # Check cache first
    cached = get_cached_answer(question)
    if cached:
        return {
            "answer": cached["answer"],
            "cached": True,
            "confidence": "high",
            "chunks": [],
        }

    # Initialize services
    embedding_service = EmbeddingService()
    compression_service = CompressionService()
    generation_service = GenerationService()

    with get_db_session() as db:
        retrieval_service = RetrievalService(db, embedding_service)
        
        # Retrieve relevant chunks from ALL papers
        retrieved_chunks = retrieval_service.retrieve_chunks(question)

        if not retrieved_chunks:
            return {
                "answer": "I couldn't find relevant information in any of your uploaded papers to answer this question. Please make sure you have uploaded relevant documents.",
                "cached": False,
                "confidence": "low",
                "chunks": [],
            }

        # Prepare chunk content and IDs
        chunk_contents = [c.content for c in retrieved_chunks]
        chunk_ids = [c.chunk_id for c in retrieved_chunks]
        paper_ids = list(set(c.paper_id for c in retrieved_chunks if c.paper_id))

        # Compress context
        compressed_context = compression_service.compress_context(
            chunk_contents, question
        )

        # Generate answer
        answer = generation_service.answer_question(
            compressed_context, question, chunk_ids
        )

        # Cache the result
        cache_answer(question, answer.text, chunk_ids, paper_ids)

        return {
            "answer": answer.text,
            "cached": False,
            "confidence": answer.confidence,
            "chunks": [
                {
                    "section": c.section_title,
                    "content": c.content,
                    "score": c.similarity_score,
                    "paper": c.paper_filename,
                }
                for c in retrieved_chunks
            ],
        }


# Page Header
page_header("😎 Ask Questions", "Query your uploaded papers using natural language")

# Check if there are papers
paper_count = get_paper_count()

if paper_count == 0:
    empty_state(
        "📭",
        "No papers available",
        "Upload papers first to start asking questions"
    )
else:
    # Info card showing paper count
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid #10b981;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <span style="font-size: 2rem;">📚</span>
            <div>
                <div style="font-weight: 600;">Searching across {paper_count} paper{'s' if paper_count > 1 else ''}</div>
                <div style="font-size: 0.85rem; color: #6b7280;">The AI will automatically find the most relevant information from all your uploaded documents.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat interface
    st.markdown("### 🤖💬 Ask a Question")

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message chat-user">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message chat-assistant">
                <strong>🤖 Assistant:</strong><br>{message["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Show confidence badge
            if "confidence" in message:
                confidence_badge(message["confidence"])
            
            # Show source chunks with paper names
            if message.get("chunks"):
                with st.expander("📚 Source Documents", expanded=False):
                    for chunk in message["chunks"]:
                        paper_name = chunk.get("paper", "Unknown")
                        st.markdown(f"""
                        <div class="source-chunk">
                            <div class="source-header">
                                <span class="source-section">📄 {paper_name} | {chunk["section"] or "General"}</span>
                                <span class="source-score">Similarity: {chunk["score"]:.1%}</span>
                            </div>
                            <div class="source-content">{chunk["content"][:300]}...</div>
                        </div>
                        """, unsafe_allow_html=True)

    # Chat input
    question = st.chat_input("Type your question here...")

    if question:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})

        # Generate answer
        with st.spinner("🔍 Searching all papers and analyzing..."):
            try:
                result = answer_question(question)
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "confidence": result["confidence"],
                    "chunks": result["chunks"],
                    "cached": result["cached"],
                })
                
                st.rerun()
                
            except Exception as e:
                error_msg = str(e)
                st.error(f"Error generating answer: {error_msg}")
                
                if "404" in error_msg or "not found" in error_msg.lower() or "503" in error_msg or "api" in error_msg.lower():
                    st.warning("⚠️ **Caution:** The external API (Gemini or ScaleDown) is not responding. Please check your API keys and service status.")
                
                logger.exception("Answer generation failed")

    # Clear history button
    if st.session_state.messages:
        st.markdown("---")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
