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
    layout="wide"
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
# SIDEBAR
# =========================================================

st.sidebar.title("🥛 DairyGuard AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "Milk Test",
        "Test History",
        "Farmers"
    ]
)


# =========================================================
# MILK TEST PAGE
# =========================================================

if page == "Milk Test":

    st.header("🧪 Milk Quality Test")


    # =====================================================
    # FARMER AND BATCH DETAILS
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        farmer_id = st.text_input(
            "👨‍🌾 Farmer ID",
            value="F001"
        )

    with col2:

        batch_id = st.text_input(
            "📦 Batch ID",
            value="B001"
        )


    st.divider()


    # =====================================================
    # CAMERA SECTION
    # =====================================================

    st.subheader("📸 Milk Sample Camera")


    if st.button("📸 Capture Milk Sample"):

        # Start with capture marked as failed
        st.session_state["camera_captured"] = False

        try:

            response = requests.get(
                f"{API_URL}/api/camera/save",
                timeout=70
            )


            if response.status_code == 200:

                camera_result = response.json()

                st.session_state[
                    "camera_captured"
                ] = True

                st.success(
                    "✅ Milk sample image captured successfully!"
                )

                st.write(
                    f"Image size: "
                    f"{camera_result.get('image_size', 0)} bytes"
                )


            else:

                st.error(
                    f"Camera capture failed: "
                    f"{response.status_code}"
                )


        except requests.exceptions.Timeout:

            st.session_state[
                "camera_captured"
            ] = False

            st.error(
                "⏱️ Camera request timed out. "
                "Please try again."
            )


        except requests.exceptions.ConnectionError:

            st.session_state[
                "camera_captured"
            ] = False

            st.error(
                "❌ Cannot connect to DairyGuard backend."
            )


        except Exception as e:

            st.session_state[
                "camera_captured"
            ] = False

            st.error(
                f"Camera error: {e}"
            )


    # =====================================================
    # DISPLAY LATEST CAPTURED IMAGE
    # =====================================================

    if st.session_state.get(
        "camera_captured",
        False
    ):

        image_path = Path(
            "uploads/milk_sample.jpg"
        )


        if image_path.exists():

            try:

                # -------------------------------------------------
                # READ THE ACTUAL IMAGE BYTES
                # -------------------------------------------------

                with open(
                    image_path,
                    "rb"
                ) as image_file:

                    image_bytes = image_file.read()


                # -------------------------------------------------
                # DISPLAY IMAGE BYTES
                # This avoids browser image caching.
                # -------------------------------------------------

                st.image(
                    image_bytes,
                    caption="Latest Captured Milk Sample",
                    width=500
                )


            except Exception as e:

                st.error(
                    f"Unable to display captured image: {e}"
                )


    st.divider()


    # =====================================================
    # SENSOR READING
    # =====================================================

    st.subheader("🌈 Sensor Reading")


    if st.button("📡 Read Sensor"):

        try:

            response = requests.get(
                f"{API_URL}/api/latest-reading",
                timeout=10
            )


            if response.status_code == 200:

                sensor_data = response.json()

                st.session_state[
                    "sensor_data"
                ] = sensor_data

                st.success(
                    "Sensor reading received!"
                )


            else:

                st.error(
                    "Unable to read sensor data."
                )


        except requests.exceptions.Timeout:

            st.error(
                "Sensor request timed out."
            )


        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to DairyGuard backend."
            )


        except Exception as e:

            st.error(
                f"Sensor error: {e}"
            )


    # =====================================================
    # DISPLAY SENSOR VALUES
    # =====================================================

    sensor_data = st.session_state.get(
        "sensor_data",
        None
    )


    if sensor_data:

        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "🔴 Red",
                sensor_data.get(
                    "red",
                    0
                )
            )


        with col2:

            st.metric(
                "🟢 Green",
                sensor_data.get(
                    "green",
                    0
                )
            )


        with col3:

            st.metric(
                "🔵 Blue",
                sensor_data.get(
                    "blue",
                    0
                )
            )


        with col4:

            temperature = sensor_data.get(
                "temperature",
                0
            )

            st.metric(
                "🌡️ Temperature",
                f"{temperature:.1f} °C"
            )


    st.divider()


    # =====================================================
    # ANALYZE CURRENT READING
    # =====================================================

    st.subheader("🔬 Milk Quality Analysis")


    if st.button(
        "🔍 Analyze Current Reading",
        type="primary"
    ):

        try:

            # -------------------------------------------------
            # GET LATEST SENSOR DATA
            # -------------------------------------------------

            response = requests.get(
                f"{API_URL}/api/latest-reading",
                timeout=10
            )


            if response.status_code != 200:

                st.error(
                    "Unable to retrieve sensor data."
                )

                st.stop()


            sensor_data = response.json()


            # -------------------------------------------------
            # CREATE REQUEST
            # -------------------------------------------------

            payload = {

                "farmer_id":
                    farmer_id,

                "batch_id":
                    batch_id,

                "red":
                    sensor_data.get(
                        "red",
                        0
                    ),

                "green":
                    sensor_data.get(
                        "green",
                        0
                    ),

                "blue":
                    sensor_data.get(
                        "blue",
                        0
                    ),

                "temperature":
                    sensor_data.get(
                        "temperature",
                        0
                    )
            }


            # -------------------------------------------------
            # SEND DATA TO FASTAPI
            # -------------------------------------------------

            response = requests.post(

                f"{API_URL}/api/milk-test",

                json=payload,

                timeout=15
            )


            if response.status_code == 200:

                result = response.json()

                st.session_state[
                    "analysis_result"
                ] = result

                st.success(
                    "Milk analysis completed successfully!"
                )


            else:

                st.error(
                    f"Analysis failed: "
                    f"{response.text}"
                )


        except requests.exceptions.Timeout:

            st.error(
                "Analysis request timed out."
            )


        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to DairyGuard backend."
            )


        except Exception as e:

            st.error(
                f"Error: {e}"
            )


    # =====================================================
    # DISPLAY ANALYSIS RESULT
    # =====================================================

    result = st.session_state.get(
        "analysis_result",
        None
    )


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
                f"{result.get('quality_score', 0)}/100"
            )


        with col2:

            milk_status = result.get(
                "milk_status",
                result.get(
                    "status",
                    "N/A"
                )
            )

            st.metric(
                "Status",
                milk_status
            )


        with col3:

            st.metric(
                "Spoilage Risk",
                result.get(
                    "spoilage_risk",
                    "N/A"
                )
            )


        with col4:

            temperature = result.get(
                "temperature",
                0
            )

            st.metric(
                "Temperature",
                f"{temperature:.1f} °C"
            )


        # =================================================
        # RGB VALUES
        # =================================================

        st.subheader(
            "🌈 Colour Sensor Values"
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Red",
                result.get(
                    "red",
                    0
                )
            )


        with col2:

            st.metric(
                "Green",
                result.get(
                    "green",
                    0
                )
            )


        with col3:

            st.metric(
                "Blue",
                result.get(
                    "blue",
                    0
                )
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
                "N/A"
            )

            st.metric(
                "Estimated Shelf Life",
                f"{shelf_life} hours"
            )


        with col2:

            shelf_risk = result.get(
                "shelf_life_risk",
                "N/A"
            )

            st.metric(
                "Shelf-Life Risk",
                shelf_risk
            )


        shelf_recommendation = result.get(
            "shelf_life_recommendation",
            result.get(
                "recommendation",
                "No recommendation available."
            )
        )


        st.info(
            f"💡 **Shelf-Life Recommendation:** "
            f"{shelf_recommendation}"
        )


        # =================================================
        # SMART MILK ROUTING
        # =================================================

        st.divider()

        st.subheader(
            "🚚 Smart Milk Routing"
        )


        routing = result.get(
            "milk_routing",
            "NOT AVAILABLE"
        )


        routing_priority = result.get(
            "routing_priority",
            "UNKNOWN"
        )


        routing_reason = result.get(
            "routing_reason",
            "No routing recommendation available."
        )


        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "Recommended Route",
                routing
            )


        with col2:

            st.metric(
                "Priority",
                routing_priority
            )


        st.info(
            f"📌 **Routing Reason:** "
            f"{routing_reason}"
        )


        # =================================================
        # AI RECOMMENDATIONS
        # =================================================

        st.divider()

        st.subheader(
            "🤖 AI Recommendations"
        )


        ai_recommendation = result.get(
            "ai_recommendation",
            "No AI recommendation available."
        )


        recommended_action = result.get(
            "recommended_action",
            "No recommended action available."
        )


        recommendation_count = result.get(
            "recommendation_count",
            0
        )


        st.info(
            f"💡 **AI Recommendation:** "
            f"{ai_recommendation}"
        )


        st.success(
            f"🎯 **Recommended Action:** "
            f"{recommended_action}"
        )


        st.caption(
            f"📊 Recommendations generated: "
            f"{recommendation_count}"
        )


        # =================================================
        # SAVE TEST
        # =================================================

        st.divider()


        if st.button(
            "💾 Save Test to Database"
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
                            0
                        ),

                    "green":
                        result.get(
                            "green",
                            0
                        ),

                    "blue":
                        result.get(
                            "blue",
                            0
                        ),

                    "temperature":
                        result.get(
                            "temperature",
                            0
                        )
                }


                save_response = requests.post(

                    f"{API_URL}/api/save-test",

                    json=save_payload,

                    timeout=15
                )


                if save_response.status_code == 200:

                    st.success(
                        "✅ Milk test saved successfully!"
                    )


                else:

                    st.error(
                        f"Failed to save test: "
                        f"{save_response.text}"
                    )


            except requests.exceptions.Timeout:

                st.error(
                    "Save request timed out."
                )


            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to DairyGuard backend."
                )


            except Exception as e:

                st.error(
                    f"Save error: {e}"
                )


