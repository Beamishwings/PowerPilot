import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return snowflake.connector.connect(
        account=os.environ.get("SNOWFLAKE_ACCOUNT"),    # e.g. abc12345.us-east-1
        user=os.environ.get("SNOWFLAKE_USER"),          # your snowflake username
        password=os.environ.get("SNOWFLAKE_PASSWORD"),  # your snowflake password
        database="POWERPILOT",
        schema="MAIN",
    )


def get_devices_for_user(user_id: str) -> list[dict]:
    """
    Pulls all devices for a user from Snowflake.
    Returns a list of dicts matching the format optimizer.py expects.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT device_name, power_on_watts, power_idle_watts, hours_on_per_day, hours_idle_per_day
        FROM devices
        WHERE user_id = %s
    """, (user_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    devices = []
    for row in rows:
        device_name, power_on_watts, power_idle_watts, hours_on_per_day, hours_idle_per_day = row
        device = {
            "device_name": device_name,
            "power_on_watts": power_on_watts or 0,
            "hours_on_per_day": hours_on_per_day or 0,
            "hours_idle_per_day": hours_idle_per_day or 0,
        }
        # only include idle watts if it was set, optimizer will default to 5% otherwise
        if power_idle_watts is not None:
            device["power_idle_watts"] = power_idle_watts
        devices.append(device)

    return devices


def get_fixed_rates() -> list[dict]:
    """
    Returns fixed demonstration energy rates (cost per kWh by hour).
    Reflects a realistic TOU curve: cheap overnight, expensive evening peak.
    """
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


def save_energy_profile(user_id: str, computed_results: dict):
    """
    Saves the full computed_results JSON blob to user_energy_profiles.
    """
    import json
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_energy_profiles (user_id, data)
        SELECT %s, PARSE_JSON(%s)
    """, (user_id, json.dumps(computed_results)))

    conn.commit()
    cursor.close()
    conn.close()
