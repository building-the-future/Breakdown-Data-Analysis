"""
Century Plyboards — Kandla Plant Breakdown Analysis Dashboard
Run:     streamlit run breakdown_dashboard.py
Needs:   FINAL_READY_FOR_ANALYSIS.xlsx  in the same folder
Install: pip install streamlit plotly pandas openpyxl
"""

import re, warnings
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")
FILE_PATH = "FINAL_READY_FOR_ANALYSIS.xlsx"

# ── Colour palette ──────────────────────────────────────────────────────────
C_BG     = "#0D0F14"
C_SURF   = "#141820"
C_SURF2  = "#1C2230"
C_BORDER = "#252D3D"
C_ORANGE = "#F97316"
C_BLUE   = "#3B82F6"
C_GREEN  = "#22C55E"
C_RED    = "#EF4444"
C_YELLOW = "#FACC15"
C_PURPLE = "#A855F7"
C_TEAL   = "#06B6D4"
C_TEXT   = "#E2E8F0"
C_MUTED  = "#64748B"
PALETTE  = [C_ORANGE, C_BLUE, C_GREEN, C_RED, C_YELLOW,
            C_PURPLE, C_TEAL, "#FB7185", "#34D399", "#60A5FA"]


# ── Layout builder — single dict, no double-key conflicts ───────────────────
def _L(height=340, title="", margin=None, extra=None):
    m = margin or dict(l=14, r=14, t=52, b=14)
    d = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font   = dict(family="'DM Mono','Courier New',monospace",
                      color=C_TEXT, size=12),
        legend = dict(bgcolor="rgba(0,0,0,0)", bordercolor=C_BORDER,
                      font=dict(color=C_TEXT, size=11)),
        margin = m,
        height = height,
        xaxis  = dict(gridcolor=C_BORDER, linecolor=C_BORDER,
                      tickfont=dict(color=C_TEXT)),
        yaxis  = dict(gridcolor=C_BORDER, linecolor=C_BORDER,
                      tickfont=dict(color=C_TEXT)),
        colorway = PALETTE,
    )
    if title:
        d["title"] = dict(text=title, font=dict(size=14, color=C_TEXT),
                          x=0, xanchor="left")
    if extra:
        d.update(extra)
    return d


# ── Page config & CSS ───────────────────────────────────────────────────────
st.set_page_config(page_title="Century Plyboards — Kandla Plant",
                   page_icon="🏭", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html,body,[class*="css"]{{
  background:{C_BG}!important;color:{C_TEXT}!important;
  font-family:'Space Grotesk',sans-serif!important;}}
[data-testid="stSidebar"]{{background:{C_SURF}!important;
  border-right:1px solid {C_BORDER}!important;}}
[data-testid="stSidebar"] *{{color:{C_TEXT}!important;}}
header[data-testid="stHeader"]{{background:transparent!important;}}

.kpi-row{{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;}}
.kpi-card{{
  flex:1;min-width:150px;background:{C_SURF};border:1px solid {C_BORDER};
  border-radius:10px;padding:16px 18px;position:relative;overflow:hidden;}}
.kpi-card::after{{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,{C_ORANGE},transparent);}}
.kpi-label{{font-size:10px;letter-spacing:.12em;text-transform:uppercase;
  color:{C_MUTED};margin-bottom:5px;font-family:'DM Mono',monospace;}}
.kpi-value{{font-size:28px;font-weight:700;color:{C_TEXT};line-height:1;}}
.kpi-sub  {{font-size:11px;color:{C_MUTED};margin-top:4px;}}

.sec-head{{
  font-size:10px;letter-spacing:.12em;text-transform:uppercase;
  color:{C_MUTED};font-family:'DM Mono',monospace;
  display:flex;align-items:center;gap:10px;margin:26px 0 12px;}}
.sec-head::after{{content:'';flex:1;height:1px;background:{C_BORDER};}}

.page-title{{font-size:24px;font-weight:700;
  background:linear-gradient(90deg,{C_ORANGE},{C_BLUE});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  margin-bottom:2px;}}
.page-sub{{font-size:11px;color:{C_MUTED};margin-bottom:20px;
  font-family:'DM Mono',monospace;}}

.stTabs [data-baseweb="tab-list"]{{background:{C_SURF}!important;
  border-radius:8px 8px 0 0;border-bottom:1px solid {C_BORDER};gap:0;}}
.stTabs [data-baseweb="tab"]{{color:{C_MUTED}!important;font-size:12px!important;
  padding:10px 16px!important;}}
.stTabs [aria-selected="true"]{{color:{C_ORANGE}!important;
  border-bottom:2px solid {C_ORANGE}!important;}}
.stTabs [data-baseweb="tab-panel"]{{background:{C_SURF}!important;
  border:1px solid {C_BORDER};border-top:none;
  border-radius:0 0 8px 8px;padding:20px;}}
