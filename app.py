import streamlit as st
from utils import init_bigquery
from pages import (
    time_impact_analysis,
    product_category_analysis,
    user_engagement_analysis,
    geographic_analysis
)

# Page config
st.set_page_config(
    page_title="GA4 E-commerce Analysis",
    page_icon="📊",
    layout="wide"
)

# Title and introduction
st.title("📊 GA4 E-commerce Data Analysis")
st.markdown("*EDHEC Team Assignment - Advanced Web Analytics*")

# Initialize BigQuery client
@st.cache_resource
def init_client():
    return init_bigquery()

client = init_client()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Analysis",
    ["Time Impact", "Product Categories", "User Engagement", "Geographic Patterns"]
)

# Page routing
if page == "Time Impact":
    time_impact_analysis(client)
elif page == "Product Categories":
    product_category_analysis(client)
elif page == "User Engagement":
    user_engagement_analysis(client)
else:
    geographic_analysis(client)

# Footer
st.markdown("---")
st.markdown("*Created with ❤️ using Streamlit and BigQuery*")