# =========================================================
# TEST HISTORY PAGE
# =========================================================

elif page == "Test History":

    st.header(
        "📋 Milk Test History"
    )


    if st.button(
        "🔄 Refresh History"
    ):

        st.rerun()


    try:

        response = requests.get(
            f"{API_URL}/api/tests",
            timeout=10
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
                    hide_index=True
                )


            else:

                st.info(
                    "No milk tests found."
                )


        else:

            st.error(
                "Unable to retrieve test history."
            )


    except requests.exceptions.Timeout:

        st.error(
            "History request timed out."
        )


    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to DairyGuard backend."
        )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )


# =========================================================
# FARMERS PAGE
# =========================================================

elif page == "Farmers":

    st.header(
        "👨‍🌾 Farmer Records"
    )


    try:

        response = requests.get(
            f"{API_URL}/api/farmers",
            timeout=10
        )


        if response.status_code == 200:

            farmers = response.json()


            if farmers:

                st.subheader(
                    "Registered Farmers"
                )


                for farmer in farmers:

                    farmer_id = farmer.get(
                        "farmer_id",
                        "N/A"
                    )


                    st.write(
                        f"👨‍🌾 **{farmer_id}**"
                    )


                    try:

                        history_response = requests.get(

                            f"{API_URL}/api/tests",

                            timeout=10
                        )


                        if (
                            history_response.status_code
                            == 200
                        ):

                            all_tests = (
                                history_response.json()
                            )


                            farmer_tests = [

                                test

                                for test
                                in all_tests

                                if test.get(
                                    "farmer_id"
                                ) == farmer_id

                            ]


                            st.caption(
                                f"Tests recorded: "
                                f"{len(farmer_tests)}"
                            )


                    except Exception:

                        pass


            else:

                st.info(
                    "No farmers found."
                )


        else:

            st.error(
                "Unable to retrieve farmers."
            )


    except requests.exceptions.Timeout:

        st.error(
            "Farmer request timed out."
        )


    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to DairyGuard backend."
        )


    except Exception as e:

        st.error(
            f"Error: {e}"
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
    value="B001"
)


if st.sidebar.button(
    "Generate QR"
):

    try:

        response = requests.get(

            f"{API_URL}/api/tests/{qr_batch_id}",

            timeout=10
        )


        if response.status_code == 200:

            batch_tests = response.json()


            if batch_tests:

                latest = batch_tests[0]


                # -------------------------------------------------
                # DIGITAL DAIRY PASSPORT
                # Adulteration removed
                # -------------------------------------------------

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
"""


                qr = qrcode.make(
                    passport_data
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
                    caption=f"Batch {qr_batch_id}"
                )


            else:

                st.sidebar.warning(
                    "No test data found for this batch."
                )


        else:

            st.sidebar.error(
                "Unable to retrieve batch data."
            )


    except requests.exceptions.Timeout:

        st.sidebar.error(
            "QR request timed out."
        )


    except requests.exceptions.ConnectionError:

        st.sidebar.error(
            "Cannot connect to DairyGuard backend."
        )


    except Exception as e:

        st.sidebar.error(
            f"QR error: {e}"
        )