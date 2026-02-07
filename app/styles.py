"""Shared CSS styles for consistent professional UI across all pages."""

PROFESSIONAL_CSS = """
<style>
/* ===== BASE STYLES ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --primary-light: #818cf8;
    --secondary: #0ea5e9;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;
    --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gradient-2: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}

.stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ===== HEADER STYLES ===== */
.hero-header {
    background: var(--gradient-2);
    padding: 2.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
}

.hero-header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: white !important;
}

.hero-header p {
    font-size: 1.1rem;
    opacity: 0.9;
    margin: 0;
}

.page-header {
    background: var(--gradient-2);
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    color: white;
}

.page-header h1 {
    font-size: 1.75rem;
    font-weight: 600;
    margin: 0;
    color: white !important;
}

.page-header p {
    font-size: 0.95rem;
    opacity: 0.9;
    margin: 0.5rem 0 0 0;
}

/* ===== CARD STYLES ===== */
.card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--gray-900);
    margin-bottom: 1rem;
    transition: all 0.2s ease;
}

.card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.card-icon {
    width: 48px;
    height: 48px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    background: var(--gray-100);
}

.card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--gray-800);
    margin: 0;
}

.card-subtitle {
    font-size: 0.85rem;
    color: var(--gray-500);
    margin: 0;
}

/* ===== STAT CARDS ===== */
.stat-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--gray-100);
    text-align: center;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary);
    margin: 0;
}

.stat-label {
    font-size: 0.85rem;
    color: var(--gray-500);
    margin: 0.25rem 0 0 0;
    font-weight: 500;
}

/* ===== FEATURE CARDS ===== */
.feature-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--gray-100);
    height: 100%;
    transition: all 0.2s ease;
    cursor: pointer;
}

.feature-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-4px);
    border-color: var(--primary-light);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.feature-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--gray-800);
    margin-bottom: 0.5rem;
}

.feature-desc {
    font-size: 0.9rem;
    color: var(--gray-500);
    line-height: 1.5;
}

/* ===== CHAT STYLES ===== */
.chat-message {
    padding: 1rem 1.25rem;
    border-radius: 12px;
    margin-bottom: 0.75rem;
    max-width: 85%;
}

.chat-user {
    background: var(--primary);
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}

.chat-assistant {
    background: var(--gray-100);
    color: var(--gray-800);
    margin-right: auto;
    border-bottom-left-radius: 4px;
}

/* ===== BADGE STYLES ===== */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-success {
    background: #dcfce7;
    color: #166534;
}

.badge-warning {
    background: #fef3c7;
    color: #92400e;
}

.badge-error {
    background: #fee2e2;
    color: #991b1b;
}

.badge-info {
    background: #e0e7ff;
    color: #3730a3;
}

/* ===== UPLOAD ZONE ===== */
.upload-zone {
    border: 2px dashed var(--gray-300);
    border-radius: 12px;
    padding: 3rem 2rem;
    text-align: center;
    background: var(--gray-50);
    transition: all 0.2s ease;
}

.upload-zone:hover {
    border-color: var(--primary);
    background: #f5f3ff;
}

.upload-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.upload-text {
    font-size: 1rem;
    color: var(--gray-600);
}

.upload-subtext {
    font-size: 0.85rem;
    color: var(--gray-400);
    margin-top: 0.5rem;
}

/* ===== PAPER CARD ===== */
.paper-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--gray-100);
    margin-bottom: 0.75rem;
    transition: all 0.2s ease;
}

.paper-card:hover {
    box-shadow: var(--shadow-md);
}

.paper-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--gray-800);
    margin: 0 0 0.5rem 0;
}

.paper-meta {
    font-size: 0.8rem;
    color: var(--gray-500);
}

/* ===== BUTTON OVERRIDES ===== */
.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    padding: 0.5rem 1.25rem;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background: var(--gradient-2);
    border: none;
}

.stButton > button[kind="primary"]:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background-color: white;
    border-right: 1px solid var(--gray-200);
}

section[data-testid="stSidebar"] .stMarkdown h2 {
    color: var(--primary);
    font-weight: 700;
    font-size: 1.5rem;
}

/* Sidebar Navigation Items */
[data-testid="stSidebarNav"] {
    padding-top: 1rem;
}

[data-testid="stSidebarNav"] ul {
    list-style: none;
    padding: 0 1rem !important;
}

[data-testid="stSidebarNav"] li {
    margin-bottom: 0.75rem !important;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.2s ease;
}

[data-testid="stSidebarNav"] li:hover {
    background-color: var(--gray-100);
    transform: translateX(4px);
}

[data-testid="stSidebarNav"] li a {
    padding: 0.85rem 1.25rem !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.75rem !important;
    text-decoration: none !important;
}

[data-testid="stSidebarNav"] li a span {
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    color: var(--gray-700) !important;
    transition: all 0.2s ease;
}

/* Active State */
[data-testid="stSidebarNav"] li a[aria-current="page"] {
    background: var(--gradient-2) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4) !important;
}

[data-testid="stSidebarNav"] li a[aria-current="page"] span {
    color: white !important;
    font-weight: 700 !important;
    letter-spacing: 0.025em;
}

[data-testid="stSidebarNav"] li a:hover span {
    color: var(--primary) !important;
}

[data-testid="stSidebarNav"] li a[aria-current="page"]:hover span {
    color: white !important;
}

/* ===== EMPTY STATE ===== */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: var(--gray-500);
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

.empty-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--gray-700);
    margin-bottom: 0.5rem;
}

.empty-desc {
    font-size: 0.95rem;
    color: var(--gray-500);
}

/* ===== SOURCE CHUNK ===== */
.source-chunk {
    background: var(--gray-50);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    border-left: 3px solid var(--primary);
}

.source-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.8rem;
}

.source-section {
    font-weight: 600;
    color: var(--gray-700);
}

.source-score {
    color: var(--gray-500);
}

.source-content {
    font-size: 0.85rem;
    color: var(--gray-600);
    line-height: 1.5;
}

/* ===== SUMMARY SECTION ===== */
.summary-content {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--gray-100);
    line-height: 1.7;
}

/* ===== LOADING ===== */
.loading-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: var(--gray-100);
}

::-webkit-scrollbar-thumb {
    background: var(--gray-300);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--gray-400);
}
</style>
"""


