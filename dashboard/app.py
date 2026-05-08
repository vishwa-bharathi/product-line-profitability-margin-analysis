import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nassau Candy | Margin Intelligence",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Dark premium background */
.stApp {
    background: #0d0f14;
    color: #e8eaf0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #13151c !important;
    border-right: 1px solid #1e2130;
}
[data-testid="stSidebar"] * { color: #c8cad4 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stDateInput label { color: #6b7280 !important; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; }

/* Header strip */
.brand-header {
    display: flex; align-items: center; gap: 16px;
    padding: 28px 0 20px 0;
    border-bottom: 1px solid #1e2130;
    margin-bottom: 28px;
}
.brand-title {
    font-family: 'Syne', sans-serif;
    font-size: 26px; font-weight: 800;
    color: #f5f6fa; letter-spacing: -0.5px;
}
.brand-sub {
    font-size: 12px; color: #4b5268;
    letter-spacing: 0.12em; text-transform: uppercase;
    margin-top: 2px;
}

/* KPI Cards */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 28px; }
.kpi-card {
    background: #13151c;
    border: 1px solid #1e2130;
    border-radius: 12px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.kpi-card.green::before  { background: linear-gradient(90deg, #10b981, #34d399); }
.kpi-card.blue::before   { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.kpi-card.amber::before  { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.kpi-card.rose::before   { background: linear-gradient(90deg, #f43f5e, #fb7185); }
.kpi-label { font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: #4b5268; margin-bottom: 8px; }
.kpi-value { font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 700; color: #f5f6fa; }
.kpi-delta { font-size: 11px; color: #6b7280; margin-top: 4px; }

/* Section headers */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 15px; font-weight: 700;
    color: #f5f6fa; letter-spacing: 0.02em;
    margin: 24px 0 14px 0;
    display: flex; align-items: center; gap: 8px;
}
.section-title span.dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #3b82f6; display: inline-block;
}

/* Risk badge */
.risk-high   { background: #2d1216; color: #f87171; border: 1px solid #7f1d1d; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
.risk-medium { background: #2d2007; color: #fbbf24; border: 1px solid #78350f; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
.risk-ok     { background: #052e16; color: #4ade80; border: 1px solid #14532d; padding: 2px 8px; border-radius: 4px; font-size: 11px; }

/* Plotly chart containers */
.stPlotlyChart { border-radius: 12px; overflow: hidden; }

/* Dataframe */
.stDataFrame { border-radius: 10px; overflow: hidden; }
.stDataFrame table { background: #13151c !important; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] { background: #13151c; border-radius: 10px; padding: 4px; gap: 2px; }
.stTabs [data-baseweb="tab"] {
    background: transparent; color: #6b7280;
    border-radius: 8px; padding: 8px 20px;
    font-size: 13px; font-family: 'DM Sans', sans-serif;
}
.stTabs [aria-selected="true"] { background: #1e2130 !important; color: #f5f6fa !important; }

/* Search box */
.stTextInput input {
    background: #13151c; border: 1px solid #1e2130;
    color: #f5f6fa; border-radius: 8px;
}

/* Metric delta override */
[data-testid="stMetricDelta"] { font-size: 12px; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #1e2130; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Plotly dark theme defaults ─────────────────────────────────────────────────
PLOT_BG   = "#13151c"
GRID_CLR  = "#1e2130"
FONT_CLR  = "#9ca3af"
AXIS_CLR  = "#374151"
PALETTE   = ["#3b82f6","#10b981","#f59e0b","#f43f5e","#8b5cf6","#06b6d4","#ec4899"]

def dark_layout(fig, title="", height=340):
    fig.update_layout(
        title=dict(text=title, font=dict(family="Syne", size=14, color="#f5f6fa"), x=0, pad=dict(l=4)),
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="DM Sans", color=FONT_CLR, size=11),
        height=height,
        margin=dict(l=16, r=16, t=40, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID_CLR, font=dict(size=11)),
        xaxis=dict(gridcolor=GRID_CLR, linecolor=AXIS_CLR, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRID_CLR, linecolor=AXIS_CLR, tickfont=dict(size=10)),
    )
    return fig

# ── Data loading & processing ──────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_data.csv")
    df.columns = df.columns.str.replace(" ", "_").str.lower()
    df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=True, errors = "coerce")
    df["ship_date"]  = pd.to_datetime(df["ship_date"],  dayfirst=True, errors = "coerce")

    # KPI columns
    df["calculated_profit"] = (df["sales"] - df["cost"]).round(2)
    df["calculated_margin"] = (df["calculated_profit"] / df["sales"]).round(4)
    df["profit_per_unit"]   = (df["calculated_profit"] / df["units"]).round(2)
    df["month"] = df["order_date"].dt.to_period("M")
    return df

df = load_data()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🍬 Nassau Candy")
    st.markdown("---")

    st.markdown("**DATE RANGE**")
    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()
    date_range = st.date_input("", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    st.markdown("**DIVISION**")
    divisions = ["All"] + sorted(df["division"].unique().tolist())
    sel_division = st.selectbox("", divisions)

    st.markdown("**MARGIN THRESHOLD**")
    margin_thresh = st.slider("Flag products below (%)", 0, 100, 50, step=5) / 100

    st.markdown("**PRODUCT SEARCH**")
    search_q = st.text_input("", placeholder="e.g. Wonka Bar...")

    st.markdown("---")
    st.caption("Nassau Candy Distributor\nMargin Intelligence v1.0")

# ── Apply filters ──────────────────────────────────────────────────────────────
if len(date_range) == 2:
    start_d, end_d = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    df_f = df[(df["order_date"] >= start_d) & (df["order_date"] <= end_d)]
else:
    df_f = df.copy()

if sel_division != "All":
    df_f = df_f[df_f["division"] == sel_division]

if search_q:
    df_f = df_f[df_f["product_name"].str.contains(search_q, case=False, na=False)]

# ── Aggregations ───────────────────────────────────────────────────────────────
total_sales  = df_f["sales"].sum()
total_profit = df_f["calculated_profit"].sum()
overall_margin = total_profit / total_sales if total_sales > 0 else 0
total_units  = df_f["units"].sum()

product_summary = df_f.groupby("product_name").agg(
    total_sales   = ("sales",              "sum"),
    total_profit  = ("calculated_profit",  "sum"),
    total_cost    = ("cost",               "sum"),
    total_units   = ("units",              "sum"),
).reset_index()
product_summary["gross_margin"]          = (product_summary["total_profit"] / product_summary["total_sales"]).round(4)
product_summary["profit_per_unit"]       = (product_summary["total_profit"] / product_summary["total_units"]).round(2)
product_summary["revenue_contribution"]  = (product_summary["total_sales"]  / product_summary["total_sales"].sum()).round(4)
product_summary["profit_contribution_%"] = (product_summary["total_profit"] / product_summary["total_profit"].sum() * 100).round(2)
product_summary["cost_ratio"]            = (product_summary["total_cost"]   / product_summary["total_sales"]).round(3)
product_summary = product_summary.sort_values("total_profit", ascending=False)

division_summary = df_f.groupby("division").agg(
    total_sales  = ("sales",             "sum"),
    total_profit = ("calculated_profit", "sum"),
).reset_index()
division_summary["avg_margin"] = (division_summary["total_profit"] / division_summary["total_sales"]).round(4)

# Pareto
pareto_df = product_summary.sort_values("total_profit", ascending=False).reset_index(drop=True)
pareto_df["cumulative_profit_%"] = (pareto_df["total_profit"].cumsum() / pareto_df["total_profit"].sum() * 100).round(2)

# Low margin flags
low_margin = product_summary[product_summary["gross_margin"] < margin_thresh].sort_values("gross_margin")

# Margin volatility
monthly_margin = df_f.groupby("month")["calculated_margin"].mean()
margin_vol = monthly_margin.std()

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
  <div>
    <div class="brand-title">🍬 Nassau Candy Distributor</div>
    <div class="brand-sub">Product Line Profitability & Margin Intelligence Dashboard</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card green">
    <div class="kpi-label">Total Revenue</div>
    <div class="kpi-value">${total_sales:,.0f}</div>
    <div class="kpi-delta">{len(df_f):,} orders in period</div>
  </div>
  <div class="kpi-card blue">
    <div class="kpi-label">Gross Profit</div>
    <div class="kpi-value">${total_profit:,.0f}</div>
    <div class="kpi-delta">After cost of goods</div>
  </div>
  <div class="kpi-card amber">
    <div class="kpi-label">Overall Margin</div>
    <div class="kpi-value">{overall_margin*100:.1f}%</div>
    <div class="kpi-delta">Profit ÷ Revenue</div>
  </div>
  <div class="kpi-card rose">
    <div class="kpi-label">Margin Volatility</div>
    <div class="kpi-value">{margin_vol*100:.2f}%</div>
    <div class="kpi-delta">Std dev across months</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Product Profitability",
    "🏢 Division Performance",
    "⚠️ Cost & Margin Diagnostics",
    "📈 Profit Concentration"
])

# ══════════════════════════════════════════════════════════════════════
# TAB 1 — PRODUCT PROFITABILITY
# ══════════════════════════════════════════════════════════════════════
with tab1:
    col_l, col_r = st.columns([3, 2], gap="medium")

    with col_l:
        st.markdown('<div class="section-title"><span class="dot"></span>Total Profit by Product</div>', unsafe_allow_html=True)
        top_n = product_summary.head(15).sort_values("total_profit")
        fig = go.Figure(go.Bar(
            x=top_n["total_profit"],
            y=top_n["product_name"],
            orientation="h",
            marker=dict(
                color=top_n["total_profit"],
                colorscale=[[0,"#1e3a5f"],[0.5,"#3b82f6"],[1,"#93c5fd"]],
                line=dict(width=0)
            ),
            text=top_n["total_profit"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=10, color="#9ca3af"),
        ))
        dark_layout(fig, height=380)
        fig.update_layout(xaxis_title="Gross Profit ($)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title"><span class="dot"></span>Profit Contribution Share</div>', unsafe_allow_html=True)
        pie_df = product_summary[product_summary["profit_contribution_%"] >= 1].copy()
        other_val = product_summary[product_summary["profit_contribution_%"] < 1]["profit_contribution_%"].sum()
        if other_val > 0:
            pie_df = pd.concat([pie_df, pd.DataFrame([{"product_name":"Other","profit_contribution_%":other_val}])], ignore_index=True)
        fig2 = go.Figure(go.Pie(
            labels=pie_df["product_name"],
            values=pie_df["profit_contribution_%"],
            hole=0.55,
            marker=dict(colors=PALETTE, line=dict(color=PLOT_BG, width=2)),
            textinfo="label+percent",
            textfont=dict(size=10),
        ))
        dark_layout(fig2, height=380)
        fig2.update_layout(showlegend=False)
        fig2.add_annotation(text=f"${total_profit:,.0f}", x=0.5, y=0.55, font=dict(family="Syne", size=16, color="#f5f6fa"), showarrow=False)
        fig2.add_annotation(text="Total Profit", x=0.5, y=0.42, font=dict(size=10, color="#6b7280"), showarrow=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title"><span class="dot"></span>Product Margin Leaderboard</div>', unsafe_allow_html=True)
    display_cols = ["product_name","total_sales","total_profit","gross_margin","profit_per_unit","revenue_contribution","profit_contribution_%"]
    display_df = product_summary[display_cols].copy()
    display_df["gross_margin"]         = (display_df["gross_margin"] * 100).round(1).astype(str) + "%"
    display_df["revenue_contribution"] = (display_df["revenue_contribution"] * 100).round(1).astype(str) + "%"
    display_df["total_sales"]          = display_df["total_sales"].apply(lambda v: f"${v:,.2f}")
    display_df["total_profit"]         = display_df["total_profit"].apply(lambda v: f"${v:,.2f}")
    display_df.columns = ["Product","Revenue","Profit","Gross Margin","Profit/Unit","Rev Contrib","Profit Contrib %"]
    st.dataframe(display_df.reset_index(drop=True), use_container_width=True, height=320)

# ══════════════════════════════════════════════════════════════════════
# TAB 2 — DIVISION PERFORMANCE
# ══════════════════════════════════════════════════════════════════════
with tab2:
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown('<div class="section-title"><span class="dot"></span>Revenue vs Profit by Division</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Revenue", x=division_summary["division"], y=division_summary["total_sales"],
                             marker_color="#3b82f6", text=division_summary["total_sales"].apply(lambda v: f"${v:,.0f}"),
                             textposition="outside", textfont=dict(size=10)))
        fig.add_trace(go.Bar(name="Profit",  x=division_summary["division"], y=division_summary["total_profit"],
                             marker_color="#10b981", text=division_summary["total_profit"].apply(lambda v: f"${v:,.0f}"),
                             textposition="outside", textfont=dict(size=10)))
        fig.update_layout(barmode="group")
        dark_layout(fig, height=340)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title"><span class="dot"></span>Average Margin by Division</div>', unsafe_allow_html=True)
        colors = ["#10b981" if m >= 0.6 else "#f59e0b" if m >= 0.45 else "#f43f5e" for m in division_summary["avg_margin"]]
        fig2 = go.Figure(go.Bar(
            x=division_summary["division"],
            y=division_summary["avg_margin"] * 100,
            marker_color=colors,
            text=(division_summary["avg_margin"]*100).apply(lambda v: f"{v:.1f}%"),
            textposition="outside", textfont=dict(size=12, color="#f5f6fa"),
        ))
        dark_layout(fig2, height=340)
        fig2.update_layout(yaxis_title="Avg Gross Margin (%)", yaxis_range=[0, 100])
        fig2.add_hline(y=50, line_dash="dash", line_color="#f43f5e", annotation_text="50% threshold", annotation_font_size=10)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title"><span class="dot"></span>Division Summary</div>', unsafe_allow_html=True)
    div_display = division_summary.copy()
    div_display["total_sales"]  = div_display["total_sales"].apply(lambda v: f"${v:,.2f}")
    div_display["total_profit"] = div_display["total_profit"].apply(lambda v: f"${v:,.2f}")
    div_display["avg_margin"]   = (div_display["avg_margin"]*100).round(1).astype(str) + "%"
    div_display.columns = ["Division","Total Revenue","Total Profit","Avg Gross Margin"]
    st.dataframe(div_display.reset_index(drop=True), use_container_width=True)

    # Margin by division over time
    st.markdown('<div class="section-title"><span class="dot"></span>Margin Trend by Division</div>', unsafe_allow_html=True)
    monthly_div = df_f.groupby(["division", df_f["order_date"].dt.to_period("M")])["calculated_margin"].mean().reset_index()
    monthly_div["order_date"] = monthly_div["order_date"].astype(str)
    fig3 = px.line(monthly_div, x="order_date", y="calculated_margin", color="division",
                   color_discrete_sequence=PALETTE, markers=False)
    dark_layout(fig3, height=300)
    fig3.update_layout(xaxis_title="Month", yaxis_title="Avg Margin", yaxis_tickformat=".0%")
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 3 — COST & MARGIN DIAGNOSTICS
# ══════════════════════════════════════════════════════════════════════
with tab3:
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown('<div class="section-title"><span class="dot"></span>Cost vs Sales Scatter</div>', unsafe_allow_html=True)
        scatter_df = product_summary.copy()
        scatter_df["margin_pct"] = (scatter_df["gross_margin"] * 100).round(1)
        scatter_df["risk"] = scatter_df["gross_margin"].apply(
            lambda m: "High Risk" if m < 0.40 else ("Watch" if m < margin_thresh else "Healthy"))
        color_map = {"High Risk":"#f43f5e","Watch":"#f59e0b","Healthy":"#10b981"}
        fig = px.scatter(scatter_df, x="total_sales", y="total_cost",
                         size="total_profit", color="risk", color_discrete_map=color_map,
                         hover_name="product_name",
                         hover_data={"total_sales":":,.2f","total_cost":":,.2f","margin_pct":":.1f","risk":True,"total_profit":False},
                         size_max=40)
        # diagonal line (cost = sales)
        max_v = max(scatter_df["total_sales"].max(), scatter_df["total_cost"].max())
        fig.add_trace(go.Scatter(x=[0, max_v], y=[0, max_v], mode="lines",
                                 line=dict(dash="dash", color="#4b5268", width=1),
                                 showlegend=False, name="Break-even"))
        dark_layout(fig, height=380)
        fig.update_layout(xaxis_title="Total Sales ($)", yaxis_title="Total Cost ($)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title"><span class="dot"></span>Cost Ratio by Product</div>', unsafe_allow_html=True)
        cost_sorted = product_summary.sort_values("cost_ratio", ascending=False)
        bar_colors = ["#f43f5e" if r > 0.6 else "#f59e0b" if r > 0.4 else "#10b981" for r in cost_sorted["cost_ratio"]]
        fig2 = go.Figure(go.Bar(
            x=cost_sorted["product_name"],
            y=cost_sorted["cost_ratio"],
            marker_color=bar_colors,
            text=(cost_sorted["cost_ratio"]*100).apply(lambda v: f"{v:.0f}%"),
            textposition="outside", textfont=dict(size=10),
        ))
        dark_layout(fig2, height=380)
        fig2.update_layout(xaxis_tickangle=-40, yaxis_title="Cost Ratio (Cost/Sales)", yaxis_tickformat=".0%")
        fig2.add_hline(y=0.5, line_dash="dot", line_color="#f59e0b", annotation_text="50% cost", annotation_font_size=9)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f'<div class="section-title"><span class="dot"></span>⚠️ Margin Risk Flags  —  below {margin_thresh*100:.0f}% threshold</div>', unsafe_allow_html=True)
    if len(low_margin) == 0:
        st.success("✅ No products below the margin threshold.")
    else:
        for _, row in low_margin.iterrows():
            level = "High Risk" if row["gross_margin"] < 0.40 else "Watch"
            badge = f'<span class="risk-high">{level}</span>' if level == "High Risk" else f'<span class="risk-medium">{level}</span>'
            st.markdown(
                f"**{row['product_name']}** — Margin: **{row['gross_margin']*100:.1f}%** | Cost Ratio: {row['cost_ratio']*100:.0f}% | "
                f"Revenue: ${row['total_sales']:,.2f} {badge}",
                unsafe_allow_html=True,
            )

# ══════════════════════════════════════════════════════════════════════
# TAB 4 — PROFIT CONCENTRATION (PARETO)
# ══════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title"><span class="dot"></span>Pareto Analysis — Profit Concentration</div>', unsafe_allow_html=True)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=pareto_df["product_name"],
        y=pareto_df["total_profit"],
        name="Total Profit",
        marker=dict(color=pareto_df["total_profit"],
                    colorscale=[[0,"#1e3a5f"],[0.5,"#3b82f6"],[1,"#bfdbfe"]]),
        showlegend=True,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=pareto_df["product_name"],
        y=pareto_df["cumulative_profit_%"],
        name="Cumulative %",
        mode="lines+markers",
        line=dict(color="#f59e0b", width=2),
        marker=dict(size=6, color="#f59e0b"),
    ), secondary_y=True)
    fig.add_hline(y=80, secondary_y=True, line_dash="dash", line_color="#f43f5e",
                  annotation_text="80% threshold", annotation_font_size=10,
                  annotation_font_color="#f43f5e")
    fig.update_layout(paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
                      font=dict(family="DM Sans", color=FONT_CLR, size=11),
                      height=400, margin=dict(l=16,r=16,t=40,b=60),
                      legend=dict(bgcolor="rgba(0,0,0,0)"),
                      xaxis=dict(gridcolor=GRID_CLR, tickangle=-40, tickfont=dict(size=10)),
                      yaxis=dict(gridcolor=GRID_CLR, title="Gross Profit ($)"),
                      yaxis2=dict(title="Cumulative Profit %", tickformat=".0f",
                                  range=[0,110], showgrid=False))
    st.plotly_chart(fig, use_container_width=True)

    # Dependency box
    st.markdown('<div class="section-title"><span class="dot"></span>Dependency Indicators</div>', unsafe_allow_html=True)
    top80_products = pareto_df[pareto_df["cumulative_profit_%"] <= 80]
    n_top = len(top80_products)
    pct_products = n_top / len(pareto_df) * 100

    col_a, col_b, col_c = st.columns(3, gap="medium")
    with col_a:
        st.metric("Products driving 80% of profit", f"{n_top} products", f"{pct_products:.0f}% of portfolio")
    with col_b:
        top_div = division_summary.sort_values("total_profit", ascending=False).iloc[0]
        div_pct = top_div["total_profit"] / total_profit * 100
        st.metric("Top Division Dependency", top_div["division"], f"{div_pct:.1f}% of total profit")
    with col_c:
        top_prod = product_summary.iloc[0]
        prod_pct = top_prod["total_profit"] / total_profit * 100
        st.metric("Top Product Dependency", top_prod["product_name"][:20]+"…", f"{prod_pct:.1f}% of profit")

    st.markdown('<div class="section-title"><span class="dot"></span>Top Products — 80% Profit Contributors</div>', unsafe_allow_html=True)
    top80_display = top80_products[["product_name","total_sales","total_profit","gross_margin","cumulative_profit_%"]].copy()
    top80_display["gross_margin"]         = (top80_display["gross_margin"]*100).round(1).astype(str)+"%"
    top80_display["total_sales"]          = top80_display["total_sales"].apply(lambda v: f"${v:,.2f}")
    top80_display["total_profit"]         = top80_display["total_profit"].apply(lambda v: f"${v:,.2f}")
    top80_display["cumulative_profit_%"]  = top80_display["cumulative_profit_%"].astype(str)+"%"
    top80_display.columns = ["Product","Revenue","Profit","Gross Margin","Cumulative Profit %"]
    st.dataframe(top80_display.reset_index(drop=True), use_container_width=True)



    st.info("""
• 4 products generate 80% of total profit.
• Chocolate division contributes 95% of total company profit.
• Kazookles shows severe margin risk with 92% cost ratio.
• Sugar division has strongest margins but weak scale.
""")

    st.subheader("Recommended Actions")

st.markdown("""
- Reduce dependency on top 4 products.
- Review Kazookles pricing and sourcing strategy.
- Scale high-margin Sugar products.
- Improve profitability in Other division.
""")
