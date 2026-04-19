import streamlit as st
import snowflake.connector
import json
import os
import requests

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="PowerPilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    background-color: #080C12;
    color: #E8EDF5;
    font-family: 'Syne', sans-serif;
}

.main { background-color: #080C12; }

/* Header */
.pilot-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 2rem 0 1rem 0;
    border-bottom: 1px solid #1E2A3A;
    margin-bottom: 2rem;
}
.pilot-logo { font-size: 2.4rem; }
.pilot-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2rem;
    color: #00D4FF;
    letter-spacing: -0.02em;
    margin: 0;
}
.pilot-sub {
    font-size: 0.85rem;
    color: #4A6080;
    margin: 0;
    font-family: 'Space Mono', monospace;
}

/* PowerScore */
.score-ring-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
    background: linear-gradient(135deg, #0D1520 0%, #111C2E 100%);
    border: 1px solid #1E2A3A;
    border-radius: 16px;
}
.score-number {
    font-family: 'Space Mono', monospace;
    font-size: 4rem;
    font-weight: 700;
    color: #00D4FF;
    line-height: 1;
}
.score-label {
    font-size: 0.75rem;
    color: #4A6080;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.4rem;
    font-family: 'Space Mono', monospace;
}
.score-bar-bg {
    width: 100%;
    height: 6px;
    background: #1E2A3A;
    border-radius: 3px;
    margin-top: 1rem;
}
.score-bar-fill {
    height: 6px;
    border-radius: 3px;
    background: linear-gradient(90deg, #0066FF, #00D4FF);
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #0D1520 0%, #111C2E 100%);
    border: 1px solid #1E2A3A;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    height: 100%;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #E8EDF5;
    line-height: 1.1;
}
.metric-unit { font-size: 0.85rem; color: #4A6080; font-family: 'Space Mono', monospace; }
.metric-label { font-size: 0.75rem; color: #4A6080; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.3rem; }
.metric-accent { color: #00D4FF; }
.metric-accent-green { color: #00FF94; }
.metric-accent-orange { color: #FF6B35; }

/* Section headers */
.section-header {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: #4A6080;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 2rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-line { flex: 1; height: 1px; background: #1E2A3A; }

/* Hour chart */
.hour-cell {
    height: 40px;
    border-radius: 4px;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 3px;
    font-size: 0.45rem;
    font-family: 'Space Mono', monospace;
    color: #4A6080;
    position: relative;
}
.hour-label { font-size: 0.5rem; font-family: 'Space Mono', monospace; color: #4A6080; text-align: center; }

/* Device table */
.device-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    padding: 0.8rem 1rem;
    border-bottom: 1px solid #1E2A3A;
    align-items: center;
}
.device-row:last-child { border-bottom: none; }
.device-row-header { font-size: 0.7rem; color: #4A6080; text-transform: uppercase; letter-spacing: 0.1em; font-family: 'Space Mono', monospace; }
.device-name { font-weight: 600; color: #E8EDF5; }
.device-val { font-family: 'Space Mono', monospace; font-size: 0.85rem; color: #A0B4CC; }
.device-cost { font-family: 'Space Mono', monospace; font-size: 0.85rem; color: #00FF94; }

/* Recommendation cards */
.rec-card {
    background: #0D1520;
    border: 1px solid #1E2A3A;
    border-left: 3px solid #00D4FF;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    font-size: 0.9rem;
    color: #C0D0E0;
    line-height: 1.5;
}
.insight-card {
    background: #0D1520;
    border: 1px solid #1E2A3A;
    border-left: 3px solid #00FF94;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    font-size: 0.9rem;
    color: #C0D0E0;
    line-height: 1.5;
}

/* Phantom load */
.phantom-bar-bg { width: 100%; height: 8px; background: #1E2A3A; border-radius: 4px; margin-top: 0.5rem; }
.phantom-bar-fill { height: 8px; border-radius: 4px; background: linear-gradient(90deg, #FF6B35, #FF3366); }

/* Chat */
.chat-bubble-user {
    background: #1E2A3A;
    border-radius: 12px 12px 2px 12px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
    color: #E8EDF5;
    max-width: 80%;
    margin-left: auto;
}
.chat-bubble-ai {
    background: #0D1A2E;
    border: 1px solid #1E2A3A;
    border-radius: 12px 12px 12px 2px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
    color: #C0D0E0;
    max-width: 80%;
    line-height: 1.5;
}

/* Streamlit overrides */
.stButton > button {
    background: linear-gradient(135deg, #0066FF, #00D4FF);
    color: #080C12;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-size: 0.9rem;
    letter-spacing: 0.05em;
}
.stButton > button:hover { opacity: 0.85; }
.stTextInput > div > div > input {
    background: #0D1520;
    border: 1px solid #1E2A3A;
    border-radius: 8px;
    color: #E8EDF5;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
}
.stSelectbox > div > div { background: #0D1520; border: 1px solid #1E2A3A; border-radius: 8px; color: #E8EDF5; }
div[data-testid="stTab"] button { font-family: 'Syne', sans-serif; font-weight: 600; color: #4A6080; }
div[data-testid="stTab"] button[aria-selected="true"] { color: #00D4FF; border-bottom-color: #00D4FF; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SNOWFLAKE  — fresh connection per call
# (avoids stale cursor issues on Streamlit Cloud)
# ─────────────────────────────────────────
def _sf_conn(autocommit=False):
    creds = dict(
        account=st.secrets["SNOWFLAKE_ACCOUNT"],
        user=st.secrets["SNOWFLAKE_USER"],
        password=st.secrets["SNOWFLAKE_PASSWORD"],
        database="POWERPILOT",
        schema="MAIN",
    )
    if autocommit:
        creds["autocommit"] = True
    return snowflake.connector.connect(**creds)


def run_query(query, params=None):
    import pandas as pd
    conn = _sf_conn()
    cur = conn.cursor()
    try:
        cur.execute(query, params) if params else cur.execute(query)
        cols = [c[0] for c in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)
    finally:
        cur.close()
        conn.close()


def run_write(query, params=None):
    conn = _sf_conn(autocommit=True)
    cur = conn.cursor()
    try:
        cur.execute(query, params) if params else cur.execute(query)
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────
# DATA FUNCTIONS  — all params use %s
# ─────────────────────────────────────────
def get_users():
    try:
        df = run_query("SELECT user_id, name, zip_code FROM POWERPILOT.MAIN.users ORDER BY name")
    except Exception:
        df = run_query("SELECT user_id, zip_code FROM POWERPILOT.MAIN.users")
    df.columns = [c.upper() for c in df.columns]
    return df


def get_devices(user_id):
    df = run_query(
        "SELECT device_name, power_on_watts, power_idle_watts, hours_on_per_day, hours_idle_per_day "
        "FROM POWERPILOT.MAIN.devices WHERE user_id = %s",
        params=(user_id,),
    )
    df.columns = [c.upper() for c in df.columns]
    devices = []
    for _, row in df.iterrows():
        def safe(val, default=0):
            try:
                f = float(val)
                return f if f == f else default
            except (TypeError, ValueError):
                return default
        d = {
            "device_name":      str(row["DEVICE_NAME"]),
            "power_on_watts":   safe(row["POWER_ON_WATTS"]),
            "hours_on_per_day": safe(row["HOURS_ON_PER_DAY"]),
            "hours_idle_per_day": safe(row["HOURS_IDLE_PER_DAY"]),
        }
        idle = safe(row["POWER_IDLE_WATTS"], default=None)
        if idle is not None:
            d["power_idle_watts"] = idle
        devices.append(d)
    return devices


def get_rates(zip_code):
    df = run_query(
        "SELECT hour, cost_per_kwh FROM POWERPILOT.MAIN.energy_rates "
        "WHERE zip_code = %s ORDER BY hour",
        params=(zip_code,),
    )
    df.columns = [c.upper() for c in df.columns]
    rate_lookup = {int(r["HOUR"]): float(r["COST_PER_KWH"]) for _, r in df.iterrows()}
    rates, last = [], 0.12
    for h in range(24):
        if h in rate_lookup:
            last = rate_lookup[h]
        rates.append({"hour": h, "cost_per_kwh": last})
    return rates


def add_device(user_id, device_name, watts, hours_on, hours_idle):
    idle_watts = round(float(watts) * 0.05, 2)
    run_write(
        "INSERT INTO POWERPILOT.MAIN.devices "
        "(user_id, device_name, power_on_watts, power_idle_watts, hours_on_per_day, hours_idle_per_day) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        params=(user_id, device_name, float(watts), idle_watts, float(hours_on), float(hours_idle)),
    )


def delete_device(user_id, device_name):
    run_write(
        "DELETE FROM POWERPILOT.MAIN.devices WHERE user_id = %s AND device_name = %s",
        params=(user_id, device_name),
    )


def create_user(user_id, name, zip_code):
    run_write(
        "INSERT INTO POWERPILOT.MAIN.users (user_id, name, zip_code) VALUES (%s, %s, %s)",
        params=(user_id, name, zip_code),
    )


# ─────────────────────────────────────────
# OPTIMIZER
# ─────────────────────────────────────────
def compute_energy_results(data):
    devices = data.get("devices", [])
    rates   = data.get("energy_rates", [])
    avg_rate = sum(r["cost_per_kwh"] for r in rates) / len(rates) if rates else 0.12

    breakdown, total_kwh = [], 0.0
    for device in devices:
        on_w  = device.get("power_on_watts", 0)
        idle_w = device.get("power_idle_watts", on_w * 0.05)
        h_on  = device.get("hours_on_per_day", 0)
        h_idle = device.get("hours_idle_per_day", 0)
        kwh   = (on_w * h_on + idle_w * h_idle) / 1000
        total_kwh += kwh
        breakdown.append({
            "device_name":   device["device_name"],
            "kwh_per_day":   round(kwh, 3),
            "cost_per_month": round(kwh * 30 * avg_rate, 2),
        })

    total_cost = round(total_kwh * 30 * avg_rate, 2)
    sr = sorted(rates, key=lambda r: r["cost_per_kwh"])
    best_hours  = [r["hour"] for r in sr[:6]]
    worst_hours = [r["hour"] for r in sr[-3:]]
    cheap, pricey = (sr[0]["cost_per_kwh"] if sr else avg_rate), (sr[-1]["cost_per_kwh"] if sr else avg_rate)
    savings_pct = round((1 - cheap / pricey) * 100) if pricey else 0
    pot_savings = round(total_cost * savings_pct / 100, 2)

    phantom_w = sum(d.get("power_on_watts", 0) * 0.05 * d.get("hours_idle_per_day", 0) for d in devices)
    phantom_kwh = round(phantom_w / 1000, 3)
    phantom_pct = round(phantom_kwh / total_kwh * 100) if total_kwh else 0

    worst_set = set(worst_hours)
    total_on  = sum(d.get("hours_on_per_day", 0) for d in devices)
    peak_pen  = round(min(30, len(worst_set) / 24 * total_on * 5))
    ineff_pen = round(min(30, phantom_pct * 0.6))
    opk_bonus = round(min(20, savings_pct * 0.2))
    score = max(0, min(100, 100 - peak_pen - ineff_pen + opk_bonus))

    return {
        "summary":      {"total_kwh_per_day": round(total_kwh, 3), "total_cost_per_month": total_cost},
        "breakdown":    breakdown,
        "optimization": {"best_hours": best_hours, "worst_hours": worst_hours,
                         "potential_savings_percent": savings_pct,
                         "potential_monthly_savings_dollars": pot_savings},
        "phantom_load": {"total_watts": round(phantom_w, 1), "daily_kwh": phantom_kwh,
                         "percentage_of_total": phantom_pct},
        "power_score":  score,
    }


# ─────────────────────────────────────────
# AI ENGINE
# ─────────────────────────────────────────
def call_groq(prompt, max_tokens=1024):
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "max_tokens": max_tokens,
              "messages": [{"role": "user", "content": prompt}]},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def generate_recommendation(data):
    devices = data.get("devices", [])
    rates   = data.get("energy_rates", [])
    results = data.get("computed_results", {})
    ps = results.get("power_score", 50)
    prompt = f"""You are an energy optimization AI. Analyze this user's energy data and return recommendations.
Devices: {json.dumps(devices)}
Rates: {json.dumps(rates)}
Summary: {json.dumps(results)}
PowerScore is {ps}/100. Return ONLY valid JSON, no extra text:
{{"current_energy_score":{ps},"new_energy_score":<int higher than {ps} max 100>,"recommendations":["<tip>","<tip>","<tip>"],"estimated_monthly_savings":<float>,"insights":["<insight>","<insight>"],"best_usage_hours":[<ints 0-23>],"worst_usage_hours":[<ints 0-23>]}}"""
    raw = call_groq(prompt)
    try:
        if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:   raw = raw.split("```")[1].split("```")[0].strip()
        return json.loads(raw)
    except Exception:
        return {"error": "Failed to parse AI response"}


def ask_question(question, data):
    prompt = f"""You are PowerPilot, a friendly home energy advisor.
Devices: {json.dumps(data.get('devices',[]))}
Rates: {json.dumps(data.get('energy_rates',[]))}
Summary: {json.dumps(data.get('computed_results',{}))}
User asks: "{question}"
Answer in 2-4 sentences. Friendly, specific, no jargon."""
    return call_groq(prompt, max_tokens=512)


# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
for key, default in [("chat_history", []), ("ai_result", None),
                     ("refresh", 0), ("prev_user", None),
                     ("show_create", False)]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("""
<div class="pilot-header">
    <div class="pilot-logo">⚡</div>
    <div>
        <div class="pilot-title">PowerPilot</div>
        <div class="pilot-sub">SMART ENERGY ADVISOR</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# USER SELECTOR + NEW PROFILE
# ─────────────────────────────────────────
_ = st.session_state.refresh          # triggers re-fetch after create
users_df = get_users()
has_name = "NAME" in users_df.columns

if users_df.empty:
    st.warning("No profiles found. Create one below to get started.")
    display_map = {}
else:
    if has_name:
        display_map = {
            row["USER_ID"]: f"{row['NAME']}  ({row['USER_ID']})"
            for _, row in users_df.iterrows()
        }
    else:
        display_map = {row["USER_ID"]: row["USER_ID"] for _, row in users_df.iterrows()}

col_sel, col_btn = st.columns([4, 1])
with col_sel:
    selected_user = None
    if display_map:
        chosen_label = st.selectbox(
            "Profile", list(display_map.values()), label_visibility="collapsed"
        )
        selected_user = next(k for k, v in display_map.items() if v == chosen_label)

with col_btn:
    if st.button("＋ New Profile"):
        st.session_state.show_create = not st.session_state.show_create

# Reset AI/chat when user switches
if selected_user != st.session_state.prev_user:
    st.session_state.ai_result = None
    st.session_state.chat_history = []
    st.session_state.prev_user = selected_user

# ── Inline create-user form ──
if st.session_state.show_create:
    with st.container():
        st.markdown(
            '<div style="background:#0D1520;border:1px solid #1E2A3A;border-radius:12px;'
            'padding:1.2rem;margin-bottom:1rem;">',
            unsafe_allow_html=True,
        )
        fc1, fc2, fc3 = st.columns([2, 2, 1])
        with fc1:
            new_name = st.text_input("Full name", placeholder="e.g. Alex Smith", key="inp_name")
        with fc2:
            new_zip  = st.text_input("ZIP code",  placeholder="e.g. 13037",      key="inp_zip", max_chars=10)
        with fc3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create", key="btn_create"):
                if new_name.strip() and new_zip.strip():
                    import uuid
                    uid = "u" + uuid.uuid4().hex[:8]
                    try:
                        create_user(uid, new_name.strip(), new_zip.strip())
                        st.success(f"Profile created for {new_name.strip()}!")
                        st.session_state.show_create = False
                        st.session_state.refresh += 1
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Name and ZIP are required.")
        st.markdown("</div>", unsafe_allow_html=True)

if selected_user is None:
    st.stop()


# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
zip_code = str(users_df.loc[users_df["USER_ID"] == selected_user, "ZIP_CODE"].iloc[0])
devices  = get_devices(selected_user)
rates    = get_rates(zip_code)
data = {"user_id": selected_user, "devices": devices, "energy_rates": rates}
computed = compute_energy_results(data)
data["computed_results"] = computed


# ─────────────────────────────────────────
# TOP METRICS
# ─────────────────────────────────────────
power_score      = computed["power_score"]
total_kwh        = computed["summary"]["total_kwh_per_day"]
total_cost       = computed["summary"]["total_cost_per_month"]
potential_savings = computed["optimization"]["potential_monthly_savings_dollars"]
phantom_pct      = computed["phantom_load"]["percentage_of_total"]

col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])
with col1:
    st.markdown(f"""
<div class="score-ring-wrap">
    <div class="score-number">{power_score}</div>
    <div class="score-label">PowerScore</div>
    <div class="score-bar-bg"><div class="score-bar-fill" style="width:{power_score}%"></div></div>
</div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""
<div class="metric-card">
    <div class="metric-value metric-accent">{total_kwh}<span class="metric-unit"> kWh</span></div>
    <div class="metric-label">Daily Usage</div>
</div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""
<div class="metric-card">
    <div class="metric-value">${total_cost}<span class="metric-unit">/mo</span></div>
    <div class="metric-label">Est. Monthly Cost</div>
</div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""
<div class="metric-card">
    <div class="metric-value metric-accent-green">${potential_savings}<span class="metric-unit">/mo</span></div>
    <div class="metric-label">Potential Savings</div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["⚡ Rates & Hours", "📊 Devices", "🤖 AI Advisor", "💬 Chat"])

# ── TAB 1: RATES ──
with tab1:
    st.markdown('<div class="section-header">Time-of-Use Rates <div class="section-line"></div></div>', unsafe_allow_html=True)

    best_h  = set(computed["optimization"]["best_hours"])
    worst_h = set(computed["optimization"]["worst_hours"])
    rate_map = {r["hour"]: r["cost_per_kwh"] for r in rates}
    max_r, min_r = max(rate_map.values(), default=0.25), min(rate_map.values(), default=0.10)

    cells = labels = ""
    for h in range(24):
        rate = rate_map.get(h, 0.13)
        hp = int(((rate - min_r) / (max_r - min_r + 0.001)) * 80 + 20)
        color = "#FF3366" if h in worst_h else ("#00FF94" if h in best_h else "#1E3A5F")
        cells  += f'<div class="hour-cell" style="background:{color};height:{hp}%;">&nbsp;</div>'
        labels += f'<div class="hour-label">{h:02d}</div>'

    st.markdown(f"""
<div style="background:#0D1520;border:1px solid #1E2A3A;border-radius:16px;padding:1.5rem;">
    <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
        <span style="font-size:0.75rem;color:#4A6080;font-family:Space Mono,monospace;">HOUR OF DAY (0-23)</span>
        <span style="font-size:0.75rem;color:#4A6080;font-family:Space Mono,monospace;">
            <span style="color:#00FF94;">■</span> Cheapest &nbsp;
            <span style="color:#FF3366;">■</span> Most Expensive
        </span>
    </div>
    <div style="display:grid;grid-template-columns:repeat(24,1fr);gap:3px;height:80px;align-items:end;">{cells}</div>
    <div style="display:grid;grid-template-columns:repeat(24,1fr);gap:3px;margin-top:4px;">{labels}</div>
</div>""", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown(f"""
<div class="metric-card" style="margin-top:1rem;">
    <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:Space Mono,monospace;">Best Hours to Run Devices</div>
    <div style="font-family:Space Mono,monospace;font-size:1.2rem;color:#00FF94;margin-top:0.5rem;">
        {", ".join(f"{h:02d}:00" for h in sorted(best_h))}
    </div>
</div>""", unsafe_allow_html=True)
    with cb:
        st.markdown(f"""
<div class="metric-card" style="margin-top:1rem;">
    <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:Space Mono,monospace;">Avoid These Hours</div>
    <div style="font-family:Space Mono,monospace;font-size:1.2rem;color:#FF3366;margin-top:0.5rem;">
        {", ".join(f"{h:02d}:00" for h in sorted(worst_h))}
    </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top:2rem;">Hidden Energy Waste <div class="section-line"></div></div>', unsafe_allow_html=True)
    pw  = computed["phantom_load"]["total_watts"]
    pkwh = computed["phantom_load"]["daily_kwh"]
    st.markdown(f"""
<div class="metric-card">
    <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:Space Mono,monospace;">Phantom Load</div>
    <div style="font-family:Space Mono,monospace;font-size:1.5rem;color:#FF6B35;margin-top:0.3rem;">{phantom_pct}% of total usage</div>
    <div style="font-size:0.8rem;color:#4A6080;margin-top:0.3rem;">{pw}W idle draw · {pkwh} kWh/day wasted</div>
    <div class="phantom-bar-bg"><div class="phantom-bar-fill" style="width:{min(phantom_pct,100)}%"></div></div>
</div>""", unsafe_allow_html=True)


# ── TAB 2: DEVICES ──
with tab2:
    st.markdown('<div class="section-header">Device Breakdown <div class="section-line"></div></div>', unsafe_allow_html=True)
    breakdown = computed["breakdown"]

    if not breakdown:
        st.info("No devices yet — add one below.")
    else:
        st.markdown("""
<div style="background:#0D1520;border:1px solid #1E2A3A;border-radius:16px;overflow:hidden;">
    <div class="device-row device-row-header">
        <div>Device</div><div>kWh/day</div><div>Cost/month</div><div>Share</div>
    </div>""", unsafe_allow_html=True)
        for item in breakdown:
            share = round(item["kwh_per_day"] / total_kwh * 100) if total_kwh else 0
            st.markdown(f"""
<div class="device-row">
    <div class="device-name">{item['device_name']}</div>
    <div class="device-val">{item['kwh_per_day']}</div>
    <div class="device-cost">${item['cost_per_month']}</div>
    <div class="device-val">{share}%</div>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Add device
    st.markdown('<div class="section-header" style="margin-top:1.5rem;">Add a Device <div class="section-line"></div></div>', unsafe_allow_html=True)
    da, db, dc, dd = st.columns([2, 1, 1, 1])
    with da: new_dev  = st.text_input("Device name", placeholder="e.g. Refrigerator", key="nd_name")
    with db: new_w    = st.number_input("Watts", min_value=1, max_value=20000, value=100, key="nd_watts")
    with dc: new_hon  = st.number_input("Hours ON/day",   min_value=0.0, max_value=24.0, value=2.0, step=0.5, key="nd_on")
    with dd: new_idle = st.number_input("Hours Idle/day", min_value=0.0, max_value=24.0, value=0.0, step=0.5, key="nd_idle")

    if st.button("⚡ Add Device"):
        if new_dev.strip():
            try:
                add_device(selected_user, new_dev.strip(), new_w, new_hon, new_idle)
                st.session_state.refresh += 1
                st.rerun()
            except Exception as e:
                st.error(f"Failed to add device: {e}")
        else:
            st.error("Device name is required.")

    # Remove device
    if breakdown:
        st.markdown('<div class="section-header" style="margin-top:1rem;">Remove a Device <div class="section-line"></div></div>', unsafe_allow_html=True)
        r1, r2 = st.columns([3, 1])
        with r1: to_del = st.selectbox("Device to remove", [i["device_name"] for i in breakdown], key="del_sel")
        with r2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Remove", key="del_btn"):
                try:
                    delete_device(selected_user, to_del)
                    st.session_state.refresh += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")


# ── TAB 3: AI ADVISOR ──
with tab3:
    st.markdown('<div class="section-header">AI Recommendations <div class="section-line"></div></div>', unsafe_allow_html=True)

    if not devices:
        st.info("Add devices first to get AI recommendations.")
    else:
        if st.button("⚡ Optimize My Usage"):
            with st.spinner("Analyzing your energy profile..."):
                st.session_state.ai_result = generate_recommendation(data)

        if st.session_state.ai_result:
            result = st.session_state.ai_result
            if "error" not in result:
                new_score = result.get("new_energy_score", power_score)
                savings   = result.get("estimated_monthly_savings", 0)
                cx, cy = st.columns(2)
                with cx:
                    st.markdown(f"""
<div class="metric-card">
    <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:Space Mono,monospace;">Score After Optimizing</div>
    <div style="font-family:Space Mono,monospace;font-size:2rem;color:#00D4FF;margin-top:0.3rem;">{power_score} → {new_score}</div>
</div>""", unsafe_allow_html=True)
                with cy:
                    st.markdown(f"""
<div class="metric-card">
    <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:Space Mono,monospace;">Est. Monthly Savings</div>
    <div style="font-family:Space Mono,monospace;font-size:2rem;color:#00FF94;margin-top:0.3rem;">${savings}</div>
</div>""", unsafe_allow_html=True)

                st.markdown('<div style="margin-top:1.5rem;font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:Space Mono,monospace;margin-bottom:0.5rem;">Recommendations</div>', unsafe_allow_html=True)
                for rec in result.get("recommendations", []):
                    st.markdown(f'<div class="rec-card">→ {rec}</div>', unsafe_allow_html=True)

                st.markdown('<div style="margin-top:1rem;font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:Space Mono,monospace;margin-bottom:0.5rem;">Insights</div>', unsafe_allow_html=True)
                for ins in result.get("insights", []):
                    st.markdown(f'<div class="insight-card">◆ {ins}</div>', unsafe_allow_html=True)
            else:
                st.error("AI response error — check your Groq API key in secrets.")


# ── TAB 4: CHAT ──
with tab4:
    st.markdown('<div class="section-header">Chat with PowerPilot <div class="section-line"></div></div>', unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-ai">⚡ {msg["content"]}</div>', unsafe_allow_html=True)

    question = st.text_input("Ask anything about your energy usage...", key="chat_input")
    if st.button("Send") and question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.spinner("Thinking..."):
            answer = ask_question(question, data)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
