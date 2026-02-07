"""View Summaries Page - Generate and view paper summaries."""

import logging
from uuid import uuid4

import streamlit as st
from sqlalchemy import select

from app.database import get_db_session
from app.models import Paper, Summary
from app.services import GenerationService
from app.styles import inject_css, page_header, empty_state

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="View Summaries - Academic Summarizer",
    page_icon="📝",
    layout="wide",
)

# Inject professional CSS
inject_css()


def get_papers():
    """Get all papers for selection."""
    with get_db_session() as db:
        stmt = select(Paper).order_by(Paper.created_at.desc())
        result = db.execute(stmt)
        papers = result.scalars().all()
        return [
            {"id": p.id, "title": p.filename, "raw_text": p.raw_text[:50000]}
            for p in papers
        ]


def get_cached_summary(paper_id: str, summary_type: str) -> str | None:
    """Check for cached summary."""
    with get_db_session() as db:
        stmt = select(Summary).where(
            Summary.paper_id == paper_id,
            Summary.summary_type == summary_type,
        )
        result = db.execute(stmt)
        cached = result.scalar_one_or_none()
        if cached:
            return cached.content
    return None


def save_summary(paper_id: str, summary_type: str, content: str):
    """Save generated summary to cache."""
    with get_db_session() as db:
        # Check if exists and update
        stmt = select(Summary).where(
            Summary.paper_id == paper_id,
            Summary.summary_type == summary_type,
        )
        existing = db.execute(stmt).scalar_one_or_none()

        if existing:
            existing.content = content
        else:
            summary = Summary(
                id=str(uuid4()),
                paper_id=paper_id,
                summary_type=summary_type,
                content=content,
            )
            db.add(summary)
        db.commit()


def generate_summary(paper_text: str, summary_type: str) -> str:
    """Generate a summary using the generation service."""
    service = GenerationService()
    
    # Map UI summary types to GenerationService summary types
    type_mapping = {
        "abstract": "abstract",
        "sections": "section",
        "key_points": "keypoints",
    }
    
    mapped_type = type_mapping.get(summary_type, "abstract")
    return service.generate_summary(paper_text, mapped_type)


# Page Header
page_header("📝 View Summaries", "Generate and view structured summaries of your papers")

# Paper selection
papers = get_papers()

if not papers:
    empty_state(
        "📭",
        "No papers available",
        "Upload a paper first to generate summaries"
    )
