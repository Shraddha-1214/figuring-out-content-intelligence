import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent

# 1. Page Configuration
st.set_page_config(
    page_title="Figuring Out | Editorial & Commerce Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Minimalist & Clean Editorial CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #FAFAFA;
        color: #1A1A1A;
    }
    
    .header-container {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 22px 26px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .header-title {
        font-size: 1.7rem;
        font-weight: 800;
        color: #111827;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .header-subtitle {
        color: #6B7280;
        font-size: 0.92rem;
        margin-top: 4px;
        font-weight: 400;
    }

    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .metric-title {
        color: #6B7280;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .metric-value {
        color: #111827;
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 6px;
    }

    .content-box {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .box-heading {
        color: #111827;
        font-size: 1.02rem;
        font-weight: 700;
        margin-bottom: 10px;
        border-bottom: 1px solid #F3F4F6;
        padding-bottom: 6px;
    }
    .box-body {
        color: #374151;
        font-size: 0.9rem;
        line-height: 1.65;
    }

    .callout-box {
        background-color: #F8FAFC;
        border-left: 4px solid #0F172A;
        border-radius: 4px;
        padding: 16px 20px;
        color: #334155;
        font-size: 0.92rem;
        line-height: 1.6;
        margin-top: 16px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Resilient Data Loading
@st.cache_data
def load_data():
    csv_path = ROOT_DIR / "data" / "processed_episodes.csv"
    raw_path = ROOT_DIR / "data" / "raw_episodes.csv"
    
    if not csv_path.exists():
        if raw_path.exists():
            from src.process_features import process_episodes
            process_episodes(str(raw_path), str(csv_path))
        else:
            return None
            
    df = pd.read_csv(csv_path)
    df["published_at"] = pd.to_datetime(df["published_at"])
    
    if "duration_minutes" not in df.columns:
        if "duration_seconds" in df.columns:
            df["duration_minutes"] = (df["duration_seconds"] / 60.0).round(1)
        else:
            df["duration_minutes"] = 60.0
            
    return df

df = load_data()

# 4. Header & Sync Button (Rendered ONLY ONCE with unique key)
col_head, col_sync = st.columns([3, 1])

with col_head:
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🎙️ Figuring Out — Content & Commerce Intelligence</div>
        <div class="header-subtitle">Performance velocity tracking, pre-interview research dossiers, and House of X brand-incubation mapping.</div>
    </div>
    """, unsafe_allow_html=True)

with col_sync:
    st.write("")
    if st.button("🔄 Sync Latest Uploads", key="btn_sync_uploads_primary", use_container_width=True, type="secondary"):
        with st.spinner("Fetching latest YouTube releases via IPv4 socket..."):
            try:
                from src.fetch_data import fetch_latest_episodes
                from src.process_features import process_episodes
                
                raw_path = str(ROOT_DIR / "data" / "raw_episodes.csv")
                proc_path = str(ROOT_DIR / "data" / "processed_episodes.csv")
                
                fetch_latest_episodes(output_csv=raw_path)
                process_episodes(raw_path, proc_path)
                
                st.cache_data.clear()
                st.success("✅ Real-time metrics synchronized!")
                st.rerun()
            except Exception as e:
                st.error(f"Sync connection error: {e}")

st.write("")

# 5. Guard Check
if df is None or df.empty:
    st.warning("⚠️ No episode dataset found. Please run ingestion or verify data/processed_episodes.csv.")
    st.stop()

# 6. Top KPI Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Episodes Analyzed</div>
        <div class="metric-value">{len(df)}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Average Views / Episode</div>
        <div class="metric-value">{int(df['view_count'].mean()):,}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Avg. Engagement Rate</div>
        <div class="metric-value">{df['engagement_rate_pct'].mean():.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Hit Outlier Benchmark</div>
        <div class="metric-value">{int(df['view_count'].median() * 1.5):,}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# 7. Tab Navigation
tab_performance, tab_matrix, tab_briefing, tab_repurpose = st.tabs([
    "📊 Performance & Outliers",
    "🎯 Category Supply vs Demand",
    "📝 Guest Intelligence Dossier",
    "⚡ Clip & Brand Intelligence"
])

# ----------------- TAB 1: PERFORMANCE & VELOCITY -----------------
with tab_performance:
    st.write("")
    col_plot, col_df = st.columns([3, 2])

    with col_plot:
        fig_scatter = px.scatter(
            df,
            x="duration_minutes",
            y="views_per_day",
            size="view_count",
            color="category",
            hover_name="title",
            title="Views Per Day (Velocity) vs. Episode Duration",
            template="plotly_white",
            color_discrete_sequence=["#2563EB", "#7C3AED", "#059669", "#D97706", "#DC2626", "#0284C7", "#9333EA"]
        )
        fig_scatter.update_layout(
            font=dict(family="Plus Jakarta Sans", color="#374151"),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(title=dict(text="Category"), orientation="h", y=-0.25)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_df:
        st.markdown("**Top 5 Velocity Outliers (Views/Day)**")
        top_table = df.sort_values(by="views_per_day", ascending=False)[
            ["title", "category", "views_per_day"]
        ].head(5)
        st.dataframe(top_table, hide_index=True, use_container_width=True)

# ----------------- TAB 2: CATEGORY MATRIX -----------------
with tab_matrix:
    st.write("")
    cat_summary = df.groupby("category").agg(
        episodes=("video_id", "count"),
        avg_views=("view_count", "mean")
    ).reset_index()

    col_s, col_d = st.columns(2)

    with col_s:
        fig_sup = px.bar(
            cat_summary,
            x="category",
            y="episodes",
            title="Content Inventory (Episode Count)",
            color="category",
            template="plotly_white",
            color_discrete_sequence=["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444", "#06B6D4", "#A855F7"]
        )
        fig_sup.update_layout(font=dict(family="Plus Jakarta Sans", color="#374151"), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", showlegend=False)
        st.plotly_chart(fig_sup, use_container_width=True)

    with col_d:
        fig_dem = px.bar(
            cat_summary,
            x="category",
            y="avg_views",
            title="Audience Demand (Average Views)",
            color="category",
            template="plotly_white",
            color_discrete_sequence=["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444", "#06B6D4", "#A855F7"]
        )
        fig_dem.update_layout(font=dict(family="Plus Jakarta Sans", color="#374151"), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", showlegend=False)
        st.plotly_chart(fig_dem, use_container_width=True)

    st.markdown("""
    <div class="callout-box">
        <b>💡 Strategic Supply-Demand Matrix:</b> While <b>Geopolitics & Defense</b> commands continuous release inventory, <b>Health, Science & Mind</b> and <b>Forensics/True Crime</b> verticals exhibit asymmetric viewership per episode. Balancing release frequency into these under-indexed categories presents the clearest immediate growth opportunity.
    </div>
    """, unsafe_allow_html=True)

# ----------------- TAB 3: GUEST INTELLIGENCE DOSSIER -----------------
with tab_briefing:
    st.write("")
    col_in1, col_in2 = st.columns([2, 1])
    with col_in1:
        guest_name = st.text_input("Prospective Guest Name", value="Dr. Arvind Kumar", key="guest_name_input")
    with col_in2:
        topic_domain = st.selectbox("Topic Vertical", [
            "Sports, Athletes & High Performance",
            "True Crime & Forensic Psychology",
            "Geopolitics & National Security",
            "Education & Competitive Exams",
            "Business, Startups & Venture Capital",
            "Health, Biohacking & Neuroscience", 
            "Personal Finance & Wealth", 
            "Spirituality, Philosophy & Ancient History",
            "Culture & Creator Economy"
        ], key="guest_topic_select")

    if st.button("Generate Pre-Interview Briefing", type="primary", key="btn_gen_briefing"):
        st.write("")
        st.markdown(f"#### Research Dossier: **{guest_name}** ({topic_domain})")
        
        c_left, c_right = st.columns(2)

        with c_left:
            st.markdown(f"""
            <div class="content-box">
                <div class="box-heading">📌 1. Strategic Framing & Angle</div>
                <div class="box-body">
                    <ul>
                        <li><b>Domain Focus:</b> {topic_domain}</li>
                        <li><b>Audience Tension:</b> Actionable operational truths vs. standard industry clichés.</li>
                        <li><b>Editorial Objective:</b> Demystify domain-specific playbooks into concrete consumer takeaways.</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="content-box">
                <div class="box-heading">❓ 2. High-Impact Question Arc</div>
                <div class="box-body">
                    <ol>
                        <li><b>The Contrarian Hook:</b> "What is the most widely repeated rule in your domain that you believe is completely wrong?"</li>
                        <li><b>The Data Reality:</b> "Over the last 3 years, what macro shift is taking place that the general audience is overlooking?"</li>
                        <li><b>The Bottleneck:</b> "Where do 90% of practitioners fail right before they reach mastery?"</li>
                        <li><b>The Execution:</b> "If an ambitious individual started today, what is the single most important lever to focus on?"</li>
                    </ol>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c_right:
            st.markdown("""
            <div class="content-box">
                <div class="box-heading">🎬 3. Short-Form Hook Concepts (Reels / Shorts)</div>
                <div class="box-body">
                    <ul>
                        <li><i>"The uncomfortable reality about this space nobody warns you about..."</i></li>
                        <li><i>"If you are still approaching this like it's 2020, you're falling behind."</i></li>
                        <li><i>"The exact 3-step framework top operators use behind closed doors."</i></li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="content-box">
                <div class="box-heading">⚠️ 4. Editorial Guardrails</div>
                <div class="box-body">
                    <ul>
                        <li>Ground all technical terminology into concrete, everyday analogies.</li>
                        <li>Back all historical and financial claims with verified data points.</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ----------------- TAB 4: CLIP & BRAND INTELLIGENCE -----------------
with tab_repurpose:
    st.write("")
    st.markdown("### 🎬 Verified Video Chapter & Clip Intelligence")
    st.caption("Extracts exact timestamps, actual episode topics, and House of X brand opportunities across the entire podcast duration.")

    col_v1, col_v2 = st.columns([2, 1])
    with col_v1:
        vid_input = st.text_input("YouTube Episode URL or Video ID", value="https://www.youtube.com/watch?v=sample", key="input_yt_url")
    with col_v2:
        vert_input = st.selectbox("Product Synergy Vertical", [
            "Sports, Athletes & High Performance",
            "True Crime & Forensic Psychology",
            "Geopolitics & National Security",
            "Education & Competitive Exams",
            "Business, Startups & Venture Capital",
            "Health, Biohacking & Neuroscience", 
            "Personal Finance & Wealth", 
            "Spirituality, Philosophy & Ancient History",
            "Culture & Creator Economy"
        ], key="synergy_vertical_select")

    if st.button("Extract Verified Clips & Commerce Angles", type="primary", key="btn_extract_clips"):
        from src.transcript_intelligence import extract_video_id, calculate_real_clip_intelligence, generate_house_of_x_angle
        
        v_id = extract_video_id(vid_input)
        
        with st.spinner("Extracting complete chapter timeline and metadata across entire episode..."):
            ep_title, clips, err_msg = calculate_real_clip_intelligence(v_id, vert_input)
            brand_angle = generate_house_of_x_angle(vert_input)

        if err_msg:
            st.warning(f"⚠️ {err_msg}")
        else:
            st.write("")
            st.markdown(f"#### 📺 Episode: **{ep_title}**")
            st.caption(f"Total Highlights Extracted: **{len(clips)} chapters** | Synergy Category: `{vert_input}`")
            st.write("")
            
            st.markdown("#### 🔥 Complete Episode Timeline & Short-Form Hooks")
            
            for idx, seg in enumerate(clips, 1):
                st.markdown(f"""
                <div class="content-box">
                    <div class="box-heading">Chapter #{idx} — Timestamp: <b>{seg['start']}</b> <span style="font-size:0.8rem; color:#6B7280; margin-left:8px;">({seg['source']})</span></div>
                    <div class="box-body">
                        <p><b>Topic / Insight:</b> {seg['headline']}</p>
                        <p><b>Summary:</b> <i>"{seg['quote']}"</i></p>
                        <p><b>Suggested Reel Hook:</b> <code>{seg['hook']}</code></p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("#### 🛍️ House of X — Content-to-Commerce Opportunity Map")
            st.markdown(f"""
            <div class="callout-box">
                <p><b>🏷️ Product White-Space:</b> {brand_angle['white_space']}</p>
                <p><b>🎯 Target Demographic:</b> {brand_angle['demographic']}</p>
                <p><b>🚀 Distribution Strategy:</b> {brand_angle['wedge']}</p>
                <p><b>📊 Unit Economics & Moat:</b> {brand_angle['unit_economics']}</p>
            </div>
            """, unsafe_allow_html=True)