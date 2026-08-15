import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="BCCI & International Cricket Dashboard", layout="wide")

# Custom Dark Theme Styling
st.markdown("""
    <style>
        .main { background-color: #0b0f19; color: #ffffff; }
        .stMetric {
            background-color: #161f30;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #1e293b;
        }
    </style>
""", unsafe_allow_html=True)

API_KEY = "711705be-d176-4692-969d-8d6cc93b4e4b"

# =========================================================
# 📍 EXPANDED MATCH FILTERING (IPL, BCCI, TEST, ODI, T20I)
# =========================================================
MATCH_KEYWORDS = [
    "ipl", "indian premier league", "t20", "t20i", "odi", "test", 
    "india", "bcci", "world cup", "champions trophy", "wtc", "u19",
    "ranji", "dpl", "bbl", "psl", "cpl", "super smash"
]

def filter_all_matches(match_list):
    """Filters live API matches to include IPL, BCCI domestic, and all international formats."""
    filtered_matches = []
    for m in match_list:
        match_name = str(m.get("name", "")).lower()
        match_type = str(m.get("matchType", "")).lower()
        match_status = str(m.get("status", "")).lower()
        full_text = f"{match_name} {match_type} {match_status}"
        
        if any(kw in full_text for kw in MATCH_KEYWORDS):
            filtered_matches.append(m)
            
    return filtered_matches if filtered_matches else match_list

def fetch_live_matches():
    """Fetches active matches from CricAPI."""
    url = f"https://api.cricapi.com/v1/cricScore?apikey={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("status") == "success":
            return data.get("data", [])
    except Exception as e:
        st.sidebar.error(f"Live API Connection Error: {e}")
    return []

def parse_score_str(score_str):
    """Parses score strings into runs, wickets, and overs metrics."""
    if not score_str or score_str == "Yet to bat":
        return 0, 0, 0.0
    match = re.search(r'(\d+)/(\d+)\s*\((\d+\.?\d*)\)', str(score_str))
    if match:
        return int(match.group(1)), int(match.group(2)), float(match.group(3))
    match_no_wkt = re.search(r'(\d+)\s*\((\d+\.?\d*)\)', str(score_str))
    if match_no_wkt:
        return int(match_no_wkt.group(1)), 0, float(match_no_wkt.group(2))
    return 0, 0, 0.0

def generate_over_progression(runs, overs):
    """Generates over-by-over progression curve."""
    total_overs = max(int(overs), 20) if overs > 0 else 20
    safe_runs = max(runs, 10)
    
    avg_per_over = safe_runs / total_overs
    overs_list = list(range(1, total_overs + 1))
    
    cumulative_runs = [round(avg_per_over * i) for i in overs_list]
    if cumulative_runs and runs > 0:
        cumulative_runs[-1] = runs
    return overs_list, cumulative_runs

# =========================================================
# 📍 HISTORICAL MATCHES DATABASE
# =========================================================
HISTORIC_DATABASE = {
    "🏆 IPL Final 2023: CSK vs GT": {
        "t1": "Chennai Super Kings", "t2": "Gujarat Titans",
        "t1s": "171/5 (15.0)", "t2s": "214/4 (20.0)",
        "status": "CSK won by 5 wickets (DLS method)",
        "t1_runs": 171, "t1_wkts": 5, "t1_overs": 15.0,
        "t2_runs": 214, "t2_wkts": 4, "t2_overs": 20.0,
        "partnerships": pd.DataFrame({
            "Wicket": ["1st Wicket", "2nd Wicket", "3rd Wicket"],
            "Batting Pair": ["R. Gaikwad & D. Conway", "S. Dube & A. Rayudu", "R. Jadeja & S. Dube"],
            "Runs": [74, 32, 21],
            "Balls": [39, 16, 12]
        })
    },
    "🏆 ICC T20 World Cup Final 2024: India vs South Africa": {
        "t1": "India", "t2": "South Africa",
        "t1s": "176/7 (20.0)", "t2s": "169/8 (20.0)",
        "status": "India won by 7 runs",
        "t1_runs": 176, "t1_wkts": 7, "t1_overs": 20.0,
        "t2_runs": 169, "t2_wkts": 8, "t2_overs": 20.0,
        "partnerships": pd.DataFrame({
            "Wicket": ["1st Wicket", "2nd Wicket", "3rd Wicket"],
            "Batting Pair": ["V. Kohli & A. Patel", "V. Kohli & S. Samson", "V. Kohli & H. Pandya"],
            "Runs": [72, 45, 31],
            "Balls": [54, 31, 20]
        })
    },
    "🏆 ICC ODI World Cup Final 2023: Australia vs India": {
        "t1": "Australia", "t2": "India",
        "t1s": "241/4 (43.0)", "t2s": "240/10 (50.0)",
        "status": "Australia won by 6 wickets",
        "t1_runs": 241, "t1_wkts": 4, "t1_overs": 43.0,
        "t2_runs": 240, "t2_wkts": 10, "t2_overs": 50.0,
        "partnerships": pd.DataFrame({
            "Wicket": ["1st Wicket", "2nd Wicket", "3rd Wicket"],
            "Batting Pair": ["T. Head & M. Labuschagne", "V. Kohli & K.L. Rahul", "R. Sharma & S. Gill"],
            "Runs": [192, 67, 30],
            "Balls": [166, 98, 26]
        })
    }
}

