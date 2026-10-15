import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timezone

# ==========================================================
# CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="AWS IoT | Environmental Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = (
    "https://f8h2fq7tbj.execute-api."
    "us-east-1.amazonaws.com/sensor-data"
)

# ==========================================================
# PREMIUM DARK THEME
# ==========================================================

st.markdown("""
<style>
    .stApp {
        background: #080F1D;
        color: #E8F0FA;
    }

    [data-testid="stSidebar"] {
        background: #101B2E;
        border-right: 1px solid #25354C;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    h1, h2, h3 {
        color: #F1F6FF !important;
    }

    .hero {
        padding: 24px 28px;
        background: linear-gradient(
            110deg, #132B47, #0B1728
        );
        border: 1px solid #29405A;
        border-radius: 18px;
        margin-bottom: 24px;
    }

    .hero-title {
        font-size: 32px;
        font-weight: 800;
        color: #F1F7FF;
    }

    .hero-subtitle {
        color: #A5B9CE;
        margin-top: 8px;
        font-size: 14px;
    }

    .sensor-card {
        background: linear-gradient(
            145deg, #15243A, #101B2D
        );
        border: 1px solid #283B53;
        border-radius: 16px;
        padding: 22px;
        min-height: 170px;
        margin-bottom: 15px;
    }

    .sensor-label {
        color: #A9BED3;
        font-size: 14px;
        margin-bottom: 14px;
    }

    .sensor-value {
        font-size: 32px;
        font-weight: 800;
        color: #F4F8FF;
    }

    .sensor-unit {
        font-size: 16px;
        color: #B2C6D8;
    }

    .sensor-status {
        font-size: 12px;
        color: #4ADE80;
        margin-top: 12px;
    }

    .section-heading {
        color: #EDF5FF;
        font-size: 21px;
        font-weight: 700;
        margin: 24px 0 14px 0;
    }

    .info-panel {
        background: #122238;
        border: 1px solid #29405A;
        border-radius: 14px;
        padding: 20px;
        margin: 12px 0;
        color: #C6D6E6;
    }

    div.stButton > button {
        border-radius: 10px;
        border: 1px solid #245A7B;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #283B53;
        border-radius: 12px;
    }

    .footer {
        color: #7187A2;
        text-align: center;
        padding: 25px 0;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DEMO DATA LOADER
# ==========================================

def load_demo_data():
    import json
    from pathlib import Path

    file_path = Path(__file__).resolve().parent / "sensor_data.json"

    with open(file_path, "r", encoding="utf-8") as file:
        payload = json.load(file)

    records = []

    for item in payload.get("Items", []):
        records.append({
            "device_id": item["device_id"]["S"],
            "timestamp": item["timestamp"]["S"],
            "temperature": float(item["temperature"]["N"]),
            "humidity": float(item["humidity"]["N"]),
            "air_quality": float(item["air_quality"]["N"]),
            "co2": float(item["co2"]["N"])
        })

    df = pd.DataFrame(records)

    if not df.empty:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            utc=True,
            format="ISO8601"
        )

        df = df.sort_values("timestamp")

    return df


# ==========================================================
# AWS API DATA FETCHING
# ==========================================================

@st.cache_data(ttl=30, show_spinner=False)
def fetch_sensor_data():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()

        payload = response.json()
        records = payload.get("data", [])

        df = pd.DataFrame(records)

        if df.empty:
            raise ValueError("AWS returned no sensor data")

        required_columns = [
            "device_id",
            "timestamp",
            "temperature",
            "humidity",
            "air_quality",
            "co2"
        ]

        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing API fields: {', '.join(missing)}"
            )

        numeric_columns = [
            "temperature",
            "humidity",
            "air_quality",
            "co2"
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            format="ISO8601",
            utc=True,
            errors="coerce"
        )

        df = df.dropna(
            subset=["timestamp"] + numeric_columns
        )

        if df.empty:
            raise ValueError("No valid AWS sensor readings")

        df = df.sort_values("timestamp")

        return df, "LIVE"

    except (requests.RequestException, ValueError, KeyError, TypeError):
        return load_demo_data(), "DEMO"


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def sensor_card(icon, label, value, unit, status):
    return f"""
    <div class="sensor-card">
        <div class="sensor-label">{icon} {label}</div>
        <div class="sensor-value">
            {value}
            <span class="sensor-unit">{unit}</span>
        </div>
        <div class="sensor-status">{status}</div>
    </div>
    """


def create_chart(df, column, title, color, unit):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df[column],
            mode="lines+markers",
            line=dict(color=color, width=3),
            marker=dict(size=8),
            fill="tozeroy",
            fillcolor="rgba(56,189,248,0.06)",
            hovertemplate=(
                "%{x}<br>%{y} " + unit +
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=17, color="#E8F0FA")
        ),
        paper_bgcolor="#101B2D",
        plot_bgcolor="#101B2D",
        font=dict(color="#A9BED3"),
        height=330,
        margin=dict(l=20, r=20, t=60, b=25),
        xaxis=dict(
            showgrid=True,
            gridcolor="#24364D"
        ),
        yaxis=dict(
            title=unit,
            showgrid=True,
            gridcolor="#24364D"
        ),
        hovermode="x unified"
    )

    return fig


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    st.markdown("## 🌍 ENVIRONMENT IQ")
    st.caption("AWS Cloud Monitoring Platform")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📊 Overview",
            "📈 Sensor Analytics",
            "🚨 Environmental Alerts",
            "☁️ Cloud Status",
            "📋 Sensor History"
        ]
    )

    st.divider()

    auto_refresh = st.toggle(
        "Auto-refresh every 30 seconds",
        value=False
    )

    if st.button("🔄 Refresh Now", use_container_width=True):
        fetch_sensor_data.clear()
        st.rerun()

    st.divider()

    st.caption("Cloud Infrastructure")

    st.markdown("☁️ AWS API Gateway")
    st.markdown("⚡ AWS Lambda")
    st.markdown("🗄️ AWS DynamoDB")

    st.caption(
        "Configured AWS services. Connection status "
        "is displayed in the main dashboard."
    )

    st.divider()
    st.caption("Region: us-east-1")
    st.caption("Environment: AWS Academy Lab")


# ==========================================================
# AUTO REFRESH
# ==========================================================

if auto_refresh:
    if hasattr(st, "autorefresh"):
        st.autorefresh(interval=30000, key="iot_refresh")
    else:
        # Streamlit versions without built-in autorefresh
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(
                interval=30000,
                key="iot_refresh"
            )
        except ImportError:
            st.sidebar.warning(
                "Install streamlit-autorefresh "
                "to enable automatic refresh."
            )


# ==========================================================
# FETCH LIVE CLOUD API RESPONSE
# ==========================================================
fetch_time = datetime.now(timezone.utc)

try:
    with st.spinner("Loading environmental sensor data..."):
        df, data_mode = fetch_sensor_data()

    if df.empty:
        st.warning("No valid sensor readings available.")
        st.stop()

    api_connected = (data_mode == "LIVE")

    if api_connected:
        st.success("🟢 LIVE AWS MODE — Connected to AWS Cloud API")
    else:
        st.warning(
            "🟡 DEMO MODE — Displaying simulated historical sensor "
            "readings. AWS Cloud API is unavailable."
        )

except Exception as e:
    api_connected = False
    st.error("Unable to load environmental sensor data.")
    st.code(str(e))
    st.stop()


latest = df.iloc[-1]

temperature = float(latest["temperature"])
humidity = float(latest["humidity"])
air_quality = float(latest["air_quality"])
co2 = float(latest["co2"])


# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
<div class="hero">
    <div class="hero-title">
        🌍 Environmental Intelligence Dashboard
    </div>
    <div class="hero-subtitle">
        AWS Cloud-Powered IoT Sensor Monitoring
        | Environmental Analytics | Alert Management
    </div>
</div>
""", unsafe_allow_html=True)