.stSelectbox>div>div,.stMultiSelect>div>div{{
  background:{C_SURF2}!important;border-color:{C_BORDER}!important;}}
::-webkit-scrollbar{{width:5px;height:5px;}}
::-webkit-scrollbar-track{{background:{C_BG};}}
::-webkit-scrollbar-thumb{{background:{C_BORDER};border-radius:3px;}}

/* Force dark mode — override Streamlit's light theme variables */
:root {{
    --background-color: {C_BG} !important;
    --secondary-background-color: {C_SURF} !important;
    --text-color: {C_TEXT} !important;
    --font: 'Space Grotesk', sans-serif !important;
}}
[data-testid="stAppViewContainer"] {{
    background-color: {C_BG} !important;
}}
[data-testid="stMain"] {{
    background-color: {C_BG} !important;
}}
[data-testid="stBottom"] {{
    background-color: {C_BG} !important;
}}
section[data-testid="stSidebarContent"] {{
    background-color: {C_SURF} !important;
}}
/* Override any white backgrounds Streamlit injects */
div[class*="block-container"] {{
    background-color: {C_BG} !important;
}}
/* Inputs, dropdowns, text areas */
input, textarea, select {{
    background-color: {C_SURF2} !important;
    color: {C_TEXT} !important;
}}

</style>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# DATA LOAD & CLEAN
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="Loading plant data…")
def load_data(path):
    df = pd.read_excel(path)

    # Dates
    df["BD Open Date"] = pd.to_datetime(df["BD Open Date"], errors="coerce")
    df = df.dropna(subset=["BD Open Date"])

    # Fault type → exactly MECHANICAL or ELECTRICAL
    df["Fault Type"] = (df["Fault Type"].astype(str).str.strip().str.upper()
        .apply(lambda x: "MECHANICAL" if "MECH" in x
               else ("ELECTRICAL" if "ELEC" in x else "MECHANICAL")))

    # Reason
    df["Reason"] = (df["Reason"].astype(str).str.strip().str.lower()
        .str.replace(r"\s+", " ", regex=True).replace("nan", "unknown"))

    # Hour from BD Open Time
    df["Hour"] = (pd.to_datetime(df["BD Open Time"],
                                 format="%H:%M:%S", errors="coerce").dt.hour)

    # Machine Group — strip all "NO <digits>" suffixes
    def _grp(name):
        s = str(name).strip().upper()
        s = re.sub(r"\s+NO[-\s]*\d+.*$", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s*-\s*\d+$", "", s)
        return re.sub(r"\s+", " ", s).strip()

    df["Machine Group"] = df["Machine Final"].apply(_grp)
    df = df[df["Machine Group"].notna() &
            (df["Machine Group"] != "") &
            (df["Machine Group"] != "NAN")]

    # Downtime
    df["Breakdown Minutes"] = (pd.to_numeric(df["Breakdown Minutes"], errors="coerce")
                                .fillna(0).clip(lower=0))
    df["Breakdown Hours"] = df["Breakdown Minutes"] / 60

    # Time helpers
    df["Month"]     = df["BD Open Date"].dt.to_period("M").astype(str)
    df["Month_dt"]  = df["BD Open Date"].dt.to_period("M").dt.to_timestamp()
    df["DayOfWeek"] = df["BD Open Date"].dt.day_name()
    df["Day"]       = df["BD Open Date"].dt.date

    return df.reset_index(drop=True)


# ═══════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def kpi(label, value, sub=""):
    return (f'<div class="kpi-card">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-sub">{sub}</div></div>')

def sec(title):
    st.markdown(f'<div class="sec-head"><span>{title}</span></div>',
                unsafe_allow_html=True)

CFG = {"displayModeBar": False}

def _o(val, max_val):   # orange cell
    a = round(float(val) / max(max_val, 1) * 0.65, 3)
    return f"background-color:rgba(249,115,22,{a});color:{C_TEXT}"

def _b(val, max_val):   # blue cell
    a = round(float(val) / max(max_val, 1) * 0.65, 3)
    return f"background-color:rgba(59,130,246,{a});color:{C_TEXT}"


# ═══════════════════════════════════════════════════════════════════════════
# PIE HELPER — always shows correct % by pre-computing text
# ═══════════════════════════════════════════════════════════════════════════
def _pie(labels, values, title, height=300, hole=0.52,
         colors=None, show_legend=True):
    values = [int(v) for v in values]
    total  = sum(values) or 1
    cols   = (colors or PALETTE)[:len(labels)]
    texts  = [f"{l}<br><b>{v:,}</b> ({v/total*100:.1f}%)"
              for l, v in zip(labels, values)]
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        text=texts, textinfo="text",
        hole=hole,
        marker=dict(colors=cols, line=dict(color=C_BG, width=2)),
        hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>",
        sort=False, direction="clockwise",
    ))
    layout = _L(height, title)
    layout["showlegend"]  = show_legend
    layout["annotations"] = [dict(text=f"<b>{total:,}</b><br>Total",
                                  x=0.5, y=0.5, showarrow=False,
                                  font=dict(size=13, color=C_TEXT))]
    fig.update_layout(**layout)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# CHART BUILDERS
