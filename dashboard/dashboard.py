import streamlit as st
import requests
import pandas as pd
import qrcode

from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DairyGuard AI",
    page_icon="🥛",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ============================================================
# SESSION STATE
# ============================================================

if "sensor_data" not in st.session_state:
    st.session_state.sensor_data = None

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "camera_image" not in st.session_state:
    st.session_state.camera_image = None

if "qr_path" not in st.session_state:
    st.session_state.qr_path = None


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background-color: #f4f7fb;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* ========================================================
       HEADINGS
       ======================================================== */

    h1 {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    h2 {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    h3 {
        color: #0f172a !important;
        font-weight: 750 !important;
    }

    h4 {
        color: #0f172a !important;
        font-weight: 700 !important;
    }


    /* ========================================================
       NORMAL TEXT
       ======================================================== */

    p {
        color: #334155 !important;
    }

    span {
        color: inherit;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #0f172a 0%,
            #172554 50%,
            #1e3a8a 100%
        );
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] p {
        color: #e2e8f0 !important;
    }

    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        color: #ffffff !important;
    }


    /* ========================================================
       RADIO BUTTON
       ======================================================== */

    [data-testid="stRadio"] label {
        color: #0f172a !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        color: #ffffff !important;
    }


    /* ========================================================
       TEXT INPUT - IMPORTANT VISIBILITY FIX
       ======================================================== */

    [data-testid="stTextInput"] label {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    [data-testid="stTextInput"] label p {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    [data-testid="stTextInput"] input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;

        border: 2px solid #cbd5e1 !important;
        border-radius: 10px !important;

        font-size: 16px !important;
        font-weight: 600 !important;

        padding: 10px 12px !important;
    }

    [data-testid="stTextInput"] input::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }

    [data-testid="stTextInput"] input:focus {
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;

        border: 2px solid #2563eb !important;

        box-shadow:
            0 0 0 2px rgba(37, 99, 235, 0.15) !important;
    }

    [data-testid="stTextInput"] [data-baseweb="input"] {
        background-color: #ffffff !important;
    }

    [data-testid="stTextInput"] [data-baseweb="base-input"] {
        background-color: #ffffff !important;
    }

    [data-testid="stTextInput"] [data-baseweb="input"] input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
    }


    /* ========================================================
       SIDEBAR INPUT
       ======================================================== */

    [data-testid="stSidebar"] input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
    }


    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {
        background-color: #ffffff !important;

        border: 1px solid #dbe3ee !important;

        border-radius: 16px !important;

        padding: 18px !important;

        box-shadow:
            0 5px 18px rgba(15, 23, 42, 0.07) !important;
    }

    [data-testid="stMetricLabel"] {
        color: #475569 !important;
    }

    [data-testid="stMetricLabel"] p {
        color: #475569 !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetricValue"] div {
        color: #0f172a !important;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        min-height: 44px !important;

        border-radius: 10px !important;

        font-weight: 700 !important;

        border: 1px solid #cbd5e1 !important;

        color: #0f172a !important;

        background-color: #ffffff !important;
    }

    .stButton > button:hover {
        border-color: #2563eb !important;

        color: #1d4ed8 !important;

        background-color: #eff6ff !important;
    }


    /* ========================================================
       ALERT BOXES
       ======================================================== */

    [data-testid="stAlert"] {
        border-radius: 12px !important;
    }


    /* ========================================================
       DATAFRAME
       ======================================================== */

    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
    }


    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {
        border-color: #dbe3ee !important;
    }


    /* ========================================================
       SELECTBOX
       ======================================================== */

    [data-testid="stSelectbox"] label {
        color: #0f172a !important;
        font-weight: 700 !important;
    }


    /* ========================================================
       CAPTIONS
       ======================================================== */

    .stCaption {
        color: #64748b !important;
    }


    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def api_get(endpoint, timeout=10):
    return requests.get(
        f"{API_URL}{endpoint}",
        timeout=timeout
    )


