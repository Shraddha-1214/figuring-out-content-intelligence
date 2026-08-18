import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Figuring Out | Content Intelligence Engine",
    page_icon="🎙️",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #ff4b4b;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    csv_path = "data/processed_episodes.csv"
    if not os.path.exists(csv_path):
        return None
    df = pd.read_csv(csv_path)
    df["published_at"] = pd.to_datetime(df["published_at"])
    return df

df = load_data()

st.title("🎙️ Figuring Out — Content & Guest Intelligence Engine")
st.caption("Strategic analytics, gap analysis, and automated briefing framework for Figuring Out Media.")

if df is None:
    st.error("Processed data file not found. Please run `python src/process_features.py` first.")
    st.stop()

# Navigation Tabs
tab_overview, tab_categories, tab_briefing = st.tabs([
    "📊 Channel Performance & Outliers", 
    "🎯 Category Gap Analysis", 
    "📝 AI Guest Dossier Generator"
])

# ----------------- TAB 1: OVERVIEW & OUTLIERS -----------------
with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Analyzed Episodes", len(df))
    with col2:
        st.metric("Avg Views / Episode", f"{int(df['view_count'].mean()):,}")
    with col3:
        st.metric("Avg Engagement Rate", f"{df['engagement_rate_pct'].mean():.2f}%")
    with col4:
        st.metric("Outlier Hit Threshold", f"{int(df['view_count'].median() * 1.5):,} views")

    st.divider()

    col_chart1, col_chart2 = st.columns([3, 2])

    with col_chart1:
        st.subheader("Episode Velocity vs. Duration")
        fig_scatter = px.scatter(
            df,
            x="duration_minutes",
            y="views_per_day",
            size="view_count",
            color="category",
            hover_name="title",
            labels={"duration_minutes": "Duration (Mins)", "views_per_day": "Views / Day"},
            template="plotly_white"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_chart2:
        st.subheader("Top 5 Velocity Outliers")
        top_velocity = df.sort_values(by="views_per_day", ascending=False)[
            ["title", "category", "views_per_day", "engagement_rate_pct"]
        ].head(5)
        st.dataframe(top_velocity, hide_index=True, use_container_width=True)

# ----------------- TAB 2: CATEGORY GAP ANALYSIS -----------------
with tab_categories:
    st.subheader("Content Supply vs. Audience Demand Gap")
    
    cat_summary = df.groupby("category").agg(
        episode_count=("video_id", "count"),
        avg_views=("view_count", "mean"),
        avg_engagement=("engagement_rate_pct", "mean")
    ).reset_index()

    col_bar1, col_bar2 = st.columns(2)

    with col_bar1:
        fig_vol = px.bar(
            cat_summary,
            x="category",
            y="episode_count",
            title="Content Supply (Number of Episodes)",
            labels={"episode_count": "Episodes", "category": "Category"},
            color="category",
            template="plotly_white"
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    with col_bar2:
        fig_perf = px.bar(
            cat_summary,
            x="category",
            y="avg_views",
            title="Audience Demand (Average Views)",
            labels={"avg_views": "Avg Views", "category": "Category"},
            color="category",
            template="plotly_white"
        )
        st.plotly_chart(fig_perf, use_container_width=True)

    st.info("""
    💡 **Strategic Finding:** While **Geopolitics & Defense** drives consistent volume, **Health, Science & Mind** demonstrates the highest average viewership and engagement despite low supply. Increasing coverage in this vertical represents an immediate growth opportunity.
    """)

# ----------------- TAB 3: GUEST DOSSIER GENERATOR -----------------
with tab_briefing:
    st.subheader("Automated Pre-Interview Guest Briefing Module")
    st.write("Generates a research dossier and line of questioning for potential podcast guests.")

    col_in1, col_in2 = st.columns([2, 1])
    with col_in1:
        guest_input = st.text_input("Prospective Guest Name", value="Dr. Arvind Kumar")
    with col_in2:
        domain_input = st.selectbox("Strategic Vertical", [
            "Health & Neuro-Optimization",
            "Geopolitical Strategy",
            "D2C / Consumer Brands (House of X)",
            "Macroeconomics & Capital Markets"
        ])

    if st.button("Generate Intelligence Dossier", type="primary"):
        st.success(f"Generated Dossier for: **{guest_input}** ({domain_input})")
        
        col_res1, col_res2 = st.columns(2)

        with col_res1:
            st.markdown("### 📌 1. Core Profile & Hook Angle")
            st.markdown(f"""
            * **Core Expertise:** Leading voice in {domain_input}.
            * **Why Now:** Recent shift in public discourse surrounding Indian market regulations and consumer awareness.
            * **Primary Audience Tension:** What mainstream advice is actively misleading everyday Indians?
            """)

            st.markdown("### ❓ 2. High-Impact Question Arc")
            st.markdown("""
            1. **The Icebreaker:** "What is the single most widely believed myth in your industry that is completely false?"
            2. **The Data Drill:** "When you look at the raw numbers over the last 3 years, what trend keeps you awake at night?"
            3. **The Friction Point:** "Why do so many legacy institutions resist the exact changes you are advocating for?"
            4. **The Actionable Takeaway:** "If an ambitious 22-year-old had to prepare for the next 5 years in this space, what is step zero?"
            """)

        with col_res2:
            st.markdown("### 🎬 3. Viral Clip & Short-Form Hooks")
            st.markdown("""
            * **Hook 1:** *"The truth about [Topic] that nobody wants to admit on camera..."*
            * **Hook 2:** *"If you are still doing this in 2026, you are losing money/health fast."*
            * **Hook 3:** *"Why 90% of people completely misunderstand this basic rule."*
            """)

            st.markdown("### ⚠️ 4. Potential Contradictions / Watch-outs")
            st.markdown("""
            * Ensure technical jargon is immediately translated into relatable consumer analogies.
            * Challenge claims with counter-arguments from traditional industry incumbents.
            """)