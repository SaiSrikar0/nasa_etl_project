import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client
import os
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse

# Load environment variables
load_dotenv(dotenv_path="../.env")

# Page config
st.set_page_config(
    page_title="NASA APOD Explorer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = os.getenv("supabase_url")
    key = os.getenv("supabase_key")
    if not url or not key:
        st.error("❌ Missing Supabase credentials in .env file")
        st.stop()
    return create_client(url, key)

supabase = init_supabase()

# Airflow configuration
AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://localhost:8080")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "airflow")
DAG_ID = "nasa_etl_pipeline"

# ============== AIRFLOW TRIGGER ==============
def get_record_count():
    """Get current record count from Supabase"""
    try:
        response = supabase.table("nasa_apod").select("*", count="exact").execute()
        return len(response.data) if response.data else 0
    except:
        return 0

def trigger_dag():
    """Trigger Airflow DAG via REST API"""
    try:
        # Capture count before pipeline run
        count_before = get_record_count()
        
        url = f"{AIRFLOW_URL}/api/v1/dags/{DAG_ID}/dagRuns"
        headers = {"Content-Type": "application/json"}
        payload = {"conf": {}}
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            # Give pipeline time to complete (adjust as needed)
            import time
            time.sleep(8)
            
            # Check count after pipeline run
            count_after = get_record_count()
            
            # Determine message based on whether new data was added
            if count_after > count_before:
                message = f"✅ Pipeline completed! Added {count_after - count_before} new record(s)."
            else:
                message = "ℹ️ Pipeline completed. You are up to date – no new information has been extracted."
            
            return True, message
        else:
            return False, f"❌ Failed to trigger pipeline: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"❌ Error triggering pipeline: {str(e)}"

# ============== DARK THEME CSS ==============
dark_css = """
<style>
body, .stMarkdown, .stMetric, .stCaption, p {{
    color: #e6edf3 !important;
}}

.header-title {{
    font-size: 3rem;
    font-weight: 900;
    color: #00d4ff !important;
    margin-bottom: 0.5rem;
}}

.subtitle {{
    font-size: 1.1rem;
    color: #e6edf3 !important;
    margin-bottom: 2rem;
}}

.stat-box {{
    padding: 1.5rem;
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(88, 166, 255, 0.1) 100%);
    border: 1px solid #00d4ff;
    border-radius: 12px;
    color: #e6edf3 !important;
    text-align: center;
    font-weight: bold;
    transition: all 0.3s ease;
}}

.stat-box div {{
    color: #e6edf3 !important;
}}

.stat-box:hover {{
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 212, 255, 0.2);
}}

.apod-card {{
    padding: 1.5rem;
    border: 2px solid #58a6ff;
    border-radius: 12px;
    background: #161b22;
    color: #e6edf3 !important;
    transition: all 0.3s ease;
}}

.apod-card * {{
    color: #e6edf3 !important;
}}

.apod-card:hover {{
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(0, 212, 255, 0.2);
    border-color: #00d4ff;
}}

.featured-section {{
    background: linear-gradient(135deg, #161b22 0%, rgba(0, 212, 255, 0.05) 100%);
    padding: 2rem;
    border-radius: 15px;
    border-left: 5px solid #00d4ff;
    margin-bottom: 2rem;
}}

.featured-section h2, .featured-section h3, .featured-section * {{
    color: #e6edf3 !important;
}}

.badge {{
    display: inline-block;
    padding: 0.5rem 1rem;
    background: #00d4ff;
    color: #0e1117;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: bold;
    margin-right: 0.5rem;
}}
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# ============== SIDEBAR ==============
with st.sidebar:
    st.title("⚙️ Settings & Filters")
    
    st.subheader("🔍 Search & Filter")
    search_term = st.text_input("Search by title or keyword:", placeholder="e.g., galaxy, nebula")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date:", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End date:", datetime.now())
    
    media_type = st.selectbox(
        "Media type:",
        ["All", "image", "video"],
        help="Filter by image or video content"
    )
    
    st.divider()
    st.subheader("ℹ️ About Pipeline")
    st.info("""
    **Data Flow:**
    🌐 NASA API → Extract
    🔄 Transform (JSON → CSV)
    💾 Load (Supabase)
    
    **Schedule:** Daily at 5:30 AM UTC
    **Database:** PostgreSQL (Supabase)
    **Orchestration:** Apache Airflow
    
    [GitHub](https://github.com/SaiSrikar0/nasa_etl_project) | [NASA APOD](https://apod.nasa.gov/)
    """)

# ============== HEADER ==============
col_title, col_button = st.columns([4, 1])

with col_title:
    st.markdown("<div class='header-title'>🚀 NASA APOD Explorer</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Explore the Universe – Daily Astronomy Picture of the Day</div>", unsafe_allow_html=True)

with col_button:
    st.write("")  # Spacer for alignment
    if st.button("▶️ Run Pipeline", type="primary", use_container_width=True, help="Manually trigger Airflow DAG"):
        with st.spinner("⏳ Running pipeline..."):
            success, message = trigger_dag()
            if success:
                st.success(message)
                st.balloons()
                st.cache_data.clear()
            else:
                st.error(message)

st.divider()

# ============== FETCH DATA ==============
@st.cache_data(ttl=3600)
def fetch_apod_data():
    try:
        response = supabase.table("nasa_apod").select("*").order("date", desc=True).execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_stats():
    try:
        response = supabase.table("nasa_apod").select("*", count="exact").execute()
        total_count = len(response.data) if response.data else 0
        if response.data:
            latest_date = max([r["date"] for r in response.data if r.get("date")])
            return total_count, latest_date
        return total_count, None
    except:
        return 0, None

# Fetch all data
df = fetch_apod_data()

if df.empty:
    st.warning("⚠️ No APOD data found. Ensure the pipeline has run at least once.")
    st.stop()

# ============== STATS DASHBOARD ==============
st.subheader("📊 Dashboard")
total_records, latest_update = get_stats()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="stat-box">
        <div style="font-size: 2.5rem;">📷</div>
        <div style="font-size: 1.8rem; margin: 0.5rem 0;">{total_records}</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">Total Records</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-box">
        <div style="font-size: 2.5rem;">📅</div>
        <div style="font-size: 1.2rem; margin: 0.5rem 0;">{latest_update if latest_update else 'N/A'}</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">Latest Update</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    image_count = len(df[df["media_type"] == "image"]) if "media_type" in df.columns else 0
    st.markdown(f"""
    <div class="stat-box">
        <div style="font-size: 2.5rem;">🖼️</div>
        <div style="font-size: 1.8rem; margin: 0.5rem 0;">{image_count}</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">Images</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    video_count = len(df[df["media_type"] == "video"]) if "media_type" in df.columns else 0
    st.markdown(f"""
    <div class="stat-box">
        <div style="font-size: 2.5rem;">🎬</div>
        <div style="font-size: 1.8rem; margin: 0.5rem 0;">{video_count}</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">Videos</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============== FEATURED APOD ==============
if not df.empty:
    featured = df.iloc[0]  # Most recent
    st.markdown("""
    <div class="featured-section">
        <h2 style="margin-top: 0;">⭐ Featured APOD</h2>
    </div>
    """, unsafe_allow_html=True)
    
    feat_col1, feat_col2 = st.columns([1, 1])
    
    with feat_col1:
        # Play video if media_type is video, else show image
        f_url = featured.get("image_url") or featured.get("url")
        f_type = str(featured.get("media_type", "")).lower()
        if f_url:
            if f_type == "video" or any(f_url.lower().endswith(ext) for ext in [".mp4", ".webm", ".ogg"]):
                try:
                    st.video(f_url)
                except:
                    st.write(f"🎥 [Watch Video]({f_url})")
            else:
                try:
                    st.image(f_url, use_column_width=True)
                except:
                    st.warning("📸 Image unavailable")
    
    with feat_col2:
        st.markdown(f"### {featured['title']}")
        st.caption(f"📅 {featured['date']}")
        st.write(featured['explanation'])
        col1, col2 = st.columns(2)
        with col1:
            media_badge = "🖼️ Image" if featured["media_type"] == "image" else "🎬 Video"
            st.markdown(f"<div class='badge'>{media_badge}</div>", unsafe_allow_html=True)

st.divider()

# ============== FILTER & DISPLAY GALLERY ==============
st.subheader("🖼️ Gallery")

# Apply filters
df_filtered = df.copy()

if search_term:
    mask = (
        df_filtered["title"].str.contains(search_term, case=False, na=False) |
        df_filtered["explanation"].str.contains(search_term, case=False, na=False)
    )
    df_filtered = df_filtered[mask]

if media_type != "All":
    df_filtered = df_filtered[df_filtered["media_type"] == media_type]

# Date filter
df_filtered["date"] = pd.to_datetime(df_filtered["date"])
df_filtered = df_filtered[(df_filtered["date"].dt.date >= start_date) & (df_filtered["date"].dt.date <= end_date)]

# Sort by date descending
df_filtered = df_filtered.sort_values("date", ascending=False)

# Results info
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.metric("Results", len(df_filtered))
with col2:
    if not df_filtered.empty:
        st.metric("Date Range", f"{df_filtered['date'].dt.date.min()} to {df_filtered['date'].dt.date.max()}")

if df_filtered.empty:
    st.info("📭 No results match your filters. Try adjusting your search.")
else:
    # Display in grid (4 columns for better layout)
    cols = st.columns(4)
    for idx, (_, row) in enumerate(df_filtered.iterrows()):
        col = cols[idx % 4]
        
        with col:
            st.markdown(f"<div class='apod-card'>", unsafe_allow_html=True)
            
            # Image/Video: play video or show image
            url = row.get("image_url") or row.get("url")
            m_type = str(row.get("media_type", "")).lower()
            if url:
                if m_type == "video" or any(url.lower().endswith(ext) for ext in [".mp4", ".webm", ".ogg"]):
                    try:
                        st.video(url)
                    except:
                        st.write(f"🎥 [Watch]({url})")
                else:
                    try:
                        st.image(url, use_column_width=True)
                    except:
                        st.write("📸 Image unavailable")
            
            # Date
            st.caption(f"📅 {row['date'].date()}")
            
            # Title
            title = row['title'][:40] + "..." if len(row['title']) > 40 else row['title']
            st.markdown(f"**{title}**")
            
            # Explanation (truncated)
            explanation = row.get("explanation", "")
            if len(explanation) > 100:
                explanation = explanation[:100] + "..."
            st.caption(explanation)
            
            # Media type badge
            media_badge = "🖼️ Image" if row["media_type"] == "image" else "🎬 Video"
            st.markdown(f"<div class='badge'>{media_badge}</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

# ============== FOOTER ==============
st.divider()
st.markdown("""
<center style="opacity: 0.6; margin-top: 2rem;">

**NASA APOD Explorer** | Built with Streamlit & Supabase

Data updated daily via Apache Airflow | [GitHub](https://github.com/SaiSrikar0/nasa_etl_project) | [NASA APOD](https://apod.nasa.gov/)

</center>
""", unsafe_allow_html=True)

