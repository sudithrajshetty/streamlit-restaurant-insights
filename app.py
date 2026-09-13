
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# PAGE
# =========================================================
st.set_page_config(
    page_title="NEXUS | Restaurant Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# GLOBAL CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

.stApp {
    background:
        radial-gradient(circle at 10% 5%, rgba(0,245,200,.10), transparent 25%),
        radial-gradient(circle at 90% 5%, rgba(120,70,255,.12), transparent 28%),
        #05070d;
    color: #edf4ff;
}

.block-container {
    max-width: 1850px;
    padding: 1.2rem 2rem 2rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080c15 0%, #05070d 100%);
    border-right: 1px solid rgba(0,245,200,.16);
}

section[data-testid="stSidebar"] h3 {
    font-family: "Space Mono", monospace;
    color: #00f5c8;
}

/* Hero */
.nexus-hero {
    padding: 25px 28px;
    border: 1px solid rgba(0,245,200,.24);
    border-radius: 22px;
    background:
        linear-gradient(115deg, rgba(0,245,200,.08), rgba(115,75,255,.09)),
        rgba(8,12,20,.78);
    box-shadow: 0 0 45px rgba(0,245,200,.06);
    margin-bottom: 18px;
}

.nexus-kicker {
    color: #00f5c8;
    font-family: "Space Mono", monospace;
    font-size: 12px;
    letter-spacing: 2px;
    font-weight: 700;
}

.nexus-title {
    font-family: Inter, sans-serif;
    font-size: 38px;
    line-height: 1.1;
    font-weight: 800;
    margin: 7px 0 8px;
}

.nexus-subtitle {
    color: #8e9ab2;
    font-size: 15px;
    margin: 0;
}

/* KPI cards */
.kpi {
    padding: 19px 20px;
    min-height: 125px;
    border-radius: 17px;
    border: 1px solid rgba(255,255,255,.08);
    background: linear-gradient(145deg, rgba(15,21,34,.96), rgba(8,12,20,.94));
    box-shadow: 0 10px 35px rgba(0,0,0,.20);
}

.kpi-label {
    color: #8995ab;
    font-family: "Space Mono", monospace;
    font-size: 11px;
    letter-spacing: 1.2px;
}

.kpi-value {
    font-size: 29px;
    font-weight: 800;
    margin-top: 9px;
}

.kpi-sub {
    color: #00f5c8;
    font-family: "Space Mono", monospace;
    font-size: 10px;
    margin-top: 6px;
}

/* Section headers */
.section-title {
    margin: 26px 0 11px;
    color: #00f5c8;
    font-family: "Space Mono", monospace;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.7px;
}

/* Insight cards */
.insight {
    border: 1px solid rgba(0,245,200,.14);
    border-radius: 15px;
    background: rgba(10,15,25,.88);
    padding: 16px 18px;
    min-height: 115px;
}

.insight-head {
    color: #00f5c8;
    font-family: "Space Mono", monospace;
    font-size: 10px;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.insight-text {
    color: #dbe6f7;
    font-size: 13px;
    line-height: 1.55;
}

/* Filter boxes */
.filter-info {
    border: 1px solid rgba(0,245,200,.13);
    border-radius: 12px;
    padding: 11px;
    margin: 10px 0 15px;
    background: rgba(0,245,200,.035);
    color: #8e9ab2;
    font-family: "Space Mono", monospace;
    font-size: 10px;
}

/* Streamlit widgets */
.stButton button {
    width: 100%;
    border: 1px solid rgba(0,245,200,.25);
    background: rgba(0,245,200,.045);
    color: #00f5c8;
    border-radius: 10px;
}

.stButton button:hover {
    border-color: #00f5c8;
    color: #ffffff;
}

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(0,245,200,.12);
    border-radius: 14px;
}

/* Hide menu/footer for cleaner app */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA
# =========================================================
@st.cache_data
def load_data():
    data = pd.read_csv("restaurants.csv")

    # Standardize column names
    data.columns = [
        str(c).strip().replace(" ", "_")
        for c in data.columns
    ]

    # Common alternative column names
    rename_map = {}

    for c in data.columns:
        low = c.lower()
        if low in ["restaurant_name", "restaurant"]:
            rename_map[c] = "Name"
        elif low in ["city_name"]:
            rename_map[c] = "City"
        elif low in ["rating", "ratings"]:
            rename_map[c] = "Rating"
        elif low in ["votes", "vote"]:
            rename_map[c] = "Votes"
        elif low in ["cost", "average_cost", "average_cost_for_two", "cost_for_two"]:
            rename_map[c] = "Cost"
        elif low in ["cuisines", "cuisine_type"]:
            rename_map[c] = "Cuisine"
        elif low in ["locality", "area", "location_name"]:
            rename_map[c] = "Locality"

    data = data.rename(columns=rename_map)

    required = ["Name", "City", "Cuisine", "Rating", "Votes", "Cost"]

    for col in required:
        if col not in data.columns:
            data[col] = 0 if col in ["Rating", "Votes", "Cost"] else "Unknown"

    if "Locality" not in data.columns:
        data["Locality"] = "Unknown"

    # Clean numeric columns
    for col in ["Rating", "Votes", "Cost"]:
        data[col] = (
            data[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.extract(r"([-+]?\d*\.?\d+)")[0]
        )
        data[col] = pd.to_numeric(data[col], errors="coerce")

    # Clean text
    for col in ["Name", "City", "Cuisine", "Locality"]:
        data[col] = (
            data[col]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

    data["Votes"] = data["Votes"].fillna(0)

    # Valid ratings/cost
    data = data[
        data["Rating"].notna() &
        data["Cost"].notna()
    ].copy()

    # Keep realistic rating values
    data = data[
        (data["Rating"] >= 0) &
        (data["Rating"] <= 5)
    ].copy()

    return data


df = load_data()


# =========================================================
# HELPERS
# =========================================================
def chart_style(fig, height=390):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter",
            color="#dbe6f7"
        ),
        title_font=dict(
            family="Inter",
            size=15,
            color="#edf4ff"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)"
        ),
        hoverlabel=dict(
            bgcolor="#101722",
            font_color="#ffffff"
        )
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,.055)",
        zeroline=False
    )
    return fig


