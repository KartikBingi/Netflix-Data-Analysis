import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Netflix Live Analytics",
    page_icon="🍿",
    layout="wide"
)

# Custom CSS for Netflix Dark Aesthetic
st.markdown("""
<style>
    .stApp {
        background-color: #141414;
        color: #FFFFFF;
    }
    .metric-card {
        background-color: #1F1F1F;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #E50914;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading & Processing
# -----------------------------------------------------------------------------
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv('netflix_data.csv')
    
    # Process dates
    df['date_added'] = df['date_added'].str.strip()
    df['date_added_clean'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added_clean'].dt.year
    df['month_added'] = df['date_added_clean'].dt.month_name()
    
    # Impute missing values
    df['director'] = df['director'].fillna('Unknown')
    df['cast'] = df['cast'].fillna('Unknown')
    df['country'] = df['country'].fillna('Unknown')
    df['rating'] = df['rating'].fillna('Unknown')
    
    # Extract numerical duration
    df['duration_num'] = df['duration'].str.extract('(\d+)').astype(float)
    return df

df = load_and_clean_data()

# -----------------------------------------------------------------------------
# Interactive Sidebar Filters
# -----------------------------------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", width=160)
st.sidebar.title("Interactive Controls")

# Search bar
search_query = st.sidebar.text_input("🔍 Search Title / Cast / Director", "")

# Content Type Filter
content_types = st.sidebar.multiselect(
    "Content Type",
    options=df['type'].unique().tolist(),
    default=df['type'].unique().tolist()
)

# Year Range Slider
min_year = int(df['year_added'].min()) if not df['year_added'].isna().all() else 2008
max_year = int(df['year_added'].max()) if not df['year_added'].isna().all() else 2021

selected_years = st.sidebar.slider(
    "Year Added Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Country Filter
all_countries = sorted(list(set(df['country'].str.split(', ').explode().dropna().unique())))
if 'Unknown' in all_countries:
    all_countries.remove('Unknown')

selected_countries = st.sidebar.multiselect(
    "Filter by Country",
    options=all_countries,
    default=[]
)

# Apply Filters
filtered_df = df[
    (df['type'].isin(content_types)) &
    (df['year_added'] >= selected_years[0]) &
    (df['year_added'] <= selected_years[1])
]

if selected_countries:
    filtered_df = filtered_df[filtered_df['country'].apply(lambda c: any(country in str(c) for country in selected_countries))]

if search_query:
    filtered_df = filtered_df[
        filtered_df['title'].str.contains(search_query, case=False, na=False) |
        filtered_df['cast'].str.contains(search_query, case=False, na=False) |
        filtered_df['director'].str.contains(search_query, case=False, na=False)
    ]

# -----------------------------------------------------------------------------
# Dashboard Body
# -----------------------------------------------------------------------------
st.title("🍿 Netflix Interactive EDA & Content Intelligence")

# Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Titles Found", f"{len(filtered_df):,}")
m2.metric("Movies", f"{len(filtered_df[filtered_df['type']=='Movie']):,}")
m3.metric("TV Shows", f"{len(filtered_df[filtered_df['type']=='TV Show']):,}")
m4.metric("Avg Movie Duration", f"{filtered_df[filtered_df['type']=='Movie']['duration_num'].mean():.0f} min" if not filtered_df[filtered_df['type']=='Movie'].empty else "N/A")

st.markdown("---")

# Row 1: Interactive Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Content Additions Over Time")
    trend_df = filtered_df.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig_trend = px.line(
        trend_df,
        x='year_added',
        y='count',
        color='type',
        markers=True,
        color_discrete_map={'Movie': '#E50914', 'TV Show': '#FFFFFF'},
        template='plotly_dark'
    )
    fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.subheader("🎯 Content Rating Breakdown")
    rating_df = filtered_df['rating'].value_counts().reset_index()
    rating_df.columns = ['rating', 'count']
    fig_rating = px.bar(
        rating_df.head(10),
        x='rating',
        y='count',
        color_discrete_sequence=['#E50914'],
        template='plotly_dark'
    )
    fig_rating.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_rating, use_container_width=True)

st.markdown("---")

# Row 2: Genre & Geography Analysis
col3, col4 = st.columns(2)

with col3:
    st.subheader("🏷️ Top 10 Genres Distribution")
    genres_series = filtered_df['listed_in'].str.split(', ').explode().value_counts().head(10).reset_index()
    genres_series.columns = ['genre', 'count']
    fig_genre = px.pie(
        genres_series,
        names='genre',
        values='count',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Reds_r,
        template='plotly_dark'
    )
    fig_genre.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_genre, use_container_width=True)

with col4:
    st.subheader("🌍 Top Content Producing Countries")
    country_series = filtered_df[filtered_df['country'] != 'Unknown']['country'].str.split(', ').explode().value_counts().head(10).reset_index()
    country_series.columns = ['country', 'count']
    fig_country = px.bar(
        country_series,
        x='count',
        y='country',
        orientation='h',
        color='count',
        color_continuous_scale='Reds',
        template='plotly_dark'
    )
    fig_country.update_layout(yaxis={'categoryorder': 'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_country, use_container_width=True)

st.markdown("---")

# Interactive Data Table & Selection
st.subheader("🔎 Explorer & Deep Dive")
st.dataframe(
    filtered_df[['title', 'type', 'director', 'country', 'release_year', 'rating', 'duration', 'listed_in']],
    use_container_width=True,
    height=300
)