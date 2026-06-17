import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")
plt.rcParams["figure.figsize"] = (10, 5)

# =========================
# LOAD DATA
# =========================

df = pd.read_csv("nykaa.csv")

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])
print()
print(df.info())
print()
print("Missing values:")
print(df.isnull().sum().sort_values(ascending=False))
print()
print("Summary statistics:")
print(df.describe().T.round(2))

# =========================
# FEATURE ENGINEERING
# =========================

df["CTR"] = np.where(
    df["Impressions"] > 0,
    (df["Clicks"] / df["Impressions"]) * 100,
    0
)

df["Conversion_Rate"] = np.where(
    df["Clicks"] > 0,
    (df["Conversions"] / df["Clicks"]) * 100,
    0
)

df["Cost_Per_Click"] = np.where(
    df["Clicks"] > 0,
    df["Acquisition_Cost"] / df["Clicks"],
    0
)

df["Cost_Per_Lead"] = np.where(
    df["Leads"] > 0,
    df["Acquisition_Cost"] / df["Leads"],
    0
)

df["Cost_Per_Acquisition"] = np.where(
    df["Conversions"] > 0,
    df["Acquisition_Cost"] / df["Conversions"],
    0
)

df["ROAS"] = np.where(
    df["Acquisition_Cost"] > 0,
    df["Revenue"] / df["Acquisition_Cost"],
    0
)

print("Derived metrics summary:")
print(df[["CTR", "Conversion_Rate", "Cost_Per_Click",
          "Cost_Per_Lead", "Cost_Per_Acquisition", "ROAS"]].describe().round(2))

# =========================
# KPIs
# =========================

print()
print("Total Revenue:", df["Revenue"].sum())
print("Total Cost:", df["Acquisition_Cost"].sum())
print("Total Impressions:", df["Impressions"].sum())
print("Total Clicks:", df["Clicks"].sum())
print("Total Leads:", df["Leads"].sum())
print("Total Conversions:", df["Conversions"].sum())
print("Average ROI:", round(df["ROI"].mean(), 2))
print("Average ROAS:", round(df["ROAS"].mean(), 2))

# =========================
# REVENUE BY CAMPAIGN TYPE
# =========================

campaign_rev = df.groupby("Campaign_Type")["Revenue"].sum().sort_values(ascending=False)
print()
print("Revenue by Campaign Type:")
print(campaign_rev)

campaign_rev.plot(kind="bar", figsize=(10, 5))
plt.title("Revenue by Campaign Type")
plt.ylabel("Revenue")
plt.tight_layout()
plt.show()

print()
print("ROI by Campaign Type:")
print(df.groupby("Campaign_Type")["ROI"].mean().sort_values(ascending=False))

# =========================
# CHANNEL PERFORMANCE
# =========================

channel = df.groupby("Channel_Used").agg({
    "Revenue": "sum",
    "Conversions": "sum",
    "ROI": "mean"
})
print()
print("Channel Performance (top by Revenue):")
print(channel.sort_values("Revenue", ascending=False))

# =========================
# CUSTOMER SEGMENT
# =========================

segment = df.groupby("Customer_Segment").agg({
    "Revenue": "sum",
    "Conversions": "sum",
    "ROI": "mean"
})
print()
print("Segment Performance:")
print(segment.sort_values("Revenue", ascending=False))

segment["Revenue"].sort_values().plot(kind="bar")
plt.title("Revenue by Customer Segment")
plt.tight_layout()
plt.show()

# =========================
# TARGET AUDIENCE
# =========================

audience = df.groupby("Target_Audience").agg({
    "Revenue": "sum",
    "Conversions": "sum",
    "ROI": "mean"
})
print()
print("Audience Performance:")
print(audience.sort_values("Revenue", ascending=False))

# =========================
# MARKETING FUNNEL
# =========================