else:
    # Paper selector card
    st.markdown("""
    <p><strong style="font-size: 20px;">📄 Select a Paper 👇</strong></p>


    """, unsafe_allow_html=True)
    
    paper_options = {p["title"]: p for p in papers}
    selected_title = st.selectbox(
        "Choose a paper",
        list(paper_options.keys()),
        label_visibility="collapsed",
    )
    selected_paper = paper_options[selected_title]

    st.markdown("---")

    # Summary type cards
    st.markdown("### 📋 Summary Types")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">Abstract Summary</div>
            <div class="feature-desc">A concise overview capturing the main contribution and findings of the paper.</div>
        </div>
        """, unsafe_allow_html=True)
        abstract_btn = st.button("Generate Abstract", key="gen_abstract", use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📑</div>
            <div class="feature-title">Section Summary</div>
            <div class="feature-desc">Breakdown of each section with key points and methodology details.</div>
        </div>
        """, unsafe_allow_html=True)
        sections_btn = st.button("Generate Sections", key="gen_sections", use_container_width=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⭐</div>
            <div class="feature-title">Key Points</div>
            <div class="feature-desc">Bullet-point list of the most important takeaways and findings.</div>
        </div>
        """, unsafe_allow_html=True)
        keypoints_btn = st.button("Generate Key Points", key="gen_keypoints", use_container_width=True)

    st.markdown("---")

    # Generated summaries display
    st.markdown("### 📖 Generated Summaries")

    # Abstract
    if abstract_btn:
        with st.spinner("🔄 Generating abstract summary..."):
            try:
                cached = get_cached_summary(selected_paper["id"], "abstract")
                if cached:
                    summary = cached
                    st.info("📋 Using cached summary")
                else:
                    summary = generate_summary(selected_paper["raw_text"], "abstract")
                    save_summary(selected_paper["id"], "abstract", summary)
                    st.success("✅ Summary generated!")
                
                st.session_state["abstract_summary"] = summary
            except Exception as e:
                error_msg = str(e)
                st.error(f"Error generating summary: {error_msg}")
                if "404" in error_msg or "not found" in error_msg.lower() or "503" in error_msg or "api" in error_msg.lower():
                    st.warning("⚠️ **Caution:** The external API (Gemini) is not responding. Please check your API keys and service status.")

    if "abstract_summary" in st.session_state:
        st.markdown("""
        <div class="card" style="border-left: 4px solid #6366f1;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <span style="font-weight: 600;">📄 Abstract Summary</span>
                <span class="badge badge-info">Abstract</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="summary-content">
            {st.session_state["abstract_summary"]}
        </div>
        """, unsafe_allow_html=True)

    # Sections
    if sections_btn:
        with st.spinner("🔄 Generating section summary..."):
            try:
                cached = get_cached_summary(selected_paper["id"], "sections")
                if cached:
                    summary = cached
                    st.info("📋 Using cached summary")
                else:
                    summary = generate_summary(selected_paper["raw_text"], "sections")
                    save_summary(selected_paper["id"], "sections", summary)
                    st.success("✅ Summary generated!")
                
                st.session_state["sections_summary"] = summary
            except Exception as e:
                error_msg = str(e)
                st.error(f"Error generating summary: {error_msg}")
                if "404" in error_msg or "not found" in error_msg.lower() or "503" in error_msg or "api" in error_msg.lower():
                    st.warning("⚠️ **Caution:** The external API (Gemini) is not responding. Please check your API keys and service status.")

    if "sections_summary" in st.session_state:
        st.markdown("""
        <div class="card" style="border-left: 4px solid #10b981;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <span style="font-weight: 600;">📑 Section Summary</span>
                <span class="badge badge-success">Sections</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="summary-content">
            {st.session_state["sections_summary"]}
        </div>
        """, unsafe_allow_html=True)

    # Key Points
    if keypoints_btn:
        with st.spinner("🔄 Generating key points..."):
            try:
                cached = get_cached_summary(selected_paper["id"], "key_points")
                if cached:
                    summary = cached
                    st.info("📋 Using cached summary")
                else:
                    summary = generate_summary(selected_paper["raw_text"], "key_points")
                    save_summary(selected_paper["id"], "key_points", summary)
                    st.success("✅ Summary generated!")
                
                st.session_state["keypoints_summary"] = summary
            except Exception as e:
                error_msg = str(e)
                st.error(f"Error generating summary: {error_msg}")
                if "404" in error_msg or "not found" in error_msg.lower() or "503" in error_msg or "api" in error_msg.lower():
                    st.warning("⚠️ **Caution:** The external API (Gemini) is not responding. Please check your API keys and service status.")

    if "keypoints_summary" in st.session_state:
        st.markdown("""
        <div class="card" style="border-left: 4px solid #f59e0b;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <span style="font-weight: 600;">⭐ Key Points</span>
                <span class="badge badge-warning">Key Points</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="summary-content">
            {st.session_state["keypoints_summary"]}
        </div>
        """, unsafe_allow_html=True)

    # Tips
    st.markdown("---")
    st.markdown("""
    <div class="card" style="background: #eff6ff; border-left: 4px solid #3b82f6;">
        <div style="font-weight: 600; margin-bottom: 0.5rem;">💡 Tips</div>
        <ul style="margin: 0; padding-left: 1.25rem; color: #374151;">
            <li>Summaries are cached for faster access next time</li>
            <li>Use <strong>Abstract</strong> for quick overview</li>
            <li>Use <strong>Sections</strong> for detailed breakdown</li>
            <li>Use <strong>Key Points</strong> for bullet-point insights</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
