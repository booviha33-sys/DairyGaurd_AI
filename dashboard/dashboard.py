import streamlit as st
import requests
import pandas as pd
import qrcode

from pathlib import Path


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="DairyGuard AI",
    page_icon="🥛",
    layout="wide",
)


# =========================================================
# API CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8000"


# =========================================================
# TITLE
# =========================================================

st.title("🥛 DairyGuard AI")

st.caption(
    "Intelligent Milk Quality Assessment and Spoilage Prediction System"
)


# =========================================================
# SESSION STATE
# =========================================================

if "sensor_data" not in st.session_state:
    st.session_state["sensor_data"] = None

if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None

if "camera_image_bytes" not in st.session_state:
    st.session_state["camera_image_bytes"] = None

if "mbrt_results" not in st.session_state:
    st.session_state["mbrt_results"] = []


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🥛 DairyGuard AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "Milk Test",
        "Test History",
        "Farmers",
    ],
)


# =========================================================
# HELPER: API ERROR
# =========================================================

def show_api_error(response):

    try:

        detail = response.json().get(
            "detail",
            response.text,
        )

    except Exception:

        detail = response.text

    st.error(
        f"API Error {response.status_code}: {detail}"
    )


# =========================================================
# MILK TEST PAGE
# =========================================================

if page == "Milk Test":

    st.header("🧪 Milk Quality Test")


    # =====================================================
    # FARMER AND BATCH
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        farmer_id = st.text_input(
            "👨‍🌾 Farmer ID",
            value="F001",
        )

    with col2:

        batch_id = st.text_input(
            "📦 Batch ID",
            value="B001",
        )


    st.divider()


    # =====================================================
    # NORMAL CAMERA
    # =====================================================

    st.subheader("📸 Milk Sample Camera")

    if st.button(
        "📸 Capture Milk Sample",
        use_container_width=True,
    ):

        try:

            response = requests.get(
                f"{API_URL}/api/camera/save",
                timeout=70,
            )

            if response.status_code == 200:

                result = response.json()

                image_path = Path(
                    result.get(
                        "image_path",
                        "",
                    )
                )

                if image_path.exists():

                    st.session_state[
                        "camera_image_bytes"
                    ] = image_path.read_bytes()

                else:

                    latest_path = Path(
                        result.get(
                            "latest_image_path",
                            "uploads/milk_sample.jpg",
                        )
                    )

                    if latest_path.exists():

                        st.session_state[
                            "camera_image_bytes"
                        ] = latest_path.read_bytes()

                st.success(
                    "✅ Fresh milk sample image captured!"
                )

                st.caption(
                    f"Image size: "
                    f"{result.get('image_size', 0)} bytes"
                )

            else:

                show_api_error(response)

        except requests.exceptions.Timeout:

            st.error(
                "⏱️ Camera request timed out."
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Cannot connect to DairyGuard backend."
            )

        except Exception as e:

            st.error(
                f"Camera error: {e}"
            )


    if st.session_state[
        "camera_image_bytes"
    ]:

        st.image(
            st.session_state[
                "camera_image_bytes"
            ],
            caption="Latest Fresh Milk Sample",
            width=500,
        )


    st.divider()


    # =====================================================
    # LIVE SENSOR
    # =====================================================

    st.subheader("🌈 Live Colour Sensor")

    if st.button(
        "📡 Read Sensor",
        use_container_width=True,
    ):

        try:

            response = requests.get(
                f"{API_URL}/api/latest-reading",
                timeout=10,
            )

            if response.status_code == 200:

                st.session_state[
                    "sensor_data"
                ] = response.json()

                st.success(
                    "✅ ESP32 sensor reading received!"
                )

            else:

                show_api_error(response)

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Cannot connect to DairyGuard backend."
            )

        except requests.exceptions.Timeout:

            st.error(
                "⏱️ Sensor request timed out."
            )

        except Exception as e:

            st.error(
                f"Sensor error: {e}"
            )


    sensor_data = st.session_state[
        "sensor_data"
    ]


    if sensor_data:

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "🔴 Red",
                f"{sensor_data.get('red', 0):.0f}",
            )

        with col2:

            st.metric(
                "🟢 Green",
                f"{sensor_data.get('green', 0):.0f}",
            )

        with col3:

            st.metric(
                "🔵 Blue",
                f"{sensor_data.get('blue', 0):.0f}",
            )

        with col4:

            st.metric(
                "🌡️ Temperature",
                f"{sensor_data.get('temperature', 0):.1f} °C",
            )


    st.divider()


    # =====================================================
    # MILK QUALITY ANALYSIS
    # =====================================================

    st.subheader("🔬 Milk Quality Analysis")

    if st.button(
        "🔍 Analyze Current Reading",
        type="primary",
        use_container_width=True,
    ):

        try:

            response = requests.get(
                f"{API_URL}/api/latest-reading",
                timeout=10,
            )

            if response.status_code != 200:

                show_api_error(response)

                st.stop()

            sensor_data = response.json()

            payload = {

                "farmer_id":
                    farmer_id,

                "batch_id":
                    batch_id,

                "red":
                    sensor_data.get(
                        "red",
                        0,
                    ),

                "green":
                    sensor_data.get(
                        "green",
                        0,
                    ),

                "blue":
                    sensor_data.get(
                        "blue",
                        0,
                    ),

                "temperature":
                    sensor_data.get(
                        "temperature",
                        0,
                    ),
            }

            response = requests.post(
                f"{API_URL}/api/milk-test",
                json=payload,
                timeout=15,
            )

            if response.status_code == 200:

                st.session_state[
                    "analysis_result"
                ] = response.json()

                st.success(
                    "✅ Milk analysis completed!"
                )

            else:

                show_api_error(response)

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Cannot connect to DairyGuard backend."
            )

        except requests.exceptions.Timeout:

            st.error(
                "⏱️ Analysis request timed out."
            )

        except Exception as e:

            st.error(
                f"Analysis error: {e}"
            )


    result = st.session_state[
        "analysis_result"
    ]


    if result:

        st.divider()

        st.header("📊 Milk Quality Results")


        # =================================================
        # QUALITY OVERVIEW
        # =================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Quality Score",
                f"{result.get('quality_score', 0)}/100",
            )

        with col2:

            st.metric(
                "Status",
                result.get(
                    "status",
                    result.get(
                        "milk_status",
                        "N/A",
                    ),
                ),
            )

        with col3:

            st.metric(
                "Spoilage Risk",
                result.get(
                    "spoilage_risk",
                    "N/A",
                ),
            )

        with col4:

            st.metric(
                "Temperature",
                f"{result.get('temperature', 0):.1f} °C",
            )


        # =================================================
        # RGB
        # =================================================

        st.subheader("🌈 Colour Sensor Values")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Red",
                f"{result.get('red', 0):.0f}",
            )

        with col2:

            st.metric(
                "Green",
                f"{result.get('green', 0):.0f}",
            )

        with col3:

            st.metric(
                "Blue",
                f"{result.get('blue', 0):.0f}",
            )


        # =================================================
        # SHELF LIFE
        # =================================================

        st.divider()

        st.subheader(
            "⏳ AI Shelf-Life Prediction"
        )

        col1, col2 = st.columns(2)

        with col1:

            shelf_life = result.get(
                "estimated_shelf_life_hours",
                "N/A",
            )

            st.metric(
                "Estimated Shelf Life",
                f"{shelf_life} hours",
            )

        with col2:

            st.metric(
                "Shelf-Life Risk",
                result.get(
                    "shelf_life_risk",
                    "N/A",
                ),
            )

        st.info(
            "💡 **Shelf-Life Recommendation:** "
            + str(
                result.get(
                    "recommendation",
                    result.get(
                        "shelf_life_recommendation",
                        "No recommendation available.",
                    ),
                )
            )
        )


        # =================================================
        # ROUTING
        # =================================================

        st.divider()

        st.subheader(
            "🚚 Smart Milk Routing"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Recommended Route",
                result.get(
                    "milk_routing",
                    "NOT AVAILABLE",
                ),
            )

        with col2:

            st.metric(
                "Priority",
                result.get(
                    "routing_priority",
                    "UNKNOWN",
                ),
            )

        st.info(
            "📌 **Routing Reason:** "
            + str(
                result.get(
                    "routing_reason",
                    "No routing recommendation available.",
                )
            )
        )


        # =================================================
        # AI RECOMMENDATION
        # =================================================

        st.divider()

        st.subheader(
            "🤖 AI Recommendations"
        )

        st.info(
            "💡 **AI Recommendation:** "
            + str(
                result.get(
                    "ai_recommendation",
                    "No AI recommendation available.",
                )
            )
        )

        st.success(
            "🎯 **Recommended Action:** "
            + str(
                result.get(
                    "recommended_action",
                    "No recommended action available.",
                )
            )
        )

        st.caption(
            "📊 Recommendations generated: "
            + str(
                result.get(
                    "recommendation_count",
                    0,
                )
            )
        )


        # =================================================
        # SAVE TEST
        # =================================================

        st.divider()

        if st.button(
            "💾 Save Test to Database",
            use_container_width=True,
        ):

            try:

                save_payload = {

                    "farmer_id":
                        farmer_id,

                    "batch_id":
                        batch_id,

                    "red":
                        result.get(
                            "red",
                            0,
                        ),

                    "green":
                        result.get(
                            "green",
                            0,
                        ),

                    "blue":
                        result.get(
                            "blue",
                            0,
                        ),

                    "temperature":
                        result.get(
                            "temperature",
                            0,
                        ),

                    "quality_score":
                        result.get(
                            "quality_score"
                        ),

                    "status":
                        result.get(
                            "status",
                            result.get(
                                "milk_status"
                            ),
                        ),

                    "spoilage_risk":
                        result.get(
                            "spoilage_risk"
                        ),
                }

                save_response = requests.post(
                    f"{API_URL}/api/save-test",
                    json=save_payload,
                    timeout=15,
                )

                if save_response.status_code == 200:

                    st.success(
                        "✅ Milk test saved successfully!"
                    )

                else:

                    show_api_error(
                        save_response
                    )

            except Exception as e:

                st.error(
                    f"Save error: {e}"
                )


    # =====================================================
    # MBRT MONITORING
    # =====================================================

    st.divider()

    st.header(
        "🧪 MBRT Microbial-Quality Monitoring"
    )

    st.info(
        "Place the milk + MBRT working solution inside "
        "the closed chamber. Press Start MBRT to begin "
        "fresh image monitoring."
    )


    # =====================================================
    # START / STOP
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "▶️ Start MBRT",
            use_container_width=True,
        ):

            try:

                response = requests.post(
                    f"{API_URL}/api/mbrt/start",
                    json={
                        "farmer_id": farmer_id,
                        "batch_id": batch_id,
                    },
                    timeout=10,
                )

                if response.status_code == 200:

                    data = response.json()

                    st.success(
                        "✅ MBRT monitoring started!"
                    )

                    st.caption(
                        f"Fresh image interval: "
                        f"{data.get('interval_seconds', 30)} seconds"
                    )

                else:

                    show_api_error(response)

            except Exception as e:

                st.error(
                    f"MBRT start error: {e}"
                )


    with col2:

        if st.button(
            "⏹️ Stop MBRT",
            use_container_width=True,
        ):

            try:

                response = requests.post(
                    f"{API_URL}/api/mbrt/stop",
                    timeout=10,
                )

                if response.status_code == 200:

                    st.success(
                        "🛑 MBRT monitoring stopped."
                    )

                else:

                    show_api_error(response)

            except Exception as e:

                st.error(
                    f"MBRT stop error: {e}"
                )


    # =====================================================
    # MBRT STATUS
    # =====================================================

    try:

        status_response = requests.get(
            f"{API_URL}/api/mbrt/status",
            timeout=5,
        )

        if status_response.status_code == 200:

            mbrt = status_response.json()

            if mbrt.get("running"):

                st.success(
                    "🟢 MBRT monitoring is running"
                )

            else:

                st.warning(
                    "⚪ MBRT monitoring is stopped"
                )


            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Elapsed Time",
                    f"{mbrt.get('elapsed_minutes', 0):.2f} min",
                )

            with col2:

                st.metric(
                    "Fresh Images",
                    mbrt.get(
                        "images_captured",
                        0,
                    ),
                )

            with col3:

                latest = mbrt.get(
                    "latest"
                )

                if latest:

                    st.metric(
                        "Latest Reading",
                        f"{latest.get('elapsed_minutes', 0):.2f} min",
                    )

                else:

                    st.metric(
                        "Latest Reading",
                        "Waiting",
                    )


            # =================================================
            # LATEST MBRT IMAGE
            # =================================================

            latest = mbrt.get(
                "latest"
            )

            if latest:

                image_path = Path(
                    latest.get(
                        "image_path",
                        "",
                    )
                )

                if image_path.exists():

                    image_bytes = (
                        image_path.read_bytes()
                    )

                    st.image(
                        image_bytes,
                        caption=(
                            "Latest Fresh MBRT Image — "
                            f"{latest.get('elapsed_minutes', 0):.2f} min"
                        ),
                        width=500,
                    )


                # =============================================
                # COLOUR ANALYSIS
                # =============================================

                colour = latest.get(
                    "colour"
                )

                if colour:

                    st.subheader(
                        "🎨 MBRT Camera Colour Analysis"
                    )

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.metric(
                            "Red",
                            f"{colour.get('red', 0):.2f}",
                        )

                    with col2:

                        st.metric(
                            "Green",
                            f"{colour.get('green', 0):.2f}",
                        )

                    with col3:

                        st.metric(
                            "Blue",
                            f"{colour.get('blue', 0):.2f}",
                        )

                    with col4:

                        st.metric(
                            "Blue Score",
                            f"{colour.get('blue_score', 0):.2f}",
                        )


                    # =========================================
                    # MICROBIAL ACTIVITY ESTIMATE
                    # =========================================

                    mbrt_data = latest.get(
                        "mbrt"
                    )

                    if mbrt_data:

                        st.subheader(
                            "🧫 Microbial Activity Estimate"
                        )

                        col1, col2, col3 = st.columns(3)

                        with col1:

                            st.metric(
                                "Microbial Activity",
                                mbrt_data.get(
                                    "microbial_activity",
                                    "NOT AVAILABLE"
                                )
                            )

                        with col2:

                            st.metric(
                                "MBRT Status",
                                mbrt_data.get(
                                    "mbrt_status",
                                    "MONITORING"
                                )
                            )

                        with col3:

                            st.metric(
                                "Microbial Count",
                                mbrt_data.get(
                                    "microbial_count",
                                    "NOT CALIBRATED"
                                )
                            )

                        st.info(
                            "🧪 **Basis:** "
                            + str(
                                mbrt_data.get(
                                    "basis",
                                    "MBRT colour-change behaviour"
                                )
                            )
                        )



            # =================================================
            # MBRT TIMELINE
            # =================================================

            results = mbrt.get(
                "results",
                [],
            )

            if results:

                rows = []

                for item in results:

                    colour = (
                        item.get(
                            "colour"
                        )
                        or {}
                    )

                    rows.append({

                        "Time (min)":
                            item.get(
                                "elapsed_minutes",
                                0,
                            ),

                        "Red":
                            colour.get(
                                "red",
                                0,
                            ),

                        "Green":
                            colour.get(
                                "green",
                                0,
                            ),

                        "Blue":
                            colour.get(
                                "blue",
                                0,
                            ),

                        "Blue Score":
                            colour.get(
                                "blue_score",
                                0,
                            ),

                        "Microbial Activity":
                            (
                                item.get(
                                    "mbrt"
                                ) or {}
                            ).get(
                                "microbial_activity",
                                "N/A"
                            ),

                    })


                if rows:

                    st.subheader(
                        "📈 MBRT Monitoring Timeline"
                    )

                    df_mbrt = pd.DataFrame(
                        rows
                    )

                    st.dataframe(
                        df_mbrt,
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.line_chart(
                        df_mbrt.set_index(
                            "Time (min)"
                        )[
                            [
                                "Red",
                                "Green",
                                "Blue",
                            ]
                        ]
                    )


    except requests.exceptions.ConnectionError:

        st.warning(
            "MBRT status unavailable: backend is not connected."
        )

    except Exception as e:

        st.warning(
            f"MBRT status error: {e}"
        )


    # =====================================================
    # MBRT NOTE
    # =====================================================



# =========================================================
# TEST HISTORY
# =========================================================

elif page == "Test History":

    st.header(
        "📋 Milk Test History"
    )

    if st.button(
        "🔄 Refresh History",
        use_container_width=True,
    ):

        st.rerun()


    try:

        response = requests.get(
            f"{API_URL}/api/tests",
            timeout=10,
        )

        if response.status_code == 200:

            tests = response.json()

            if tests:

                df = pd.DataFrame(
                    tests
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No milk tests found."
                )

        else:

            show_api_error(response)

    except Exception as e:

        st.error(
            f"History error: {e}"
        )


# =========================================================
# FARMERS
# =========================================================

elif page == "Farmers":

    st.header(
        "👨‍🌾 Farmer Records"
    )

    try:

        response = requests.get(
            f"{API_URL}/api/farmers",
            timeout=10,
        )

        if response.status_code == 200:

            farmers = response.json()

            if farmers:

                all_tests = []

                try:

                    history_response = requests.get(
                        f"{API_URL}/api/tests",
                        timeout=10,
                    )

                    if history_response.status_code == 200:

                        all_tests = (
                            history_response.json()
                        )

                except Exception:

                    all_tests = []


                for farmer in farmers:

                    farmer_id_value = farmer.get(
                        "farmer_id",
                        "N/A",
                    )

                    farmer_tests = [

                        test

                        for test in all_tests

                        if test.get(
                            "farmer_id"
                        )
                        == farmer_id_value

                    ]

                    st.write(
                        f"👨‍🌾 **{farmer_id_value}**"
                    )

                    st.caption(
                        f"Tests recorded: "
                        f"{len(farmer_tests)}"
                    )

                    st.divider()

            else:

                st.info(
                    "No farmers found."
                )

        else:

            show_api_error(response)

    except Exception as e:

        st.error(
            f"Farmer error: {e}"
        )


# =========================================================
# DIGITAL DAIRY PASSPORT
# =========================================================

st.sidebar.divider()

st.sidebar.subheader(
    "📱 Digital Dairy Passport"
)

qr_batch_id = st.sidebar.text_input(
    "Enter Batch ID",
    value="B001",
)


if st.sidebar.button(
    "Generate QR",
):

    try:

        response = requests.get(
            f"{API_URL}/api/tests/{qr_batch_id}",
            timeout=10,
        )

        if response.status_code == 200:

            batch_tests = response.json()

            if batch_tests:

                latest = batch_tests[-1]

                # -----------------------------------------
                # Adulteration is intentionally excluded.
                # Current hardware does not perform an
                # adulteration test.
                # -----------------------------------------

                passport_data = f"""
DairyGuard AI - Digital Dairy Passport

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

MBRT Prototype Status:
{latest.get('mbrt_status', 'N/A')}

MBRT Time:
{latest.get('mbrt_time_seconds', 'N/A')} seconds

MBRT Blue Score:
{latest.get('mbrt_blue_score', 'N/A')}
"""

                qr = qrcode.make(
                    passport_data
                )

                Path(
                    "uploads"
                ).mkdir(
                    exist_ok=True
                )

                qr_path = (
                    Path("uploads")
                    / f"QR_{qr_batch_id}.png"
                )

                qr.save(
                    qr_path
                )

                st.sidebar.success(
                    "QR generated successfully!"
                )

                st.sidebar.image(
                    str(qr_path),
                    caption=(
                        f"Batch {qr_batch_id}"
                    ),
                )

            else:

                st.sidebar.warning(
                    "No test data found for this batch."
                )

        else:

            show_api_error(
                response
            )

    except Exception as e:

        st.sidebar.error(
            f"QR error: {e}"
        )