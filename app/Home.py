"""Academic Paper Summarizer - Streamlit Application Entry Point."""

import logging
import streamlit as st
from sqlalchemy import select, func

from app.config import get_settings
from app.database import get_db_session, init_db
from app.models import Paper, QueryCache, Summary
from app.styles import inject_css, hero_header, stat_card, feature_card

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_stats():
    """Get application statistics from database."""
    try:
        with get_db_session() as db:
            papers = db.execute(select(func.count()).select_from(Paper)).scalar() or 0
            questions = db.execute(select(func.count()).select_from(QueryCache)).scalar() or 0
            summaries = db.execute(select(func.count()).select_from(Summary)).scalar() or 0
            return papers, questions, summaries
    except Exception:
        return 0, 0, 0


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="Academic Summarizer | Homepage",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject professional CSS
    inject_css()

    # Sidebar
    with st.sidebar:
        st.markdown("## 🏠 Homepage")
        st.markdown("---")
        st.markdown("""
        **Features:**
        - 📄 Upload academic PDFs
        - ❓ Ask questions about papers
        - 📝 Generate structured summaries
        
        **Powered by:**
        - Google Gemini AI
        - ScaleDown Compression
        - PostgreSQL
        """)
        st.markdown("---")
        
        # Database status
        try:
            settings = get_settings()
            st.success("✅ System Ready")
        except Exception as e:
            st.error(f"❌ Config error: {e}")

    # Hero Header
    hero_header(
        "🚀 Academic Paper Summarizer",
        "Your intelligent portal for academic research and paper analysis"
    )

    # Statistics
    papers_count, questions_count, summaries_count = get_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        stat_card(str(papers_count), "Papers Uploaded")
    with col2:
        stat_card(str(questions_count), "Questions Answered")
    with col3:
        stat_card(str(summaries_count), "Summaries Generated")

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature Cards
    st.markdown("### 🛠️ Quick Access")
    
    col1, col2 = st.columns(2)
    
    with col1:
        feature_card(
            "📤",
            "Upload Papers",
            "Index new academic PDFs for semantic search and analysis."
        )
        if st.button("View Uploads", key="nav_upload", use_container_width=True):
            st.switch_page("pages/1_📄_Upload_Papers.py")
    
    with col2:
        feature_card(
            "📚",
            "Manage Library",
            "View and manage your current list of indexed academic papers."
        )
        if st.button("View Library", key="nav_library", use_container_width=True):
            st.switch_page("pages/1_📄_Upload_Papers.py")

    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        feature_card(
            "❓",
            "Ask Questions",
            "Get instant, AI-powered answers from your entire document collection."
        )
        if st.button("View Questions", key="nav_questions", use_container_width=True):
            st.switch_page("pages/2_❓_Ask_Questions.py")
    
    with col4:
        feature_card(
            "📝",
            "View Summaries",
            "Generate structured overviews and abstracts for your papers."
        )
        if st.button("View Summaries", key="nav_summaries", use_container_width=True):
            st.switch_page("pages/3_📝_View_Summaries.py")

    # How it works
    st.markdown("---")
    st.markdown("### 🔬 Pipeline Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;">
            <div style="font-size: 2.2rem;">1️⃣</div>
            <div style="font-weight: 700; color: #1e293b; margin: 0.75rem 0;">INGESTION</div>
            <div style="font-size: 0.85rem; color: #64748b;">Multi-PDF Extraction</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;">
            <div style="font-size: 2.2rem;">2️⃣</div>
            <div style="font-weight: 700; color: #1e293b; margin: 0.75rem 0;">INDEXING</div>
            <div style="font-size: 0.85rem; color: #64748b;">Vector Embedding</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;">
            <div style="font-size: 2.2rem;">3️⃣</div>
            <div style="font-weight: 700; color: #1e293b; margin: 0.75rem 0;">RETRIEVAL</div>
            <div style="font-size: 0.85rem; color: #64748b;">Semantic Search</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;">
            <div style="font-size: 2.2rem;">4️⃣</div>
            <div style="font-weight: 700; color: #1e293b; margin: 0.75rem 0;">SYNTHESIS</div>
            <div style="font-size: 0.85rem; color: #64748b;">Gemini Generation</div>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #9ca3af; font-size: 0.85rem;">'
        'Academic Paper Summarizer • Professional AI Research Assistant'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