def inject_css():
    """Inject professional CSS into the Streamlit page."""
    import streamlit as st
    st.markdown(PROFESSIONAL_CSS, unsafe_allow_html=True)


def hero_header(title: str, subtitle: str = ""):
    """Render a hero header section."""
    import streamlit as st
    html = f'''
    <div class="hero-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Render a page header section."""
    import streamlit as st
    html = f'''
    <div class="page-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def stat_card(value: str, label: str):
    """Render a statistics card."""
    import streamlit as st
    html = f'''
    <div class="stat-card">
        <p class="stat-value">{value}</p>
        <p class="stat-label">{label}</p>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def feature_card(icon: str, title: str, description: str):
    """Render a feature card."""
    import streamlit as st
    html = f'''
    <div class="feature-card">
        <div class="feature-icon">{icon}</div>
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{description}</div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def paper_card(filename: str, date: str, chunks: int, paper_id: str):
    """Render a paper info card."""
    import streamlit as st
    html = f'''
    <div class="paper-card">
        <div class="paper-title">📄 {filename}</div>
        <div class="paper-meta">
            <span>📅 {date}</span> • 
            <span>📝 {chunks} chunks</span> • 
            <span>🔑 {paper_id[:8]}...</span>
        </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def confidence_badge(confidence: str):
    """Render a confidence badge."""
    import streamlit as st
    badges = {
        "high": ("🟢", "badge-success", "High Confidence"),
        "medium": ("🟡", "badge-warning", "Medium Confidence"),
        "low": ("🟠", "badge-error", "Low Confidence"),
        "not_found": ("🔴", "badge-error", "Not Found"),
    }
    icon, cls, text = badges.get(confidence, ("⚪", "badge-info", confidence))
    html = f'<span class="badge {cls}">{icon} {text}</span>'
    st.markdown(html, unsafe_allow_html=True)


def source_chunk(section: str, score: float, content: str):
    """Render a source chunk card."""
    import streamlit as st
    html = f'''
    <div class="source-chunk">
        <div class="source-header">
            <span class="source-section">📑 {section or "General"}</span>
            <span class="source-score">Similarity: {score:.1%}</span>
        </div>
        <div class="source-content">{content[:300]}...</div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def empty_state(icon: str, title: str, description: str):
    """Render an empty state placeholder."""
    import streamlit as st
    html = f'''
    <div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <div class="empty-title">{title}</div>
        <div class="empty-desc">{description}</div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)
