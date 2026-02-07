"""Paper Upload Page - Upload and manage academic PDFs."""

import logging
from uuid import uuid4

import streamlit as st
from sqlalchemy import select, func

from app.config import get_settings
from app.database import get_db_session
from app.models import Paper, Chunk, Embedding
from app.services import PDFService, ChunkingService, EmbeddingService
from app.styles import inject_css, page_header, paper_card, empty_state

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Upload Papers - Academic Summarizer",
    page_icon="📄",
    layout="wide",
)

# Inject professional CSS
inject_css()


def process_pdf(uploaded_file) -> str:
    """Process an uploaded PDF file and store in database."""
    pdf_service = PDFService()
    chunking_service = ChunkingService()
    embedding_service = EmbeddingService()

    # Read PDF bytes
    pdf_bytes = uploaded_file.read()

    with st.status("Processing paper...", expanded=True) as status:
        # Extract text
        st.write("📖 Extracting text from PDF...")
        try:
            raw_text = pdf_service.extract_text(pdf_bytes)
            metadata = pdf_service.extract_metadata(pdf_bytes)
        except Exception as e:
            st.error(f"Failed to extract text: {e}")
            raise

        # Chunk text
        st.write("✂️ Splitting into chunks...")
        chunks = chunking_service.chunk_text(raw_text)
        st.write(f"   Created {len(chunks)} chunks")

        # Generate embeddings
        st.write("🧠 Generating embeddings...")
        chunk_texts = [c.content for c in chunks]
        embeddings = embedding_service.embed_batch(chunk_texts)
        st.write(f"   Generated {len(embeddings)} embeddings")

        # Store in database
        st.write("💾 Saving to database...")
        with get_db_session() as db:
            # Create paper record
            # Use filename as title as requested by user
            title = uploaded_file.name
            paper = Paper(
                id=str(uuid4()),
                title=title,
                filename=uploaded_file.name,
                raw_text=raw_text,
                metadata_=metadata,
            )
            db.add(paper)
            db.flush()

            # Create chunk and embedding records
            for chunk_data, embedding_vector in zip(chunks, embeddings):
                chunk = Chunk(
                    id=str(uuid4()),
                    paper_id=paper.id,
                    chunk_index=chunk_data.chunk_index,
                    content=chunk_data.content,
                    section_title=chunk_data.section_title,
                    token_count=chunk_data.token_count,
                )
                db.add(chunk)
                db.flush()

                embedding = Embedding(
                    id=str(uuid4()),
                    chunk_id=chunk.id,
                    embedding=embedding_vector,
                )
                db.add(embedding)

            db.commit()
            paper_id = paper.id

        status.update(label="✅ Paper processed successfully!", state="complete")

    return paper_id


def get_papers():
    """Get all papers from database."""
    with get_db_session() as db:
        stmt = select(Paper).order_by(Paper.created_at.desc())
        result = db.execute(stmt)
        papers = result.scalars().all()
        # Convert to list of dicts to avoid detached instance issues
        return [
            {
                "id": p.id,
                "title": p.title,
                "filename": p.filename,
                "created_at": p.created_at,
                "metadata": p.metadata_,
            }
            for p in papers
        ]


def get_paper_stats(paper_id: str) -> dict:
    """Get chunk count for a paper."""
    with get_db_session() as db:
        count = db.execute(
            select(func.count()).select_from(Chunk).where(Chunk.paper_id == paper_id)
        ).scalar()
        return {"chunk_count": count}


def delete_paper(paper_id: str):
    """Delete a paper and all related data."""
    with get_db_session() as db:
        paper = db.get(Paper, paper_id)
        if paper:
            db.delete(paper)
            db.commit()


def delete_all_papers():
    """Delete all papers and related data from the system."""
    with get_db_session() as db:
        # Delete all papers (cascades to chunks, embeddings, summaries, query_cache)
        db.execute(select(Paper))  # Just to ensure table exists
        from sqlalchemy import delete
        db.execute(delete(Paper))
        db.commit()


# Page Header
page_header("📄 Upload Papers", "Upload academic PDFs to analyze and query them with AI")

# Upload section
st.markdown("### 📤 Upload New Paper")

