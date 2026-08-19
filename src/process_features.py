import pandas as pd
import numpy as np
import os
import re

def categorize_title(title):
    t = str(title).lower()
    if any(k in t for k in ["kill", "murder", "crime", "dead", "police", "jail", "cbi", "psycho"]):
        return "True Crime & Forensics"
    elif any(k in t for k in ["war", "china", "pakistan", "army", "modi", "geopolitic", "navy", "spy", "raw", "border"]):
        return "Geopolitics & Defense"
    elif any(k in t for k in ["ias", "upsc", "khan sir", "divyakirti", "exam", "student", "teacher", "study"]):
        return "Education & Exams"
    elif any(k in t for k in ["cricket", "athlete", "olympic", "sports", "football", "fitness", "body", "workout"]):
        return "Sports & Performance"
    elif any(k in t for k in ["health", "brain", "sleep", "diet", "doctor", "gut", "nutrition", "dna"]):
        return "Health, Science & Mind"
    elif any(k in t for k in ["crore", "money", "invest", "stock", "tax", "rich", "wealth", "mutual fund", "market"]):
        return "Finance & Wealth"
    elif any(k in t for k in ["startup", "business", "founder", "ai", "brand", "tech", "sales"]):
        return "Startups & Business"
    else:
        return "Culture & Society"

def process_episodes(input_csv="data/raw_episodes.csv", output_csv="data/processed_episodes.csv"):
    df = pd.read_csv(input_csv)
    
    # 1. Parse dates and calculate age
    df['published_at'] = pd.to_datetime(df['published_at'])
    now = pd.Timestamp.now(tz=df['published_at'].dt.tz)
    df['days_live'] = (now - df['published_at']).dt.total_seconds() / (24 * 3600)
    df['days_live'] = df['days_live'].apply(lambda x: max(x, 1.0))
    
    # 2. Duration Conversions (Ensuring BOTH columns exist)
    if 'duration_seconds' in df.columns:
        df['duration_minutes'] = (df['duration_seconds'] / 60.0).round(1)
    elif 'duration_minutes' in df.columns:
        df['duration_seconds'] = df['duration_minutes'] * 60.0
    else:
        df['duration_seconds'] = 3600
        df['duration_minutes'] = 60.0
        
    # 3. Engagement & Velocity Metrics
    df['views_per_day'] = (df['view_count'] / df['days_live']).round(0).astype(int)
    df['engagement_rate_pct'] = (((df['like_count'] + df['comment_count']) / df['view_count']) * 100).round(2)
    df['comments_per_10k_views'] = ((df['comment_count'] / df['view_count']) * 10000).round(1)
    
    # 4. Content Taxonomy & Outlier Thresholds
    df['category'] = df['title'].apply(categorize_title)
    median_views = df['view_count'].median()
    df['is_outlier_hit'] = df['view_count'] >= (median_views * 1.5)
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    return df

if __name__ == "__main__":
    process_episodes()