import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
from datetime import datetime, timedelta

st.set_page_config(page_title="Riyadh Apartments Market Insights", layout="wide")
st.title("Riyadh Apartments Market Insights")


@st.cache_data
def load_data():
    # Load the cleaned data we saved earlier
    df = df = pd.read_csv(r'C:\Users\Welly\PycharmProjects\WeekendProject2\riyadh_apartments_cleaned.csv')

    # Convert date column if it exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df


df = load_data()

# Rename columns to match your Streamlit code if needed
column_mapping = {
    'date': 'listing_date',
    'price_sar': 'rent',  # Assuming you want to analyze rental prices
    'area_sqm': 'size'
}
df = df.rename(columns=column_mapping)

st.sidebar.header("Filters")

# Date range filter
if 'listing_date' in df.columns:
    date_min, date_max = st.sidebar.date_input(
        "Listing Date Range",
        value=[df['listing_date'].min(), df['listing_date'].max()]
    )

# Property type filter
property_types = df['property_type'].unique() if 'property_type' in df.columns else []
selected_types = st.sidebar.multiselect(
    "Property Type", options=property_types, default=property_types
)

# Region filter
regions = df['region'].unique() if 'region' in df.columns else []
selected_regions = st.sidebar.multiselect(
    "Region", options=regions, default=regions
)

# Size filter
if 'size' in df.columns:
    size_min, size_max = st.sidebar.slider(
        "Size (sqm)", float(df['size'].min()), float(df['size'].max()),
        (float(df['size'].min()), float(df['size'].max()))
    )

# Price filter
if 'rent' in df.columns:
    rent_min, rent_max = st.sidebar.slider(
        "Price (SAR)", int(df['rent'].min()), int(df['rent'].max()),
        (int(df['rent'].min()), int(df['rent'].max()))
    )

# Apply filters
df_filtered = df.copy()
if 'listing_date' in df.columns:
    df_filtered = df_filtered[
        (df_filtered['listing_date'] >= pd.to_datetime(date_min)) &
        (df_filtered['listing_date'] <= pd.to_datetime(date_max))
        ]
if 'size' in df.columns:
    df_filtered = df_filtered[df_filtered['size'].between(size_min, size_max)]
if 'rent' in df.columns:
    df_filtered = df_filtered[df_filtered['rent'].between(rent_min, rent_max)]
if selected_types:
    df_filtered = df_filtered[df_filtered['property_type'].isin(selected_types)]
if selected_regions:
    df_filtered = df_filtered[df_filtered['region'].isin(selected_regions)]

# Display metrics
col1, col2, col3 = st.columns(3)
if 'rent' in df_filtered.columns:
    col1.metric("Avg Price", f"{df_filtered['rent'].mean():,.0f} SAR")
    col2.metric("Median Price", f"{df_filtered['rent'].median():,.0f} SAR")
col3.metric("Total Listings", f"{df_filtered.shape[0]}")

st.markdown("---")

# Price trends over time
if 'listing_date' in df_filtered.columns and 'rent' in df_filtered.columns:
    st.subheader("Price Trends Over Time")
    df_filtered['month'] = df_filtered['listing_date'].dt.to_period('M').dt.to_timestamp()
    monthly = df_filtered.groupby('month')['rent'].mean().reset_index()
    fig_trend = px.line(monthly, x='month', y='rent', title='Average Monthly Price')
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# Map visualization
if all(col in df_filtered.columns for col in ['latitude', 'longitude', 'rent']):
    st.subheader("Property Prices by Location")
    fig_map = px.scatter_mapbox(
        df_filtered.sample(min(500, len(df_filtered))),
        lat="latitude",
        lon="longitude",
        color="rent",
        size="size" if 'size' in df_filtered.columns else None,
        hover_name="neighborhood",
        zoom=10,
        mapbox_style="carto-positron"
    )
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# Correlation analysis
st.subheader("Feature Correlations")
num_cols = []
if 'rent' in df_filtered.columns: num_cols.append('rent')
if 'size' in df_filtered.columns: num_cols.append('size')
if 'bedrooms' in df_filtered.columns: num_cols.append('bedrooms')
if 'bathrooms' in df_filtered.columns: num_cols.append('bathrooms')

if len(num_cols) > 1:
    corr = df_filtered[num_cols].corr()
    fig_corr = px.imshow(corr, text_auto=True, title="Correlation Matrix")
    st.plotly_chart(fig_corr, use_container_width=True)

if st.checkbox("Show raw data"):
    st.dataframe(df_filtered)