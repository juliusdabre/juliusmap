
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Suburb & SA3 Data Explorer", layout="wide")

st.title("Suburb & SA3 Data Explorer")

# Load data
sa3_df = pd.read_excel('Suburb Excel and Radar January 2025.xlsx', sheet_name='SA3')
suburb_df = pd.read_excel('Suburb Excel and Radar January 2025.xlsx', sheet_name='Suburb')

sa3_df.columns = sa3_df.columns.str.strip()
suburb_df.columns = suburb_df.columns.str.strip()

st.sidebar.header("Navigation")
section = st.sidebar.radio("Go to:", ["SA3 Overview", "Suburb Overview", "Custom Analysis"])

if section == "SA3 Overview":
    st.header("SA3 Overview")
    st.dataframe(sa3_df.head(20))
    if st.checkbox("Show all columns"):
        st.write(sa3_df.columns.tolist())
    # Plot 12M Price Change by SA3
    if st.button("Plot 12M Price Change by SA3 (Capital Region)"):
        cap_df = sa3_df[sa3_df['Sa4'].str.lower() == 'capital region']
        cap_df['12M Price Change'] = pd.to_numeric(cap_df['12M Price Change'], errors='coerce')
        fig = px.bar(cap_df, y='SA3', x='12M Price Change', orientation='h', title='12M Price Change by SA3 in Capital Region')
        st.plotly_chart(fig, use_container_width=True)

elif section == "Suburb Overview":
    st.header("Suburb Overview")
    st.dataframe(suburb_df.head(20))
    if st.checkbox("Show all columns"):
        st.write(suburb_df.columns.tolist())
    # Plot Median Price by Suburb
    if st.button("Plot Median Price by Suburb (Top 20)"):
        suburb_df['Median'] = pd.to_numeric(suburb_df['Median'], errors='coerce')
        top20 = suburb_df.sort_values('Median', ascending=False).head(20)
        fig = px.bar(top20, y='Suburb', x='Median', orientation='h', title='Top 20 Suburbs by Median Price')
        st.plotly_chart(fig, use_container_width=True)

elif section == "Custom Analysis":
    st.header("Custom Analysis")
    st.write("Select a sheet and columns to explore:")
    sheet = st.selectbox("Sheet", ["SA3", "Suburb"])
    if sheet == "SA3":
        df = sa3_df
    else:
        df = suburb_df
    col = st.selectbox("Column", df.columns)
    st.write(df[[col]].head(30))
    if df[col].dtype in ['float64', 'int64']:
        st.write(df[col].describe())
        fig = px.histogram(df, x=col, nbins=30, title="Distribution of " + col)
        st.plotly_chart(fig, use_container_width=True)
