import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(
    page_title="Netflix EDA Dashboard",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------------------------------------------------------
# Data Loading & Preprocessing
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('netflix_data.csv')
    
    # Preprocessing date column
    df['date_added'] = df['date_added'].str.strip()
    df['date_added_clean'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added_clean'].dt.year
    df['month_added'] = df['date_added_clean'].dt.month_name()
    
    # Fill missing values
    df['director'] = df['director'].fillna('Unknown')
    df['cast'] = df['cast'].fillna('Unknown')
    df['country'] = df['country'].fillna('Unknown')
    df['rating'] = df['rating'].fillna(df['rating'].mode()[0])
    
    # Numeric duration
    df['duration_num'] = df['duration'].str.extract('(\d+)').astype(float)
    return df

df = load_data()

# -----------------------------------------------------------------------------
# Sidebar Filters
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 Filter Options")

# Filter by Type
type_filter = st.sidebar.multiselect(
    "Select Content Type:",
    options=df['type'].unique(),
    default=df['type'].unique()
)

# Filter by Year Added
min_year = int(df['year_added'].min()) if not df['year_added'].isna().all() else 2008
max_year = int(df['year_added'].max()) if not df['year_added'].isna().all() else 2021

year_range = st.sidebar.slider(
    "Select Year Range (Added):",
    min_value=min_year,
    max_value=max_year,
    value=(2015, max_year)
)

# Apply Filters
filtered_df = df[
    (df['type'].isin(type_filter)) &
    (df['year_added'] >= year_range[0]) &
    (df['year_added'] <= year_range[1])
]

# -----------------------------------------------------------------------------
# Main Dashboard UI
# -----------------------------------------------------------------------------
st.title("🎬 Netflix Exploratory Data Analysis Dashboard")
st.markdown("An interactive overview of content trends, country distribution, ratings, and genres on Netflix.")

# Key Performance Indicators (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Titles", len(filtered_df))
col2.metric("Movies", len(filtered_df[filtered_df['type'] == 'Movie']))
col3.metric("TV Shows", len(filtered_df[filtered_df['type'] == 'TV Show']))
col4.metric("Unique Countries", filtered_df[filtered_df['country'] != 'Unknown']['country'].nunique())

st.divider()

# -----------------------------------------------------------------------------
# Visualizations
# -----------------------------------------------------------------------------
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("📊 Content Type Distribution")
    fig, ax = plt.subplots(figsize=(6, 4))
    type_counts = filtered_df['type'].value_counts()
    if not type_counts.empty:
        ax.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', colors=['#E50914', '#221F1F'], startangle=90)
        st.pyplot(fig)
    else:
        st.info("No data available for selected filters.")

with row1_col2:
    st.subheader("🌍 Top 10 Producing Countries")
    top_countries = (
        filtered_df[filtered_df['country'] != 'Unknown']['country']
        .str.split(', ')
        .explode()
        .value_counts()
        .head(10)
    )
    if not top_countries.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=top_countries.values, y=top_countries.index, palette='Reds_r', ax=ax)
        ax.set_xlabel("Number of Titles")
        st.pyplot(fig)
    else:
        st.info("No country data available.")

st.divider()

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("📈 Titles Added Over Time")
    yearly_data = filtered_df.groupby(['year_added', 'type']).size().unstack().fillna(0)
    if not yearly_data.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        yearly_data.plot(kind='line', marker='o', color=['#E50914', '#221F1F'], ax=ax)
        ax.set_xlabel("Year Added")
        ax.set_ylabel("Count")
        st.pyplot(fig)
    else:
        st.info("No yearly data available.")

with row2_col2:
    st.subheader("🏷️ Top 10 Genres")
    top_genres = (
        filtered_df['listed_in']
        .str.split(', ')
        .explode()
        .value_counts()
        .head(10)
    )
    if not top_genres.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=top_genres.values, y=top_genres.index, color='#E50914', ax=ax)
        ax.set_xlabel("Count")
        st.pyplot(fig)
    else:
        st.info("No genre data available.")

# -----------------------------------------------------------------------------
# Raw Dataset Viewer
# -----------------------------------------------------------------------------
st.divider()
st.subheader("📄 Dataset Preview")
if st.checkbox("Show Raw Data Table"):
    st.dataframe(filtered_df[['title', 'type', 'director', 'country', 'release_year', 'rating', 'duration', 'listed_in']])