funnel = pd.DataFrame({
    "Stage": ["Impressions", "Clicks", "Leads", "Conversions"],
    "Count": [
        df["Impressions"].sum(),
        df["Clicks"].sum(),
        df["Leads"].sum(),
        df["Conversions"].sum()
    ]
})
print()
print("Marketing Funnel:")
print(funnel)

# =========================
# MONTHLY REVENUE TREND
# =========================

df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.to_period("M")

monthly = df.groupby("Month")["Revenue"].sum()
monthly.plot(marker="o", figsize=(12, 5))
plt.title("Monthly Revenue Trend")
plt.tight_layout()
plt.show()

# =========================
# PLOTLY DASHBOARD
# =========================

df["Month"] = df["Date"].dt.strftime("%Y-%m")
df["ROAS"] = df["Revenue"] / df["Acquisition_Cost"]

total_revenue = df["Revenue"].sum()
total_cost = df["Acquisition_Cost"].sum()
total_conversions = df["Conversions"].sum()
avg_roi = df["ROI"].mean()
avg_ctr = df["CTR"].mean()
avg_roas = df["ROAS"].mean()

fig = make_subplots(
    rows=3, cols=2,
    specs=[
        [{"type": "indicator"}, {"type": "indicator"}],
        [{"type": "bar"},       {"type": "treemap"}],
        [{"type": "scatter"},   {"type": "funnel"}]
    ],
    subplot_titles=(
        "Total Revenue", "Marketing Efficiency",
        "Revenue by Channel", "Customer Segment Revenue",
        "Revenue Trend", "Marketing Funnel"
    )
)

# KPI 1 — Revenue
fig.add_trace(
    go.Indicator(
        mode="number",
        value=total_revenue,
        title={"text": "Revenue ₹"},
        number={"valueformat": ","}
    ),
    row=1, col=1
)

# KPI 2 — ROAS + ROI
fig.add_trace(
    go.Indicator(
        mode="number+delta",
        value=avg_roas,
        delta={"reference": 1},
        title={"text": f"ROAS<br>ROI={avg_roi:.2f}%"}
    ),
    row=1, col=2
)

# Channel bar chart
channel_df = df.groupby("Channel_Used")["Revenue"].sum().reset_index()
fig.add_trace(
    go.Bar(x=channel_df["Channel_Used"], y=channel_df["Revenue"], name="Revenue"),
    row=2, col=1
)

# Customer segment treemap
segment_df = df.groupby("Customer_Segment")["Revenue"].sum().reset_index()
fig.add_trace(
    go.Treemap(
        labels=segment_df["Customer_Segment"],
        parents=[""] * len(segment_df),
        values=segment_df["Revenue"]
    ),
    row=2, col=2
)

# Monthly trend
monthly_df = df.groupby("Month")["Revenue"].sum().reset_index()
fig.add_trace(
    go.Scatter(
        x=monthly_df["Month"],
        y=monthly_df["Revenue"],
        mode="lines+markers",
        name="Revenue"
    ),
    row=3, col=1
)

# Funnel
fig.add_trace(
    go.Funnel(
        y=["Impressions", "Clicks", "Leads", "Conversions"],
        x=[
            df["Impressions"].sum(),
            df["Clicks"].sum(),
            df["Leads"].sum(),
            df["Conversions"].sum()
        ]
    ),
    row=3, col=2
)

fig.update_layout(
    height=1200,
    width=1600,
    template="plotly_dark",
    title={"text": "NYKAA MARKETING ANALYTICS DASHBOARD", "x": 0.5},
    showlegend=False
)

# Revenue by Campaign Type (separate chart)
px.bar(
    df.groupby("Campaign_Type")["Revenue"].sum().reset_index(),
    x="Campaign_Type",
    y="Revenue",
    color="Revenue",
    title="Revenue by Campaign Type"
).show()

fig.show()

# =========================
# SUNBURST CHART
# =========================

px.sunburst(
    df,
    path=["Channel_Used", "Campaign_Type", "Customer_Segment"],
    values="Revenue"
).show()
