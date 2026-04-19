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

/* Device table */
.device-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    padding: 0.8rem 1rem;
    border-bottom: 1px solid #1E2A3A;
    align-items: center;
}
.device-row:last-child { border-bottom: none; }
.device-row-header {
    font-size: 0.7rem;
    color: #4A6080;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'Space Mono', monospace;
}
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
div[data-testid="stTab"] button {
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    color: #4A6080;
}
div[data-testid="stTab"] button[aria-selected="true"] {
    color: #00D4FF;
    border-bottom-color: #00D4FF;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# FIXED CONFIG — single demo user
# ─────────────────────────────────────────
USER_ID = "u1"

# ─────────────────────────────────────────
# SNOWFLAKE CONNECTION
# ─────────────────────────────────────────
def get_snowflake_connection():
    """Always open a fresh connection - cached connections go stale on Snowflake."""
    return snowflake.connector.connect(
        account=st.secrets["SNOWFLAKE_ACCOUNT"],
        user=st.secrets["SNOWFLAKE_USER"],
        password=st.secrets["SNOWFLAKE_PASSWORD"],
        database="POWERPILOT",
        schema="MAIN",
    )

def run_query(query, params=None):
    import pandas as pd
    conn = get_snowflake_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()

# ─────────────────────────────────────────
# DATA FUNCTIONS
# ─────────────────────────────────────────
def get_devices(user_id):
    df = run_query(
        "SELECT device_name, power_on_watts, power_idle_watts, hours_on_per_day, hours_idle_per_day FROM POWERPILOT.MAIN.devices WHERE user_id = %s",
        params=[user_id]
    )
    devices = []
    for _, row in df.iterrows():
        def safe(val, default=0):
            try:
                f = float(val)
                return f if f == f else default
            except (TypeError, ValueError):
                return default

        device = {
            "device_name": str(row["DEVICE_NAME"]),
            "power_on_watts": safe(row["POWER_ON_WATTS"]),
            "hours_on_per_day": safe(row["HOURS_ON_PER_DAY"]),
            "hours_idle_per_day": safe(row["HOURS_IDLE_PER_DAY"]),
        }
        idle = safe(row["POWER_IDLE_WATTS"], default=None)
        if idle is not None:
            device["power_idle_watts"] = idle
        devices.append(device)
    return devices

def get_fixed_rates():
    return [
        {"hour": 0,  "cost_per_kwh": 0.08},
        {"hour": 1,  "cost_per_kwh": 0.08},
        {"hour": 2,  "cost_per_kwh": 0.08},
        {"hour": 3,  "cost_per_kwh": 0.08},
        {"hour": 4,  "cost_per_kwh": 0.08},
        {"hour": 5,  "cost_per_kwh": 0.08},
        {"hour": 6,  "cost_per_kwh": 0.11},
        {"hour": 7,  "cost_per_kwh": 0.13},
        {"hour": 8,  "cost_per_kwh": 0.13},
        {"hour": 9,  "cost_per_kwh": 0.15},
        {"hour": 10, "cost_per_kwh": 0.15},
        {"hour": 11, "cost_per_kwh": 0.15},
        {"hour": 12, "cost_per_kwh": 0.15},
        {"hour": 13, "cost_per_kwh": 0.15},
        {"hour": 14, "cost_per_kwh": 0.15},
        {"hour": 15, "cost_per_kwh": 0.15},
        {"hour": 16, "cost_per_kwh": 0.20},
        {"hour": 17, "cost_per_kwh": 0.25},
        {"hour": 18, "cost_per_kwh": 0.25},
        {"hour": 19, "cost_per_kwh": 0.25},
        {"hour": 20, "cost_per_kwh": 0.22},
        {"hour": 21, "cost_per_kwh": 0.18},
        {"hour": 22, "cost_per_kwh": 0.12},
        {"hour": 23, "cost_per_kwh": 0.10},
    ]

# ─────────────────────────────────────────
# OPTIMIZER
# ─────────────────────────────────────────
def compute_energy_results(data):
    devices = data.get("devices", [])
    rates = data.get("energy_rates", [])

    avg_rate = sum(r["cost_per_kwh"] for r in rates) / len(rates) if rates else 0.12

    breakdown = []
    total_kwh = 0.0

    COOLING_MONTHS_SET = {6, 7, 8, 9}
    HEATING_MONTHS_SET = {11, 12, 1, 2, 3}

    for device in devices:
        on_watts = device.get("power_on_watts", 0)
        idle_watts = device.get("power_idle_watts", on_watts * 0.05)
        hours_on = device.get("hours_on_per_day", 0)
        hours_idle = device.get("hours_idle_per_day", 0)
        kwh_per_day = (on_watts * hours_on + idle_watts * hours_idle) / 1000
        kind = _classify(device["device_name"])
        # For HVAC devices, cost_per_month reflects only the months they actually run
        if kind == "cooling":
            active_months = len(COOLING_MONTHS_SET)
            seasonal_cost = round(kwh_per_day * 30 * avg_rate * active_months / 12, 2)
        elif kind == "heating":
            active_months = len(HEATING_MONTHS_SET)
            seasonal_cost = round(kwh_per_day * 30 * avg_rate * active_months / 12, 2)
        else:
            seasonal_cost = round(kwh_per_day * 30 * avg_rate, 2)
        # Phantom load for this device: idle draw = 5% of on_watts * idle hours
        device_phantom_watts = on_watts * 0.05 * hours_idle
        device_phantom_cost = round(device_phantom_watts / 1000 * 30 * avg_rate, 2)
        total_kwh += kwh_per_day
        breakdown.append({
            "device_name": device["device_name"],
            "device_type": kind,
            "kwh_per_day": round(kwh_per_day, 3),
            "cost_per_month": seasonal_cost,
            "phantom_watts": round(device_phantom_watts, 1),
            "phantom_cost_month": device_phantom_cost,
        })

    total_cost_per_month = round(total_kwh * 30 * avg_rate, 2)
    sorted_rates = sorted(rates, key=lambda r: r["cost_per_kwh"])
    best_hours = [r["hour"] for r in sorted_rates[:6]]
    worst_hours = [r["hour"] for r in sorted_rates[-3:]]
    cheapest = sorted_rates[0]["cost_per_kwh"] if sorted_rates else avg_rate
    most_expensive = sorted_rates[-1]["cost_per_kwh"] if sorted_rates else avg_rate
    savings_pct = round((1 - cheapest / most_expensive) * 100) if most_expensive else 0
    potential_savings = round(total_cost_per_month * savings_pct / 100, 2)

    phantom_watts = sum(
        device.get("power_on_watts", 0) * 0.05 * device.get("hours_idle_per_day", 0)
        for device in devices
    )
    phantom_kwh = round(phantom_watts / 1000, 3)
    phantom_pct = round(phantom_kwh / total_kwh * 100) if total_kwh and total_kwh == total_kwh else 0

    worst_set = set(worst_hours)
    total_on_hours = sum(d.get("hours_on_per_day", 0) for d in devices)

    # Peak usage penalty: each device-hour during peak costs 0.5 pts, capped at 20.
    peak_device_hours = sum(d.get("hours_on_per_day", 0) for d in devices)
    peak_usage_penalty = round(min(20, peak_device_hours * 0.5))

    # Phantom/idle inefficiency penalty: capped at 15 pts
    inefficiency_penalty = round(min(15, phantom_pct * 0.4))

    # Off-peak bonus: up to 15 pts
    off_peak_bonus = round(min(15, savings_pct * 0.25))

    # Consumption penalty: daily essentials (~10 kWh) incur no penalty.
    # Only excess above 10 kWh/day is penalised; max 20 pts at 60+ kWh/day.
    excess_kwh = max(0.0, total_kwh - 10.0)
    consumption_penalty = round(min(20, (excess_kwh / 50.0) * 20))

    power_score = max(0, min(100, 100 - peak_usage_penalty - inefficiency_penalty - consumption_penalty + off_peak_bonus))

    return {
        "summary": {
            "total_kwh_per_day": round(total_kwh, 3),
            "total_cost_per_month": total_cost_per_month,
        },
        "breakdown": breakdown,
        "optimization": {
            "best_hours": best_hours,
            "worst_hours": worst_hours,
            "potential_savings_percent": savings_pct,
            "potential_monthly_savings_dollars": potential_savings,
        },
        "phantom_load": {
            "total_watts": round(phantom_watts, 1),
            "daily_kwh": phantom_kwh,
            "percentage_of_total": phantom_pct,
        },
        "power_score": power_score,
    }

# ─────────────────────────────────────────
# AI ENGINE (Groq via raw requests)
# ─────────────────────────────────────────
def call_groq(prompt, max_tokens=1024):
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def generate_recommendation(data):
    devices = data.get("devices", [])
    rates = data.get("energy_rates", [])
    results = data.get("computed_results", {})
    power_score = results.get("power_score", 50)

    prompt = f"""You are an energy optimization AI assistant. Analyze this user's energy usage data and return actionable recommendations.

User devices and usage:
{json.dumps(devices, indent=2)}

Time-of-use energy rates (cost per kWh by hour):
{json.dumps(rates, indent=2)}

Computed energy summary:
{json.dumps(results, indent=2)}

The user's current PowerScore is {power_score}/100.
Estimate new_energy_score as what their score could reach if they follow your recommendations (must be higher than {power_score} and MUST NOT exceed 100).

Return a JSON object with exactly this structure (no extra text, just JSON):
{{
  "current_energy_score": {power_score},
  "new_energy_score": <integer higher than {power_score}, max 100>,
  "recommendations": ["<tip>", "<tip>", "<tip>"],
  "estimated_monthly_savings": <float dollars>,
  "insights": ["<insight>", "<insight>"],
  "best_usage_hours": [<hour integers>],
  "worst_usage_hours": [<hour integers>]
}}"""

    raw = call_groq(prompt, max_tokens=1024)
    try:
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        return json.loads(raw)
    except Exception:
        return {"error": "Failed to parse AI response", "raw": raw}

def ask_question(question, data):
    devices = data.get("devices", [])
    results = data.get("computed_results", {})
    rates = data.get("energy_rates", [])

    prompt = f"""You are PowerPilot, a friendly home energy advisor. The user is looking at their home energy dashboard and has a question.

Their devices:
{json.dumps(devices, indent=2)}

Their energy rates by hour:
{json.dumps(rates, indent=2)}

Their current usage summary:
{json.dumps(results, indent=2)}

The user asks: "{question}"

Answer in 2-4 sentences. Be specific to their actual devices and data. Be friendly and practical. No jargon."""

    return call_groq(prompt, max_tokens=512)


def fetch_device_defaults(device_name: str) -> dict:
    """
    Ask Groq to return DOE-average wattage and usage hours for a named device.
    Returns a dict with keys: power_on_watts, hours_on_per_day, hours_idle_per_day.
    Falls back to safe defaults on any failure.
    """
    prompt = f"""You are an energy data expert. A user wants to add "{device_name}" to their home energy tracker.

Using US Department of Energy averages and real-world data for typical American households, provide:
- power_on_watts: the device's typical active wattage (integer)
- hours_on_per_day: average hours the device runs actively per day (float, 0-24)
- hours_idle_per_day: average hours the device sits in standby/idle per day (float, 0-24)

Rules:
- hours_on_per_day + hours_idle_per_day must be <= 24
- Be specific to the device. A refrigerator runs 24h but compressor cycles ~8h active.
- For HVAC, assume a typical US home during peak season.
- Return ONLY a JSON object, no explanation, no markdown:

{{"power_on_watts": <int>, "hours_on_per_day": <float>, "hours_idle_per_day": <float>, "notes": "<one short sentence explaining the estimate>"}}"""

    try:
        raw = call_groq(prompt, max_tokens=200)
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        result = json.loads(raw)
        # Clamp values to valid ranges
        on_w = max(1, min(10000, int(result.get("power_on_watts", 100))))
        h_on = max(0.0, min(24.0, float(result.get("hours_on_per_day", 4))))
        h_idle = max(0.0, min(24.0 - h_on, float(result.get("hours_idle_per_day", 2))))
        notes = result.get("notes", "")
        return {"power_on_watts": on_w, "hours_on_per_day": h_on, "hours_idle_per_day": h_idle, "notes": notes}
    except Exception:
        return {"power_on_watts": 100, "hours_on_per_day": 4.0, "hours_idle_per_day": 2.0, "notes": ""}


# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────

# ─────────────────────────────────────────
# MONTHLY PROJECTION
# ─────────────────────────────────────────
MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
COOLING_MONTHS = {6,7,8,9}
HEATING_MONTHS = {11,12,1,2,3}
COOLING_KEYWORDS = ["ac","a/c","air conditioner","air conditioning","central air","window ac","mini split","mini-split","swamp cooler","evaporative cooler"]
HEATING_KEYWORDS = ["heat","heater","heating","furnace","boiler","heat pump","space heater","baseboard heat","electric heat","radiant heat","floor heat"]
COOLING_INTENSITY = {6:0.70,7:1.00,8:0.95,9:0.60}
HEATING_INTENSITY = {11:0.60,12:1.00,1:1.00,2:0.85,3:0.55}
STANDARD_SCALAR = {1:1.05,2:1.03,3:1.00,4:0.97,5:0.95,6:0.96,7:0.98,8:0.97,9:0.96,10:0.97,11:1.02,12:1.08}

def _classify(name):
    n = name.lower()
    if any(k in n for k in COOLING_KEYWORDS): return "cooling"
    if any(k in n for k in HEATING_KEYWORDS): return "heating"
    return "standard"

def load_devices_from_snowflake(user_id):
    """Load saved devices for this user from Snowflake. Returns [] if table empty or missing."""
    try:
        df = run_query(
            "SELECT device_name, power_on_watts, power_idle_watts, hours_on_per_day, hours_idle_per_day FROM POWERPILOT.MAIN.devices WHERE user_id = %s",
            params=[user_id]
        )
        devices = []
        for _, row in df.iterrows():
            def safe(val, default=0):
                try:
                    f = float(val)
                    return f if f == f else default
                except (TypeError, ValueError):
                    return default
            device = {
                "device_name": str(row["DEVICE_NAME"]),
                "power_on_watts": safe(row["POWER_ON_WATTS"]),
                "hours_on_per_day": safe(row["HOURS_ON_PER_DAY"]),
                "hours_idle_per_day": safe(row["HOURS_IDLE_PER_DAY"]),
            }
            idle = safe(row["POWER_IDLE_WATTS"], default=None)
            if idle is not None:
                device["power_idle_watts"] = idle
            devices.append(device)
        return devices
    except Exception as e:
        st.error(f"Could not load devices from Snowflake: {e}")
        return []


def save_devices_to_snowflake(user_id, devices):
    """Overwrite all devices for this user in Snowflake."""
    conn = get_snowflake_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM POWERPILOT.MAIN.devices WHERE user_id = %s", (user_id,))
        for d in devices:
            cursor.execute("""
                INSERT INTO POWERPILOT.MAIN.devices
                    (user_id, device_name, power_on_watts, power_idle_watts, hours_on_per_day, hours_idle_per_day)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                d["device_name"],
                d.get("power_on_watts", 0),
                d.get("power_idle_watts", d.get("power_on_watts", 0) * 0.05),
                d.get("hours_on_per_day", 0),
                d.get("hours_idle_per_day", 0),
            ))
        conn.commit()
        cursor.close()
    except Exception as e:
        st.error(f"Could not save devices: {e}")
    finally:
        conn.close()


def compute_monthly_projection(devices, avg_rate):
    projection = {}
    for i, month in enumerate(MONTH_NAMES, start=1):
        cost = 0.0
        for d in devices:
            name = d["device_name"]
            kind = _classify(name)
            on_w = d.get("power_on_watts", 0)
            idle_w = d.get("power_idle_watts", on_w * 0.05)
            h_on = d.get("hours_on_per_day", 0)
            h_idle = d.get("hours_idle_per_day", 0)
            if kind == "cooling":
                if i not in COOLING_MONTHS: continue
                intensity = COOLING_INTENSITY.get(i, 0.8)
                kwh = (on_w * intensity * h_on + idle_w * h_idle) / 1000
            elif kind == "heating":
                if i not in HEATING_MONTHS: continue
                intensity = HEATING_INTENSITY.get(i, 0.8)
                kwh = (on_w * intensity * h_on + idle_w * h_idle) / 1000
            else:
                scalar = STANDARD_SCALAR.get(i, 1.0)
                kwh = ((on_w * h_on + idle_w * h_idle) / 1000) * scalar
            cost += kwh * 30 * avg_rate
        projection[month] = round(cost, 2)
    return projection

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None
if "devices" not in st.session_state:
    st.session_state.devices = load_devices_from_snowflake(USER_ID)
if "device_sort_by" not in st.session_state:
    st.session_state.device_sort_by = None
if "device_sort_dir" not in st.session_state:
    st.session_state.device_sort_dir = "desc"

# ─────────────────────────────────────────
# LOAD DATA (fixed single user, fixed rates)
# ─────────────────────────────────────────
devices = st.session_state.devices
rates = get_fixed_rates()

data = {
    "user_id": USER_ID,
    "devices": devices,
    "energy_rates": rates,
}
computed = compute_energy_results(data)
data["computed_results"] = computed

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
# TOP METRICS
# ─────────────────────────────────────────
power_score = computed["power_score"]
total_kwh = computed["summary"]["total_kwh_per_day"]
total_cost = computed["summary"]["total_cost_per_month"]
potential_savings = computed["optimization"]["potential_monthly_savings_dollars"]
phantom_pct = computed["phantom_load"]["percentage_of_total"]

col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])

with col1:
    st.markdown(f"""
    <div class="score-ring-wrap">
        <div class="score-number">{power_score}</div>
        <div class="score-label">PowerScore</div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{power_score}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value metric-accent">{total_kwh}<span class="metric-unit"> kWh</span></div>
        <div class="metric-label">Daily Usage</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">${total_cost}<span class="metric-unit">/mo</span></div>
        <div class="metric-label">Est. Monthly Cost</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value metric-accent-green">${potential_savings}<span class="metric-unit">/mo</span></div>
        <div class="metric-label">Potential Savings</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚡ Rates & Hours", "📊 Devices", "📈 Projection", "🤖 AI Advisor", "💬 Chat"])

# ── TAB 1: RATES & HOURS (interactive hover chart) ──
with tab1:
    st.markdown('<div class="section-header">Time-of-Use Rates <div class="section-line"></div></div>', unsafe_allow_html=True)

    best_hours = set(computed["optimization"]["best_hours"])
    worst_hours = set(computed["optimization"]["worst_hours"])

    rate_map = {r["hour"]: r["cost_per_kwh"] for r in rates}
    max_rate = max(rate_map.values())
    min_rate = min(rate_map.values())

    # Build per-bar data for JS
    bars_data = []
    for h in range(24):
        rate = rate_map[h]
        height_pct = int(((rate - min_rate) / (max_rate - min_rate + 0.001)) * 70 + 20)
        if h in worst_hours:
            category = "peak"
            color = "#FF3366"
            label = "Peak — avoid if possible"
        elif h in best_hours:
            category = "cheap"
            color = "#00FF94"
            label = "Off-peak — great time to run devices"
        else:
            category = "mid"
            color = "#1E3A5F"
            label = "Standard rate"
        bars_data.append({
            "hour": h,
            "rate": rate,
            "height": height_pct,
            "color": color,
            "label": label,
            "category": category,
        })

    bars_json = json.dumps(bars_data)


    hour_labels = "".join(
        f'<div style="font-size:0.5rem;font-family:Space Mono,monospace;color:#4A6080;text-align:center;">{h:02d}</div>'
        for h in range(24)
    )

    import streamlit.components.v1 as components
    components.html(f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background: transparent; font-family: 'Space Mono', monospace; }}
    </style>
    <div style="background:#0D1520;border:1px solid #1E2A3A;border-radius:16px;padding:1.2rem;position:relative;">

        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
            <span style="font-size:0.7rem;color:#4A6080;font-family:monospace;">HOUR OF DAY (0-23)</span>
            <span style="font-size:0.7rem;color:#4A6080;font-family:monospace;">
                <span style="color:#00FF94;">&#9632;</span> Off-peak &nbsp;
                <span style="color:#4A7FA5;">&#9632;</span> Standard &nbsp;
                <span style="color:#FF3366;">&#9632;</span> Peak
            </span>
        </div>

        <div id="pp-tooltip" style="
            display:none;
            position:absolute;
            top:3.2rem;
            background:#0A1628;
            border:1px solid #2A3F5F;
            border-radius:10px;
            padding:0.55rem 0.9rem;
            font-family:monospace;
            font-size:0.72rem;
            color:#E8EDF5;
            pointer-events:none;
            white-space:nowrap;
            z-index:100;
            box-shadow:0 4px 24px rgba(0,0,0,0.6);
            min-width:190px;
        "></div>

        <div id="pp-chart" style="
            display:grid;
            grid-template-columns:repeat(24,1fr);
            gap:3px;
            height:100px;
            align-items:end;
            position:relative;
            cursor:crosshair;
        "></div>

        <div style="display:grid;grid-template-columns:repeat(24,1fr);gap:3px;margin-top:5px;">
            {hour_labels}
        </div>
    </div>

    <script>
    (function() {{
        const bars = {bars_json};
        const chart = document.getElementById('pp-chart');
        const tooltip = document.getElementById('pp-tooltip');

        bars.forEach(function(b) {{
            const bar = document.createElement('div');
            bar.style.height = b.height + '%';
            bar.style.background = b.color;
            bar.style.borderRadius = '4px 4px 2px 2px';
            bar.style.transition = 'filter 0.12s, transform 0.12s';
            bar.style.cursor = 'crosshair';
            bar.style.transformOrigin = 'bottom';

            bar.addEventListener('mouseenter', function() {{
                bar.style.filter = 'brightness(1.5)';
                bar.style.transform = 'scaleY(1.07)';

                const ampm = b.hour < 12 ? 'AM' : 'PM';
                const h12 = b.hour === 0 ? 12 : b.hour > 12 ? b.hour - 12 : b.hour;
                const timeStr = h12 + ':00 ' + ampm;

                tooltip.innerHTML =
                    '<div style="color:#4A6080;font-size:0.62rem;margin-bottom:5px;letter-spacing:0.05em;">' +
                        'HOUR ' + String(b.hour).padStart(2,'0') + ' &nbsp;&middot;&nbsp; ' + timeStr +
                    '</div>' +
                    '<div style="font-size:0.95rem;color:#E8EDF5;margin-bottom:5px;">' +
                        '$' + b.rate.toFixed(4) +
                        '<span style="font-size:0.65rem;color:#4A6080;"> / kWh</span>' +
                    '</div>' +
                    '<div style="color:' + b.color + ';font-size:0.7rem;">&#9679; ' + b.label + '</div>';

                const chartRect = chart.getBoundingClientRect();
                const barRect = bar.getBoundingClientRect();
                const barCenterX = barRect.left - chartRect.left + barRect.width / 2;
                const tooltipWidth = 210;
                const maxLeft = chartRect.width - tooltipWidth - 8;
                tooltip.style.left = Math.max(4, Math.min(barCenterX - tooltipWidth / 2, maxLeft)) + 'px';
                tooltip.style.display = 'block';
            }});

            bar.addEventListener('mouseleave', function() {{
                bar.style.filter = '';
                bar.style.transform = '';
                tooltip.style.display = 'none';
            }});

            chart.appendChild(bar);
        }});
    }})();
    </script>
    """, height=185)


    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class="metric-card" style="margin-top:1rem;">
            <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:'Space Mono',monospace;">Best Hours to Run Devices</div>
            <div style="font-family:'Space Mono',monospace;font-size:1.2rem;color:#00FF94;margin-top:0.5rem;">
                {", ".join(f"{h:02d}:00" for h in sorted(best_hours))}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class="metric-card" style="margin-top:1rem;">
            <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:'Space Mono',monospace;">Avoid These Hours</div>
            <div style="font-family:'Space Mono',monospace;font-size:1.2rem;color:#FF3366;margin-top:0.5rem;">
                {", ".join(f"{h:02d}:00" for h in sorted(worst_hours))}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Phantom load
    st.markdown('<div class="section-header" style="margin-top:2rem;">Hidden Energy Waste <div class="section-line"></div></div>', unsafe_allow_html=True)
    phantom_watts = computed["phantom_load"]["total_watts"]
    phantom_kwh = computed["phantom_load"]["daily_kwh"]

    st.markdown(f"""
    <div class="metric-card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:'Space Mono',monospace;">Phantom Load</div>
                <div style="font-family:'Space Mono',monospace;font-size:1.5rem;color:#FF6B35;margin-top:0.3rem;">{phantom_pct}% of total usage</div>
                <div style="font-size:0.8rem;color:#4A6080;margin-top:0.3rem;">{phantom_watts}W idle draw · {phantom_kwh} kWh/day wasted</div>
            </div>
        </div>
        <div class="phantom-bar-bg">
            <div class="phantom-bar-fill" style="width:{min(phantom_pct,100)}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── TAB 2: DEVICE BREAKDOWN ──
with tab2:
    st.markdown('<div class="section-header">Device Breakdown <div class="section-line"></div></div>', unsafe_allow_html=True)

    breakdown = computed["breakdown"]

    # ── Sort controls ──
    def _set_sort(col):
        if st.session_state.device_sort_by == col:
            st.session_state.device_sort_dir = "asc" if st.session_state.device_sort_dir == "desc" else "desc"
        else:
            st.session_state.device_sort_by = col
            st.session_state.device_sort_dir = "desc"

    # Pre-compute shares so we can sort by them
    breakdown_with_share = []
    for item in breakdown:
        share = round(item["kwh_per_day"] / total_kwh * 100) if total_kwh else 0
        breakdown_with_share.append({**item, "share": share})

    sort_by = st.session_state.device_sort_by
    sort_dir = st.session_state.device_sort_dir
    if sort_by == "kwh":
        breakdown_with_share = sorted(breakdown_with_share, key=lambda x: x["kwh_per_day"], reverse=(sort_dir == "desc"))
    elif sort_by == "cost":
        breakdown_with_share = sorted(breakdown_with_share, key=lambda x: x["cost_per_month"], reverse=(sort_dir == "desc"))
    elif sort_by == "share":
        breakdown_with_share = sorted(breakdown_with_share, key=lambda x: x["share"], reverse=(sort_dir == "desc"))

    def _sort_arrow(col):
        if st.session_state.device_sort_by != col:
            return " ↕"
        return " ↓" if st.session_state.device_sort_dir == "desc" else " ↑"

    # ── Device table header with clickable sort buttons ──
    hdr_name, hdr_kwh, hdr_cost, hdr_share, hdr_del = st.columns([2, 1, 1, 1, 0.4])
    with hdr_name:
        st.markdown('<div style="padding:0.5rem 0.5rem;font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:Space Mono,monospace;border-bottom:1px solid #1E2A3A;">Device</div>', unsafe_allow_html=True)
    with hdr_kwh:
        if st.button(f"kWh/day{_sort_arrow('kwh')}", key="sort_kwh", help="Sort by kWh/day"):
            _set_sort("kwh"); st.rerun()
    with hdr_cost:
        if st.button(f"Cost/mo{_sort_arrow('cost')}", key="sort_cost", help="Sort by Cost/month"):
            _set_sort("cost"); st.rerun()
    with hdr_share:
        if st.button(f"Share{_sort_arrow('share')}", key="sort_share", help="Sort by Share"):
            _set_sort("share"); st.rerun()
    with hdr_del:
        st.markdown("", unsafe_allow_html=True)

    st.markdown('<div style="border-bottom:1px solid #1E2A3A;margin-bottom:0.2rem;"></div>', unsafe_allow_html=True)

    # ── Device rows ──
    for display_idx, item in enumerate(breakdown_with_share):
        # Find original index in session_state.devices for deletion
        orig_idx = next(
            (i for i, d in enumerate(st.session_state.devices) if d["device_name"] == item["device_name"]),
            display_idx
        )
        share = item["share"]
        kind = item.get("device_type", "standard")
        if kind == "cooling":
            season_badge = ' <span style="font-size:0.62rem;color:#00D4FF;background:#0A1E2E;border:1px solid #00D4FF44;border-radius:4px;padding:1px 5px;margin-left:4px;">❄ Summer only</span>'
        elif kind == "heating":
            season_badge = ' <span style="font-size:0.62rem;color:#FF6B35;background:#1E0A00;border:1px solid #FF6B3544;border-radius:4px;padding:1px 5px;margin-left:4px;">🔥 Winter only</span>'
        else:
            season_badge = ""
        cost_note = '<span style="font-size:0.65rem;color:#4A6080;"> avg</span>' if kind in ("cooling","heating") else ""
        col_name, col_kwh, col_cost, col_share, col_del = st.columns([2, 1, 1, 1, 0.4])
        with col_name:
            st.markdown(f'<div style="padding:0.7rem 0.5rem;font-weight:600;color:#E8EDF5;border-bottom:1px solid #1E2A3A;">{item["device_name"]}{season_badge}</div>', unsafe_allow_html=True)
        with col_kwh:
            kwh_color = "#00D4FF" if sort_by == "kwh" else "#A0B4CC"
            st.markdown(f'<div style="padding:0.7rem 0.5rem;font-family:Space Mono,monospace;font-size:0.85rem;color:{kwh_color};border-bottom:1px solid #1E2A3A;">{item["kwh_per_day"]}</div>', unsafe_allow_html=True)
        with col_cost:
            cost_color = "#00D4FF" if sort_by == "cost" else "#00FF94"
            st.markdown(f'<div style="padding:0.7rem 0.5rem;font-family:Space Mono,monospace;font-size:0.85rem;color:{cost_color};border-bottom:1px solid #1E2A3A;">${item["cost_per_month"]}{cost_note}</div>', unsafe_allow_html=True)
        with col_share:
            share_color = "#00D4FF" if sort_by == "share" else "#A0B4CC"
            st.markdown(f'<div style="padding:0.7rem 0.5rem;font-family:Space Mono,monospace;font-size:0.85rem;color:{share_color};border-bottom:1px solid #1E2A3A;">{share}%</div>', unsafe_allow_html=True)
        with col_del:
            if st.button("🗑", key=f"del_{display_idx}", help=f"Remove {item['device_name']}"):
                st.session_state.devices.pop(orig_idx)
                save_devices_to_snowflake(USER_ID, st.session_state.devices)
                st.session_state.ai_result = None
                st.rerun()

    # ── Add Device expander ──
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Staging keys for AI-prefilled values (never collide with widget keys) ──
    if "_add_watts_val" not in st.session_state:
        st.session_state["_add_watts_val"] = 100
    if "_add_hours_on_val" not in st.session_state:
        st.session_state["_add_hours_on_val"] = 4
    if "_add_hours_idle_val" not in st.session_state:
        st.session_state["_add_hours_idle_val"] = 2
    if "_add_device_notes" not in st.session_state:
        st.session_state["_add_device_notes"] = ""
    if "_add_ai_loaded" not in st.session_state:
        st.session_state["_add_ai_loaded"] = False

    with st.expander("＋ Add a Device", expanded=False):
        st.markdown('<div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:Space Mono,monospace;margin-bottom:1rem;">New Device Parameters</div>', unsafe_allow_html=True)

        # ── Device name row + AI lookup button ──
        name_col, btn_col = st.columns([3, 1])
        with name_col:
            new_name = st.text_input(
                "Device Name",
                placeholder="e.g. Washing Machine, Central AC, Mini Fridge…",
                key="add_name",
            )
        with btn_col:
            st.markdown("<div style='margin-top:1.75rem;'></div>", unsafe_allow_html=True)
            lookup_clicked = st.button("⚡ AI Lookup", key="ai_lookup", help="Auto-fill wattage & hours using DOE averages")

        if lookup_clicked:
            name_val = st.session_state.get("add_name", "").strip()
            if not name_val:
                st.warning("Enter a device name first, then click AI Lookup.")
            else:
                with st.spinner(f"Looking up DOE averages for **{name_val}**…"):
                    defaults = fetch_device_defaults(name_val)
                h_on = int(round(defaults["hours_on_per_day"]))
                h_idle = min(int(round(defaults["hours_idle_per_day"])), 24 - h_on)
                # Write to staging keys — safe because these are not widget keys
                st.session_state["_add_watts_val"] = defaults["power_on_watts"]
                st.session_state["_add_hours_on_val"] = h_on
                st.session_state["_add_hours_idle_val"] = h_idle
                st.session_state["_add_device_notes"] = defaults.get("notes", "")
                st.session_state["_add_ai_loaded"] = True
                st.rerun()

        # Show AI note banner if defaults were just loaded
        if st.session_state.get("_add_ai_loaded") and st.session_state.get("_add_device_notes"):
            st.markdown(f"""
            <div style="background:#0A1E10;border:1px solid #00FF9433;border-left:3px solid #00FF94;
                        border-radius:8px;padding:0.6rem 1rem;margin-bottom:0.8rem;
                        font-size:0.8rem;color:#80FFCC;font-family:Space Mono,monospace;">
                ⚡ AI estimate: {st.session_state['_add_device_notes']}
            </div>
            """, unsafe_allow_html=True)

        # ── Wattage + sliders ──
        # When AI Lookup fires, we write the staging keys AND forcibly update the
        # widget keys so the new value is reflected immediately after rerun.
        if st.session_state.get("_add_ai_loaded"):
            st.session_state["add_watts"] = st.session_state["_add_watts_val"]
            st.session_state["add_hours_on"] = st.session_state["_add_hours_on_val"]
            st.session_state["add_hours_idle"] = st.session_state["_add_hours_idle_val"]
            st.session_state["_add_ai_loaded"] = False  # consume the flag

        new_watts = st.number_input(
            "Wattage (W)",
            min_value=1,
            max_value=10000,
            value=st.session_state.get("add_watts", 100),
            step=10,
            key="add_watts",
        )

        st.markdown('<div style="font-size:0.75rem;color:#4A6080;font-family:Space Mono,monospace;margin:1rem 0 0.3rem 0;">HOURS PER DAY</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.72rem;color:#4A6080;margin-bottom:0.5rem;">Split the 24-hour day between active and idle time. Remaining hours are off.</div>', unsafe_allow_html=True)

        hours_on = st.slider(
            "Hours ON per day",
            min_value=0.0,
            max_value=24.0,
            value=float(st.session_state.get("add_hours_on", 4)),
            step=0.25,
            key="add_hours_on",
            format="%.2f h",
        )
        remaining = round(24.0 - hours_on, 2)
        hours_idle = st.slider(
            "Hours IDLE per day",
            min_value=0.0,
            max_value=remaining,
            value=min(float(st.session_state.get("add_hours_idle", 2)), remaining),
            step=0.25,
            key="add_hours_idle",
            format="%.2f h",
        )
        hours_off = round(24.0 - hours_on - hours_idle, 2)

        # Live preview bar
        st.markdown(f"""
        <div style="display:flex;gap:6px;margin:0.8rem 0;height:18px;border-radius:6px;overflow:hidden;">
            <div style="flex:{max(hours_on,0.01)};background:#00D4FF;border-radius:4px;" title="ON"></div>
            <div style="flex:{max(hours_idle,0.01)};background:#FF6B35;border-radius:4px;" title="IDLE"></div>
            <div style="flex:{max(hours_off,0.01)};background:#1E2A3A;border-radius:4px;" title="OFF"></div>
        </div>
        <div style="display:flex;gap:1.5rem;font-size:0.7rem;font-family:Space Mono,monospace;color:#4A6080;margin-bottom:1rem;">
            <span><span style="color:#00D4FF;">■</span> ON: {hours_on:.2f}h</span>
            <span><span style="color:#FF6B35;">■</span> IDLE: {hours_idle:.2f}h</span>
            <span><span style="color:#4A6080;">■</span> OFF: {hours_off:.2f}h</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Add Device", key="add_submit"):
            if new_name.strip():
                st.session_state.devices.append({
                    "device_name": new_name.strip(),
                    "power_on_watts": float(new_watts),
                    "power_idle_watts": float(new_watts) * 0.05,
                    "hours_on_per_day": float(hours_on),
                    "hours_idle_per_day": float(hours_idle),
                })
                save_devices_to_snowflake(USER_ID, st.session_state.devices)
                st.session_state.ai_result = None
                # Reset all add-device state for next use
                for k in ["add_watts", "add_hours_on", "add_hours_idle",
                          "_add_watts_val", "_add_hours_on_val", "_add_hours_idle_val",
                          "_add_device_notes", "_add_ai_loaded"]:
                    st.session_state.pop(k, None)
                st.rerun()
            else:
                st.warning("Please enter a device name.")

# ── TAB 4: AI ADVISOR ──
with tab4:
    st.markdown('<div class="section-header">AI Recommendations <div class="section-line"></div></div>', unsafe_allow_html=True)

    if st.button("⚡ Optimize My Usage"):
        with st.spinner("Analyzing your energy profile..."):
            result = generate_recommendation(data)
            st.session_state.ai_result = result

    if st.session_state.ai_result:
        result = st.session_state.ai_result
        if "error" not in result:
            new_score = min(100, result.get("new_energy_score", power_score))
            monthly_savings = result.get("estimated_monthly_savings", 0)

            col_x, col_y = st.columns(2)
            with col_x:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:'Space Mono',monospace;">Score After Optimizing</div>
                    <div style="font-family:'Space Mono',monospace;font-size:2rem;color:#00D4FF;margin-top:0.3rem;">{power_score} → {new_score}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_y:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:'Space Mono',monospace;">Est. Monthly Savings</div>
                    <div style="font-family:'Space Mono',monospace;font-size:2rem;color:#00FF94;margin-top:0.3rem;">${monthly_savings}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div style="margin-top:1.5rem;font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:Space Mono,monospace;margin-bottom:0.5rem;">Recommendations</div>', unsafe_allow_html=True)
            for rec in result.get("recommendations", []):
                st.markdown(f'<div class="rec-card">→ {rec}</div>', unsafe_allow_html=True)

            st.markdown('<div style="margin-top:1rem;font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:Space Mono,monospace;margin-bottom:0.5rem;">Insights</div>', unsafe_allow_html=True)
            for insight in result.get("insights", []):
                st.markdown(f'<div class="insight-card">◆ {insight}</div>', unsafe_allow_html=True)
        else:
            st.error("AI response error. Check your Groq API key in secrets.")

# ── TAB 5: CHAT ──
with tab5:
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

# ── TAB 3: PROJECTION ──
with tab3:
    st.markdown('<div class="section-header">Annual Cost Projection <div class="section-line"></div></div>', unsafe_allow_html=True)

    avg_rate_proj = sum(r["cost_per_kwh"] for r in rates) / len(rates) if rates else 0.12
    monthly_proj = compute_monthly_projection(devices, avg_rate_proj)

    months = MONTH_NAMES
    costs = [monthly_proj[m] for m in months]
    annual_total = round(sum(costs), 2)
    avg_monthly = round(annual_total / 12, 2)
    savings_pct = computed["optimization"]["potential_savings_percent"]
    annual_savings = round(annual_total * savings_pct / 100, 2)

    # ── Summary metric cards ──
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:'Space Mono',monospace;">Annual Total</div>
            <div style="font-family:'Space Mono',monospace;font-size:2rem;color:#E8EDF5;margin-top:0.4rem;">${annual_total:,.2f}</div>
            <div style="font-size:0.75rem;color:#4A6080;margin-top:0.3rem;">projected this year</div>
        </div>
        """, unsafe_allow_html=True)
    with mc2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:'Space Mono',monospace;">Avg Monthly Cost</div>
            <div style="font-family:'Space Mono',monospace;font-size:2rem;color:#00D4FF;margin-top:0.4rem;">${avg_monthly:,.2f}</div>
            <div style="font-size:0.75rem;color:#4A6080;margin-top:0.3rem;">per month average</div>
        </div>
        """, unsafe_allow_html=True)
    with mc3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:0.7rem;color:#4A6080;text-transform:uppercase;letter-spacing:0.1em;font-family:'Space Mono',monospace;">Potential Annual Savings</div>
            <div style="font-family:'Space Mono',monospace;font-size:2rem;color:#00FF94;margin-top:0.4rem;">${annual_savings:,.2f}</div>
            <div style="font-size:0.75rem;color:#4A6080;margin-top:0.3rem;">if shifted to off-peak hours</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Interactive line chart with savings toggle ──
    import streamlit.components.v1 as components
    savings_costs = [round(c * (1 - savings_pct / 100), 2) for c in costs]
    chart_data = [{"month": m, "cost": c, "savings_cost": s} for m, c, s in zip(months, costs, savings_costs)]
    chart_json = json.dumps(chart_data)
    all_vals = costs + savings_costs
    max_cost = max(all_vals) if all_vals else 1
    min_cost = min(v for v in all_vals if v > 0) if any(v > 0 for v in all_vals) else 0

    components.html(f"""
    <style>
        * {{ box-sizing:border-box; margin:0; padding:0; }}
        body {{ background:transparent; font-family:monospace; }}
        .tog-btn {{
            font-family:monospace; font-size:0.7rem; padding:4px 12px;
            border-radius:6px; border:1px solid; cursor:pointer;
            transition:all 0.15s; letter-spacing:0.05em;
        }}
    </style>
    <div style="background:#0D1520;border:1px solid #1E2A3A;border-radius:16px;padding:1.4rem 1.6rem;position:relative;">

        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.2rem;">
            <div style="font-size:0.7rem;color:#4A6080;letter-spacing:0.1em;">MONTHLY COST PROJECTION</div>
            <div style="display:flex;gap:8px;">
                <button id="tog-actual" class="tog-btn" style="color:#00D4FF;border-color:#00D4FF;background:#00D4FF22;">&#11044; Actual</button>
                <button id="tog-savings" class="tog-btn" style="color:#00FF94;border-color:#00FF94;background:#00FF9422;">&#11044; With Savings</button>
            </div>
        </div>

        <div id="proj-tooltip" style="display:none;position:absolute;background:#0A1628;border:1px solid #2A3F5F;border-radius:10px;padding:0.5rem 0.85rem;font-family:monospace;font-size:0.72rem;color:#E8EDF5;pointer-events:none;white-space:nowrap;z-index:100;box-shadow:0 4px 24px rgba(0,0,0,0.6);min-width:160px;"></div>

        <div style="position:relative;">
            <div id="proj-yaxis" style="position:absolute;left:0;top:0;bottom:24px;width:52px;display:flex;flex-direction:column;justify-content:space-between;align-items:flex-end;padding-right:8px;"></div>
            <div style="margin-left:56px;">
                <svg id="proj-svg" width="100%" height="220" style="overflow:visible;"></svg>
                <div id="proj-xlabels" style="display:grid;grid-template-columns:repeat(12,1fr);margin-top:6px;"></div>
            </div>
        </div>
    </div>

    <script>
    (function() {{
        const data = {chart_json};
        const maxC = {max_cost};
        const minC = {min_cost};
        const PAD = 12, H = 200;
        let showActual = true, showSavings = true;

        const svg    = document.getElementById('proj-svg');
        const tip    = document.getElementById('proj-tooltip');
        const yaxis  = document.getElementById('proj-yaxis');
        const xlabels = document.getElementById('proj-xlabels');
        const togA   = document.getElementById('tog-actual');
        const togS   = document.getElementById('tog-savings');

        const range = maxC - minC || 1;
        for (let i = 4; i >= 0; i--) {{
            const val = minC + (range * i / 4);
            const div = document.createElement('div');
            div.style.cssText = 'font-size:0.6rem;color:#4A6080;font-family:monospace;';
            div.textContent = '$' + val.toFixed(0);
            yaxis.appendChild(div);
        }}
        data.forEach(function(d) {{
            const div = document.createElement('div');
            div.style.cssText = 'font-size:0.6rem;color:#4A6080;font-family:monospace;text-align:center;';
            div.textContent = d.month;
            xlabels.appendChild(div);
        }});

        function getY(v) {{ return PAD + (H - PAD) * (1 - (v - minC) / range); }}
        function mkPath(pts) {{ return pts.map((p,i)=>(i===0?'M':'L')+p.x.toFixed(1)+','+p.y.toFixed(1)).join(' '); }}
        function ns(tag) {{ return document.createElementNS('http://www.w3.org/2000/svg', tag); }}

        let elActualArea, elActualLine, elSavingsArea, elSavingsLine;
        let aDots=[], sDots=[];

        function render(W) {{
            svg.innerHTML=''; aDots=[]; sDots=[];
            const step = W / 12;

            const apts = data.map((d,i)=>({{ x:step*i+step/2, y:getY(d.cost),         cost:d.cost, sc:d.savings_cost, month:d.month }}));
            const spts = data.map((d,i)=>({{ x:step*i+step/2, y:getY(d.savings_cost),  cost:d.cost, sc:d.savings_cost, month:d.month }}));

            // Defs
            const defs = ns('defs');
            [['linegrad','rgba(0,212,255,0.3)','rgba(0,212,255,0)'],
             ['savingsgrad','rgba(0,255,148,0.2)','rgba(0,255,148,0)']].forEach(([id,c0,c1])=>{{
                const g=ns('linearGradient');
                g.setAttribute('id',id); g.setAttribute('x1','0'); g.setAttribute('y1','0');
                g.setAttribute('x2','0'); g.setAttribute('y2','1');
                [[0,c0],[1,c1]].forEach(([pct,col])=>{{
                    const s=ns('stop'); s.setAttribute('offset',pct); s.setAttribute('stop-color',col); g.appendChild(s);
                }});
                defs.appendChild(g);
            }});
            svg.appendChild(defs);

            // Grid
            for(let i=0;i<=4;i++){{
                const y=PAD+(H-PAD)*i/4, gl=ns('line');
                gl.setAttribute('x1','0');gl.setAttribute('x2',W);gl.setAttribute('y1',y);gl.setAttribute('y2',y);
                gl.setAttribute('stroke','#1E2A3A');gl.setAttribute('stroke-width','1');
                svg.appendChild(gl);
            }}

            function mkArea(pts,gid){{
                const el=ns('path');
                el.setAttribute('d', mkPath(pts)+' L'+pts[pts.length-1].x.toFixed(1)+','+(H+PAD)+' L'+pts[0].x.toFixed(1)+','+(H+PAD)+' Z');
                el.setAttribute('fill','url(#'+gid+')'); return el;
            }}
            function mkLine(pts,color,w,dash){{
                const el=ns('path'); el.setAttribute('d',mkPath(pts));
                el.setAttribute('stroke',color); el.setAttribute('stroke-width',w);
                el.setAttribute('fill','none'); el.setAttribute('stroke-linejoin','round'); el.setAttribute('stroke-linecap','round');
                if(dash) el.setAttribute('stroke-dasharray',dash); return el;
            }}

            elSavingsArea = mkArea(spts,'savingsgrad'); svg.appendChild(elSavingsArea);
            elSavingsLine = mkLine(spts,'#00FF94','2','6,3'); svg.appendChild(elSavingsLine);
            elActualArea  = mkArea(apts,'linegrad');   svg.appendChild(elActualArea);
            elActualLine  = mkLine(apts,'#00D4FF','2.5',null); svg.appendChild(elActualLine);

            // Savings dots
            spts.forEach(function(p){{
                const d=ns('circle');
                d.setAttribute('cx',p.x); d.setAttribute('cy',p.y); d.setAttribute('r','3');
                d.setAttribute('fill','#00FF94'); d.setAttribute('stroke','#080C12'); d.setAttribute('stroke-width','2');
                svg.appendChild(d); sDots.push(d);
            }});

            // Actual dots + hit zones
            apts.forEach(function(p,idx){{
                const vl=ns('line');
                vl.setAttribute('x1',p.x);vl.setAttribute('x2',p.x);vl.setAttribute('y1',0);vl.setAttribute('y2',H+PAD);
                vl.setAttribute('stroke','#2A3F5F');vl.setAttribute('stroke-width','1');vl.setAttribute('stroke-dasharray','4,3');
                vl.style.display='none'; svg.appendChild(vl);

                const d=ns('circle');
                d.setAttribute('cx',p.x);d.setAttribute('cy',p.y);d.setAttribute('r','4');
                d.setAttribute('fill','#00D4FF');d.setAttribute('stroke','#080C12');d.setAttribute('stroke-width','2');
                svg.appendChild(d); aDots.push(d);

                const hit=ns('rect');
                hit.setAttribute('x',p.x-step/2);hit.setAttribute('y',0);
                hit.setAttribute('width',step);hit.setAttribute('height',H+PAD);
                hit.setAttribute('fill','transparent');hit.style.cursor='crosshair';
                svg.appendChild(hit);

                hit.addEventListener('mouseenter',function(){{
                    if(showActual){{ d.setAttribute('r','6'); d.setAttribute('fill','#FFD700'); }}
                    if(showSavings) sDots[idx].setAttribute('r','5');
                    vl.style.display='';
                    let html='<div style="color:#4A6080;font-size:0.62rem;margin-bottom:6px;letter-spacing:0.05em;">'+p.month.toUpperCase()+'</div>';
                    if(showActual)  html+='<div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;"><span style="color:#00D4FF;font-size:0.65rem;">&#11044; Actual</span><span style="font-size:0.9rem;color:#E8EDF5;">$'+p.cost.toFixed(2)+'</span><span style="font-size:0.6rem;color:#4A6080;">/mo</span></div>';
                    if(showSavings) html+='<div style="display:flex;align-items:center;gap:6px;"><span style="color:#00FF94;font-size:0.65rem;">&#11044; Savings</span><span style="font-size:0.9rem;color:#00FF94;">$'+p.sc.toFixed(2)+'</span><span style="font-size:0.6rem;color:#4A6080;">/mo</span></div>';
                    tip.innerHTML=html;
                    const sr=svg.getBoundingClientRect(), wr=svg.parentElement.parentElement.getBoundingClientRect();
                    const tx=sr.left-wr.left+p.x, ty=sr.top-wr.top+p.y-64;
                    tip.style.left=Math.max(4,Math.min(tx-80, wr.width-180))+'px';
                    tip.style.top=Math.max(4,ty)+'px'; tip.style.display='block';
                }});
                hit.addEventListener('mouseleave',function(){{
                    d.setAttribute('r','4'); d.setAttribute('fill','#00D4FF');
                    sDots[idx].setAttribute('r','3');
                    vl.style.display='none'; tip.style.display='none';
                }});
            }});

            applyVis();
        }}

        function applyVis(){{
            if(!elActualLine) return;
            [elActualLine,elActualArea].forEach(el=>el.style.display=showActual?'':'none');
            aDots.forEach(d=>d.style.display=showActual?'':'none');
            [elSavingsLine,elSavingsArea].forEach(el=>el.style.display=showSavings?'':'none');
            sDots.forEach(d=>d.style.display=showSavings?'':'none');
        }}
        function styleBtn(btn,on,color){{
            btn.style.background=on?color+'22':'transparent';
            btn.style.color=on?color:'#4A6080';
            btn.style.borderColor=on?color:'#2A3A4A';
            btn.style.opacity=on?'1':'0.5';
        }}

        togA.addEventListener('click',function(){{ showActual=!showActual; styleBtn(togA,showActual,'#00D4FF'); applyVis(); }});
        togS.addEventListener('click',function(){{ showSavings=!showSavings; styleBtn(togS,showSavings,'#00FF94'); applyVis(); }});

        function waitForWidth(){{
            const w=svg.getBoundingClientRect().width;
            if(w<10){{ setTimeout(waitForWidth,50); return; }}
            render(w);
        }}
        waitForWidth();
    }})();
    </script>
    """, height=340)