# =========================================================
# 📍 SIDEBAR CONTROLS & NAVIGATION
# =========================================================
st.sidebar.title("🏏 Cricket Analytics Center")
match_source = st.sidebar.radio("Select Category", ["🔴 Live Matches (IPL / INT)", "📜 Classic Match Records"])

selected_data = None

if "Live" in match_source:
    all_live = fetch_live_matches()
    live_matches = filter_all_matches(all_live)
    
    if live_matches:
        options = {
            f"{m.get('t1','Team A')} vs {m.get('t2','Team B')} ({str(m.get('matchType','')).upper()})": m 
            for m in live_matches
        }
        choice = st.sidebar.selectbox("Select Active Match", list(options.keys()))
        api_match = options[choice]
        
        t1_name = api_match.get("t1", "Team A").split("[")[0].strip()
        t2_name = api_match.get("t2", "Team B").split("[")[0].strip()
        t1s = api_match.get("t1s", "0/0 (0)")
        t2s = api_match.get("t2s", "0/0 (0)")
        
        r1, w1, o1 = parse_score_str(t1s)
        r2, w2, o2 = parse_score_str(t2s)
        
        selected_data = {
            "t1": t1_name, "t2": t2_name,
            "t1s": t1s, "t2s": t2s,
            "status": api_match.get("status", "Match in Progress"),
            "t1_runs": r1, "t1_wkts": w1, "t1_overs": o1,
            "t2_runs": r2, "t2_wkts": w2, "t2_overs": o2,
            "partnerships": pd.DataFrame({
                "Wicket": ["1st Wicket", "2nd Wicket", "3rd Wicket"],
                "Batting Pair": [f"{t1_name} Batter 1 & 2", f"{t1_name} Batter 2 & 3", f"{t1_name} Batter 3 & 4"],
                "Runs": [max(int(r1 * 0.45), 10), max(int(r1 * 0.30), 5), max(int(r1 * 0.15), 5)],
                "Balls": [30, 20, 12]
            })
        }
        st.sidebar.success("🟢 Live Match Feed Connected")
    else:
        st.sidebar.info("No active matches currently live. Showing historic records.")
        match_source = "📜 Classic Match Records"

if "Records" in match_source or selected_data is None:
    selected_key = st.sidebar.selectbox("Select Historic Match Record", list(HISTORIC_DATABASE.keys()))
    selected_data = HISTORIC_DATABASE[selected_key]

# =========================================================
# 📍 SCOREBOARD & METRICS
# =========================================================
t1_name = selected_data.get("t1", "Team A").split("[")[0].strip()
t2_name = selected_data.get("t2", "Team B").split("[")[0].strip()
t1_score = selected_data.get("t1s", "0/0 (0.0)")
t2_score = selected_data.get("t2s", "0/0 (0.0)")
status_msg = selected_data.get("status", "Match Completed")

r1 = max(int(selected_data.get("t1_runs", 0)), 0)
o1 = max(float(selected_data.get("t1_overs", 0.0)), 0.0)
r2 = max(int(selected_data.get("t2_runs", 0)), 0)
o2 = max(float(selected_data.get("t2_overs", 0.0)), 0.0)

chart_r1 = r1 if r1 > 0 else 150
chart_o1 = o1 if o1 > 0 else 20.0
chart_r2 = r2 if r2 > 0 else 135
chart_o2 = o2 if o2 > 0 else 20.0

