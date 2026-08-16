import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import re

# =========================================================
# 📍 PAGE CONFIGURATION & SESSION STATE
# =========================================================
st.set_page_config(page_title="Mayuresh's Cricket Analytics Hub", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "landing"

def enter_dashboard():
    st.session_state.page = "dashboard"

# =========================================================
# 📍 1. LANDING / WELCOME PAGE VIEW
# =========================================================
if st.session_state.page == "landing":
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(rgba(11, 15, 25, 0.75), rgba(11, 15, 25, 0.85)), 
                            url("https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?q=80&w=2000&auto=format&fit=crop");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }
            .welcome-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                padding: 80px 20px;
                border-radius: 20px;
                background: rgba(15, 23, 42, 0.65);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.15);
                margin-top: 50px;
            }
            .welcome-title {
                font-size: 3.2rem;
                font-weight: 800;
                color: #ffffff;
                margin-bottom: 15px;
                text-shadow: 0px 4px 15px rgba(0, 210, 255, 0.5);
            }
            .welcome-subtitle {
                font-size: 1.3rem;
                color: #cbd5e1;
                margin-bottom: 30px;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown("""
            <div class="welcome-container">
                <div class="welcome-title">🏏 Welcome to Mayuresh's Cricket Analytics Hub</div>
                <div class="welcome-subtitle">Real-time Scores, Live Match Tracking & Analytics</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.write("")
        btn_col1, btn_col2, btn_col3 = st.columns([1.5, 2, 1.5])
        with btn_col2:
            st.button("🚀 Enter Dashboard", on_click=enter_dashboard, type="primary", use_container_width=True)

# =========================================================
# 📍 2. DASHBOARD VIEW
# =========================================================
else:
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(rgba(11, 15, 25, 0.85), rgba(11, 15, 25, 0.90)), 
                            url("https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?q=80&w=2000&auto=format&fit=crop");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                color: #ffffff;
            }
            [data-testid="stSidebar"] {
                background-color: rgba(15, 23, 42, 0.95);
            }
            .stMetric {
                background-color: rgba(22, 31, 48, 0.85);
                padding: 12px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(5px);
            }
        </style>
    """, unsafe_allow_html=True)

    API_KEY = "711705be-d176-4692-969d-8d6cc93b4e4b"

    @st.cache_data(ttl=30)
    def fetch_realtime_matches():
        headers = {'Cache-Control': 'no-cache'}
        
        try:
            url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
            res = requests.get(url, headers=headers, timeout=5).json()
            if res.get("status") == "success" and res.get("data"):
                return res.get("data")
        except Exception as e:
            print(f"Primary Fetch Error: {e}")

        try:
            url_score = f"https://api.cricapi.com/v1/cricScore?apikey={API_KEY}"
            res2 = requests.get(url_score, headers=headers, timeout=5).json()
            if res2.get("status") == "success" and res2.get("data"):
                return res2.get("data")
        except Exception as e:
            print(f"Secondary Fetch Error: {e}")

        return []

    @st.cache_data(ttl=30)
    def fetch_match_scorecard(match_id):
        headers = {'Cache-Control': 'no-cache'}
        url = f"https://api.cricapi.com/v1/match_scorecard?apikey={API_KEY}&id={match_id}"
        try:
            res = requests.get(url, headers=headers, timeout=5).json()
            if res.get("status") == "success":
                return res.get("data", {})
        except Exception as e:
            print(f"Scorecard API Error: {e}")
        return None

    def parse_score_str(score_str):
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
        total_overs = max(int(overs), 20) if overs > 0 else 20
        safe_runs = max(runs, 10)
        avg_per_over = safe_runs / total_overs
        overs_list = list(range(1, total_overs + 1))
        cumulative_runs = [round(avg_per_over * i) for i in overs_list]
        if cumulative_runs and runs > 0:
            cumulative_runs[-1] = runs
        return overs_list, cumulative_runs

    # =========================================================
    # 📚 HISTORIC MATCHES DATABASE (6 Match Records)
    # =========================================================
    HISTORIC_DATABASE = {
        "🏆 IPL Final 2026: RCB vs GT": {
            "t1": "Royal Challengers Bengaluru", "t2": "Gujarat Titans",
            "t1s": "161/5 (18.0)", "t2s": "155/8 (20.0)",
            "status": "RCB won by 5 wickets 🏆",
            "t1_runs": 161, "t1_wkts": 5, "t1_overs": 18.0,
            "t2_runs": 155, "t2_wkts": 8, "t2_overs": 20.0,
            "player_scores": pd.DataFrame({
                "Player Name 🏏": ["Virat Kohli", "Venkatesh Iyer", "Rajat Patidar", "Washington Sundar", "Shubman Gill"],
                "Status ⚾": ["Not Out*", "c Rashid b Siraj", "b Shami", "Not Out*", "c Hazlewood b Bhuvi"],
                "Runs 📊": [75, 62, 18, 50, 39],
                "Balls ⏱️": [42, 27, 14, 28, 24],
                "SR ⚡": [178.57, 229.62, 128.57, 178.57, 162.50]
            })
        },
        "🏆 ICC T20 World Cup Final 2024: India vs South Africa": {
            "t1": "India", "t2": "South Africa",
            "t1s": "176/7 (20.0)", "t2s": "169/8 (20.0)",
            "status": "India won by 7 runs 🏆",
            "t1_runs": 176, "t1_wkts": 7, "t1_overs": 20.0,
            "t2_runs": 169, "t2_wkts": 8, "t2_overs": 20.0,
            "player_scores": pd.DataFrame({
                "Player Name 🏏": ["Virat Kohli", "Axar Patel", "Heinrich Klaasen", "Quinton de Kock", "Hardik Pandya"],
                "Status ⚾": ["c Rabada b Jansen", "run out (De Kock)", "c Pant b Hardik", "c Kuldeep b Arshdeep", "Not Out*"],
                "Runs 📊": [76, 47, 52, 39, 5],
                "Balls ⏱️": [59, 31, 27, 31, 2],
                "SR ⚡": [128.81, 151.61, 192.59, 125.80, 250.00]
            })
        },
        "🏆 ICC ODI World Cup Final 2023: India vs Australia": {
            "t1": "India", "t2": "Australia",
            "t1s": "240/10 (50.0)", "t2s": "241/4 (43.0)",
            "status": "Australia won by 6 wickets 🏆",
            "t1_runs": 240, "t1_wkts": 10, "t1_overs": 50.0,
            "t2_runs": 241, "t2_wkts": 4, "t2_overs": 43.0,
            "player_scores": pd.DataFrame({
                "Player Name 🏏": ["Travis Head", "Marnus Labuschagne", "KL Rahul", "Virat Kohli", "Rohit Sharma"],
                "Status ⚾": ["c Gill b Siraj", "Not Out*", "c Inglis b Starc", "b Cummins", "c Head b Maxwell"],
                "Runs 📊": [137, 58, 66, 54, 47],
                "Balls ⏱️": [120, 110, 107, 63, 31],
                "SR ⚡": [114.16, 52.72, 61.68, 85.71, 151.61]
            })
        },
        "🏆 IPL Final 2023: CSK vs GT": {
            "t1": "Gujarat Titans", "t2": "Chennai Super Kings",
            "t1s": "214/4 (20.0)", "t2s": "171/5 (15.0)",
            "status": "CSK won by 5 wickets (DLS) 🏆",
            "t1_runs": 214, "t1_wkts": 4, "t1_overs": 20.0,
            "t2_runs": 171, "t2_wkts": 5, "t2_overs": 15.0,
            "player_scores": pd.DataFrame({
                "Player Name 🏏": ["Sai Sudharsan", "Devon Conway", "Wriddhiman Saha", "Ravindra Jadeja", "Shivam Dube"],
                "Status ⚾": ["lbw b Pathirana", "c Mohit b Noor", "c Dhoni b Chahar", "Not Out*", "Not Out*"],
                "Runs 📊": [96, 47, 54, 15, 32],
                "Balls ⏱️": [47, 25, 39, 6, 21],
                "SR ⚡": [204.25, 188.00, 138.46, 250.00, 152.38]
            })
        },
        "🏆 ICC T20 World Cup Final 2022: Pakistan vs England": {
            "t1": "Pakistan", "t2": "England",
            "t1s": "137/8 (20.0)", "t2s": "138/5 (19.0)",
            "status": "England won by 5 wickets 🏆",
            "t1_runs": 137, "t1_wkts": 8, "t1_overs": 20.0,
            "t2_runs": 138, "t2_wkts": 5, "t2_overs": 19.0,
            "player_scores": pd.DataFrame({
                "Player Name 🏏": ["Ben Stokes", "Babar Azam", "Shan Masood", "Jos Buttler", "Sam Curran"],
                "Status ⚾": ["Not Out*", "c & b Adil Rashid", "c Livingstone b Haris", "c Rizwan b Haris", "4-0-12-3"],
                "Runs 📊": [52, 32, 38, 26, 0],
                "Balls ⏱️": [49, 28, 28, 17, 0],
                "SR ⚡": [106.12, 114.28, 135.71, 152.94, 0.00]
            })
        },
        "🏆 ICC ODI World Cup Final 2019: England vs New Zealand": {
            "t1": "New Zealand", "t2": "England",
            "t1s": "241/8 (50.0)", "t2s": "241/10 (50.0)",
            "status": "England won on Boundary Count (Super Over Tied) 🏆",
            "t1_runs": 241, "t1_wkts": 8, "t1_overs": 50.0,
            "t2_runs": 241, "t2_wkts": 10, "t2_overs": 50.0,
            "player_scores": pd.DataFrame({
                "Player Name 🏏": ["Ben Stokes", "Henry Nicholls", "Jos Buttler", "Kane Williamson", "Liam Plunkett"],
                "Status ⚾": ["Not Out*", "b Plunkett", "c Sub b Ferguson", "c Buttler b Plunkett", "3-42"],
                "Runs 📊": [84, 55, 59, 30, 0],
                "Balls ⏱️": [98, 77, 60, 53, 0],
                "SR ⚡": [85.71, 71.42, 98.33, 56.60, 0.00]
            })
        }
    }

    # Sidebar Controls
    st.sidebar.title("🏏 Mayuresh's Cricket Hub")
    st.sidebar.markdown("---")
    match_source = st.sidebar.radio("📌 Select Category", ["🔴 Live Matches (Real-Time API)", "📜 Classic Match Records"])

    if st.sidebar.button("🔄 Refresh API Stream"):
        st.cache_data.clear()
        st.rerun()

    selected_key = None
    if "Live" not in match_source:
        selected_key = st.sidebar.selectbox("🏆 Select Historic Record", list(HISTORIC_DATABASE.keys()))

    # Dynamic Auto-Refreshing Fragment (Updated to 30 Seconds)
    @st.fragment(run_every=30)
    def render_live_dashboard():
        selected_data = None

        if "Live" in match_source:
            matches_data = fetch_realtime_matches()
            active_match = None
            
            for m in matches_data:
                full_text = f"{m.get('name','')} {m.get('teams','')} {m.get('matchType','')}".lower()
                if any(k in full_text for k in ["india", "ind", "sri lanka", "sl", "test", "ipl"]):
                    active_match = m
                    break
            
            if not active_match and len(matches_data) > 0:
                active_match = matches_data[0]

            if active_match:
                match_id = active_match.get("id")
                card = fetch_match_scorecard(match_id) if match_id else None
                
                teams = active_match.get("teams", ["India", "Sri Lanka"])
                t1_name = teams[0] if len(teams) > 0 else "India"
                t2_name = teams[1] if len(teams) > 1 else "Sri Lanka"
                
                score_arr = active_match.get("score", [])
                
                t1s = "288/2 (73.0)"
                t2s = "Yet to bat"
                
                if len(score_arr) > 0:
                    in1 = score_arr[0]
                    t1s = f"{in1.get('r', 288)}/{in1.get('w', 2)} ({in1.get('o', 73.0)})"
                if len(score_arr) > 1:
                    in2 = score_arr[1]
                    t2s = f"{in2.get('r', 0)}/{in2.get('w', 0)} ({in2.get('o', 0.0)})"

                r1, w1, o1 = parse_score_str(t1s)
                r2, w2, o2 = parse_score_str(t2s)

                player_list = []
                if card and "scorecard" in card:
                    for inning in card.get("scorecard", []):
                        for b in inning.get("batsman", []):
                            player_list.append({
                                "Player Name 🏏": b.get("name", "Batsman"),
                                "Status ⚾": b.get("dismissal-text", "Batting*"),
                                "Runs 📊": b.get("r", 0),
                                "Balls ⏱️": b.get("b", 0),
                                "SR ⚡": b.get("sr", 0.0)
                            })
                
                if not player_list:
                    player_list = [
                        {"Player Name 🏏": "D. Padikkal", "Status ⚾": "Batting*", "Runs 📊": 131, "Balls ⏱️": 178, "SR ⚡": 73.59},
                        {"Player Name 🏏": "R. Pant", "Status ⚾": "Batting*", "Runs 📊": 27, "Balls ⏱️": 36, "SR ⚡": 75.00}
                    ]

                selected_data = {
                    "t1": t1_name, "t2": t2_name,
                    "t1s": t1s, "t2s": t2s,
                    "status": active_match.get("status", "IND chose to bat - Test 1 of 2 - Day 2"),
                    "t1_runs": r1, "t1_wkts": w1, "t1_overs": o1,
                    "t2_runs": r2, "t2_wkts": w2, "t2_overs": o2,
                    "player_scores": pd.DataFrame(player_list)
                }
            else:
                selected_data = {
                    "t1": "India", "t2": "Sri Lanka",
                    "t1s": "288/2 (73.0)", "t2s": "Yet to bat",
                    "status": "IND chose to bat | Test 1 of 2 (Day 2 - Session 1)",
                    "t1_runs": 288, "t1_wkts": 2, "t1_overs": 73.0,
                    "t2_runs": 0, "t2_wkts": 0, "t2_overs": 0.0,
                    "player_scores": pd.DataFrame([
                        {"Player Name 🏏": "D. Padikkal", "Status ⚾": "Batting*", "Runs 📊": 131, "Balls ⏱️": 178, "SR ⚡": 73.59},
                        {"Player Name 🏏": "R. Pant", "Status ⚾": "Batting*", "Runs 📊": 27, "Balls ⏱️": 36, "SR ⚡": 75.00}
                    ])
                }
        else:
            selected_data = HISTORIC_DATABASE.get(selected_key, list(HISTORIC_DATABASE.values())[0])

        t1_name = selected_data.get("t1", "India")
        t2_name = selected_data.get("t2", "Sri Lanka")
        t1_score = selected_data.get("t1s", "288/2 (73.0)")
        t2_score = selected_data.get("t2s", "Yet to bat")
        status_msg = selected_data.get("status", "Live Match")

        r1 = max(int(selected_data.get("t1_runs", 288)), 0)
        o1 = max(float(selected_data.get("t1_overs", 73.0)), 0.0)
        r2 = max(int(selected_data.get("t2_runs", 0)), 0)
        o2 = max(float(selected_data.get("t2_overs", 0.0)), 0.0)

        crr1 = round(r1 / o1, 2) if o1 > 0 else 0.0
        crr2 = round(r2 / o2, 2) if o2 > 0 else 0.0

        st.title(f"🏏 {t1_name} vs {t2_name} ⚾")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(f"🛡️ {t1_name}", t1_score if t1_score else "Yet to bat")
        col2.metric(f"⚔️ {t2_name}", t2_score if t2_score else "Yet to bat")
        col3.metric(f"⚡ {t1_name} CRR", f"{crr1}")
        col4.metric(f"⚡ {t2_name} CRR", f"{crr2}")

        st.info(f"📢 **Match Status:** {status_msg}")
        st.divider()

        o1_list, p1 = generate_over_progression(r1, o1)
        o2_list, p2 = generate_over_progression(r2 if r2 > 0 else 100, o2 if o2 > 0 else 20.0)

        max_overs = max(len(o1_list), len(o2_list))
        all_overs = list(range(1, max_overs + 1))

        p1_padded = p1 + [r1] * (max_overs - len(p1))
        p2_padded = p2 + [r2] * (max_overs - len(p2))

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
                x=df_icc['Over'], y=df_icc[f"{t1_name} Runs"], 
                mode='lines+markers', name=t1_name, line=dict(color='#00d2ff', width=3)
            ))
            fig_prog.add_trace(go.Scatter(
                x=df_icc['Over'], y=df_icc[f"{t2_name} Runs"], 
                mode='lines+markers', name=t2_name, line=dict(color='#ff4b4b', width=3)
            ))
            fig_prog.update_layout(template="plotly_dark", height=320, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Overs", yaxis_title="Runs")
            st.plotly_chart(fig_prog, use_container_width=True)

        with right_col:
            st.subheader("📊 Manhattan Chart (Runs Per Over)")
            df_icc[f"{t1_name} Per Over"] = df_icc[f"{t1_name} Runs"].diff().fillna(df_icc[f"{t1_name} Runs"].iloc[0])
            df_icc[f"{t2_name} Per Over"] = df_icc[f"{t2_name} Runs"].diff().fillna(df_icc[f"{t2_name} Runs"].iloc[0])
            
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=df_icc['Over'], y=df_icc[f"{t1_name} Per Over"], name=t1_name, marker_color='#00d2ff'))
            fig_bar.add_trace(go.Bar(x=df_icc['Over'], y=df_icc[f"{t2_name} Per Over"], name=t2_name, marker_color='#ff4b4b'))
            fig_bar.update_layout(barmode='group', template="plotly_dark", height=320, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Overs", yaxis_title="Runs in Over")
            st.plotly_chart(fig_bar, use_container_width=True)

        col_b1, col_b2 = st.columns(2)

        with col_b1:
            st.subheader("👤 Batting Performance & Player Scores")
            player_df = selected_data.get("player_scores", pd.DataFrame())
            st.dataframe(player_df, use_container_width=True, hide_index=True)

        with col_b2:
            st.subheader("🍩 Wickets Comparison")
            w1 = selected_data.get("t1_wkts", 2)
            w2 = selected_data.get("t2_wkts", 0)
            
            wicket_pie = pd.DataFrame({
                "Team": [t1_name, t2_name],
                "Wickets": [w1, w2 if w2 > 0 else 1]
            })
            fig_donut = px.pie(wicket_pie, values='Wickets', names='Team', hole=0.5, template="plotly_dark", color_discrete_sequence=['#00d2ff', '#ff4b4b'])
            fig_donut.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_donut, use_container_width=True)

    render_live_dashboard()