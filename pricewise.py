import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Shopping Trends Dashboard",page_icon="🛍",layout="wide")

# -------------------------------
# CUSTOM STYLING
# -------------------------------
st.markdown("""
<style>
/* GLOBAL FONT FOR DASHBOARD */
html, body, [class*="css"]  {
    font-family: "Times New Roman", Georgia, serif;
}
/* BACKGROUND IMAGE */
.stApp {
    background-image: url("https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-attachment: fixed;
}

/* DARK OVERLAY */
.stApp::before {
   content: " ";
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.65);
    pointer-events: none;
}

/* GLASS CONTAINER */
.block-container{
    background: rgba(20,20,20,0.6);
    padding:30px;
    border-radius:15px;
    backdrop-filter: blur(12px);
}

/* KPI CARDS */
.kpi-card{
    padding:20px;
    border-radius:10px;
    text-align:center;
    color:white;
    font-weight:bold;
    box-shadow:0 4px 15px rgba(0,0,0,0.5);
}

.kpi-title{
    font-size:26px;
    margin-bottom:5px;
}

.kpi-value{
    font-size:32px;
}

.sales {background: linear-gradient(180deg,#1e90ff,#00509a);}
.orders {background: linear-gradient(180deg,#2ed573,#008000);}
.rating {background: linear-gradient(180deg,#ff9f43,#d35400);}
.avg-val {background: linear-gradient(180deg,#ff4b9f,#900048);}

/* SIDEBAR STYLE */
section[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#1f2937,#111827);
}

section[data-testid="stSidebar"] label{
    color:white !important;
    font-weight:600;
}

/* HEADINGS */
h1{
    color:white;
    text-align:center;
    font-size:44px;
    font-family:"Times New Roman", Georgia, serif;
}

h2{
    color:white !important;
    text-align:center;
    font-size:34px;
    font-family:"Times New Roman", Georgia, serif;
}

h3{
    color:white !important;
    text-align:center;
    font-size:28px;
    font-family:"Times New Roman", Georgia, serif;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
col1,col2,col3 = st.columns([1,4,1])

with col2:
    st.markdown("""
    <h1 style="
    font-family:'Times New Roman', serif;
    font-size:46px;
    text-align:center;
    margin-top:20px;
    color:white;
    ">
                <span style="color:#2ed573;">🛍</span>Shopping Trends Dashboard
    </h1>
    """, unsafe_allow_html=True)

# -------------------------------
# FILE UPLOAD
# -------------------------------
if "shopping_trends.csv" in os.listdir():
    data=pd.read_csv("shopping_trends.csv")
else:
    st.header("Upload Shopping Trends CSV")
    uploaded_file = st.sidebar.file_uploader("Upload shopping_trends.csv", type=["csv"]
    )
    if uploaded_file is None:
        st.info("Upload dataset to view dashboard")
        st.stop()

    data = pd.read_csv(uploaded_file)
data.columns = data.columns.str.strip()

required_cols = [
    "Age","Gender","Item Purchased","Category",
    "Purchase Amount (USD)","Location","Season",
    "Review Rating","Payment Method"
]

if not all(col in data.columns for col in required_cols):
    st.error(f"Dataset must contain columns: {required_cols}")
    st.stop()

data["Purchase Amount (USD)"] = pd.to_numeric(data["Purchase Amount (USD)"], errors="coerce")
data = data[required_cols].dropna(subset=["Age","Gender","Category","Purchase Amount (USD)","Review Rating","Payment Method"])

# -------------------------------
# CURRENCY CONVERSION 
# -------------------------------
USD_TO_INR = 92.54
data["Purchase Amount (INR)"] = (data["Purchase Amount (USD)"] * USD_TO_INR).round(0)

# -------------------------------
# ASSIGN LOCATIONS
# -------------------------------
cities = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    "Kochi", "Thiruvananthapuram", "Kozhikode", "Coimbatore",
    "Mysore", "Chandigarh", "Indore", "Bhopal",
    "Visakhapatnam", "Vijayawada", "Madurai", "Tirupati",
    "Goa", "Mangalore", "Noida", "Gurgaon",
    "Patna", "Ranchi", "Raipur", "Dehradun",
    "Amritsar", "Varanasi", "Udaipur", "Jodhpur", "Shimla"
]

# Weighted probabilities 
weights = [
    12,12,11,11,10,   # Mumbai, Delhi, Bangalore, Chennai, Hyderabad
    9,9,8,7,6,        # Kolkata, Pune, Ahmedabad, Jaipur, Lucknow
    4,4,3,3,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1  # Rest 25 smaller cities
]

# Confirm lengths match
assert len(cities) == len(weights)

# Normalize weights
weights = np.array(weights) / sum(weights)
np.random.seed(42)
# Assign cities to data rows
data["Location"] = np.random.choice(cities, size=len(data), p=weights)

# -------------------------------
# FIX PAYMENT METHODS
# -------------------------------
known_methods = ["Cash", "UPI", "Paytm", "PhonePe", "Credit Card", "Debit Card"]
data["Payment Method"] = data["Payment Method"].apply(
    lambda x: x if x in known_methods else np.random.choice(known_methods)
)

# -------------------------------
# FILTERS
# -------------------------------
st.markdown(
    "<h1 style='color:white; font-size:42px;'>Filters</h1>",
    unsafe_allow_html=True
)
col1, col2=st.columns(2)
with col1:
    st.markdown(
        "<p style='color:white; font-size:26px; font-weight:bold; text-align:center;'>Category</p>",
        unsafe_allow_html=True
    )
    category = st.selectbox(
        "",
        ["All"] + list(data["Category"].unique())
    )
with col2:
    st.markdown(
        "<p style='color:white; font-size:26px; font-weight:bold; text-align:center;'>Season</p>",
        unsafe_allow_html=True
    )

    season = st.selectbox(
        "",
       ["All"] + list(data["Season"].unique())
    )
filtered = data.copy()

if category != "All":
    filtered = filtered[filtered["Category"] == category]

if season != "All":
    filtered = filtered[filtered["Season"] == season]

# -------------------------------
# KPI METRICS
# -------------------------------
total_sales = filtered["Purchase Amount (INR)"].sum()
total_orders = filtered.shape[0]
avg_rating = filtered["Review Rating"].mean()
avg_purchase_val = filtered["Purchase Amount (INR)"].mean()

k1,k2,k3,k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card sales">
    <div class="kpi-title">Total Sales</div>
    <div class="kpi-value">₹{total_sales:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card orders">
    <div class="kpi-title">Total Orders</div>
    <div class="kpi-value">{total_orders}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card rating">
    <div class="kpi-title">Average Rating</div>
    <div class="kpi-value">⭐ {avg_rating:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card avg-val">
    <div class="kpi-title">Avg Purchase Value</div>
    <div class="kpi-value">₹{avg_purchase_val:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# CUSTOMER SATISFACTION GAUGE
# -------------------------------
st.markdown("""
<h2 style='
    text-align:center; 
    font-family: "Times New Roman", Georgia, serif; 
    font-weight:bold; 
    font-size:32px; 
    color:#FFD700; 
    text-shadow: 2px 2px 4px #000000;
'>
    Customer Satisfaction
</h2>
""", unsafe_allow_html=True)
st.markdown("""
<p style='
    text-align:center; 
    font-family: "Times New Roman", Georgia, serif; 
    font-size:24px; 
    font-weight:bold; 
    color:#FF69B4; 
    letter-spacing:1px;
'>
    Average Rating
</p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])