def money(v):
    return f"₹{v:,.0f}"


# =========================================================
# SIDEBAR / FILTERS
# =========================================================
st.sidebar.markdown("### ◈ NEXUS CONTROL")
st.sidebar.caption("FILTER MATRIX / DATA EXPLORER")

st.sidebar.markdown(
    '<div class="filter-info">Adjust the matrix to change every KPI, chart and insight.</div>',
    unsafe_allow_html=True
)

cities = sorted(df["City"].dropna().unique().tolist())

# Search first
search = st.sidebar.text_input(
    "SEARCH",
    placeholder="Restaurant / cuisine / locality"
)

# City
selected_cities = st.sidebar.multiselect(
    "CITY",
    cities,
    default=cities[:8] if len(cities) > 8 else cities
)

# Cuisine
all_cuisines = (
    df["Cuisine"]
    .str.split(", ")
    .explode()
    .dropna()
    .str.strip()
    .replace("", "Unknown")
    .unique()
    .tolist()
)

all_cuisines = sorted(all_cuisines)

selected_cuisines = st.sidebar.multiselect(
    "CUISINE",
    all_cuisines,
    default=[]
)

# Rating
rating_range = st.sidebar.slider(
    "RATING",
    0.0,
    5.0,
    (3.0, 5.0),
    0.1
)

# Cost
min_cost = int(max(0, df["Cost"].min()))
max_cost = int(max(min_cost, df["Cost"].max()))

if min_cost < max_cost:
    cost_range = st.sidebar.slider(
        "COST FOR TWO",
        min_cost,
        max_cost,
        (
            int(df["Cost"].quantile(.05)),
            int(df["Cost"].quantile(.95))
        )
    )
else:
    cost_range = (min_cost, max_cost)

# Votes
max_votes = int(max(0, df["Votes"].max()))