def api_post(endpoint, data=None, timeout=15):
    return requests.post(
        f"{API_URL}{endpoint}",
        json=data,
        timeout=timeout
    )


def safe_number(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def show_api_error(response):

    try:
        detail = response.json().get(
            "detail",
            response.text
        )
    except Exception:
        detail = response.text

    st.error(
        f"API Error {response.status_code}: {detail}"
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🥛 DairyGuard AI")

    st.caption(
        "Intelligent Milk Quality System"
    )

    st.divider()

    st.subheader("MAIN MENU")

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🧪 Milk Test",
            "🧫 MBRT Monitoring",
            "📋 Test History",
            "👨‍🌾 Farmers",
            "📱 Digital Dairy Passport",
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.subheader("SYSTEM STATUS")

    try:

        response = api_get(
            "/",
            timeout=3
        )

        if response.status_code == 200:

            st.success(
                "🟢 Backend Online"
            )

        else:

            st.warning(
                "🟡 Backend Error"
            )

    except Exception:

        st.error(
            "🔴 Backend Offline"
        )

    st.caption(
        "FastAPI • Port 8000"
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title("🥛 DairyGuard AI")

st.subheader(
    "Intelligent Milk Quality Assessment System"
)

st.caption(
    "MBRT Monitoring • Spoilage Risk • "
    "Shelf-Life Estimation • Smart Routing • "
    "Digital Dairy Traceability"
)

st.divider()


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.header("📊 System Overview")

    st.write(
        "Real-time overview of the DairyGuard AI prototype."
    )

    # --------------------------------------------------------
    # GET LATEST SENSOR
    # --------------------------------------------------------

    try:

        response = api_get(
            "/api/latest-reading",
            timeout=5
        )

        if response.status_code == 200:

            st.session_state.sensor_data = (
                response.json()
            )

    except Exception:
        pass

    sensor = (
        st.session_state.sensor_data
        or {}
    )

    red = safe_number(
        sensor.get("red", 0)
    )

    green = safe_number(
        sensor.get("green", 0)
    )

    blue = safe_number(
        sensor.get("blue", 0)
    )

    temperature = safe_number(
        sensor.get("temperature", 0)
    )

    quality = safe_number(
        sensor.get("quality_score", 0)
    )

    status = sensor.get(
        "status",
        "NOT TESTED"
    )

    risk = sensor.get(
        "spoilage_risk",
        "UNKNOWN"
    )

    # --------------------------------------------------------
    # STATUS CARDS
    # --------------------------------------------------------

    st.subheader("Current Milk Status")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "🌡️ Temperature",
            f"{temperature:.1f} °C"
        )

    with c2:

        st.metric(
            "⭐ Quality Score",
            f"{quality:.0f}/100"
        )

    with c3:

        st.metric(
            "⚠️ Spoilage Risk",
            str(risk)
        )

    with c4:

        st.metric(
            "🧪 Test Status",
            str(status)
        )

    st.divider()

    # --------------------------------------------------------
    # LIVE SENSOR
    # --------------------------------------------------------

    st.header("🌈 Live Sensor Monitoring")

    st.write(
        "Measurements received from the ESP32 colour "
        "and temperature sensors."
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "🔴 Red",
            f"{red:.0f}"
        )

    with c2:

        st.metric(
            "🟢 Green",
            f"{green:.0f}"
        )

    with c3:

        st.metric(
            "🔵 Blue",
            f"{blue:.0f}"
        )

    if st.button(
        "📡 Refresh Sensor",
        use_container_width=True
    ):

        try:

            response = api_get(
                "/api/latest-reading"
            )

            if response.status_code == 200:

                st.session_state.sensor_data = (
                    response.json()
                )

                st.success(
                    "Sensor reading updated."
                )

                st.rerun()

            else:

                show_api_error(response)

        except Exception as e:

            st.error(
                f"Sensor error: {e}"
            )

    st.divider()

    # --------------------------------------------------------
    # WORKFLOW
    # --------------------------------------------------------

    st.header("🔄 DairyGuard AI Workflow")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.info(
            "🔬 **1. COLLECT**\n\n"
            "ESP32 + ESP32-CAM + TCS34725 + DS18B20"
        )

    with c2:

        st.info(
            "📡 **2. TRANSMIT**\n\n"
            "Sensor data is sent through Wi-Fi."
        )

    with c3:

        st.info(
            "⚙️ **3. ANALYSE**\n\n"
            "FastAPI processes the milk readings."
        )

    with c4:

        st.success(
            "📊 **4. DISPLAY**\n\n"
            "Streamlit presents the results."
        )


# ============================================================
# MILK TEST
# ============================================================

elif page == "🧪 Milk Test":

    st.header("🧪 Milk Quality Test")

    st.write(
        "Enter batch details, collect sensor data "
        "and analyse milk quality."
    )

    # --------------------------------------------------------
    # FARMER AND BATCH
    # --------------------------------------------------------

    c1, c2 = st.columns(2)

    with c1:

        farmer_id = st.text_input(
            "👨‍🌾 Farmer ID",
            value="F001",
            key="farmer_id_input"
        )

    with c2:

        batch_id = st.text_input(
            "📦 Batch ID",
            value="B001",
            key="batch_id_input"
        )

    st.divider()

    # --------------------------------------------------------
    # CAMERA
    # --------------------------------------------------------

    st.header("📸 Milk Sample Camera")

    st.info(
        "Place the milk sample inside the closed camera testing chamber."
    )

    if st.button(
        "📸 Capture Milk Sample",
        type="primary",
        use_container_width=True
    ):

        try:

            response = api_get(
                "/api/camera/save",
                timeout=70
            )

            if response.status_code == 200:

                result = response.json()

                image_path = Path(
                    result.get(
                        "image_path",
                        "uploads/milk_sample.jpg"
                    )
                )

                if not image_path.exists():

                    image_path = Path(
                        "uploads/milk_sample.jpg"
                    )

                if image_path.exists():

                    st.session_state.camera_image = (
                        image_path.read_bytes()
                    )

                    st.success(
                        "✅ Fresh milk sample image captured."
                    )

                else:

                    st.warning(
                        "Image captured but local image "
                        "file was not found."
                    )

            else:

                show_api_error(response)

        except Exception as e:

            st.error(
                f"Camera error: {e}"
            )

    if st.session_state.camera_image:

        st.image(
            st.session_state.camera_image,
            caption="Latest Milk Sample",
            use_container_width=True
        )

    else:

        st.info(
            "📷 No camera image captured yet."
        )

    st.divider()

    # --------------------------------------------------------
    # SENSOR
    # --------------------------------------------------------

    st.header("🌈 ESP32 Sensor Reading")

    if st.button(
        "📡 Read Sensor",
        use_container_width=True
    ):

        try:

            response = api_get(
                "/api/latest-reading"
            )

            if response.status_code == 200:

                st.session_state.sensor_data = (
                    response.json()
                )

                st.success(
                    "✅ ESP32 sensor reading received."
                )

            else:

                show_api_error(response)

        except Exception as e:

            st.error(
                f"Sensor error: {e}"
            )

    sensor = (
        st.session_state.sensor_data
        or {}
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "🔴 Red",
            f"{safe_number(sensor.get('red')):.0f}"
        )

    with c2:

        st.metric(
            "🟢 Green",
            f"{safe_number(sensor.get('green')):.0f}"
        )

    with c3:

        st.metric(
            "🔵 Blue",
            f"{safe_number(sensor.get('blue')):.0f}"
        )

    with c4:

        st.metric(
            "🌡️ Temperature",
            f"{safe_number(sensor.get('temperature')):.2f} °C"
        )

    st.divider()

    # --------------------------------------------------------
    # ANALYSIS
    # --------------------------------------------------------

    st.header("🔬 Milk Quality Analysis")

    if st.button(
        "🚀 Analyse Current Reading",
        type="primary",
        use_container_width=True
    ):

        payload = {
            "farmer_id": farmer_id,
            "batch_id": batch_id,
            "red": safe_number(
                sensor.get("red")
            ),
            "green": safe_number(
                sensor.get("green")
            ),
            "blue": safe_number(
                sensor.get("blue")
            ),
            "temperature": safe_number(
                sensor.get("temperature")
            )
        }

        try:

            response = api_post(
                "/api/milk-test",
                payload,
                timeout=20
            )

            if response.status_code == 200:

                st.session_state.analysis_result = (
                    response.json()
                )

                st.success(
                    "✅ Milk quality analysis completed."
                )

            else:

                show_api_error(response)

        except Exception as e:

            st.error(
                f"Analysis error: {e}"
            )

    result = (
        st.session_state.analysis_result
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    if result:

        st.divider()

        st.header("📊 Milk Quality Result")

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "⭐ Quality Score",
                f"{safe_number(result.get('quality_score')):.0f}/100"
            )

        with c2:

            st.metric(
                "🧪 Status",
                str(
                    result.get(
                        "status",
                        "N/A"
                    )
                )
            )

        with c3:

            st.metric(
                "⚠️ Spoilage Risk",
                str(
                    result.get(
                        "spoilage_risk",
                        "N/A"
                    )
                )
            )

        with c4:

            st.metric(
                "🌡️ Temperature",
                f"{safe_number(result.get('temperature')):.1f} °C"
            )

        # ----------------------------------------------------
        # RGB
        # ----------------------------------------------------

        st.subheader("🌈 Colour Sensor Values")

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "🔴 Red",
                f"{safe_number(result.get('red')):.0f}"
            )

        with c2:

            st.metric(
                "🟢 Green",
                f"{safe_number(result.get('green')):.0f}"
            )

        with c3:

            st.metric(
                "🔵 Blue",
                f"{safe_number(result.get('blue')):.0f}"
            )

        # ----------------------------------------------------
        # SHELF LIFE
        # ----------------------------------------------------

        st.subheader("⏳ Shelf-Life Estimation")

        shelf_life = result.get(
            "estimated_shelf_life_hours",
            result.get(
                "shelf_life_hours",
                "N/A"
            )
        )

        shelf_risk = result.get(
            "shelf_life_risk",
            result.get(
                "risk",
                "N/A"
            )
        )

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Estimated Shelf Life",
                f"{shelf_life} hours"
            )

        with c2:

            st.metric(
                "Shelf-Life Risk",
                str(shelf_risk)
            )

        recommendation = result.get(
            "recommendation",
            result.get(
                "shelf_life_recommendation",
                "No recommendation available."
            )
        )

        st.info(
            f"💡 Shelf-Life Recommendation: {recommendation}"
        )

        # ----------------------------------------------------
        # SMART ROUTING
        # ----------------------------------------------------

        st.subheader("🚚 Smart Milk Routing")

        routing = result.get(
            "routing",
            {}
        )

        if isinstance(routing, dict):

            route = routing.get(
                "route",
                routing.get(
                    "recommended_route",
                    "N/A"
                )
            )

            priority = routing.get(
                "priority",
                "N/A"
            )

        else:

            route = result.get(
                "milk_routing",
                "N/A"
            )

            priority = result.get(
                "routing_priority",
                "N/A"
            )

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Recommended Route",
                str(route)
            )

        with c2:

            st.metric(
                "Priority",
                str(priority)
            )

        # ----------------------------------------------------
        # AI RECOMMENDATION
        # ----------------------------------------------------

        st.subheader("🤖 AI Decision Support")

        ai_recommendation = result.get(
            "ai_recommendation",
            result.get(
                "recommendation",
                "No recommendation available."
            )
        )

        recommended_action = result.get(
            "recommended_action",
            "Review the milk test result."
        )

        st.info(
            f"💡 {ai_recommendation}"
        )

        st.success(
            f"🎯 Recommended Action: {recommended_action}"
        )

        # ----------------------------------------------------
        # SAVE TEST
        # ----------------------------------------------------

        st.divider()

        if st.button(
            "💾 Save Test Result",
            use_container_width=True
        ):

            save_payload = {
                "farmer_id": farmer_id,
                "batch_id": batch_id,
                "red": safe_number(
                    result.get("red")
                ),
                "green": safe_number(
                    result.get("green")
                ),
                "blue": safe_number(
                    result.get("blue")
                ),
                "temperature": safe_number(
                    result.get("temperature")
                ),
                "quality_score": safe_number(
                    result.get("quality_score")
                ),
                "status": result.get(
                    "status",
                    "NOT TESTED"
                ),
                "spoilage_risk": result.get(
                    "spoilage_risk",
                    "UNKNOWN"
                )
            }

            try:

                response = api_post(
                    "/api/save-test",
                    save_payload
                )

                if response.status_code == 200:

                    st.success(
                        "✅ Test result saved successfully."
                    )

                else:

                    show_api_error(response)

            except Exception as e:

                st.error(
                    f"Save error: {e}"
                )