header_left, header_right = st.columns([3, 1])

with header_left:
        if api_connected:
            st.success("🟢 AWS Cloud API Connected")
        else:
            st.warning("🟡 Demo Data Active — AWS API Offline")

with header_right:
    st.caption(
        "Last fetched: " +
        fetch_time.strftime("%H:%M:%S UTC")
    )


# ==========================================================
# OVERVIEW
# ==========================================================

if page == "📊 Overview":

    st.markdown(
        '<div class="section-heading">'
        'Environmental Sensor Overview'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            sensor_card(
                "🌡️",
                "Temperature",
                f"{temperature:.2f}",
                "°C",
                "● High" if temperature > 35
                else "● Within demo limits"
            ),
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            sensor_card(
                "💧",
                "Humidity",
                f"{humidity:.2f}",
                "%",
                "● Sensor reading available"
            ),
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            sensor_card(
                "🌬️",
                "Air Quality",
                f"{air_quality:.0f}",
                "index",
                "● Sensor reading available"
            ),
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            sensor_card(
                "☁️",
                "CO₂ Level",
                f"{co2:.0f}",
                "ppm",
                "● High" if co2 > 1000
                else "● Within demo limits"
            ),
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="section-heading">'
        'Environmental Trends'
        '</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            create_chart(
                df, "temperature",
                "Temperature Trend",
                "#38BDF8", "°C"
            ),
            use_container_width=True
        )

    with right:
        st.plotly_chart(
            create_chart(
                df, "humidity",
                "Humidity Trend",
                "#A78BFA", "%"
            ),
            use_container_width=True
        )

    left2, right2 = st.columns(2)

    with left2:
        st.plotly_chart(
            create_chart(
                df, "co2",
                "CO₂ Concentration",
                "#FB923C", "ppm"
            ),
            use_container_width=True
        )

    with right2:
        st.plotly_chart(
            create_chart(
                df, "air_quality",
                "Air Quality Trend",
                "#4ADE80", "index"
            ),
            use_container_width=True
        )


