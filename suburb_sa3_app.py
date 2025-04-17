
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
    </style>
    """, unsafe_allow_html=True)

# Load and prepare data
@st.cache_data
def load_data():
    sa3_df = pd.read_excel('Suburb Excel and Radar January 2025.xlsx', sheet_name='SA3')
    sa3_df.columns = sa3_df.columns.str.strip()
    
    # Convert price columns to numeric
    price_cols = ['Median', '12M Price Change', 'Sale Price Median NoW', 
                 'Sale Price Median 2M % Change', 'Sale Price Median -12M']
    for col in price_cols:
        sa3_df[col] = pd.to_numeric(sa3_df[col], errors='coerce')
    
    return sa3_df

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header('Filters')
selected_sa4 = st.sidebar.multiselect('Select SA4 Region', 
                                    options=sorted(df['Sa4'].unique()),
                                    default=df['Sa4'].unique()[0])

# Filter data based on selection
filtered_df = df[df['Sa4'].isin(selected_sa4)] if selected_sa4 else df

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
tab1, tab2, tab3 = st.tabs(["Price Analysis", "Radar Analysis", "Market Metrics"])

with tab1:
    # Price change heatmap
    st.subheader("2-Month Price Change Heatmap by SA3")
    fig_heatmap = px.treemap(filtered_df,
                            path=[px.Constant("All"), 'Sa4', 'SA3'],
                            values='Median',
                            color='Sale Price Median 2M % Change',
                            color_continuous_scale='RdYlBu',
                            title='Price Change Heatmap')
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Price trends
    st.subheader("Price Trends")
    fig_trends = go.Figure()
    for sa3 in filtered_df['SA3'].unique()[:10]:  # Limit to top 10 for visibility
        sa3_data = filtered_df[filtered_df['SA3'] == sa3]
        fig_trends.add_trace(go.Scatter(
            name=sa3,
            x=['Now', '-2M', '-12M'],
            y=[sa3_data['Sale Price Median NoW'].iloc[0],
               sa3_data['Sale Price Median -2M'].iloc[0],
               sa3_data['Sale Price Median -12M'].iloc[0]],
            mode='lines+markers'
        ))
    fig_trends.update_layout(title='Price Trends by SA3',
                           xaxis_title='Time Period',
                           yaxis_title='Median Price')
    st.plotly_chart(fig_trends, use_container_width=True)

with tab2:
    # Radar chart
    st.subheader("Market Indicators Radar")
    selected_sa3 = st.selectbox('Select SA3 for Radar Analysis',
                               options=filtered_df['SA3'].unique())
    
    radar_data = filtered_df[filtered_df['SA3'] == selected_sa3].iloc[0]
    
    # Prepare radar chart data
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
        name=selected_sa3
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

with tab3:
    # Market metrics analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales Turnover vs Yield")
        fig_scatter = px.scatter(filtered_df,
                               x='Sales Turnover',
                               y='Yield',
                               color='Sa4',
                               size='Median',
                               hover_data=['SA3'],
                               title='Sales Turnover vs Yield')
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        st.subheader("Affordability Analysis")
        fig_afford = px.scatter(filtered_df,
                              x='Buy Affordability',
                              y='Rent Affordability',
                              color='Sa4',
                              size='Median',
                              hover_data=['SA3'],
                              title='Buy vs Rent Affordability')
        st.plotly_chart(fig_afford, use_container_width=True)

# Footer with additional metrics
st.markdown("---")
st.subheader("Detailed Metrics Table")
st.dataframe(filtered_df[['SA3', 'Sa4', 'Median', '12M Price Change', 
                         'Sales Turnover', 'Yield', 'Buy Affordability',
                         'Rent Affordability']].sort_values('Median', ascending=False),
            use_container_width=True)