# ============================================================
# MBRT MONITORING
# ============================================================

elif page == "🧫 MBRT Monitoring":

    st.header(
        "🧫 MBRT Microbial-Quality Monitoring"
    )

    st.write(
        "Monitor methylene-blue colour-change behaviour "
        "using the ESP32-CAM."
    )

    st.info(
        "Place milk + MBRT working solution inside the "
        "closed testing chamber."
    )

    c1, c2 = st.columns(2)

    with c1:

        mbrt_farmer = st.text_input(
            "👨‍🌾 Farmer ID",
            value="F001",
            key="mbrt_farmer"
        )

    with c2:

        mbrt_batch = st.text_input(
            "📦 Batch ID",
            value="B001",
            key="mbrt_batch"
        )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "▶️ Start MBRT",
            type="primary",
            use_container_width=True
        ):

            try:

                response = api_post(
                    "/api/mbrt/start",
                    {
                        "farmer_id": mbrt_farmer,
                        "batch_id": mbrt_batch
                    }
                )

                if response.status_code == 200:

                    st.success(
                        "🟢 MBRT monitoring started."
                    )

                else:

                    show_api_error(response)

            except Exception as e:

                st.error(
                    f"MBRT start error: {e}"
                )

    with c2:

        if st.button(
            "⏹️ Stop MBRT",
            use_container_width=True
        ):

            try:

                response = api_post(
                    "/api/mbrt/stop"
                )

                if response.status_code == 200:

                    st.success(
                        "MBRT monitoring stopped."
                    )

                else:

                    show_api_error(response)

            except Exception as e:

                st.error(
                    f"MBRT stop error: {e}"
                )

    st.divider()

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    try:

        response = api_get(
            "/api/mbrt/status",
            timeout=5
        )

        if response.status_code == 200:

            mbrt = response.json()

            running = mbrt.get(
                "running",
                False
            )

            if running:

                st.success(
                    "🟢 MBRT monitoring is RUNNING"
                )

            else:

                st.info(
                    "⚪ MBRT monitoring is STOPPED"
                )

            results = mbrt.get(
                "results",
                []
            )

            latest = mbrt.get(
                "latest",
                None
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "⏱️ Elapsed Time",
                    f"{safe_number(mbrt.get('elapsed_minutes')):.2f} min"
                )

            with c2:

                st.metric(
                    "📸 Images Captured",
                    len(results)
                )

            with c3:

                st.metric(
                    "🔵 Monitoring",
                    "RUNNING"
                    if running
                    else "STOPPED"
                )

            # ------------------------------------------------
            # LATEST
            # ------------------------------------------------

            if latest:

                st.divider()

                st.subheader(
                    "📸 Latest MBRT Observation"
                )

                image_path = Path(
                    latest.get(
                        "image_path",
                        latest.get(
                            "mbrt_image_path",
                            ""
                        )
                    )
                )

                c1, c2 = st.columns(2)

                with c1:

                    if image_path.exists():

                        st.image(
                            str(image_path),
                            caption="Latest MBRT Image",
                            use_container_width=True
                        )

                    else:

                        st.info(
                            "Latest MBRT image is not available."
                        )

                with c2:

                    st.subheader(
                        "🎨 Colour Analysis"
                    )

                    cc1, cc2 = st.columns(2)

                    with cc1:

                        st.metric(
                            "Red",
                            f"{safe_number(latest.get('red')):.2f}"
                        )

                    with cc2:

                        st.metric(
                            "Green",
                            f"{safe_number(latest.get('green')):.2f}"
                        )

                    cc1, cc2 = st.columns(2)

                    with cc1:

                        st.metric(
                            "Blue",
                            f"{safe_number(latest.get('blue')):.2f}"
                        )

                    with cc2:

                        st.metric(
                            "Blue Score",
                            f"{safe_number(latest.get('blue_score')):.2f}"
                        )

                # ------------------------------------------------
                # MICROBIAL ACTIVITY
                # ------------------------------------------------

                st.divider()

                st.subheader(
                    "🦠 Microbial Activity Estimate"
                )

                activity = latest.get(
                    "microbial_activity",
                    "NOT AVAILABLE"
                )

                microbial_count = latest.get(
                    "microbial_count",
                    "NOT CALIBRATED"
                )

                mbrt_status = latest.get(
                    "mbrt_status",
                    "MONITORING"
                )

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.metric(
                        "Microbial Activity",
                        str(activity)
                    )

                with c2:

                    st.metric(
                        "MBRT Status",
                        str(mbrt_status)
                    )

                with c3:

                    st.metric(
                        "Microbial Count",
                        str(microbial_count)
                    )

                st.warning(
                    "⚠️ Prototype classification only. "
                    "This is not a calibrated CFU/mL measurement."
                )

            # ------------------------------------------------
            # TIMELINE
            # ------------------------------------------------

            if results:

                st.divider()

                st.subheader(
                    "📈 MBRT Colour Timeline"
                )

                rows = []

                for item in results:

                    rows.append(
                        {
                            "Time (min)": safe_number(
                                item.get(
                                    "elapsed_minutes",
                                    0
                                )
                            ),
                            "Red": safe_number(
                                item.get(
                                    "red",
                                    0
                                )
                            ),
                            "Green": safe_number(
                                item.get(
                                    "green",
                                    0
                                )
                            ),
                            "Blue": safe_number(
                                item.get(
                                    "blue",
                                    0
                                )
                            ),
                            "Blue Score": safe_number(
                                item.get(
                                    "blue_score",
                                    0
                                )
                            ),
                            "Activity": item.get(
                                "microbial_activity",
                                "N/A"
                            )
                        }
                    )

                df = pd.DataFrame(rows)

                if not df.empty:

                    chart = df.set_index(
                        "Time (min)"
                    )[
                        [
                            "Red",
                            "Green",
                            "Blue"
                        ]
                    ]

                    st.line_chart(
                        chart,
                        use_container_width=True
                    )

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

        else:

            show_api_error(response)

    except Exception as e:

        st.error(
            f"MBRT error: {e}"
        )