# ==========================================================
# SENSOR ANALYTICS
# ==========================================================

elif page == "📈 Sensor Analytics":

    st.subheader("📈 Advanced Sensor Analytics")

    selected_sensor = st.selectbox(
        "Choose sensor metric",
        [
            "temperature",
            "humidity",
            "air_quality",
            "co2"
        ]
    )

    color_map = {
        "temperature": "#38BDF8",
        "humidity": "#A78BFA",
        "air_quality": "#4ADE80",
        "co2": "#FB923C"
    }

    unit_map = {
        "temperature": "°C",
        "humidity": "%",
        "air_quality": "index",
        "co2": "ppm"
    }

    st.plotly_chart(
        create_chart(
            df,
            selected_sensor,
            selected_sensor.replace("_", " ").title(),
            color_map[selected_sensor],
            unit_map[selected_sensor]
        ),
        use_container_width=True
    )

    a, b, c = st.columns(3)

    a.metric(
        "Average",
        f"{df[selected_sensor].mean():.2f}"
    )

    b.metric(
        "Minimum",
        f"{df[selected_sensor].min():.2f}"
    )

    c.metric(
        "Maximum",
        f"{df[selected_sensor].max():.2f}"
    )

# ==========================================================
# ENVIRONMENTAL ALERTS
# ==========================================================

elif page == "🚨 Environmental Alerts":

    st.subheader("🚨 Environmental Alert Center")

    st.caption(
        "Real-time monitoring using illustrative project "
        "thresholds, not certified health or safety limits."
    )

    # Demo alert severity thresholds
    def get_severity(value, warning, critical):
        if value >= critical:
            return "CRITICAL"
        elif value >= warning:
            return "WARNING"
        return "NORMAL"

    alerts = [
        {
            "name": "Temperature",
            "value": temperature,
            "unit": "°C",
            "warning": 30,
            "critical": 35
        },
        {
            "name": "Humidity",
            "value": humidity,
            "unit": "%",
            "warning": 60,
            "critical": 75
        },
        {
            "name": "CO₂",
            "value": co2,
            "unit": "ppm",
            "warning": 800,
            "critical": 1200
        },
        {
            "name": "Air Quality Index",
            "value": air_quality,
            "unit": "",
            "warning": 100,
            "critical": 150
        }
    ]

    # Calculate severity for each sensor
    for alert in alerts:
        alert["severity"] = get_severity(
            alert["value"],
            alert["warning"],
            alert["critical"]
        )

    normal_count = sum(
        a["severity"] == "NORMAL" for a in alerts
    )

    warning_count = sum(
        a["severity"] == "WARNING" for a in alerts
    )

    critical_count = sum(
        a["severity"] == "CRITICAL" for a in alerts
    )

    # Alert summary cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🟢 Normal", normal_count)

    with col2:
        st.metric("🟠 Warning", warning_count)

    with col3:
        st.metric("🔴 Critical", critical_count)

    st.markdown("---")
    st.markdown("### Live Sensor Alerts")

    for alert in alerts:

        message = (
            f"{alert['name']}: "
            f"{alert['value']:.2f} {alert['unit']}"
        )

        if alert["severity"] == "CRITICAL":
            st.error(f"🔴 CRITICAL — {message}")

        elif alert["severity"] == "WARNING":
            st.warning(f"🟠 WARNING — {message}")

        else:
            st.success(f"🟢 NORMAL — {message}")

    st.markdown("---")
    st.markdown("### ⚙️ Alert Configuration")

    st.dataframe(
        [
            {
                "Sensor": a["name"],
                "Warning Threshold": a["warning"],
                "Critical Threshold": a["critical"],
                "Current Severity": a["severity"]
            }
            for a in alerts
        ],
        use_container_width=True,
        hide_index=True
    )

    # ======================================================
    # ALERT HISTORY
    # ======================================================

    st.markdown("---")
    st.markdown("### 📜 Environmental Alert History")

    st.caption(
        "Historical warning and critical events "
        "detected from AWS sensor readings."
    )

    alert_history = []

    thresholds = {
        "temperature": ("Temperature", 30, 35, "°C"),
        "humidity": ("Humidity", 60, 75, "%"),
        "co2": ("CO₂", 800, 1200, "ppm"),
        "air_quality": ("Air Quality Index", 100, 150, "")
    }

    for _, reading in df.iterrows():
        for column, config in thresholds.items():

            name, warning, critical, unit = config

            value = pd.to_numeric(
                reading.get(column),
                errors="coerce"
            )

            if pd.isna(value):
                continue

            if value >= critical:
                severity = "🔴 CRITICAL"
            elif value >= warning:
                severity = "🟠 WARNING"
            else:
                continue

            alert_history.append({
                "Timestamp": reading["timestamp"],
                "Device ID": reading["device_id"],
                "Sensor": name,
                "Value": f"{value:.2f} {unit}".strip(),
                "Severity": severity
            })

    if alert_history:

        history_df = pd.DataFrame(alert_history)

        history_df = history_df.sort_values(
            by="Timestamp",
            ascending=False
        )

        st.metric(
            "Total Historical Alerts",
            len(history_df)
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            label="📥 Download Alert History (CSV)",
            data=history_df.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="iot_alert_history.csv",
            mime="text/csv",
            use_container_width=True
        )

    else:
        st.success(
            "🟢 No warning or critical events "
            "found in the available sensor history."
        )

