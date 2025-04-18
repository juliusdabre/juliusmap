
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

# Set page config
st.set_page_config(page_title="Property Market Analysis", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stRadio > div{
        flex-direction:row;
    }
    .stSelectbox {
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Load and prepare data
@st.cache_data
def load_data():
    # Load SA3 data
    sa3_df = pd.read_excel('Suburb Excel and Radar January 2025.xlsx', sheet_name='SA3')
    sa3_df.columns = sa3_df.columns.str.strip()
    
    # Convert price columns to numeric
    price_cols = ['Median', '12M Price Change', 'Sale Price Median NoW', 
                 'Sale Price Median 2M % Change', 'Sale Price Median -12M']
    for col in price_cols:
        sa3_df[col] = pd.to_numeric(sa3_df[col], errors='coerce')
    
    # Extract suburbs list from the 'Suburbs' column if it exists
    if 'Suburbs' in sa3_df.columns:
        suburbs_list = []
        for suburbs in sa3_df['Suburbs'].dropna():
            if isinstance(suburbs, str):
                suburbs_list.extend([s.strip() for s in suburbs.split(',')])
        suburbs_list = sorted(list(set(suburbs_list)))
    else:
        suburbs_list = []
    
    return sa3_df, suburbs_list

# Load data
df, suburbs_list = load_data()

# Sidebar filters
st.sidebar.header('Filters')

# Region selection
filter_level = st.sidebar.radio('Filter Level', 
                              ['SA4', 'SA3', 'Suburb'],
                              horizontal=True)

if filter_level == 'SA4':
    selected_sa4 = st.sidebar.multiselect('Select SA4 Region(s)', 
                                        options=sorted(df['Sa4'].unique()),
                                        default=df['Sa4'].unique()[0])
    filtered_df = df[df['Sa4'].isin(selected_sa4)] if selected_sa4 else df
    
elif filter_level == 'SA3':
    selected_sa3 = st.sidebar.multiselect('Select SA3 Region(s)',
                                        options=sorted(df['SA3'].unique()),
                                        default=df['SA3'].unique()[0])
    filtered_df = df[df['SA3'].isin(selected_sa3)] if selected_sa3 else df

else:  # Suburb level
    if suburbs_list:
        selected_suburbs = st.sidebar.multiselect('Select Suburb(s)',
                                                options=suburbs_list)
        filtered_df = df[df['Suburbs'].str.contains('|'.join(selected_suburbs), na=False)] if selected_suburbs else df
    else:
        st.sidebar.warning('Suburb data not available')
        filtered_df = df

# Additional filters
price_range = st.sidebar.slider('Median Price Range',
                              float(df['Median'].min()),
                              float(df['Median'].max()),
                              (float(df['Median'].min()), float(df['Median'].max())))

yield_range = st.sidebar.slider('Yield Range (%)',
                              float(df['Yield'].min()),
                              float(df['Yield'].max()),
                              (float(df['Yield'].min()), float(df['Yield'].max())))

# Apply additional filters
filtered_df = filtered_df[
    (filtered_df['Median'].between(price_range[0], price_range[1])) &
    (filtered_df['Yield'].between(yield_range[0], yield_range[1]))
]

# Main layout
st.title('Property Market Analysis Dashboard')

# Top metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Median Price", 
              f"${filtered_df['Median'].median():,.0f}",
              f"{filtered_df['12M Price Change'].median():.1f}%")
with col2:
    st.metric("Avg Sales Turnover", 
              f"{filtered_df['Sales Turnover'].mean():.1f}%")
with col3:
    st.metric("Avg Yield", 
              f"{filtered_df['Yield'].mean():.1f}%")
with col4:
    st.metric("Avg Buy Affordability", 
              f"{filtered_df['Buy Affordability'].mean():.1f}")

# Create tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["Price Analysis", "Market Performance", "Detailed Data"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Price distribution
        st.subheader("Price Distribution")
        fig_dist = px.histogram(filtered_df,
                              x='Median',
                              nbins=30,
                              title='Price Distribution',
                              color='Sa4')
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Price change scatter
        st.subheader("Price Change vs Current Median")
        fig_scatter = px.scatter(filtered_df,
                               x='Median',
                               y='12M Price Change',
                               color='Sa4',
                               size='Sales Turnover',
                               hover_data=['SA3'],
                               title='Price Change vs Median Price')
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Radar chart
        st.subheader("Market Performance Radar")
        if len(filtered_df) > 0:
            selected_region = st.selectbox('Select Region for Radar Analysis',
                                         options=filtered_df['SA3'].unique())
            
            radar_data = filtered_df[filtered_df['SA3'] == selected_region].iloc[0]
            
            categories = ['Sales Turnover', 'Yield', 'Buy Affordability',
                         'Rent Affordability', 'Growth Gap']
            
            values = [radar_data['Sales Turnover'],
                     radar_data['Yield'],
                     radar_data['Buy Affordability'],
                     radar_data['Rent Affordability'],
                     radar_data['Growth Gap']]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=selected_region
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(values)]
                    )),
                showlegend=True
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    
    with col2:
        # Yield vs Turnover
        st.subheader("Yield vs Sales Turnover")
        fig_yield = px.scatter(filtered_df,
                             x='Yield',
                             y='Sales Turnover',
                             color='Sa4',
                             size='Median',
                             hover_data=['SA3'],
                             title='Yield vs Sales Turnover Analysis')
        st.plotly_chart(fig_yield, use_container_width=True)

with tab3:
    # Detailed data view
    st.subheader("Detailed Market Data")
    
    # Column selector
    selected_columns = st.multiselect(
        'Select Columns to Display',
        options=df.columns,
        default=['SA3', 'Sa4', 'Median', '12M Price Change', 'Sales Turnover', 
                'Yield', 'Buy Affordability', 'Rent Affordability']
    )
    
    # Sort selector
    sort_column = st.selectbox('Sort By', options=selected_columns)
    sort_order = st.radio('Sort Order', ['Ascending', 'Descending'], horizontal=True)
    
    # Display sorted dataframe
    st.dataframe(
        filtered_df[selected_columns].sort_values(
            sort_column,
            ascending=(sort_order == 'Ascending')
        ),
        use_container_width=True
    )

    # Download button
    csv = filtered_df[selected_columns].to_csv(index=False)
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name="property_market_data.csv",
        mime="text/csv"
    )

# Footer with summary stats
st.markdown("---")
st.subheader("Summary Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Number of Regions", len(filtered_df))
with col2:
    st.metric("Price Range", 
              f"${filtered_df['Median'].min():,.0f} - ${filtered_df['Median'].max():,.0f}")
with col3:
    st.metric("Average Yield",
              f"{filtered_df['Yield'].mean():.2f}%")
