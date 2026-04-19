# PowerPilot

PowerPilot — Smart Home Energy Advisor
PowerPilot is an AI-powered home energy dashboard that helps users understand, optimize, 
and reduce their electricity consumption through device tracking, time-of-use rate analysis, and LLM-generated recommendations.

Sustainability
Residential energy use accounts for roughly 20% of U.S. greenhouse gas emissions. Much of that waste comes from poor timing, phantom loads, and a lack of visibility
— not the appliances themselves. PowerPilot addresses this by surfacing hidden inefficiencies, guiding users to shift usage off-peak, and making consumption data concrete enough to drive real behavioral change.

Features
PowerScore — A 0–100 efficiency rating based on peak-hour behavior, phantom load, and total consumption. Hover to see your tier and recommended next steps.
Device Breakdown — Track daily kWh, monthly cost, and energy share per device. Seasonal appliances (AC, heating) are automatically adjusted for the months they run.
AI Device Lookup — Auto-fills wattage and usage hours for any device using U.S. Department of Energy averages.
Annual Projection — Interactive month-by-month cost chart with seasonal modeling and an off-peak savings toggle.
AI Advisor — Groq-powered recommendations personalized to your devices and rate schedule, with an estimated new PowerScore if followed.
Chat — Ask any energy question in plain English and get answers grounded in your actual data.
Rate Chart — Hourly electricity rate visualization with peak/off-peak color coding and hover tooltips.

Database Schema
Snowflake is used exclusively to persist device data across sessions. All scoring and AI calls are handled in-app.
sqlCREATE TABLE POWERPILOT.MAIN.devices (
    user_id            VARCHAR,
    device_name        VARCHAR,
    power_on_watts     FLOAT,
    power_idle_watts   FLOAT,
    hours_on_per_day   FLOAT,
    hours_idle_per_day FLOAT
);