# ═══════════════════════════════════════════════════════════════════════════

# ── FIXED: each month shows its OWN count and hours, not cumulative ─────────
def c_monthly_trend(df, grp_title="Plant Overview"):
    """
    Bar  = breakdown COUNT per individual month
    Line = downtime HOURS per individual month
    Both reset each month — NOT cumulative.
    """
    m = (df.groupby("Month_dt", sort=True)
           .agg(Count=("Machine Group", "count"),
                Hours=("Breakdown Hours", "sum"))
           .reset_index())
    # Ensure Hours is per-month only (groupby + sum already gives this,
    # but we explicitly verify it's not cumsum)
    m["Hours"] = m["Hours"].round(1)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=m["Month_dt"], y=m["Count"], name="BD Count / Month",
        marker=dict(color=C_ORANGE, line_width=0), opacity=.85,
        text=m["Count"], textposition="outside",
        textfont=dict(color=C_MUTED, size=10),
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=m["Month_dt"], y=m["Hours"], name="Downtime hrs / Month",
        mode="lines+markers+text",
        line=dict(color=C_BLUE, width=2.5),
        marker=dict(size=7, color=C_BLUE),
        text=m["Hours"].round(0).astype(int),
        textposition="top center",
        textfont=dict(color=C_BLUE, size=9),
    ), secondary_y=True)

    title = (f"{grp_title} — Monthly Breakdown Count & Downtime Hours"
             if grp_title != "Plant Overview"
             else "Monthly Breakdown Count & Downtime Hours  (per month)")
    layout = _L(340, title)
    fig.update_layout(**layout)
    fig.update_yaxes(title_text="BD Count / Month", secondary_y=False,
                     gridcolor=C_BORDER, tickfont=dict(color=C_TEXT),
                     rangemode="tozero")
    fig.update_yaxes(title_text="Downtime hrs / Month", secondary_y=True,
                     gridcolor=C_BORDER, tickfont=dict(color=C_TEXT),
                     showgrid=False, rangemode="tozero")
    fig.update_xaxes(tickformat="%b %Y", tickangle=-30)
    return fig


def c_fault_pie(df):
    fc = df["Fault Type"].value_counts().reset_index()
    fc.columns = ["Fault", "Count"]
    cols = [C_ORANGE if "MECH" in f else C_BLUE for f in fc["Fault"]]
    return _pie(fc["Fault"].tolist(), fc["Count"].tolist(),
                "Fault Type Split", height=310, hole=0.55,
                colors=cols, show_legend=True)


def c_monthly_fault_stacked(df):
    m = (df.groupby(["Month_dt", "Fault Type"], sort=True).size()
           .reset_index(name="Count"))
    mech = m[m["Fault Type"] == "MECHANICAL"]
    elec = m[m["Fault Type"] == "ELECTRICAL"]
    fig  = go.Figure()
    fig.add_trace(go.Bar(
        x=mech["Month_dt"], y=mech["Count"], name="MECHANICAL",
        marker=dict(color=C_ORANGE, line_width=0),
        text=mech["Count"], textposition="inside",
        textfont=dict(size=9, color="white"),
    ))
    fig.add_trace(go.Bar(
        x=elec["Month_dt"], y=elec["Count"], name="ELECTRICAL",
        marker=dict(color=C_BLUE, line_width=0),
        text=elec["Count"], textposition="inside",
        textfont=dict(size=9, color="white"),
    ))
    fig.update_layout(**_L(320, "Monthly Breakdown — Mechanical vs Electrical",
                           extra={"barmode": "stack"}))
    fig.update_xaxes(tickformat="%b %Y", tickangle=-30)
    return fig


def c_group_pie(df):
    m = (df.groupby("Machine Group").size()
           .reset_index(name="Count")
           .sort_values("Count", ascending=False))
    top  = m.head(10).copy()
    rest = int(m.iloc[10:]["Count"].sum())
    if rest > 0:
        top = pd.concat([top,
                         pd.DataFrame([{"Machine Group": "OTHERS",
                                         "Count": rest}])],
                        ignore_index=True)
    return _pie(top["Machine Group"].tolist(), top["Count"].tolist(),
                "Breakdown Share by Machine Group", height=400, hole=0.42)


def c_top_count(df, top_n=15):
    m = (df.groupby("Machine Group").size()
           .reset_index(name="Count")
           .sort_values("Count", ascending=False)
           .head(top_n).sort_values("Count"))
    fig = go.Figure(go.Bar(
        x=m["Count"], y=m["Machine Group"], orientation="h",
        marker=dict(color=C_ORANGE, line_width=0),
        text=m["Count"], textposition="outside",
        textfont=dict(color=C_MUTED, size=10),
    ))
    fig.update_layout(**_L(max(300, top_n * 28),
                           f"Top {top_n} Machine Groups — Breakdown Count",
                           margin=dict(l=165, r=70, t=52, b=10)))
    return fig