# ==========================================================
# CLOUD STATUS
# ==========================================================

elif page == "☁️ Cloud Status":

    st.subheader("☁️ AWS Cloud Infrastructure")

    if api_connected:
        st.success("🟢 AWS API Gateway endpoint is reachable.")
    else:
        st.warning(
            "🟡 AWS API Gateway is unavailable. "
            "The dashboard is using simulated historical data."
        )

    st.markdown("""
    <div class="info-panel">
        <b>Cloud Architecture</b><br><br>
        Streamlit Dashboard<br>
        ↓<br>
        Amazon API Gateway (HTTP API)<br>
        ↓<br>
        AWS Lambda (Python)<br>
        ↓<br>
        Amazon DynamoDB
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### API Information")

    st.code(API_URL, language="text")

    st.metric("Records Retrieved", len(df))

    st.metric(
        "Latest Sensor Timestamp",
        str(latest["timestamp"])
    )

    if api_connected:
        st.info(
            "The AWS API request succeeded. This confirms "
            "the endpoint is responding, but does not "
            "independently verify each AWS service."
        )
    else:
        st.info(
            "Demo Mode is active. Sensor readings are loaded "
            "from the local JSON file, not from AWS."
        )


# ==========================================================
# SENSOR HISTORY
# ==========================================================

elif page == "📋 Sensor History":

    st.subheader("📋 Historical Sensor Readings")

    devices = sorted(
        df["device_id"].astype(str).unique().tolist()
    )

    selected_devices = st.multiselect(
        "Filter by device",
        devices,
        default=devices
    )

    filtered_df = df[
        df["device_id"].astype(str).isin(
            selected_devices
        )
    ]

    
    # Date range filter
    if not filtered_df.empty:
        filtered_df = filtered_df.copy()

        filtered_df["timestamp"] = pd.to_datetime(
            filtered_df["timestamp"],
            utc=True,
            errors="coerce"
        )

        filtered_df = filtered_df.dropna(subset=["timestamp"])

        if not filtered_df.empty:
            min_date = filtered_df["timestamp"].min().date()
            max_date = filtered_df["timestamp"].max().date()

            st.caption(
                f"Available sensor data: {min_date} to {max_date} (UTC)"
            )

            selected_dates = st.date_input(
                "📅 Filter by date range (UTC)",
                value=(min_date, max_date),
                key="sensor_history_date_range"
            )

            if len(selected_dates) == 2:
                start_date, end_date = selected_dates

                filtered_df = filtered_df[
                    (filtered_df["timestamp"].dt.date >= start_date)
                    & (filtered_df["timestamp"].dt.date <= end_date)
                ]

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_df.to_csv(index=False)

    st.download_button(
        label="📥 Download Sensor Data (CSV)",
        data=csv_data,
        file_name="iot_environmental_sensor_data.csv",
        mime="text/csv",
        use_container_width=True
    )



# ==========================================================
# FOOTER
# ==========================================================

st.markdown("""
<div class="footer">
    AWS IoT Environmental Monitoring System
    | Built with Python, Streamlit, AWS Lambda,
    API Gateway & DynamoDB
    <br>
    Educational cloud project — simulated sensor readings
</div>
""", unsafe_allow_html=True)
