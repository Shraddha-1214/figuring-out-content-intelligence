import os
import re
import pandas as pd
import numpy as np

def extract_guest_and_category(title):
    """
    Parses guest names and assigns strategic content verticals based on keyword taxonomy.
    """
    categories = {
        "Geopolitics & Defense": [
            "war", "china", "pakistan", "raw", "army", "isi", "intelligence", 
            "geopolitics", "modi", "india", "navy", "air force", "israel", "iran"
        ],
        "Finance, Investing & Wealth": [
            "crore", "money", "invest", "stock", "tax", "rich", "market", 
            "wealth", "fund", "scam", "gold", "crypto", "salary", "real estate"
        ],
        "Business & Entrepreneurship": [
            "startup", "business", "brand", "company", "ceo", "founder", 
            "built", "sales", "shark", "d2c", "scale", "revenue"
        ],
        "Health, Science & Mind": [
            "brain", "body", "health", "doctor", "sleep", "diet", "food", 
            "aging", "neuro", "cancer", "sugar", "dna", "fitness"
        ],
        "Spirituality, Culture & Society": [
            "god", "temple", "spiritual", "karma", "history", "ancient", 
            "vedas", "sanatan", "crime", "mafia", "lawyer"
        ]
    }
    
    assigned_category = "General / Society & Culture"
    lower_title = title.lower()
    
    for cat, keywords in categories.items():
        if any(kw in lower_title for kw in keywords):
            assigned_category = cat
            break
            
    # Extract guest name (handles formats like "- Guest Name", "| Guest Name", "Ft. Guest Name")
    guest = "Featured Specialist"
    
    ft_match = re.search(r'(?:ft\.|featuring)\s*([A-Za-z\s.]+)(?:\||-|$)', title, re.IGNORECASE)
    dash_match = re.search(r'[-|–]\s*([A-Za-z\s.]+)(?:\||$)', title)
    
    if ft_match:
        extracted = ft_match.group(1).strip()
    elif dash_match:
        extracted = dash_match.group(1).strip()
    else:
        extracted = ""
        
    if extracted:
        cleaned_words = [w for w in extracted.split() if w.lower() not in ["podcast", "figuring", "out", "raj", "shamani", "ep"]]
        if 1 <= len(cleaned_words) <= 4:
            guest = " ".join(cleaned_words)

    return pd.Series([guest, assigned_category], index=["guest_name", "category"])

def process_episodes(input_path="data/raw_episodes.csv", output_path="data/processed_episodes.csv"):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file {input_path} not found.")

    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} raw podcast records.")

    # 1. Standardize Timestamps and calculate lifespan in days
    df["published_at"] = pd.to_datetime(df["published_at"])
    now = pd.Timestamp.now(tz=df["published_at"].dt.tz)
    df["days_live"] = (now - df["published_at"]).dt.days.clip(lower=1)

    # 2. Audience Engagement Metrics
    df["views_per_day"] = (df["view_count"] / df["days_live"]).round(2)
    
    # Interaction rate (Likes + Comments per 100 views)
    df["engagement_rate_pct"] = (
        ((df["like_count"] + df["comment_count"]) / df["view_count"]) * 100
    ).round(2)
    
    # Debate/Discussion index: Comments generated per 10,000 views
    df["comments_per_10k_views"] = (
        (df["comment_count"] / df["view_count"]) * 10000
    ).round(2)

    # 3. Categorization & Guest Parsing
    df[["guest_name", "category"]] = df["title"].apply(extract_guest_and_category)

    # 4. Outlier Identification (Episodes with view count > 1.5x channel median)
    median_views = df["view_count"].median()
    df["is_outlier_hit"] = df["view_count"] >= (1.5 * median_views)

    # 5. Export processed features
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Feature engineering complete. Saved to: {output_path}")

    # Display Strategic Insights
    print("\n" + "="*50)
    print("      CONTENT INTELLIGENCE SUMMARY      ")
    print("="*50)
    print("\n--- Category Breakdown (Count & Average Views) ---")
    cat_summary = df.groupby("category").agg(
        episodes=("video_id", "count"),
        avg_views=("view_count", "mean"),
        avg_engagement=("engagement_rate_pct", "mean")
    ).round(2).sort_values(by="avg_views", ascending=False)
    print(cat_summary)

    print("\n--- Top 3 Outlier Episodes by Velocity (Views / Day) ---")
    top_velocity = df.sort_values(by="views_per_day", ascending=False)[
        ["title", "category", "views_per_day", "engagement_rate_pct"]
    ].head(3)
    print(top_velocity.to_string(index=False))
    print("="*50)

if __name__ == "__main__":
    process_episodes()