def c_top_hours(df, top_n=15):
    m = (df.groupby("Machine Group")["Breakdown Hours"].sum()
           .reset_index(name="Hours")
           .sort_values("Hours", ascending=False)
           .head(top_n).sort_values("Hours"))
    fig = go.Figure(go.Bar(
        x=m["Hours"].round(1), y=m["Machine Group"], orientation="h",
        marker=dict(color=C_BLUE, line_width=0),
        text=[f"{v:.1f}h" for v in m["Hours"].round(1)],
        textposition="outside",
        textfont=dict(color=C_MUTED, size=10),
    ))
    fig.update_layout(**_L(max(300, top_n * 28),
                           f"Top {top_n} Machine Groups — Downtime Hours",
                           margin=dict(l=165, r=70, t=52, b=10)))
    return fig


def c_fault_by_machine(df, top_n=15):
    top_m = (df.groupby("Machine Group").size()
               .sort_values(ascending=False).head(top_n).index.tolist())
    sub   = df[df["Machine Group"].isin(top_m)]
    pivot = sub.groupby(["Machine Group", "Fault Type"]).size().unstack(fill_value=0)
    pivot = pivot.loc[sorted(pivot.index, key=lambda x: pivot.loc[x].sum())]
    mech  = pivot.get("MECHANICAL", pd.Series(0, index=pivot.index))
    elec  = pivot.get("ELECTRICAL",  pd.Series(0, index=pivot.index))
    fig   = go.Figure()
    fig.add_trace(go.Bar(
        x=mech.values, y=pivot.index, orientation="h",
        name="MECHANICAL", marker=dict(color=C_ORANGE, line_width=0),
        text=mech.values, textposition="inside",
        textfont=dict(size=10, color="white"),
    ))
    fig.add_trace(go.Bar(
        x=elec.values, y=pivot.index, orientation="h",
        name="ELECTRICAL",  marker=dict(color=C_BLUE, line_width=0),
        text=elec.values, textposition="inside",
        textfont=dict(size=10, color="white"),
    ))
    fig.update_layout(**_L(max(300, top_n * 28),
                           f"Top {top_n} Machines — Mechanical vs Electrical",
                           margin=dict(l=165, r=70, t=52, b=10),
                           extra={"barmode": "stack"}))
    return fig


def c_top_reasons(df, top_n=12):
    r = (df.groupby("Reason")
           .agg(Count=("Machine Group", "count"),
                Hours=("Breakdown Hours", "sum"))
           .sort_values("Count", ascending=False)
           .head(top_n).sort_values("Count").reset_index())
    clrs = [C_ORANGE if i >= len(r) - 3 else C_SURF2 for i in range(len(r))]
    fig  = go.Figure(go.Bar(
        x=r["Count"], y=r["Reason"], orientation="h",
        marker=dict(color=clrs, line=dict(color=C_BORDER, width=1)),
        text=r["Count"], textposition="outside",
        textfont=dict(color=C_MUTED, size=10),
        customdata=r["Hours"].round(1),
        hovertemplate="<b>%{y}</b><br>Count: %{x}<br>Downtime: %{customdata}h<extra></extra>",
    ))
    fig.update_layout(**_L(max(300, top_n * 32),
                           f"Top {top_n} Failure Reasons  (top 3 highlighted)",
                           margin=dict(l=210, r=80, t=52, b=10)))
    return fig


def c_mtbf(df, top_n=15):
    total_days = max((df["BD Open Date"].max() -
                      df["BD Open Date"].min()).days, 1)
    m = df.groupby("Machine Group").size().reset_index(name="Count")
    m = m[m["Count"] > 1]
    m["MTBF"] = (total_days / m["Count"]).round(1)
    m = m.sort_values("MTBF").head(top_n)
    clrs = [C_RED    if v < 3  else
            (C_YELLOW if v < 7  else C_GREEN)
            for v in m["MTBF"]]
    fig = go.Figure(go.Bar(
        x=m["MTBF"], y=m["Machine Group"], orientation="h",
        marker=dict(color=clrs, line_width=0),
        text=[f"{v}d" for v in m["MTBF"]], textposition="outside",
        textfont=dict(color=C_MUTED, size=10),
        hovertemplate="<b>%{y}</b><br>MTBF: %{x} days<extra></extra>",
    ))
    fig.update_layout(**_L(max(300, top_n * 28),
                           f"MTBF — {top_n} Most Critical Groups  "
                           f"(🔴 <3d  🟡 <7d  🟢 ≥7d)",
                           margin=dict(l=165, r=90, t=52, b=10)))
    return fig