with col2:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_rating,
        number={'font': {'size': 45, 'color': '#FFD700', 'family': 'Times New Roman, Georgia, serif'}},
        gauge={'axis': {'range': [0,5], 'tickfont': {'size': 18, 'color':'white', 'family': 'Times New Roman, Georgia, serif'}},
            'bar': {'color': "#FFD700", 'thickness': 0.25},
            'bgcolor': "rgba(0,0,0,0)", 
            'borderwidth': 2,
            'bordercolor': "white",
            'steps': [
                {'range':[0,2], 'color':'rgba(255,77,77,0.3)'},
                {'range':[2,3], 'color':'rgba(255,165,2,0.3)'},
                {'range':[3,4], 'color':'rgba(46,213,115,0.3)'},
                {'range':[4,5], 'color':'rgba(30,144,255,0.3)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 6},
                'thickness': 0.75,
                'value': avg_rating
            }
        }
    ))

    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=300,
        margin=dict(t=10,b=10)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
# -------------------------------
# COMMON CHART FONT STYLE
# -------------------------------
chart_style = dict(title=dict(text=""),font=dict(
        family="Times New Roman",
        size=18,
        color="white"
    ),                            
    title_font=dict(
        family="Times New Roman",
        size=28,
        color="white"
    ),
    xaxis=dict(
        title_font=dict(size=22, family="Times New Roman", color="white"),
        tickfont=dict(size=18, family="Times New Roman", color="white")
    ),
    yaxis=dict(
        title_font=dict(size=22, family="Times New Roman", color="white"),
        tickfont=dict(size=18, family="Times New Roman", color="white")
    ),
    legend=dict(
        font=dict(size=18, family="Times New Roman", color="white"),
        title_font=dict(size=20, family="Times New Roman", color="white")
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

# -------------------------------
# CUMULATIVE SALES TREND
# -------------------------------
st.markdown("### Sales Growth Trend")
filtered_sorted = filtered.reset_index(drop=True)

# Create order sequence
filtered_sorted["Order Number"] = filtered_sorted.index + 1
# Cumulative sales
filtered_sorted["Cumulative Sales"] = (
    filtered_sorted["Purchase Amount (INR)"].cumsum()
)

fig_line = px.line(
    filtered_sorted,
    x="Order Number",
    y="Cumulative Sales"
)
fig_line.update_layout(**chart_style)
st.plotly_chart(fig_line, use_container_width=True)

# -------------------------------
# CHARTS
# -------------------------------
col1,col2 = st.columns(2)

with col1:
    st.markdown("### Sales by Category")

    cat_sales = filtered.groupby("Category")["Purchase Amount (INR)"].sum().reset_index()

    fig1 = px.bar(
        cat_sales,
        x="Category",
        y="Purchase Amount (INR)",
        color="Category",
        color_discrete_map={"Accessories":"#3A86FF","Clothing":"#00BBF9","Footwear":"#06D6A0","Outwear":"#8338EC"}
    )
    fig1.update_layout(**chart_style)
    st.plotly_chart(fig1,use_container_width=True)

with col2:
    st.markdown("### Purchases by Gender")

    fig2 = px.pie(
        filtered,
        names="Gender",
        hole=0.45,
        color_discrete_sequence=["#FF6B9A","#4CC9F0"]
    )

    fig2.update_layout(**chart_style)
    fig2.update_traces(textfont_size=18,textfont_family="Times New Roman")
    st.plotly_chart(fig2,use_container_width=True)
col3,col4 = st.columns(2)

with col3:
    st.markdown("### Sales by Season")

    season_sales = filtered.groupby("Season")["Purchase Amount (INR)"].sum().reset_index()

    fig3 = px.bar(
        season_sales,
        x="Season",
        y="Purchase Amount (INR)",
        color="Season",
        color_discrete_map={"Summer":"#FFD166","Winter":"#EF476F","Spring":"#06D6A0","Autumn":"#118AB2"}
    )

    fig3.update_layout(**chart_style)
    st.plotly_chart(fig3,use_container_width=True)

with col4:
    st.markdown("### Customer Age Groups")

    filtered["Age Group"] = pd.cut(
        filtered["Age"],
        bins=[18,25,35,45,60,100],
        labels=["18-25","26-35","36-45","46-60","60 +"]
    )

    age = filtered["Age Group"].value_counts().reset_index()
    age.columns=["Age Group","Customers"]

    fig4 = px.pie(
        age,
        names="Age Group",
        values="Customers",
        hole=0.45,
        color_discrete_sequence=["#FFBE0B","#FB5607","#FF006E","#8338EC"]
    )

    fig4.update_layout(**chart_style)
    fig4.update_traces(textfont_size=18,textfont_family="Times New Roman")
    st.plotly_chart(fig4,use_container_width=True)

# -------------------------------
# PAYMENT METHODS
# -------------------------------
st.markdown("### Payment Methods")

payment = filtered["Payment Method"].value_counts().reset_index()
payment.columns=["Payment Method","Count"]

fig_payment = px.bar(
    payment,
    x="Payment Method",
    y="Count",
    color="Payment Method",
    color_discrete_sequence=["#00F5D4","#9B5DE5","#F15BB5","#FEE440","#00BBF9"]
)

fig_payment.update_layout(**chart_style)
st.plotly_chart(fig_payment,use_container_width=True)

# -------------------------------
# SALES BY LOCATION 
# -------------------------------
st.markdown("### Sales by Location (Top 10 Cities) ")
location_sales = (
    filtered.groupby("Location")["Purchase Amount (INR)"]
    .sum()
    .sort_values(ascending=False)
    .head(10) 
    .reset_index()
)

# Horizontal bar chart
fig_location = px.bar(
    location_sales,
    x="Purchase Amount (INR)",
    y="Location",
    orientation="h",  
    color="Location",
    color_discrete_sequence=[
        "#3A86FF","#4CC9F0","#06D6A0","#FFD166","#EF476F",
        "#8338EC","#FF006E","#00BBF9","#F15BB5","#9B5DE5"
    ],
    labels={"Purchase Amount (INR)": "Sales (₹)"}
)

fig_location.update_layout(**chart_style)
fig_location.update_layout(
    height=650,
    yaxis=dict(categoryorder="total ascending")
)  
st.plotly_chart(fig_location, use_container_width=True)

# -------------------------------
# DATA TABLE
# -------------------------------
st.markdown("### Filtered Data")
filtered_inr = filtered[["Age","Gender","Item Purchased","Category","Purchase Amount (INR)","Location","Season","Review Rating","Payment Method"]]
st.dataframe(filtered_inr,use_container_width=True)

csv = filtered_inr.to_csv(index=False).encode('utf-8')

st.download_button(
    "Download Filtered Data",
    csv,
    "shopping_filtered_inr.csv",
    "text/csv"
)