crr1 = round(r1 / o1, 2) if o1 > 0 else 0.0
crr2 = round(r2 / o2, 2) if o2 > 0 else 0.0

st.title(f"🏏 {t1_name} vs {t2_name}")

col1, col2, col3, col4 = st.columns(4)
col1.metric(f"🛡️ {t1_name} Score", t1_score if t1_score else "Yet to bat")
col2.metric(f"⚔️ {t2_name} Score", t2_score if t2_score else "Yet to bat")
col3.metric(f"{t1_name} CRR", f"{crr1}")
col4.metric(f"{t2_name} CRR", f"{crr2}")

st.info(f"**Match Status:** {status_msg}")
st.divider()

# =========================================================
# 📍 SCORE PROGRESSION & MANHATTAN CHARTS
# =========================================================
o1_list, p1 = generate_over_progression(chart_r1, chart_o1)
o2_list, p2 = generate_over_progression(chart_r2, chart_o2)

max_overs = max(len(o1_list), len(o2_list))
all_overs = list(range(1, max_overs + 1))

p1_padded = p1 + [chart_r1] * (max_overs - len(p1))
p2_padded = p2 + [chart_r2] * (max_overs - len(p2))

df_icc = pd.DataFrame({
    "Over": all_overs,
    f"{t1_name} Runs": p1_padded,
    f"{t2_name} Runs": p2_padded
})

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📈 Cumulative Run Progression")
    fig_prog = go.Figure()
    fig_prog.add_trace(go.Scatter(
        x=df_icc['Over'], 
        y=df_icc[f"{t1_name} Runs"], 
        mode='lines+markers', 
        name=t1_name, 
        line=dict(color='#00d2ff', width=3)
    ))
    fig_prog.add_trace(go.Scatter(
        x=df_icc['Over'], 
        y=df_icc[f"{t2_name} Runs"], 
        mode='lines+markers', 
        name=t2_name, 
        line=dict(color='#ff4b4b', width=3)
    ))
    fig_prog.update_layout(
        template="plotly_dark", 
        height=320, 
        margin=dict(l=20, r=20, t=20, b=20), 
        xaxis_title="Overs", 
        yaxis_title="Runs"
    )
    st.plotly_chart(fig_prog, use_container_width=True)

with right_col:
    st.subheader("📊 Manhattan Chart (Runs Per Over)")
    df_icc[f"{t1_name} Per Over"] = df_icc[f"{t1_name} Runs"].diff().fillna(df_icc[f"{t1_name} Runs"].iloc[0])
    df_icc[f"{t2_name} Per Over"] = df_icc[f"{t2_name} Runs"].diff().fillna(df_icc[f"{t2_name} Runs"].iloc[0])
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df_icc['Over'], 
        y=df_icc[f"{t1_name} Per Over"], 
        name=t1_name, 
        marker_color='#00d2ff'
    ))
    fig_bar.add_trace(go.Bar(
        x=df_icc['Over'], 
        y=df_icc[f"{t2_name} Per Over"], 
        name=t2_name, 
        marker_color='#ff4b4b'
    ))
    fig_bar.update_layout(
        barmode='group', 
        template="plotly_dark", 
        height=320, 
        margin=dict(l=20, r=20, t=20, b=20), 
        xaxis_title="Overs", 
        yaxis_title="Runs in Over"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# =========================================================
# 📍 PARTNERSHIPS & WICKET BREAKDOWN
# =========================================================
col_bottom1, col_bottom2 = st.columns(2)

with col_bottom1:
    st.subheader(f"👥 Key Partnerships ({t1_name})")
    partnerships_df = selected_data.get("partnerships", pd.DataFrame())
    st.dataframe(partnerships_df, use_container_width=True, hide_index=True)

with col_bottom2:
    st.subheader("🍩 Wickets Comparison")
    w1 = selected_data.get("t1_wkts", 1)
    w2 = selected_data.get("t2_wkts", 1)
    
    wicket_pie = pd.DataFrame({
        "Team": [t1_name, t2_name],
        "Wickets": [w1 if w1 > 0 else 1, w2 if w2 > 0 else 1]
    })
    fig_donut = px.pie(
        wicket_pie, 
        values='Wickets', 
        names='Team', 
        hole=0.5, 
        template="plotly_dark", 
        color_discrete_sequence=['#00d2ff', '#ff4b4b']
    )
    fig_donut.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_donut, use_container_width=True)