def c_hour_of_day(df):
    h  = df.dropna(subset=["Hour"])
    hc = h.groupby("Hour").size().reset_index(name="Count")
    all_h = pd.DataFrame({"Hour": range(24)})
    hc = all_h.merge(hc, on="Hour", how="left").fillna(0)
    hc["Count"] = hc["Count"].astype(int)

    def sc(hr):
        if 0  <= hr <  6:  return C_PURPLE
        if 6  <= hr < 14:  return C_ORANGE
        if 14 <= hr < 22:  return C_BLUE
        return C_TEAL

    fig = go.Figure(go.Bar(
        x=hc["Hour"], y=hc["Count"],
        marker=dict(color=[sc(h) for h in hc["Hour"]], line_width=0),
        text=hc["Count"], textposition="outside",
        textfont=dict(color=C_MUTED, size=9),
        hovertemplate="Hour %{x}:00 → %{y} breakdowns<extra></extra>",
    ))
    fig.update_layout(**_L(290,
                           "Breakdowns by Hour of Day  "
                           "(🟣 Night  🟠 Morning  🔵 Afternoon  🩵 Evening)",
                           extra={"xaxis": dict(tickmode="linear", dtick=1,
                                                gridcolor=C_BORDER,
                                                tickfont=dict(color=C_TEXT))}))
    return fig


def c_day_of_week(df):
    order = ["Monday", "Tuesday", "Wednesday",
             "Thursday", "Friday", "Saturday", "Sunday"]
    dc = df.groupby("DayOfWeek").size().reset_index(name="Count")
    dc["DayOfWeek"] = pd.Categorical(dc["DayOfWeek"],
                                     categories=order, ordered=True)
    dc = dc.sort_values("DayOfWeek")
    fig = go.Figure(go.Bar(
        x=dc["DayOfWeek"], y=dc["Count"],
        marker=dict(color=C_TEAL, line_width=0),
        text=dc["Count"], textposition="outside",
        textfont=dict(color=C_MUTED, size=10),
    ))
    fig.update_layout(**_L(280, "Breakdowns by Day of Week"))
    return fig


# ── Machine-tab specific charts ─────────────────────────────────────────────

def c_machine_fault_monthly(sub):
    mf   = (sub.groupby(["Month_dt", "Fault Type"], sort=True).size()
               .reset_index(name="Count"))
    mech = mf[mf["Fault Type"] == "MECHANICAL"]
    elec = mf[mf["Fault Type"] == "ELECTRICAL"]
    fig  = go.Figure()
    fig.add_trace(go.Bar(
        x=mech["Month_dt"], y=mech["Count"], name="MECHANICAL",
        marker=dict(color=C_ORANGE, line_width=0),
        text=mech["Count"], textposition="inside",
        textfont=dict(size=9, color="white"),
    ))
    fig.add_trace(go.Bar(
        x=elec["Month_dt"], y=elec["Count"], name="ELECTRICAL",
        marker=dict(color=C_BLUE, line_width=0),
        text=elec["Count"], textposition="inside",
        textfont=dict(size=9, color="white"),
    ))
    fig.update_layout(**_L(300, "Monthly Fault Type Split",
                           extra={"barmode": "stack"}))
    fig.update_xaxes(tickformat="%b %Y", tickangle=-30)
    return fig


def c_machine_hour(sub):
    h  = sub.dropna(subset=["Hour"])
    hc = h.groupby("Hour").size().reset_index(name="Count")
    all_h = pd.DataFrame({"Hour": range(24)})
    hc = all_h.merge(hc, on="Hour", how="left").fillna(0)
    hc["Count"] = hc["Count"].astype(int)

    def sc(hr):
        if 0  <= hr <  6:  return C_PURPLE
        if 6  <= hr < 14:  return C_ORANGE
        if 14 <= hr < 22:  return C_BLUE
        return C_TEAL

    fig = go.Figure(go.Bar(
        x=hc["Hour"], y=hc["Count"],
        marker=dict(color=[sc(h) for h in hc["Hour"]], line_width=0),
        text=hc["Count"], textposition="outside",
        textfont=dict(color=C_MUTED, size=9),
        hovertemplate="Hour %{x}:00 → %{y} breakdowns<extra></extra>",
    ))
    fig.update_layout(**_L(280, "Breakdowns by Hour of Day",
                           extra={"xaxis": dict(tickmode="linear", dtick=1,
                                                gridcolor=C_BORDER,
                                                tickfont=dict(color=C_TEXT))}))
    return fig


def c_machine_reasons(df, grp, top_n=10):
    sub  = df[df["Machine Group"] == grp]
    r    = sub["Reason"].value_counts().head(top_n).reset_index()
    r.columns = ["Reason", "Count"]
    r    = r.sort_values("Count")
    clrs = [C_ORANGE if i >= len(r) - 3 else C_SURF2 for i in range(len(r))]
    fig  = go.Figure(go.Bar(
        x=r["Count"], y=r["Reason"], orientation="h",
        marker=dict(color=clrs, line=dict(color=C_BORDER, width=1)),
        text=r["Count"], textposition="outside",
        textfont=dict(color=C_MUTED, size=10),
    ))
    fig.update_layout(**_L(max(260, top_n * 30),
                           "Top Failure Reasons  (top 3 highlighted)",
                           margin=dict(l=180, r=70, t=48, b=10)))
    return fig