# ============================================================
# TEST HISTORY
# ============================================================

elif page == "📋 Test History":

    st.header(
        "📋 Milk Test History"
    )

    st.write(
        "View all previously saved milk-quality test results."
    )

    if st.button(
        "🔄 Refresh History",
        use_container_width=True
    ):

        st.rerun()

    try:

        response = api_get(
            "/api/tests",
            timeout=10
        )

        if response.status_code == 200:

            tests = response.json()

            if tests:

                df = pd.DataFrame(
                    tests
                )

                # ------------------------------------------------
                # SUMMARY
                # ------------------------------------------------

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.metric(
                        "🧪 Total Tests",
                        len(df)
                    )

                with c2:

                    if "quality_score" in df.columns:

                        avg = pd.to_numeric(
                            df["quality_score"],
                            errors="coerce"
                        ).mean()

                        if pd.isna(avg):
                            avg = 0

                        st.metric(
                            "⭐ Average Quality",
                            f"{avg:.1f}/100"
                        )

                    else:

                        st.metric(
                            "⭐ Average Quality",
                            "N/A"
                        )

                with c3:

                    if "spoilage_risk" in df.columns:

                        high = (
                            df["spoilage_risk"]
                            .astype(str)
                            .str.upper()
                            .eq("HIGH")
                            .sum()
                        )

                    else:

                        high = 0

                    st.metric(
                        "🔴 High Risk Tests",
                        int(high)
                    )

                st.divider()

                search = st.text_input(
                    "🔎 Search Farmer ID / Batch ID",
                    key="history_search"
                )

                if search:

                    mask = (
                        df.astype(str)
                        .apply(
                            lambda row:
                            row.str.contains(
                                search,
                                case=False,
                                na=False
                            ).any(),
                            axis=1
                        )
                    )

                    df = df[mask]

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "📭 No milk tests found."
                )

        else:

            show_api_error(response)

    except Exception as e:

        st.error(
            f"History error: {e}"
        )


