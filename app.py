import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .header-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #111827;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .header-subtitle {
        color: #6B7280;
        font-size: 0.95rem;
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
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .box-heading {
        color: #111827;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 12px;
        border-bottom: 1px solid #F3F4F6;
        padding-bottom: 8px;
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
    return df

df = load_data()

# 4. Minimal Header
st.markdown("""
<div class="header-container">
    <div class="header-title">🎙️ Figuring Out — Content & Commerce Intelligence</div>
    <div class="header-subtitle">Performance velocity tracking, pre-interview research dossiers, and House of X brand-incubation mapping.</div>
</div>
""", unsafe_allow_html=True)

if df is None:
    st.error("Data files not found. Please ensure data/processed_episodes.csv is present.")
    st.stop()

# 5. Top KPI Row
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

# 6. Tab Navigation
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
            color_discrete_sequence=["#2563EB", "#7C3AED", "#059669", "#D97706", "#DC2626"]
        )
        fig_scatter.update_layout(
            font=dict(family="Plus Jakarta Sans", color="#374151"),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(title=dict(text="Category"), orientation="h", y=-0.2)
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
            color_discrete_sequence=["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444"]
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
            color_discrete_sequence=["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444"]
        )
        fig_dem.update_layout(font=dict(family="Plus Jakarta Sans", color="#374151"), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", showlegend=False)
        st.plotly_chart(fig_dem, use_container_width=True)

    st.markdown("""
    <div class="callout-box">
        <b>💡 Strategic Finding:</b> <b>Geopolitics & Defense</b> drives consistent release volume, but <b>Health, Science & Mind</b> commands the highest average views (~1.59M) despite having only 3 episodes. Expanding guest coverage in this vertical is the highest leverage opportunity to capture untapped demand.
    </div>
    """, unsafe_allow_html=True)

# ----------------- TAB 3: GUEST INTELLIGENCE DOSSIER -----------------
with tab_briefing:
    st.write("")
    col_in1, col_in2 = st.columns([2, 1])
    with col_in1:
        guest_name = st.text_input("Prospective Guest Name", value="Dr. Arvind Kumar")
    with col_in2:
        topic_domain = st.selectbox("Topic Vertical", [
            "Health & Neuro-Optimization",
            "Geopolitics & National Security",
            "Direct-to-Consumer & Brands (House of X)",
            "Macroeconomics & Capital Markets"
        ])

    generate = st.button("Generate Pre-Interview Briefing", type="primary")

    if generate:
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
                        <li><b>Audience Tension:</b> Unpacking actionable truths vs. theoretical generalizations.</li>
                        <li><b>Editorial Objective:</b> Demystify complex industry realities into clear consumer takeaways.</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="content-box">
                <div class="box-heading">❓ 2. High-Impact Question Arc</div>
                <div class="box-body">
                    <ol>
                        <li><b>The Contrarian Hook:</b> "What is the single most common advice in your field that is completely counterproductive?"</li>
                        <li><b>The Reality Check:</b> "Looking at the numbers over the last 3 years, what shift is happening that consumers aren't seeing?"</li>
                        <li><b>The Resistance:</b> "Why are legacy players failing to adapt to this transition?"</li>
                        <li><b>The Execution:</b> "If a 22-year-old wanted to capitalize on this trend today, what is step one?"</li>
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
                        <li><i>"The uncomfortable truth about this industry nobody talks about..."</i></li>
                        <li><i>"If you are still following this rule in 2026, you're making a mistake."</i></li>
                        <li><i>"The exact 3-step decision framework used by top operators."</i></li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="content-box">
                <div class="box-heading">⚠️ 4. Editorial Guardrails</div>
                <div class="box-body">
                    <ul>
                        <li>Ground all technical terminology into concrete, relatable analogies.</li>
                        <li>Verify factual claims against primary industry sources and data points.</li>
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
        vid_input = st.text_input("YouTube Episode URL or Video ID", value="https://www.youtube.com/watch?v=sample")
    with col_v2:
        vert_input = st.selectbox("Product Synergy Vertical", [
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
            st.caption(f"Total Highlights Extracted: **{len(clips)} chapters across full runtime** | Vertical: `{vert_input}`")
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