# Styled upload zone
st.markdown("""
<div class="upload-zone">
    <div class="upload-icon">📁</div>
    <div class="upload-text">Drag and drop your PDFs here</div>
    <div class="upload-subtext">or click to browse files (multiple files supported)</div>
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    help="Upload academic papers in PDF format (multiple files allowed)",
    label_visibility="collapsed",
    accept_multiple_files=True,
)

if uploaded_files:
    # Show all selected files
    st.markdown(f"**📎 {len(uploaded_files)} file(s) selected:**")
    for uploaded_file in uploaded_files:
        st.markdown(f"""
        <div class="card" style="border-left: 4px solid #10b981; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">📄</span>
                <div>
                    <div style="font-weight: 600;">{uploaded_file.name}</div>
                    <div style="font-size: 0.85rem; color: #6b7280;">{uploaded_file.size / 1024:.1f} KB</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🚀 Process All Papers", type="primary", use_container_width=True):
        success_count = 0
        error_count = 0
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {i+1}/{len(uploaded_files)}: {uploaded_file.name}...")
            progress_bar.progress((i + 1) / len(uploaded_files))
            
            try:
                paper_id = process_pdf(uploaded_file)
                success_count += 1
            except Exception as e:
                error_count += 1
                error_msg = str(e)
                st.error(f"❌ Failed to process {uploaded_file.name}: {error_msg}")
                
                if "404" in error_msg or "not found" in error_msg.lower() or "503" in error_msg or "api" in error_msg.lower():
                    st.warning("⚠️ **Caution:** The external API (Gemini or ScaleDown) is not responding. Please check your API keys and service status.")
                
                logger.exception(f"Paper processing failed: {uploaded_file.name}")
        
        progress_bar.empty()
        status_text.empty()
        
        if success_count > 0:
            st.success(f"✅ Successfully uploaded {success_count} paper(s)!")
            if error_count == 0:
                st.balloons()
        if error_count > 0:
            st.warning(f"⚠️ {error_count} paper(s) failed to process.")
        
        st.rerun()

st.markdown("---")

# Papers list
st.markdown("### 📚 Your Papers")

try:
    papers = get_papers()

    if not papers:
        empty_state(
            "📭",
            "No papers uploaded yet",
            "Upload your first paper above to get started!"
        )
    else:
        for paper in papers:
            stats = get_paper_stats(paper["id"])
            
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                <div class="paper-card">
                    <div class="paper-title">📄 {paper['filename']}</div>
                    <div class="paper-meta">
                        <span>📅 {paper['created_at'].strftime('%Y-%m-%d %H:%M')}</span> • 
                        <span>📝 {stats['chunk_count']} chunks</span> • 
                        <span>🔑 {paper['id'][:8]}...</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🗑️", key=f"del_{paper['id']}", help="Delete this paper"):
                    delete_paper(paper["id"])
                    st.success("Paper deleted!")
                    st.rerun()

except Exception as e:
    st.error(f"Error loading papers: {e}")
    logger.exception("Failed to load papers")

# Reset All Button
if papers:
    st.markdown("---")
    st.markdown("### ⚠️ Danger Zone")
    
    st.markdown("""
    <div class="card" style="background: #fef2f2; border-left: 4px solid #ef4444;">
        <div style="font-weight: 600; color: #991b1b; margin-bottom: 0.5rem;">🗑️ Reset All Data</div>
        <div style="font-size: 0.9rem; color: #7f1d1d;">This will permanently delete all uploaded papers, embeddings, summaries, and cached answers.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Confirmation checkbox and button
    confirm_reset = st.checkbox("I understand this action cannot be undone", key="confirm_reset")
    
    if st.button("🗑️ Delete All Papers", type="secondary", disabled=not confirm_reset, use_container_width=True):
        try:
            delete_all_papers()
            st.success("✅ All papers have been deleted!")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting papers: {e}")
            logger.exception("Failed to delete all papers")

# Tips
st.markdown("---")
st.markdown("""
<div class="card" style="background: #f0fdf4; border-left: 4px solid #10b981;">
    <div style="font-weight: 600; margin-bottom: 0.5rem;">💡 Tips</div>
    <ul style="margin: 0; padding-left: 1.25rem; color: #374151;">
        <li>Upload PDF files of academic papers for best results</li>
        <li>Papers are automatically chunked and indexed for semantic search</li>
        <li>After uploading, go to <strong>Ask Questions</strong> to query your papers</li>
    </ul>
</div>
""", unsafe_allow_html=True)