def c_machine_avg_duration(sub):
    sub2 = sub[sub["Breakdown Minutes"] > 0]
    if sub2.empty:
        return None
    m = (sub2.groupby("Month_dt", sort=True)["Breakdown Minutes"]
             .mean().round(1).reset_index())
    fig = go.Figure(go.Bar(
        x=m["Month_dt"], y=m["Breakdown Minutes"],
        marker=dict(color=C_GREEN, line_width=0),
        text=m["Breakdown Minutes"].round(0).astype(int),
        textposition="outside",
        textfont=dict(color=C_MUTED, size=10),
    ))
    fig.update_layout(**_L(280, "Avg Breakdown Duration per Month (minutes)"))
    fig.update_xaxes(tickformat="%b %Y", tickangle=-30)
    return fig


def c_machine_worst_months(sub):
    m = (sub.groupby("Month_dt", sort=True)
           .agg(Count=("Machine Group", "count"),
                Hours=("Breakdown Hours", "sum"))
           .reset_index()
           .sort_values("Count", ascending=False).head(6))
    m["Label"] = m["Month_dt"].dt.strftime("%b %Y")
    fig = go.Figure(go.Bar(
        x=m["Count"], y=m["Label"], orientation="h",
        marker=dict(color=C_RED, line_width=0),
        text=m["Count"], textposition="outside",
        textfont=dict(color=C_MUTED, size=10),
        customdata=m["Hours"].round(1),
        hovertemplate="<b>%{y}</b><br>BDs: %{x}<br>Hours: %{customdata}h<extra></extra>",
    ))
    fig.update_layout(**_L(260, "Worst Months — Breakdown Count",
                           margin=dict(l=90, r=70, t=48, b=10)))
    return fig


