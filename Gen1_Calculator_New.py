"""
Rubus Picking KPI — Gen 1 Calculator
Streamlit application with editable financial parameters
"""

import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(
    page_title="Rubus Picking KPI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'DM Serif Display', serif; letter-spacing: -0.02em; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: #f0f4f0; border-radius: 12px; padding: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 20px; font-weight: 500; font-size: 0.9rem; color: #4a5568; background: transparent; }
.stTabs [aria-selected="true"] { background: #1a4731 !important; color: white !important; }
[data-testid="metric-container"] { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; }
[data-testid="metric-container"] [data-testid="stMetricLabel"] { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: #6b7280; font-weight: 600; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 1.6rem; color: #1a4731; font-family: 'DM Serif Display', serif; }
section[data-testid="stSidebar"] { background: #1a4731; }
section[data-testid="stSidebar"] * { color: #e8f5e9 !important; }
section[data-testid="stSidebar"] .stNumberInput input { background: #ffffff !important; border: none !important; color: #1a1a1a !important; font-weight: 600 !important; border-radius: 6px !important; }
section[data-testid="stSidebar"] .stNumberInput > div,
section[data-testid="stSidebar"] .stNumberInput [data-baseweb="input"],
section[data-testid="stSidebar"] .stNumberInput [data-baseweb="base-input"] { background: #ffffff !important; border: none !important; border-radius: 6px !important; }
section[data-testid="stSidebar"] .stNumberInput button { background: #ffffff !important; border: none !important; color: #111111 !important; border-radius: 4px !important; }
section[data-testid="stSidebar"] .stNumberInput button svg, section[data-testid="stSidebar"] .stNumberInput button p { color: #111111 !important; fill: #111111 !important; }
section[data-testid="stSidebar"] hr { border-color: #2d7a52 !important; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: #a5d6a7 !important; }
section[data-testid="stSidebar"] label { color: #c8e6c9 !important; font-size: 0.82rem !important; }
.stButton > button { background: #1a4731; color: white; border: none; border-radius: 8px; padding: 8px 20px; font-weight: 500; }
.stButton > button:hover { background: #245c3f; }
.streamlit-expanderHeader { background: #f0f7f0 !important; border-radius: 8px !important; font-weight: 500; }
[data-testid="stFileUploadDropzone"] { border: 2px dashed #1a4731 !important; border-radius: 12px !important; background: #f0f7f0 !important; }
hr { border-color: #e5e7eb; }
.device-card { background: #f0f7f0; border: 1px solid #a5d6a7; border-left: 4px solid #1a4731; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; }
.device-card-warn { background: #fff8e1; border: 1px solid #ffe082; border-left: 4px solid #f59e0b; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; }

/* ── Financial table alignment ── */
.fin-header { font-weight: 700; font-size: 0.82rem; text-transform: uppercase;
              letter-spacing: 0.06em; color: #6b7280; padding-bottom: 4px;
              border-bottom: 2px solid #e5e7eb; margin-bottom: 6px; }
.fin-total  { font-weight: 700; font-size: 1rem; color: #1a4731;
              background: #f0f7f0; border-radius: 8px; padding: 10px 12px; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
SPEEDS     = [200, 400, 600, 800, 1000]
ROW_LENGTH = 3333
REQUIRED_COLUMNS = [
    "Pick Event Number", "Pick Date", "Yield Kg", "Variety Area (ha)",
    "Total Harvest Hours", "Total Harvest Cost", "Distinct Picker Count",
]

def fmt_dollar(v): return f"${v:,.2f}"
def fmt_int(v):    return f"{v:,}"

# ── Column widths used for EVERY financial row: Item | Value | Life | Annual | Total
COL_W = [2.5, 1.3, 1.1, 1.4, 1.6]

def _fin_header(cols):
    """Render the header row for a financial table."""
    cols[0].markdown("**Item**")
    cols[1].markdown("**Value ($)**")
    cols[2].markdown("**Life (yrs)**")
    cols[3].markdown("**Annual Rate**")
    cols[4].markdown("**Total**")

def _fin_row(label, key_val, key_life, default_val, default_life,
             multiplier, suffix="", note=""):
    """
    Render one aligned financial row.
    Returns (annual_rate, total).
    multiplier: scalar applied to annual_rate → total
    """
    cols = st.columns(COL_W)
    display_label = f"{label}{f' ({note})' if note else ''}"
    cols[0].write(display_label)
    val  = cols[1].number_input("", value=float(default_val), min_value=0.0,
                                step=100.0, key=key_val, label_visibility="collapsed")
    life = cols[2].number_input("", value=float(default_life), min_value=0.1,
                                step=1.0,   key=key_life, label_visibility="collapsed")
    annual = val / life if life > 0 else 0.0
    total  = annual * multiplier
    cols[3].write(f"${annual:,.2f}")
    cols[4].write(f"${total:,.2f}")
    return annual, total


def compute_pick_calcs(df, total_pickers, labour_cost, max_pickrate, mid_speeds):
    out = df.copy()
    for s in SPEEDS:
        hrs_col = f"Hours/block@{s}"
        req_col = f"Required Rate@{s}"
        ben_col = f"Benefit@{s}"
        ach_col = f"Pick Achievable@{s}"
        pos_col = f"Positive Return@{s}"
        pp_col  = f"Pickable Profit@{s}"
        out[hrs_col] = out["Variety Area (ha)"] * ROW_LENGTH / s
        out[req_col] = np.where(
            (out[hrs_col] > 0) & (total_pickers > 0),
            out["Yield Kg"] / out[hrs_col] / total_pickers, 0)
        out[ben_col] = out["Total Harvest Cost"] - labour_cost * out[hrs_col]
        out[ach_col] = (out[req_col] <= max_pickrate).astype(int)
        out[pos_col] = np.where(out[ben_col] > 0, 1, np.nan)
        out[pp_col]  = np.where((out[ach_col] == 1) & (out[pos_col] == 1), out[ben_col], np.nan)

    all_pp = [f"Pickable Profit@{s}" for s in SPEEDS]
    mid_pp = [f"Pickable Profit@{s}" for s in mid_speeds]
    out["Best Profit"]     = out[all_pp].max(axis=1).fillna(0)
    out["Best Profit Mid"] = out[mid_pp].max(axis=1).fillna(0) if mid_pp else 0
   # Guard against all-NA rows before calling idxmax (pandas 3.x breaking change)
   # Pandas 3.x safe idxmax — check each row individually
    has_any_profit = out[all_pp].notna().any(axis=1)
    
    def safe_idxmax(row):
        if row.notna().any():
            return row.idxmax()
        return pd.NA
    
    opt = out[all_pp].apply(safe_idxmax, axis=1)
    out["Optimal Speed"] = (
        opt.astype(str)
        .str.extract(r"(\d+)", expand=False)
        .where(has_any_profit)
        .astype("Int64")
    )
    out["No of pickers"]   = np.where(out["Best Profit"] > 0, out["Distinct Picker Count"], np.nan)
    return out


def rename_calc_cols(df):
    rmap = {}
    for s in SPEEDS:
        rmap[f"Hours/block@{s}"]     = f"Hours per block @ {s}m/hr"
        rmap[f"Required Rate@{s}"]   = f"Required kg/hr/ppl @ {s}m/hr"
        rmap[f"Benefit@{s}"]         = f"Platform Potential Benefit @ {s}m/hr"
        rmap[f"Pick Achievable@{s}"] = f"Pick achievable @ {s}m/hr"
        rmap[f"Positive Return@{s}"] = f"Positive pick event return @ {s}m/hr"
        rmap[f"Pickable Profit@{s}"] = f"Pickable & Profitable @ {s}m"
    df.rename(columns=rmap, inplace=True)
    return df


def build_column_order(df, mid_label):
    base = ["Pick Event Number","Pick Date","Plant","Division","Location",
            "Product Variety","Cropping System","Variety Area (ha)","Yield Kg",
            "Total Harvest Hours","Total Harvest Cost","Distinct Picker Count",
            "Pick Rate Kgs/Hr (Picker Only – Derived Kgs)","Harvest Rate Kgs/Hr (Derived Kgs)"]
    calc = (
        [f"Hours per block @ {s}m/hr"            for s in SPEEDS] +
        [f"Required kg/hr/ppl @ {s}m/hr"         for s in SPEEDS] +
        [f"Platform Potential Benefit @ {s}m/hr"  for s in SPEEDS] +
        [f"Pick achievable @ {s}m/hr"            for s in SPEEDS] +
        [f"Positive pick event return @ {s}m/hr"  for s in SPEEDS] +
        [f"Pickable & Profitable @ {s}m"          for s in SPEEDS] +
        ["Best Profit", mid_label, "Optimal Speed", "No of pickers"]
    )
    base  = [c for c in base if c in df.columns]
    calc  = [c for c in calc if c in df.columns]
    extra = [c for c in df.columns if c not in set(base + calc)]
    return df[base + calc + extra]


def greedy_allocate(block_df, n_devices):
    records = []
    for _, row in block_df.iterrows():
        ds = row.get("Pick Date", set())
        if not isinstance(ds, set): ds = set()
        records.append({
            "location": row["Location"],
            "cropping_system": row.get("Cropping System", ""),
            "best_profit": float(row["Best Profit"]),
            "dates": ds, "allocated": False,
        })
    records.sort(key=lambda x: x["best_profit"], reverse=True)
    allocations, allocated_dates = [], set()
    for device_num in range(1, n_devices + 1):
        assigned = False
        for rec in records:
            if rec["allocated"] or (rec["dates"] & allocated_dates):
                continue
            rec["allocated"] = True
            allocated_dates |= rec["dates"]
            label = rec["location"]
            if rec["cropping_system"]: label += f" ({rec['cropping_system']})"
            allocations.append({"device": device_num, "assigned": True, "label": label,
                                 "location": rec["location"], "cropping_system": rec["cropping_system"],
                                 "best_profit": rec["best_profit"], "pick_events": len(rec["dates"])})
            assigned = True
            break
        if not assigned:
            allocations.append({"device": device_num, "assigned": False, "label": None,
                                 "location": None, "cropping_system": None,
                                 "best_profit": 0.0, "pick_events": 0})
    return allocations


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🌿 Rubus KPI")
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Harvest Inputs")
pickers         = st.sidebar.number_input("Pickers",                  value=5,    step=1,   min_value=0)
supervisors     = st.sidebar.number_input("Supervisors",              value=1,    step=1,   min_value=0)
picker_cost     = st.sidebar.number_input("Picker Cost ($/hr)",       value=32.0, step=0.5, min_value=0.0)
supervisor_cost = st.sidebar.number_input("Supervisor Cost ($/hr)",   value=36.0, step=0.5, min_value=0.0)
max_pickrate    = st.sidebar.number_input("Max Pick Rate (kg/hr/ppl)",value=8.0,  step=0.5, min_value=0.1)
st.sidebar.markdown("---")
st.sidebar.markdown("**Mid-Speed Profit Range**")
speed_range = st.sidebar.select_slider("Speed range (m/hr)", options=SPEEDS, value=(400, 600))
mid_speeds  = [s for s in SPEEDS if speed_range[0] <= s <= speed_range[1]]
total_pickers = pickers + supervisors
labour_cost   = pickers * picker_cost + supervisors * supervisor_cost

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_results, tab_optimiser = st.tabs(["📊 Harvest Results", "🧩 Block Optimiser & Financial Analysis"])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1
# ═══════════════════════════════════════════════════════════════════════════
with tab_results:
    st.title("🌱 Gen 1 Calculator — Harvest Results")
    DATA_PATH = "data/Actuals_Data.xlsx"   # adjust filename to match your actual file

    if not os.path.exists(DATA_PATH):
        st.error(f"Data file not found at: `{DATA_PATH}`")
        st.stop()
    
    try:
        df = pd.read_csv(DATA_PATH) if DATA_PATH.endswith(".csv") else pd.read_excel(DATA_PATH)
    except Exception as e:
        st.error(f"Could not read file: {e}"); st.stop()

    df.columns = df.columns.str.strip()
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"**Missing required columns:** {', '.join(missing)}"); st.stop()

    df["Pick Date"] = pd.to_datetime(df["Pick Date"], errors="coerce")
    st.success(f"✅ File loaded — **{len(df):,} rows**, **{df.columns.size} columns**")

    valid_dates = df["Pick Date"].dropna()
    if valid_dates.empty:
        st.error("No valid dates found in 'Pick Date' column."); st.stop()

    min_date, max_date = valid_dates.min().date(), valid_dates.max().date()
    st.sidebar.markdown("---")
    st.sidebar.header("📅 Date Filter")
    date_range_sel = st.sidebar.date_input("Select date range", value=(min_date, max_date),
                                            min_value=min_date, max_value=max_date, format="YYYY/MM/DD")
    if isinstance(date_range_sel, (list, tuple)) and len(date_range_sel) == 2:
        start_date, end_date = date_range_sel
    else:
        st.sidebar.info("Select an end date to continue."); st.stop()

    st.sidebar.markdown(
        f'<div style="background:#245c3f;border-radius:8px;padding:8px 12px;margin-top:-8px;'
        f'font-size:0.82rem;color:#a5d6a7;line-height:1.6;">📅 '
        f'<b style="color:#e8f5e9;">{start_date.strftime("%d %b %Y")}</b>'
        f' &nbsp;→&nbsp; <b style="color:#e8f5e9;">{end_date.strftime("%d %b %Y")}</b></div>',
        unsafe_allow_html=True)
    st.sidebar.markdown("")

    if start_date > end_date:
        st.sidebar.error("Start must be before End."); st.stop()

    df_time = df[(df["Pick Date"].dt.date >= start_date) & (df["Pick Date"].dt.date <= end_date)].copy()
    if df_time.empty:
        st.warning("No rows match the selected date range."); st.stop()

    FILTER_DEFS = [(lbl, col) for lbl, col in [
        ("Plant","Plant"),("Division","Division"),("Location","Location"),
        ("Variety","Product Variety"),("Cropping System","Cropping System"),
    ] if col in df_time.columns]

    for _, col in FILTER_DEFS:
        if f"sel_{col}" not in st.session_state:
            st.session_state[f"sel_{col}"] = set(sorted(df_time[col].dropna().astype(str).unique()))

    def _cb_select_all(col, opts): st.session_state[f"sel_{col}"] = set(opts)
    def _cb_deselect_all(col):     st.session_state[f"sel_{col}"] = set()
    def _cb_item(col, val):
        sel = set(st.session_state[f"sel_{col}"])
        sel.add(val) if st.session_state[f"_w_{col}_{val}"] else sel.discard(val)
        st.session_state[f"sel_{col}"] = sel

    def _render_filter(label, col, opts):
        sel = st.session_state[f"sel_{col}"]
        n   = len(sel & set(opts))
        with st.sidebar.expander(f"{label}  ({n} / {len(opts)})", expanded=False):
            b1, b2 = st.columns(2)
            b1.button("Select All", key=f"_btn_all_{col}", on_click=_cb_select_all, args=(col, opts), use_container_width=True)
            b2.button("Clear All",  key=f"_btn_none_{col}", on_click=_cb_deselect_all, args=(col,),  use_container_width=True)
            st.divider()
            for v in opts:
                st.checkbox(v, value=(v in sel), key=f"_w_{col}_{v}", on_change=_cb_item, args=(col, v))
        return list(sel & set(opts)) or list(opts)

    st.sidebar.markdown("---")
    st.sidebar.header("Filters")
    for i, (lbl, col) in enumerate(FILTER_DEFS):
        mask = pd.Series(True, index=df_time.index)
        for j, (_, oc) in enumerate(FILTER_DEFS):
            if j != i:
                os_ = st.session_state[f"sel_{oc}"]
                if os_: mask &= df_time[oc].astype(str).isin(os_)
        _render_filter(lbl, col, sorted(df_time.loc[mask, col].dropna().astype(str).unique()))

    df_filtered = df_time.copy()
    for _, col in FILTER_DEFS:
        sel = st.session_state[f"sel_{col}"]
        if sel: df_filtered = df_filtered[df_filtered[col].astype(str).isin(sel)]

    if df_filtered.empty:
        st.warning("No rows match the selected filters."); st.stop()

    mid_label   = f"Best Profit ({speed_range[0]}–{speed_range[1]}m)"
    filtered_df = compute_pick_calcs(df_filtered, total_pickers, labour_cost, max_pickrate, mid_speeds)
    filtered_df.rename(columns={"Best Profit Mid": mid_label}, inplace=True)
    filtered_df = rename_calc_cols(filtered_df)
    filtered_df = build_column_order(filtered_df, mid_label)

    st.session_state["df_filtered"] = filtered_df.copy()
    st.session_state["mid_label"]   = mid_label

    st.subheader("Pick Event Results")
    st.dataframe(filtered_df, use_container_width=True,
                 column_config={"Pick Event Number": st.column_config.Column(pinned=True)})

    st.subheader("Summary")
    groupable_cols = [c for c in ["Plant","Division","Location","Product Variety","Cropping System","Pick Date"] if c in filtered_df.columns]
    sg1, sg2 = st.columns(2)
    g1 = sg1.selectbox("Group by (Level 1)", groupable_cols,
                        index=groupable_cols.index("Location") if "Location" in groupable_cols else 0, key="summary_g1")
    g2_opts = ["None"] + [c for c in groupable_cols if c != g1]
    g2      = sg2.selectbox("Group by (Level 2)", g2_opts, index=0, key="summary_g2")
    group_keys = [g1] if g2 == "None" else [g1, g2]

    agg_map = {k: v for k, v in {
        "Pick Event Number": "count", "Best Profit": "sum", mid_label: "sum",
        "Distinct Picker Count": "max", "Total Harvest Cost": "sum",
        "Yield Kg": "sum", "Total Harvest Hours": "sum",
    }.items() if k in filtered_df.columns}

    summary_df = filtered_df.groupby(group_keys, dropna=False).agg(agg_map).reset_index()
    summary_df.rename(columns={
        "Pick Event Number": "Pick Events", "Best Profit": "Sum Best Profit",
        mid_label: f"Sum Best Profit ({speed_range[0]}–{speed_range[1]}m)",
        "Distinct Picker Count": "Max Pickers", "Total Harvest Cost": "Total Harvest Cost",
        "Yield Kg": "Total Yield (kg)", "Total Harvest Hours": "Total Harvest Hours",
    }, inplace=True)
    num_cols = summary_df.select_dtypes(include="number").columns.tolist()
    grand = {c: "" for c in summary_df.columns}
    grand.update(summary_df[num_cols].sum().to_dict())
    grand[group_keys[0]] = "Grand Total"
    summary_df = pd.concat([summary_df, pd.DataFrame([grand])], ignore_index=True)
    st.dataframe(summary_df, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2
# ═══════════════════════════════════════════════════════════════════════════
with tab_optimiser:
    st.title("🧩 Block Optimiser & Financial Analysis")
    st.subheader("🤖 Device Allocation")
    n_devices = st.number_input("Number of Devices", value=1, min_value=1, max_value=20, step=1, key="n_devices_input")
    st.markdown(f"Allocating **{n_devices} device(s)** using a greedy strategy: each device is assigned to the "
                "highest-profit block whose pick dates don't overlap.")
    st.divider()

    if "df_filtered" not in st.session_state:
        st.info("📊 Please upload data in the **Harvest Results** tab first."); st.stop()

    fdf       = st.session_state["df_filtered"]
    mid_label = st.session_state.get("mid_label", "Best Profit Mid")
    if fdf.empty:
        st.warning("No data available. Adjust filters in Harvest Results tab."); st.stop()

    groupable = [c for c in ["Plant","Division"] if c in fdf.columns]
    group_dim = st.selectbox("Group analysis by", ["None (all data)"] + groupable, key="opt_group_dim")
    st.divider()

    # ── optimiser renderer ────────────────────────────────────────────────
    def run_optimiser(data: pd.DataFrame, label: str):
        if "Location" not in data.columns or "Best Profit" not in data.columns:
            st.warning(f"[{label}] Missing 'Location' or 'Best Profit' columns."); return

        group_cols = ["Location"] + (["Cropping System"] if "Cropping System" in data.columns else [])

        agg = {"Best Profit": "sum"}
        if "Pick Date" in data.columns:
            def safe_date_set(x):
                try:
                    return set(pd.to_datetime(x, errors="coerce").dt.date.dropna()) if not pd.api.types.is_datetime64_any_dtype(x) else set(x.dt.date)
                except Exception: return set()
            agg["Pick Date"] = safe_date_set
        if "Distinct Picker Count" in data.columns: agg["Distinct Picker Count"] = "max"
        if "Total Harvest Cost"    in data.columns: agg["Total Harvest Cost"]    = "sum"
        if mid_label               in data.columns: agg[mid_label]               = "sum"

        block_df = (data.groupby(group_cols, dropna=False).agg(agg).reset_index()
                    .sort_values("Best Profit", ascending=False).reset_index(drop=True))
        block_df.insert(0, "Rank", block_df.index + 1)

        st.subheader(f"📋 Block Tally — {label}")
        disp_cols = [c for c in ["Rank","Location","Cropping System","Best Profit",mid_label,
                                   "Distinct Picker Count","Total Harvest Cost"] if c in block_df.columns]
        fmt = {c: "${:,.2f}" for c in ["Best Profit",mid_label,"Total Harvest Cost"] if c in block_df.columns}
        st.dataframe(block_df[disp_cols].style.format(fmt), use_container_width=True, hide_index=True)

        st.subheader(f"🤖 Device Allocation — {label} ({n_devices} device(s))")
        allocations            = greedy_allocate(block_df, n_devices)
        total_allocated_profit = 0.0
        assigned_count         = 0

        for alloc in allocations:
            dev = alloc["device"]
            if alloc["assigned"]:
                assigned_count         += 1
                total_allocated_profit += alloc["best_profit"]
                st.markdown(
                    f'<div class="device-card"><b>Device {dev}</b> &nbsp;→&nbsp; <b>{alloc["label"]}</b><br>'
                    f'<span style="color:#1a4731;font-size:0.9rem;">Best Profit: <b>${alloc["best_profit"]:,.2f}</b>'
                    f' &nbsp;|&nbsp; Pick Events: <b>{alloc["pick_events"]}</b></span></div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="device-card-warn">⚠️ <b>Device {dev}</b> — No valid block to assign.<br>'
                    f'<span style="color:#92400e;font-size:0.85rem;">All remaining blocks overlap with already-allocated dates.</span></div>',
                    unsafe_allow_html=True)

        st.markdown("")
        sm1, sm2, sm3 = st.columns(3)
        sm1.metric("Devices Assigned",      f"{assigned_count} / {n_devices}")
        sm2.metric("Total Allocated Profit", fmt_dollar(total_allocated_profit))
        sm3.metric("Blocks Available",       str(len(block_df)))

        # ── FINANCIAL ANALYSIS ─────────────────────────────────────────────
        if assigned_count > 0:
            st.subheader(f"💰 Financial Analysis — {label}")

            allocated_blocks = [(a["location"], a["cropping_system"]) for a in allocations if a["assigned"]]
            allocated_labels = [a["label"] for a in allocations if a["assigned"]]
            st.info(f"📊 **Devices Allocated To**: {', '.join(allocated_labels)}")

            allocated_block_rows = block_df[
                block_df.apply(lambda r: (r["Location"], r.get("Cropping System","")) in allocated_blocks, axis=1)
            ]
            allocated_max_pickers  = allocated_block_rows["Distinct Picker Count"].sum() if "Distinct Picker Count" in allocated_block_rows.columns else 0
            allocated_harvest_cost = allocated_block_rows["Total Harvest Cost"].sum()    if "Total Harvest Cost"    in allocated_block_rows.columns else 0
            total_blocks           = len(block_df)
            trolley_qty            = max(1, round(allocated_max_pickers * 1.2))

            # ── SAVINGS ───────────────────────────────────────────────────
            with st.expander("➕ Equipment Savings (Editable)", expanded=True):

                # Header
                hcols = st.columns(COL_W)
                hcols[0].markdown("**Item**")
                hcols[1].markdown("**Value ($)**")
                hcols[2].markdown("**Life (yrs)**")
                hcols[3].markdown("**Annual Rate**")
                hcols[4].markdown("**Total Saving**")
                st.markdown("---")

                _, chariot_total   = _fin_row("Chariot",             f"chariot_val_{label}",    f"chariot_life_{label}",    35000, 10, assigned_count)
                _, trolley_total   = _fin_row("Trolleys",            f"trolley_val_{label}",    f"trolley_life_{label}",    515.22, 10, trolley_qty,   note=f"qty: {trolley_qty}")
                _, scales_total    = _fin_row("Scales",              f"scales_val_{label}",     f"scales_life_{label}",     80,     5,  trolley_qty,   note=f"qty: {trolley_qty}")
                _, hms_total       = _fin_row("HMS Kits",            f"hms_val_{label}",        f"hms_life_{label}",        25000, 10, assigned_count)
                _, logistics_total = _fin_row("Logistics - Trolleys",f"logistics_val_{label}",  f"logistics_life_{label}",  30000,  1,
                                              assigned_count / max(total_blocks, 1))

                st.markdown("---")
                oc1, oc2 = st.columns([1, 3])
                overhead_pct   = oc1.slider("Overhead %", 0.0, 50.0, 19.0, 0.1, key=f"overhead_pct_{label}")
                overhead_total = allocated_harvest_cost * (overhead_pct / 100)
                oc2.markdown(f"**Overhead Reduction**: {overhead_pct}% of "
                             f"${allocated_harvest_cost:,.0f} = **${overhead_total:,.0f}**")

                total_savings = chariot_total + trolley_total + scales_total + hms_total + logistics_total + overhead_total
                st.markdown(f'<div class="fin-total">Total Equipment Savings: {fmt_dollar(total_savings)}</div>',
                            unsafe_allow_html=True)

            # ── COSTS ─────────────────────────────────────────────────────
            with st.expander("➖ Equipment Costs (Editable)", expanded=True):

                hcols = st.columns(COL_W)
                hcols[0].markdown("**Item**")
                hcols[1].markdown("**Value ($)**")
                hcols[2].markdown("**Life (yrs)**")
                hcols[3].markdown("**Annual Rate**")
                hcols[4].markdown("**Total Cost**")
                st.markdown("---")

                _, platform_total      = _fin_row("Picking Platform",       f"platform_val_{label}",     f"platform_life_{label}",     120000, 10, assigned_count)
                _, tablet_total        = _fin_row("Samsung Galaxy Tab",      f"tablet_val_{label}",       f"tablet_life_{label}",        1543,   5, assigned_count)
                _, it_total            = _fin_row("IT Service Charges",      f"it_val_{label}",           f"it_life_{label}",             160,   1, assigned_count)
                _, burro_std_total     = _fin_row("Burro Std with tray",     f"burro_std_val_{label}",    f"burro_std_life_{label}",     35000,  10, assigned_count)
                _, burro_sw_total      = _fin_row("Burro Software",          f"burro_sw_val_{label}",     f"burro_sw_life_{label}",       3000,   1, assigned_count)
                _, burro_maint_total   = _fin_row("Burro Maintenance",       f"burro_maint_val_{label}",  f"burro_maint_life_{label}",   30000,  10,
                                                  assigned_count / max(total_blocks, 1))

                total_costs = platform_total + tablet_total + it_total + burro_std_total + burro_sw_total + burro_maint_total
                st.markdown(f'<div class="fin-total">Total Equipment Costs: {fmt_dollar(total_costs)}</div>',
                            unsafe_allow_html=True)

            # ── FINAL RESULTS ─────────────────────────────────────────────
            net          = total_savings - total_costs
            total_benefit = total_allocated_profit + net

            st.markdown("### 📊 Final Results")
            fr1, fr2, fr3, fr4 = st.columns(4)
            fr1.metric("Harvest Profit",        fmt_dollar(total_allocated_profit))
            fr2.metric("Equipment Savings",      fmt_dollar(total_savings))
            fr3.metric("Equipment Costs",        fmt_dollar(total_costs))
            fr4.metric("Total Annual Benefit",   fmt_dollar(total_benefit),
                       delta="Profitable ✅" if total_benefit >= 0 else "Loss ⚠️")

            if total_benefit >= 0:
                st.success(f"✅ Deploying {assigned_count} device(s) generates **{fmt_dollar(total_benefit)}** total annual benefit")
            else:
                st.warning(f"⚠️ Deploying {assigned_count} device(s) results in a net annual cost of **{fmt_dollar(abs(total_benefit))}**")

        st.divider()

    # ── Dispatch ──────────────────────────────────────────────────────────
    if group_dim == "None (all data)":
        run_optimiser(fdf, "All_Filtered_Data")
    else:
        groups   = sorted(fdf[group_dim].dropna().unique())
        selected = st.multiselect(f"Select {group_dim}(s) to analyse", options=groups, default=list(groups))
        for grp in selected:
            run_optimiser(fdf[fdf[group_dim].astype(str) == str(grp)], f"{group_dim}_{grp}")
