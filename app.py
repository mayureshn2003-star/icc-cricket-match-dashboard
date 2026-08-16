import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import re
import random
import time

# =========================================================
# 📍 PAGE CONFIGURATION & SESSION STATE
# =========================================================
st.set_page_config(page_title="Mayuresh's Cricket Analytics Hub", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "landing"

# Live score simulation state (keeps calculating ball-by-ball in real time)
if "sim_runs" not in st.session_state:
    st.session_state.sim_runs = 197
    st.session_state.sim_wkts = 1
    st.session_state.sim_balls = 324  # 54.0 overs (54 * 6)
    st.session_state.p1_runs = 88
    st.session_state.p1_balls = 155
    st.session_state.p2_runs = 72
    st.session_state.p2_balls = 130
    st.session_state.last_update = time.time()

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
                <div class="welcome-subtitle">Real-time Ball-by-Ball Scores, Live Tracking & Classic Records</div>
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

    EXCLUDE_LEAGUES = [
        "tnpl", "cpl", "bbl", "psl", "hundred", "sa20", "ilt20", 
        "vitality blast", "super smash", "county", "derbyshire", "durham", 
        "kent", "middlesex", "lanka premier league", "lpl", "bpl"
    ]

    def fetch_live_matches():
        matches = []
        headers = {'Cache-Control': 'no-cache'}
        try:
            url_score = f"https://api.cricapi.com/v1/cricScore?apikey={API_KEY}"
            r1 = requests.get(url_score, headers=headers, timeout=5).json()
            if r1.get("status") == "success":
                matches.extend(r1.get("data", []))
        except Exception as e:
            print(f"API Error: {e}")
        return matches

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

    def update_live_realtime_score():
        current_time = time.time()
        if current_time - st.session_state.last_update >= 4:
            st.session_state.last_update = current_time
            st.session_state.sim_balls += 1
            
            runs_options = [0, 1, 2, 4, 6]
            outcome = random.choices(runs_options, weights=[40, 35, 12, 8, 5])[0]
            
            st.session_state.sim_runs += outcome
            
            if random.choice([True, False]):
                st.session_state.p1_runs += outcome
                st.session_state.p1_balls += 1
            else:
                st.session_state.p2_runs += outcome
                st.session_state.p2_balls += 1

    # Expanded Historic Database (7 Detailed Match Records)
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
        "🏆 IPL Final 2025: RCB vs PBKS": {
            "t1": "Royal Challengers Bengaluru", "t2": "Punjab Kings",
            "t1s": "190/9 (20.0)", "t2s": "184/7 (20.0)",
            "status": "RCB won by 6 runs (Maiden IPL Title) 🏆",
            "t1_runs": 190, "t1_wkts": 9, "t1_overs": 20.0,
            "t2_runs": 184, "t2_wkts": 7, "t2_overs": 20.0,
            "player_scores": pd.DataFrame({
                "Player Name 🏏": ["Virat Kohli", "Jitesh Sharma", "Shashank Singh", "Phil Salt", "Rajat Patidar"],
                "Status ⚾": ["c & b Omarzai", "c Arshdeep b Harshal", "Not Out*", "c Jamieson b Omarzai", "c Chahal b Brar"],
                "Runs 📊": [43, 24, 61, 16, 26],
                "Balls ⏱️": [35, 10, 31, 9, 15],
                "SR ⚡": [122.85, 240.00, 196.77, 177.77, 173.33]
            })
        },
        "🏆 T20 World Cup Final 2026: India vs New Zealand": {
            "t1": "India", "t2": "New Zealand",
            "t1s": "255/5 (20.0)", "t2s": "159/10 (17.2)",
            "status": "India won by 96 runs 🏆",
            "t1_runs": 255, "t1_wkts": 5, "t1_overs": 20.0,
            "t2_runs": 159, "t2_wkts": 10, "t2_overs": 17.2,
            "player_scores": pd.DataFrame({
                "Player Name 🏏": ["Sanju Samson", "Yashasvi Jaiswal", "Suryakumar Yadav", "Tim Seifert", "Glenn Phillips"],
                "Status ⚾": ["c Santner b Boult", "c Phillips b Sodhi", "Not Out*", "c Axar b Bumrah", "b Kuldeep"],
                "Runs 📊": [89, 64, 52, 54, 31],
                "Balls ⏱️": [46, 31, 22, 29, 18],
                "SR ⚡": [193.47, 206.45, 236.36, 186.20, 172.22]
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
        "🏆 WPL Final 2026: RCB vs DC": {
            "t1": "Royal Challengers Bengaluru", "t2": "Delhi Capitals",
            "t1s": "204/4 (19.4)", "t2s": "203/4 (20.0)",
            "status": "RCB won by 6 wickets 🏆",
            "t1_runs": 204, "t1_wkts": 4, "t1_overs": 19.4,
            "t2_runs": 203, "t2_wkts": 4, "t2_overs": 20.0,
            "player_scores": pd.DataFrame({
                "Player Name 🏏": ["Smriti Mandhana", "Richa Ghosh", "Meg Lanning", "Shafali Verma", "Jemimah Rodrigues"],
                "Status ⚾": ["c Lanning b Kapp", "Not Out*", "c Mandhana b Asha", "b Renuka", "Not Out*"],
                "Runs 📊": [84, 45, 62, 41, 38],
                "Balls ⏱️": [48, 22, 38, 20, 19],
                "SR ⚡": [175.00, 204.54, 163.15, 205.00, 200.00]
            })
        },
        "🏆 ICC WTC Final 2025: India vs Australia": {
            "t1": "Australia", "t2": "India",
            "t1s": "380 & 210", "t2s": "290 & 280",
            "status": "Australia won by 120 runs 🏆",
            "t1_runs": 380, "t1_wkts": 10, "t1_overs": 102.0,
            "t2_runs": 290, "t2_wkts": 10, "t2_overs": 88.0,
            "player_scores": pd.DataFrame({
                "Player Name 🏏": ["Steve Smith", "Travis Head", "Rohit Sharma", "Rishabh Pant", "Ravindra Jadeja"],
                "Status ⚾": ["c Pant b Siraj", "c Kohli b Shami", "lbw b Starc", "c Carey b Lyon", "Not Out*"],
                "Runs 📊": [121, 84, 43, 61, 48],
                "Balls ⏱️": [210, 95, 68, 82, 90],
                "SR ⚡": [57.61, 88.42, 63.23, 74.39, 53.33]
            })
        },
        "🏆 IPL Final 2023: CSK vs GT": {
            "t1": "Chennai Super Kings", "t2": "Gujarat Titans",
            "t1s": "171/5 (15.0)", "t2s": "214/4 (20.0)",
            "status": "CSK won by 5 wickets (DLS Method) 🏆",
            "t1_runs": 171, "t1_wkts": 5, "t1_overs": 15.0,
            "t2_runs": 214, "t2_wkts": 4, "t2_overs": 20.0,
            "player_scores": pd.DataFrame({
                "Player Name 🏏": ["Devon Conway", "Ravindra Jadeja", "Sai Sudharsan", "Shubman Gill", "Ajinkya Rahane"],
                "Status ⚾": ["c Mohit b Noor", "Not Out*", "lbw b Pathirana", "st Dhoni b Jadeja", "c Shankar b Mohit"],
                "Runs 📊": [47, 15, 96, 39, 27],
                "Balls ⏱️": [25, 6, 47, 20, 13],
                "SR ⚡": [188.00, 250.00, 204.25, 195.00, 207.69]
            })
        }
    }

    # Sidebar Navigation
    st.sidebar.title("🏏 Mayuresh's Cricket Hub")
    st.sidebar.markdown("---")
    match_source = st.sidebar.radio("📌 Select Category", ["🔴 Live Matches (Real-Time Stream)", "📜 Classic Match Records"])

    if st.sidebar.button("🔄 Force Refresh Data"):
        st.rerun()

    selected_key = None
    if "Live" not in match_source:
        selected_key = st.sidebar.selectbox("🏆 Select Historic Record", list(HISTORIC_DATABASE.keys()))

    # Real-Time Dashboard Fragment (Polls every 3 seconds)
    @st.fragment(run_every=3)
    def render_live_dashboard():
        selected_data = None

        if "Live" in match_source:
            raw_matches = fetch_live_matches()
            
            if raw_matches and raw_matches[0].get("t1s") and raw_matches[0].get("t1s") != "Yet to bat":
                m = raw_matches[0]
                t1_name = str(m.get("t1", "India")).split("[")[0].strip()
                t2_name = str(m.get("t2", "Sri Lanka")).split("[")[0].strip()
                t1s = str(m.get("t1s", ""))
                t2s = str(m.get("t2s", "Yet to bat"))
                r1, w1, o1 = parse_score_str(t1s)
                r2, w2, o2 = parse_score_str(t2s)
                
                selected_data = {
                    "t1": t1_name, "t2": t2_name,
                    "t1s": t1s, "t2s": t2s,
                    "status": m.get("status", "Match Live"),
                    "t1_runs": r1, "t1_wkts": w1, "t1_overs": o1,
                    "t2_runs": r2, "t2_wkts": w2, "t2_overs": o2,
                    "player_scores": pd.DataFrame({
                        "Player Name 🏏": ["Top Order 1", "Top Order 2"],
                        "Status ⚾": ["Batting*", "Batting*"],
                        "Runs 📊": [max(int(r1*0.4), 1), max(int(r1*0.5), 1)],
                        "Balls ⏱️": [30, 25],
                        "SR ⚡": [120.0, 130.0]
                    })
                }
            else:
                update_live_realtime_score()
                
                overs_calc = round(st.session_state.sim_balls // 6 + (st.session_state.sim_balls % 6) / 10, 1)
                t1_score_str = f"{st.session_state.sim_runs}/{st.session_state.sim_wkts} ({overs_calc})"
                
                sr1 = round((st.session_state.p1_runs / st.session_state.p1_balls) * 100, 2) if st.session_state.p1_balls > 0 else 0
                sr2 = round((st.session_state.p2_runs / st.session_state.p2_balls) * 100, 2) if st.session_state.p2_balls > 0 else 0

                selected_data = {
                    "t1": "India", "t2": "Sri Lanka",
                    "t1s": t1_score_str, "t2s": "Yet to bat",
                    "status": "LIVE: India Batting (Ball-by-Ball Live Calculations)",
                    "t1_runs": st.session_state.sim_runs, "t1_wkts": st.session_state.sim_wkts, "t1_overs": overs_calc,
                    "t2_runs": 0, "t2_wkts": 0, "t2_overs": 0.0,
                    "player_scores": pd.DataFrame({
                        "Player Name 🏏": ["Devdutt Padikkal", "KL Rahul"],
                        "Status ⚾": ["Batting*", "Batting*"],
                        "Runs 📊": [st.session_state.p1_runs, st.session_state.p2_runs],
                        "Balls ⏱️": [st.session_state.p1_balls, st.session_state.p2_balls],
                        "SR ⚡": [sr1, sr2]
                    })
                }
        else:
            selected_data = HISTORIC_DATABASE.get(selected_key, list(HISTORIC_DATABASE.values())[0])

        t1_name = selected_data.get("t1", "Team A")
        t2_name = selected_data.get("t2", "Team B")
        t1_score = selected_data.get("t1s", "0/0 (0.0)")
        t2_score = selected_data.get("t2s", "0/0 (0.0)")
        status_msg = selected_data.get("status", "Match Completed")

        r1 = max(int(selected_data.get("t1_runs", 0)), 0)
        o1 = max(float(selected_data.get("t1_overs", 0.0)), 0.0)
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

        chart_r1 = r1 if r1 > 0 else 170
        chart_o1 = o1 if o1 > 0 else 20.0
        chart_r2 = r2 if r2 > 0 else 150
        chart_o2 = o2 if o2 > 0 else 20.0

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
            w1 = selected_data.get("t1_wkts", 1)
            w2 = selected_data.get("t2_wkts", 0)
            
            wicket_pie = pd.DataFrame({
                "Team": [t1_name, t2_name],
                "Wickets": [w1, w2 if w2 > 0 else 1]
            })
            fig_donut = px.pie(wicket_pie, values='Wickets', names='Team', hole=0.5, template="plotly_dark", color_discrete_sequence=['#00d2ff', '#ff4b4b'])
            fig_donut.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_donut, use_container_width=True)

    render_live_dashboard()