# ============================================================
# FARMERS
# ============================================================

elif page == "👨‍🌾 Farmers":

    st.header(
        "👨‍🌾 Farmer Records"
    )

    st.write(
        "Farmer-wise milk testing and quality tracking."
    )

    try:

        response = api_get(
            "/api/farmers",
            timeout=10
        )

        if response.status_code == 200:

            farmers = response.json()

            if isinstance(
                farmers,
                dict
            ):

                farmers = farmers.get(
                    "farmers",
                    []
                )

            try:

                history_response = api_get(
                    "/api/tests",
                    timeout=10
                )

                if history_response.status_code == 200:

                    all_tests = (
                        history_response.json()
                    )

                else:

                    all_tests = []

            except Exception:

                all_tests = []

            if farmers:

                c1, c2 = st.columns(2)

                with c1:

                    st.metric(
                        "👨‍🌾 Total Farmers",
                        len(farmers)
                    )

                with c2:

                    st.metric(
                        "🧪 Total Tests",
                        len(all_tests)
                    )

                st.divider()

                for index, farmer in enumerate(
                    farmers
                ):

                    if isinstance(
                        farmer,
                        dict
                    ):

                        farmer_id_value = farmer.get(
                            "farmer_id",
                            farmer.get(
                                "id",
                                f"F{index + 1:03d}"
                            )
                        )

                    else:

                        farmer_id_value = str(
                            farmer
                        )

                    st.subheader(
                        f"👨‍🌾 Farmer {farmer_id_value}"
                    )

                    farmer_tests = [
                        test
                        for test in all_tests
                        if str(
                            test.get(
                                "farmer_id",
                                ""
                            )
                        )
                        == str(
                            farmer_id_value
                        )
                    ]

                    if farmer_tests:

                        latest = (
                            farmer_tests[0]
                        )

                        quality = latest.get(
                            "quality_score",
                            "N/A"
                        )

                        status = latest.get(
                            "status",
                            "N/A"
                        )

                        temperature = latest.get(
                            "temperature",
                            "N/A"
                        )

                        risk = latest.get(
                            "spoilage_risk",
                            "N/A"
                        )

                    else:

                        quality = "N/A"
                        status = "NO TEST"
                        temperature = "N/A"
                        risk = "N/A"

                    c1, c2, c3, c4 = st.columns(4)

                    with c1:

                        st.metric(
                            "🧪 Tests",
                            len(farmer_tests)
                        )

                    with c2:

                        if quality != "N/A":

                            try:

                                quality_text = (
                                    f"{float(quality):.0f}/100"
                                )

                            except Exception:

                                quality_text = str(
                                    quality
                                )

                        else:

                            quality_text = "N/A"

                        st.metric(
                            "⭐ Quality",
                            quality_text
                        )

                    with c3:

                        st.metric(
                            "📋 Status",
                            str(status)
                        )

                    with c4:

                        if temperature != "N/A":

                            try:

                                temperature_text = (
                                    f"{float(temperature):.1f} °C"
                                )

                            except Exception:

                                temperature_text = str(
                                    temperature
                                )

                        else:

                            temperature_text = "N/A"

                        st.metric(
                            "🌡️ Temperature",
                            temperature_text
                        )

                    if str(risk).upper() == "LOW":

                        st.success(
                            "🟢 Spoilage Risk: LOW"
                        )

                    elif str(risk).upper() == "MEDIUM":

                        st.warning(
                            "🟡 Spoilage Risk: MEDIUM"
                        )

                    elif str(risk).upper() == "HIGH":

                        st.error(
                            "🔴 Spoilage Risk: HIGH"
                        )

                    else:

                        st.info(
                            f"⚪ Spoilage Risk: {risk}"
                        )

                    st.divider()

            else:

                st.info(
                    "👨‍🌾 No farmer records found."
                )

        else:

            show_api_error(response)

    except Exception as e:

        st.error(
            f"Farmer error: {e}"
        )