def c_machine_downtime_by_reason(sub, top_n=8):
    """Total downtime hours per failure reason for this machine group"""
    r = (sub[sub["Breakdown Hours"] > 0]
           .groupby("Reason")["Breakdown Hours"].sum()
           .reset_index(name="Hours")
           .sort_values("Hours", ascending=False)
           .head(top_n).sort_values("Hours"))
    if r.empty:
        return None
    fig = go.Figure(go.Bar(
        x=r["Hours"].round(1), y=r["Reason"], orientation="h",
        marker=dict(color=C_TEAL, line_width=0),
        text=[f"{v:.1f}h" for v in r["Hours"].round(1)],
        textposition="outside",
        textfont=dict(color=C_MUTED, size=10),
    ))
    fig.update_layout(**_L(max(240, top_n * 30),
                           "Downtime Hours by Failure Reason",
                           margin=dict(l=180, r=70, t=48, b=10)))
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
def render_sidebar(df):
    st.sidebar.markdown(f"""
    <div style='padding:6px 0 18px'>
      <div style='font-size:16px;font-weight:700;color:{C_ORANGE}'>
        🏭 Century Plyboards</div>
      <div style='font-size:10px;color:{C_MUTED};font-family:DM Mono,monospace'>
        Kandla Plant · BD Analytics</div>
    </div>""", unsafe_allow_html=True)

    months = sorted(df["Month"].unique())
    sel_m  = st.sidebar.multiselect("📅 Month", months, default=months)
    faults = sorted(df["Fault Type"].unique())
    sel_f  = st.sidebar.multiselect("⚙️ Fault Type", faults, default=faults)
    groups = sorted(df["Machine Group"].unique())
    sel_g  = st.sidebar.multiselect("🔧 Machine Group", groups, default=groups)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style='font-size:11px;color:{C_MUTED};
                font-family:DM Mono,monospace;line-height:2.1'>
      📊 Records : <b style='color:{C_TEXT}'>{len(df):,}</b><br>
      🗓 From    : <b style='color:{C_TEXT}'>{df['BD Open Date'].min().strftime('%d %b %Y')}</b><br>
      🗓 To      : <b style='color:{C_TEXT}'>{df['BD Open Date'].max().strftime('%d %b %Y')}</b><br>
      🔧 Groups  : <b style='color:{C_TEXT}'>{df['Machine Group'].nunique()}</b>
    </div>""", unsafe_allow_html=True)

    mask = (df["Month"].isin(sel_m) &
            df["Fault Type"].isin(sel_f) &
            df["Machine Group"].isin(sel_g))
    return df[mask].copy()


# ═══════════════════════════════════════════════════════════════════════════
# PLANT OVERVIEW TAB
# ═══════════════════════════════════════════════════════════════════════════
def render_overview(df):
    total_bd   = len(df)
    total_hrs  = df["Breakdown Hours"].sum()
    mech_cnt   = int((df["Fault Type"] == "MECHANICAL").sum())
    elec_cnt   = int((df["Fault Type"] == "ELECTRICAL").sum())
    mech_pct   = mech_cnt / max(total_bd, 1) * 100
    total_days = max((df["BD Open Date"].max() -
                      df["BD Open Date"].min()).days, 1)
    avg_day    = total_bd / total_days

    st.markdown(f"""<div class="kpi-row">
        {kpi("Total Breakdowns",  f"{total_bd:,}",        f"Avg {avg_day:.1f} / day")}
        {kpi("Total Downtime",    f"{total_hrs:,.0f} hrs", f"≈ {total_hrs/24:.0f} days lost")}
        {kpi("Mechanical",        f"{mech_cnt:,}",         f"{mech_pct:.1f}% of all BDs")}
        {kpi("Electrical",        f"{elec_cnt:,}",         f"{100-mech_pct:.1f}% of all BDs")}
        {kpi("Machine Groups",    f"{df['Machine Group'].nunique()}", "Unique groups")}
    </div>""", unsafe_allow_html=True)

    sec("MONTHLY TREND — COUNT & DOWNTIME HOURS (PER MONTH, NOT CUMULATIVE)")
    c1, c2 = st.columns([3, 1.2])
    with c1: st.plotly_chart(c_monthly_trend(df), use_container_width=True, config=CFG)
    with c2: st.plotly_chart(c_fault_pie(df),     use_container_width=True, config=CFG)

    sec("FAULT COMPOSITION & MACHINE GROUP SHARE")
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(c_monthly_fault_stacked(df), use_container_width=True, config=CFG)
    with c2: st.plotly_chart(c_group_pie(df),             use_container_width=True, config=CFG)

    sec("TOP MACHINE GROUPS — COUNT & HOURS")
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(c_top_count(df), use_container_width=True, config=CFG)
    with c2: st.plotly_chart(c_top_hours(df), use_container_width=True, config=CFG)

    sec("MECHANICAL vs ELECTRICAL & MTBF")
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(c_fault_by_machine(df), use_container_width=True, config=CFG)
    with c2: st.plotly_chart(c_mtbf(df),             use_container_width=True, config=CFG)

    sec("BREAKDOWN TIMING PATTERNS  — when do machines break down?")
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(c_hour_of_day(df),  use_container_width=True, config=CFG)
    with c2: st.plotly_chart(c_day_of_week(df),  use_container_width=True, config=CFG)

    sec("TOP FAILURE REASONS")
    st.plotly_chart(c_top_reasons(df), use_container_width=True, config=CFG)

    sec("FULL MACHINE GROUP SUMMARY TABLE")
    tbl = (df.groupby("Machine Group")
             .agg(
                 Total_BDs    = ("Machine Group", "count"),
                 Downtime_hrs = ("Breakdown Hours", "sum"),
                 Mechanical   = ("Fault Type", lambda x: (x == "MECHANICAL").sum()),
                 Electrical   = ("Fault Type", lambda x: (x == "ELECTRICAL").sum()),
                 Top_Reason   = ("Reason",     lambda x: x.value_counts().idxmax()),
             ).reset_index())
    tbl["MTBF_days"]  = (total_days / tbl["Total_BDs"]).round(1)
    tbl["Avg_min_BD"] = ((tbl["Downtime_hrs"] * 60) / tbl["Total_BDs"]).round(1)
    tbl["Mech_%"]     = (tbl["Mechanical"] / tbl["Total_BDs"] * 100
                         ).round(0).astype(int).astype(str) + "%"
    tbl = tbl.sort_values("Total_BDs", ascending=False).reset_index(drop=True)
    tbl["Downtime_hrs"] = tbl["Downtime_hrs"].round(1)
    tbl.columns = ["Machine Group", "Total BDs", "Downtime hrs",
                   "Mechanical", "Electrical", "Top Reason",
                   "MTBF (days)", "Avg min/BD", "Mech %"]

    max_bd  = tbl["Total BDs"].max()  or 1
    max_hrs = tbl["Downtime hrs"].max() or 1
    st.dataframe(
        tbl.style
           .applymap(lambda v: _o(v, max_bd),  subset=["Total BDs"])
           .applymap(lambda v: _b(v, max_hrs), subset=["Downtime hrs"])
           .format({"Downtime hrs": "{:.1f}",
                    "MTBF (days)":  "{:.1f}",
                    "Avg min/BD":   "{:.1f}"}),
        use_container_width=True, height=460,
    )


# ═══════════════════════════════════════════════════════════════════════════
# MACHINE GROUP TAB  — same depth as overview
# ═══════════════════════════════════════════════════════════════════════════
def render_machine_tab(df, grp):
    sub = df[df["Machine Group"] == grp].copy()
    if sub.empty:
        st.warning("No data for this group with current filters.")
        return

    total_bd   = len(sub)
    total_hrs  = sub["Breakdown Hours"].sum()
    mech_cnt   = int((sub["Fault Type"] == "MECHANICAL").sum())
    elec_cnt   = int((sub["Fault Type"] == "ELECTRICAL").sum())
    total_days = max((df["BD Open Date"].max() -
                      df["BD Open Date"].min()).days, 1)
    mtbf        = total_days / max(total_bd, 1)
    top_reason  = sub["Reason"].value_counts().idxmax() if total_bd else "—"
    avg_dur     = sub[sub["Breakdown Minutes"] > 0]["Breakdown Minutes"].mean()
    avg_dur_str = f"{avg_dur:.0f} min" if not pd.isna(avg_dur) else "N/A"
    worst_month = (sub.groupby("Month_dt").size().idxmax().strftime("%b %Y")
                   if total_bd else "—")

    # ── KPIs ──────────────────────────────────────────────────────────────────
    st.markdown(f"""<div class="kpi-row">
        {kpi("Breakdowns",    f"{total_bd:,}",         f"MTBF: {mtbf:.1f} days")}
        {kpi("Downtime",      f"{total_hrs:,.0f} hrs",  f"Avg {total_hrs/max(total_bd,1):.1f} hrs/BD")}
        {kpi("Mechanical",    f"{mech_cnt}",             f"{mech_cnt/max(total_bd,1)*100:.0f}% of BDs")}
        {kpi("Electrical",    f"{elec_cnt}",             f"{elec_cnt/max(total_bd,1)*100:.0f}% of BDs")}
        {kpi("Avg Duration",  avg_dur_str,               f"Worst month: {worst_month}")}
    </div>""", unsafe_allow_html=True)

    # ── 1. Monthly trend + Fault pie ─────────────────────────────────────────
    sec("MONTHLY TREND & FAULT SPLIT")
    c1, c2 = st.columns([3, 1.2])
    with c1: st.plotly_chart(c_monthly_trend(sub, grp_title=grp),
                              use_container_width=True, config=CFG)
    with c2: st.plotly_chart(c_fault_pie(sub),
                              use_container_width=True, config=CFG)

    # ── 2. Monthly fault stacked + Hour of day ───────────────────────────────
    sec("FAULT TYPE BY MONTH & HOUR OF DAY PATTERN")
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(c_machine_fault_monthly(sub),
                              use_container_width=True, config=CFG)
    with c2: st.plotly_chart(c_machine_hour(sub),
                              use_container_width=True, config=CFG)

    # ── 3. Top reasons (count) + Top reasons (hours) ─────────────────────────
    sec("FAILURE REASONS — BY COUNT & BY DOWNTIME HOURS")
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(c_machine_reasons(df, grp),
                              use_container_width=True, config=CFG)
    with c2:
        dtr = c_machine_downtime_by_reason(sub)
        if dtr:
            st.plotly_chart(dtr, use_container_width=True, config=CFG)
        else:
            st.info("No downtime data available.")

       # ── 5. Breakdown log ─────────────────────────────────────────────────────
    sec("BREAKDOWN LOG")
    log = (sub[["BD Open Date", "Machine Final", "Fault Type",
                "Reason", "Breakdown Minutes", "Breakdown Hours"]]
           .sort_values("BD Open Date", ascending=False).copy())
    log["BD Open Date"]    = log["BD Open Date"].dt.strftime("%Y-%m-%d")
    log["Breakdown Hours"] = log["Breakdown Hours"].round(2)
    log.columns = ["Date", "Machine", "Fault", "Reason", "Minutes", "Hours"]

    max_min = log["Minutes"].max() or 1
    st.dataframe(
        log.style.apply(
            lambda col: [_o(v, max_min) for v in col], subset=["Minutes"]
        ),
        use_container_width=True, height=400,
    )

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    try:
        raw_df = load_data(FILE_PATH)
    except FileNotFoundError:
        st.error(f"❌ File not found: `{FILE_PATH}`\n\n"
                 "Place **FINAL_READY_FOR_ANALYSIS.xlsx** next to this script.")
        st.stop()

    df = render_sidebar(raw_df)
    if df.empty:
        st.warning("No data matches current filters.")
        st.stop()

    st.markdown("""
    <div class="page-title">Century Plyboards — Kandla Plant Breakdown Analysis</div>
    <div class="page-sub">Manufacturing Plant · 12-Month Breakdown Intelligence Dashboard</div>
    """, unsafe_allow_html=True)

    all_groups = (df.groupby("Machine Group").size()
                    .sort_values(ascending=False).index.tolist())
    tab_groups = all_groups[:14]

    labels = ["🏭 Plant Overview"] + [f"⚙️ {g.title()}" for g in tab_groups]
    tabs   = st.tabs(labels)

    with tabs[0]:
        render_overview(df)
    for i, grp in enumerate(tab_groups):
        with tabs[i + 1]:
            render_machine_tab(df, grp)


if __name__ == "__main__":
    main()