if max_votes > 0:
    min_votes = st.sidebar.number_input(
        "MINIMUM VOTES",
        min_value=0,
        max_value=max_votes,
        value=0,
        step=max(1, max_votes // 100)
    )
else:
    min_votes = 0

# Optional filters
available_optional = {}

for col in df.columns:
    low = col.lower()

    if "online" in low and ("deliver" in low or "order" in low):
        available_optional[col] = "ONLINE DELIVERY"

    if "book" in low and "table" in low:
        available_optional[col] = "TABLE BOOKING"


for col, label in available_optional.items():
    options = df[col].dropna().astype(str).unique().tolist()

    if len(options) <= 10:
        st.sidebar.multiselect(
            label,
            sorted(options),
            default=[],
            key=f"optional_{col}"
        )

if st.sidebar.button("↻ RESET FILTERS"):
    st.rerun()


# =========================================================
# APPLY FILTERS
# =========================================================
filtered = df.copy()

if selected_cities:
    filtered = filtered[
        filtered["City"].isin(selected_cities)
    ]

if selected_cuisines:
    cuisine_mask = filtered["Cuisine"].apply(
        lambda x: any(
            c.strip() in selected_cuisines
            for c in str(x).split(",")
        )
    )
    filtered = filtered[cuisine_mask]

filtered = filtered[
    filtered["Rating"].between(
        rating_range[0],
        rating_range[1]
    )
]

filtered = filtered[
    filtered["Cost"].between(
        cost_range[0],
        cost_range[1]
    )
]

filtered = filtered[
    filtered["Votes"] >= min_votes
]

if search:
    text_mask = (
        filtered["Name"].str.contains(
            search, case=False, na=False
        )
        |
        filtered["Cuisine"].str.contains(
            search, case=False, na=False
        )
        |
        filtered["Locality"].str.contains(
            search, case=False, na=False
        )
        |
        filtered["City"].str.contains(
            search, case=False, na=False
        )
    )
    filtered = filtered[text_mask]


# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="nexus-hero">
    <div class="nexus-kicker">◈ NEXUS / LIVE ANALYTICS CORE</div>
    <div class="nexus-title">Restaurant Intelligence Dashboard</div>
    <p class="nexus-subtitle">
        Discover market patterns, customer demand, cuisine clusters,
        restaurant quality and value opportunities.
    </p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# EMPTY STATE
# =========================================================
if filtered.empty:
    st.error("No restaurants match the current filter matrix.")
    st.info("Try expanding the rating/cost range or selecting more cities.")
    st.stop()


# =========================================================
# KPI
# =========================================================
restaurant_count = len(filtered)
avg_rating = filtered["Rating"].mean()
total_votes = filtered["Votes"].sum()
city_count = filtered["City"].nunique()

kpi_cols = st.columns(4)

kpi_data = [
    ("RESTAURANTS", f"{restaurant_count:,}", "FILTERED NODES"),
    ("AVG RATING", f"{avg_rating:.2f} / 5", "QUALITY INDEX"),
    ("TOTAL VOTES", f"{total_votes:,.0f}", "CUSTOMER SIGNAL"),
    ("CITIES", f"{city_count:,}", "ACTIVE MARKETS")
]

for col, (label, value, sub) in zip(kpi_cols, kpi_data):
    col.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">● {sub}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# INSIGHTS
# =========================================================
st.markdown(
    '<div class="section-title">01 // AI-STYLE MARKET INSIGHTS</div>',
    unsafe_allow_html=True
)

best_rated = filtered.loc[
    filtered["Rating"].idxmax()
]

most_voted = filtered.loc[
    filtered["Votes"].idxmax()
]

best_value_df = filtered.copy()

best_value_df["ValueScore"] = (
    best_value_df["Rating"] /
    best_value_df["Cost"].replace(0, 1)
)

best_value = best_value_df.loc[
    best_value_df["ValueScore"].idxmax()
]

top_city_series = (
    filtered.groupby("City")
    .size()
    .sort_values(ascending=False)
)

top_city = (
    top_city_series.index[0]
    if len(top_city_series)
    else "N/A"
)

top_city_count = (
    int(top_city_series.iloc[0])
    if len(top_city_series)
    else 0
)

cuisine_counts = (
    filtered["Cuisine"]
    .str.split(", ")
    .explode()
    .value_counts()
)

top_cuisine = (
    cuisine_counts.index[0]
    if len(cuisine_counts)
    else "N/A"
)

top_cuisine_count = (
    int(cuisine_counts.iloc[0])
    if len(cuisine_counts)
    else 0
)

insight_cols = st.columns(4)

insights = [
    (
        "★ TOP QUALITY",
        f"{best_rated['Name']} leads with a "
        f"{best_rated['Rating']:.1f}/5 rating in "
        f"{best_rated['City']}."
    ),
    (
        "◉ DEMAND LEADER",
        f"{most_voted['Name']} has the strongest "
        f"customer signal with {most_voted['Votes']:,.0f} votes."
    ),
    (
        "◇ VALUE PICK",
        f"{best_value['Name']} combines "
        f"{best_value['Rating']:.1f}/5 with a "
        f"{money(best_value['Cost'])} cost for two."
    ),
    (
        "⌁ MARKET CLUSTER",
        f"{top_city} has the highest restaurant density "
        f"with {top_city_count:,} restaurants. "
        f"{top_cuisine} is the leading cuisine cluster."
    )
]

for col, (head, text) in zip(insight_cols, insights):
    col.markdown(
        f"""
        <div class="insight">
            <div class="insight-head">{head}</div>
            <div class="insight-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# MARKET SIGNALS
# =========================================================
st.markdown(
    '<div class="section-title">02 // MARKET SIGNALS</div>',
    unsafe_allow_html=True
)

left, right = st.columns(2)

# City density
with left:

    city_data = (
        filtered
        .groupby("City", as_index=False)
        .agg(
            Restaurants=("Name", "count"),
            Votes=("Votes", "sum"),
            Avg_Rating=("Rating", "mean")
        )
        .sort_values(
            "Restaurants",
            ascending=False
        )
        .head(12)
        .sort_values("Restaurants")
    )

    fig = px.bar(
        city_data,
        x="Restaurants",
        y="City",
        orientation="h",
        title="Restaurant Density by City",
        hover_data={
            "Restaurants": True,
            "Votes": ":,.0f",
            "Avg_Rating": ":.2f"
        }
    )

    fig.update_traces(marker_line_width=0)

    st.plotly_chart(
        chart_style(fig, 420),
        use_container_width=True
    )


# Cost vs Rating
with right:

    sample = filtered.sample(
        min(len(filtered), 3000),
        random_state=42
    )

    fig = px.scatter(
        sample,
        x="Cost",
        y="Rating",
        size="Votes",
        hover_name="Name",
        hover_data=[
            "City",
            "Cuisine",
            "Locality"
        ],
        title="Value Map — Cost vs Rating",
        opacity=.65
    )

    fig.update_xaxes(
        title="Cost for Two"
    )

    fig.update_yaxes(
        title="Rating"
    )

    st.plotly_chart(
        chart_style(fig, 420),
        use_container_width=True
    )


# =========================================================
# CUISINE ANALYSIS
# =========================================================
st.markdown(
    '<div class="section-title">03 // CUISINE NETWORK</div>',
    unsafe_allow_html=True
)

left, right = st.columns([1.15, .85])

with left:

    cuisine_data = (
        filtered
        .assign(
            Cuisine=filtered["Cuisine"].str.split(", ")
        )
        .explode("Cuisine")
    )

    cuisine_data["Cuisine"] = (
        cuisine_data["Cuisine"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    cuisine_summary = (
        cuisine_data
        .groupby("Cuisine", as_index=False)
        .agg(
            Restaurants=("Name", "count"),
            Votes=("Votes", "sum"),
            Avg_Rating=("Rating", "mean")
        )
        .sort_values(
            "Restaurants",
            ascending=False
        )
        .head(15)
        .sort_values("Restaurants")
    )

    fig = px.bar(
        cuisine_summary,
        x="Restaurants",
        y="Cuisine",
        orientation="h",
        title="Top Cuisine Clusters",
        hover_data={
            "Restaurants": True,
            "Votes": ":,.0f",
            "Avg_Rating": ":.2f"
        }
    )

    st.plotly_chart(
        chart_style(fig, 430),
        use_container_width=True
    )


with right:

    # FIX: explicit string labels avoid pandas Interval JSON error
    rating_bins = pd.cut(
        filtered["Rating"],
        bins=[0, 3, 3.5, 4, 4.5, 5],
        labels=[
            "0–3",
            "3–3.5",
            "3.5–4",
            "4–4.5",
            "4.5–5"
        ],
        include_lowest=True
    )

    rating_dist = (
        rating_bins
        .value_counts()
        .sort_index()
        .reset_index()
    )

    rating_dist.columns = [
        "Rating Band",
        "Restaurants"
    ]

    rating_dist["Rating Band"] = (
        rating_dist["Rating Band"]
        .astype(str)
    )

    fig = px.pie(
        rating_dist,
        names="Rating Band",
        values="Restaurants",
        hole=.60,
        title="Rating Distribution"
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent"
    )

    st.plotly_chart(
        chart_style(fig, 430),
        use_container_width=True
    )


# =========================================================
# AFFORDABILITY ANALYSIS
# =========================================================
st.markdown(
    '<div class="section-title">04 // AFFORDABILITY INTELLIGENCE</div>',
    unsafe_allow_html=True
)

a, b = st.columns(2)

with a:

    cost_data = (
        filtered
        .assign(
            Cost_Band=pd.cut(
                filtered["Cost"],
                bins=6,
                duplicates="drop"
            )
        )
        .groupby("Cost_Band", observed=True)
        .agg(
            Restaurants=("Name", "count"),
            Avg_Rating=("Rating", "mean")
        )
        .reset_index()
    )

    # Convert intervals to strings before Plotly
    cost_data["Cost_Band"] = (
        cost_data["Cost_Band"]
        .astype(str)
    )

    fig = px.bar(
        cost_data,
        x="Cost_Band",
        y="Restaurants",
        title="Restaurants by Cost Segment",
        hover_data={
            "Avg_Rating": ":.2f"
        }
    )

    st.plotly_chart(
        chart_style(fig, 390),
        use_container_width=True
    )


with b:

    city_value = (
        filtered
        .groupby("City", as_index=False)
        .agg(
            Avg_Cost=("Cost", "mean"),
            Avg_Rating=("Rating", "mean"),
            Restaurants=("Name", "count")
        )
        .sort_values(
            "Restaurants",
            ascending=False
        )
        .head(12)
    )

    fig = px.scatter(
        city_value,
        x="Avg_Cost",
        y="Avg_Rating",
        size="Restaurants",
        text="City",
        title="City Quality vs Affordability"
    )

    fig.update_traces(
        textposition="top center"
    )

    st.plotly_chart(
        chart_style(fig, 390),
        use_container_width=True
    )


# =========================================================
# TOP RESTAURANTS
# =========================================================
st.markdown(
    '<div class="section-title">05 // HIGH-VALUE NODES</div>',
    unsafe_allow_html=True
)

top = (
    filtered
    .sort_values(
        ["Rating", "Votes"],
        ascending=[False, False]
    )
    .head(20)
    [
        [
            "Name",
            "City",
            "Locality",
            "Cuisine",
            "Rating",
            "Votes",
            "Cost"
        ]
    ]
    .copy()
)

top.columns = [
    "Restaurant",
    "City",
    "Locality",
    "Cuisine",
    "Rating",
    "Votes",
    "Cost / 2"
]

st.dataframe(
    top,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DOWNLOAD FILTERED DATA
# =========================================================
csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ DOWNLOAD FILTERED DATA",
    data=csv_data,
    file_name="nexus_filtered_restaurants.csv",
    mime="text/csv"
)


# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div style="
    margin-top:25px;
    padding:16px 18px;
    border-top:1px solid rgba(255,255,255,.07);
    color:#66738a;
    font-family:'Space Mono',monospace;
    font-size:10px;
    letter-spacing:.5px;
">
    NEXUS CORE • RESTAURANT INTELLIGENCE • STREAMLIT + PLOTLY
    • FILTERS ACTIVE • INSIGHTS GENERATED FROM CURRENT DATA
</div>
""", unsafe_allow_html=True)