# ============================================================
# DIGITAL DAIRY PASSPORT
# ============================================================

elif page == "📱 Digital Dairy Passport":

    st.header(
        "📱 Digital Dairy Passport"
    )

    st.write(
        "Generate a QR-based traceability record for a milk batch."
    )

    batch_id = st.text_input(
        "📦 Enter Batch ID",
        value="B001",
        key="passport_batch"
    )

    if st.button(
        "🔳 Generate Digital Passport",
        type="primary",
        use_container_width=True
    ):

        try:

            response = api_get(
                f"/api/tests/{batch_id}",
                timeout=10
            )

            if response.status_code == 200:

                batch_tests = response.json()

                if batch_tests:

                    latest = batch_tests[-1]

                    passport_data = f"""
DairyGuard AI
Digital Dairy Passport

Farmer ID:
{latest.get('farmer_id', 'N/A')}

Batch ID:
{latest.get('batch_id', 'N/A')}

Quality Score:
{latest.get('quality_score', 'N/A')}/100

Status:
{latest.get('status', 'N/A')}

Temperature:
{latest.get('temperature', 'N/A')} °C

Spoilage Risk:
{latest.get('spoilage_risk', 'N/A')}

MBRT Status:
{latest.get('mbrt_status', 'N/A')}

MBRT Time:
{latest.get('mbrt_time_seconds', 'N/A')} seconds

MBRT Blue Score:
{latest.get('mbrt_blue_score', 'N/A')}

Generated by DairyGuard AI
"""

                    qr = qrcode.make(
                        passport_data
                    )

                    qr_path = (
                        UPLOAD_DIR
                        / f"QR_{batch_id}.png"
                    )

                    qr.save(
                        qr_path
                    )

                    st.session_state.qr_path = (
                        qr_path
                    )

                    st.success(
                        "✅ Digital Dairy Passport generated."
                    )

                else:

                    st.warning(
                        "No test data found for this batch."
                    )

            else:

                show_api_error(response)

        except Exception as e:

            st.error(
                f"QR generation error: {e}"
            )

    if st.session_state.qr_path:

        st.divider()

        c1, c2 = st.columns(2)

        with c1:

            st.image(
                str(
                    st.session_state.qr_path
                ),
                caption="Digital Dairy Passport QR",
                use_container_width=True
            )

        with c2:

            st.subheader(
                "🔐 Batch Traceability"
            )

            st.write(
                "The QR code stores the selected batch's "
                "quality and MBRT prototype information."
            )

            st.info(
                "Adulteration detection is not included because "
                "the current prototype does not perform an "
                "adulteration test."
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🥛 DairyGuard AI • ESP32 • ESP32-CAM • "
    "TCS34725 • DS18B20 • MBRT • FastAPI • "
    "Streamlit • SQLite"
)