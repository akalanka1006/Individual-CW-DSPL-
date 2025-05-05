import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Set page config for a colorful and engaging experience
st.set_page_config(page_title="Sri Lanka Wages Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# Load background image or add decorative visuals 
header_img = "header_banner.png"  
try:
    st.image(header_img, use_container_width=True)
except:
    st.markdown("# 🇱🇰 Welcome to the Wages Dashboard")

# Load the cleaned dataset
@st.cache_data
def load_data():
    df = pd.read_csv("average_daily_wages_of_informal_sector_.csv")
    df.columns = df.columns.astype(str)
    return df

df = load_data()

# Sidebar filters
st.sidebar.markdown("## Filter Options")
st.sidebar.markdown("Customize your view using the options below.")
sector_options = df['Province and Sector'].unique()
selected_sectors = st.sidebar.multiselect("🔍 Select Sector/Gender(s)", sector_options, default=sector_options[:1])

year_columns = [col for col in df.columns if col != 'Province and Sector']
selected_years = st.sidebar.multiselect("📅 Select Years", year_columns, default=year_columns)

# Filtered data
filtered_df = df[df['Province and Sector'].isin(selected_sectors)][['Province and Sector'] + selected_years]

# Overview section
st.subheader("📊 Wage Overview")
st.dataframe(filtered_df, use_container_width=True)

# Download data
st.download_button("⬇️ Download Filtered Data as CSV", filtered_df.to_csv(index=False), file_name="filtered_wages.csv", mime="text/csv")

# Summary Statistics
st.subheader("📈 Summary Statistics")
if not filtered_df.empty:
    stats_df = filtered_df[selected_years].astype(float).describe().T
    stats_df = stats_df[['mean', '50%', 'std']].rename(columns={'50%': 'median'})
    st.dataframe(stats_df.style.format({"mean": "{:.2f}", "median": "{:.2f}", "std": "{:.2f}"}))

# Line chart of wage trends
st.subheader("📉 Wage Trend Over the Years")
if not filtered_df.empty:
    trend_data = filtered_df.set_index('Province and Sector').T
    trend_data.index.name = 'Year'
    trend_data = trend_data.reset_index()
    trend_data = pd.melt(trend_data, id_vars='Year', var_name='Sector', value_name='Average Wage')
    trend_data['Year'] = trend_data['Year'].astype(int)

    fig = px.line(trend_data, x='Year', y='Average Wage', color='Sector', markers=True,
                  title="Wage Trend Over Selected Years",
                  template="seaborn")
    st.plotly_chart(fig, use_container_width=True)
    st.download_button("⬇️ Download Line Chart Data", trend_data.to_csv(index=False), file_name="line_chart_data.csv", mime="text/csv")

# Bar chart comparison
st.subheader(" Comparison by Sector")
avg_by_sector = df.set_index('Province and Sector')[year_columns].mean(axis=1).reset_index()
avg_by_sector.columns = ['Province and Sector', 'Average Wage']
fig2 = px.bar(avg_by_sector, x='Province and Sector', y='Average Wage', title="Average Wages by Sector",
              color='Average Wage', color_continuous_scale='Viridis', template='ggplot2')
st.plotly_chart(fig2, use_container_width=True)
st.download_button("⬇️ Download Sector Comparison Data", avg_by_sector.to_csv(index=False), file_name="sector_comparison.csv", mime="text/csv")

st.subheader(" Additional Insights")

# 1. Heatmap of wages by year and sector
df_heat = df.set_index('Province and Sector')
fig3 = px.imshow(df_heat[selected_years].astype(float),
                 labels=dict(color="Wage"),
                 x=selected_years,
                 y=df_heat.index,
                 title="📅 Heatmap of Wages by Sector and Year",
                 color_continuous_scale='Plasma')
st.plotly_chart(fig3, use_container_width=True)

# 2. Box plot for wage distribution
melted_df = pd.melt(df, id_vars='Province and Sector', var_name='Year', value_name='Wage')
melted_df['Wage'] = pd.to_numeric(melted_df['Wage'], errors='coerce')
fig4 = px.box(melted_df, x='Year', y='Wage', title="📦 Wage Distribution by Year", points="all", template="plotly_dark")
st.plotly_chart(fig4, use_container_width=True)

# 3. Pie chart for a selected year
st.subheader("🎯 Wage Distribution Pie Chart")
pie_year = st.selectbox("Choose a Year for Pie Chart", year_columns)
pie_df = df[['Province and Sector', pie_year]].copy()
pie_df[pie_year] = pd.to_numeric(pie_df[pie_year], errors='coerce')
fig5 = px.pie(pie_df, values=pie_year, names='Province and Sector', title=f"Wage Distribution in {pie_year}",
              color_discrete_sequence=px.colors.sequential.RdBu)
st.plotly_chart(fig5, use_container_width=True)

# Narrative Insights
st.markdown("---")
st.subheader("🧠 Key Insights and Recommendations")
st.markdown("""
<div class='highlight'>
- 📈 Wage Growth: Wages in several industries have been steadily rising over time, which suggests economic expansion and higher incomes.<br>
- 🧑‍🤝‍🧑 Gender/Sectoral Disparities: Significant disparities in average salaries between industries and genders point to possible areas for policy change.<br>
- 🧭 Provincial Differences: The distinct salary trends found in each province may be a reflection of regional economic activity or variations in the cost of living.<br>
- 💡 Recommendation: Promote skill-building initiatives in low-wage industries to increase output and profits.<br>
- 📊 Data-Driven Policy: In order to ensure fair pay distribution, authorities might utilize this data to customize economic policies at the regional level.
</div>
""", unsafe_allow_html=True)

# Footer 
st.markdown("---")

