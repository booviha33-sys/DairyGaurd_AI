# =========================================================
# DAIRYGUARD AI - FASTAPI BACKEND
# =========================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
from typing import Optional
from io import BytesIO

import requests
import time
import threading

from PIL import Image

from backend.database import SessionLocal, MilkTest

from backend.model import (
    predict_shelf_life,
    recommend_milk_routing,
    generate_ai_recommendation,
    analyze_mbrt_result
)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="DairyGuard AI API",
    description=(
        "Milk quality, sensor, camera and MBRT "
        "prototype API"
    ),
    version="1.0.0"
)


# =========================================================
# CONFIGURATION
# =========================================================

CAMERA_URL = "http://10.88.17.1/capture"

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MBRT_DIR = UPLOAD_DIR / "mbrt"

MBRT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# LATEST ESP32 SENSOR READING
# =========================================================

latest_reading = {
    "farmer_id": "",
    "batch_id": "",
    "red": 0.0,
    "green": 0.0,
    "blue": 0.0,
    "temperature": 0.0
}


# =========================================================
# MBRT STATE
# =========================================================

MBRT_RUNNING = False

MBRT_START_TIME = None

MBRT_THREAD = None

# Fresh image every 30 seconds
MBRT_INTERVAL_SECONDS = 30

# Maximum monitoring duration = 30 minutes
MBRT_MAX_DURATION_SECONDS = 30 * 60

# Store latest MBRT observations
MBRT_RESULTS = []

# Maximum results retained in memory
MBRT_MAX_RESULTS = 200

# Prototype only.
# This value is NOT used to claim a scientific endpoint.
MBRT_BLUE_THRESHOLD = 10.0


# =========================================================
# REQUEST MODELS
# =========================================================

class MilkTestRequest(BaseModel):

    farmer_id: str

    batch_id: str

    red: float

    green: float

    blue: float

    temperature: float


class SaveTestRequest(BaseModel):

    farmer_id: str

    batch_id: str

    red: float

    green: float

    blue: float

    temperature: float

    quality_score: Optional[float] = None

    status: Optional[str] = None

    spoilage_risk: Optional[str] = None

    mbrt_time_seconds: Optional[float] = None

    mbrt_blue_score: Optional[float] = None

    mbrt_status: Optional[str] = None

    mbrt_image_path: Optional[str] = None


class MBRTStartRequest(BaseModel):

    farmer_id: Optional[str] = None

    batch_id: Optional[str] = None


# =========================================================
# BASIC ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "DairyGuard AI API is running",
        "version": "1.0.0"
    }


# =========================================================
# COLOUR ANALYSIS
# =========================================================

def analyze_colour(
    red,
    green,
    blue
):

    average = (
        red + green + blue
    ) / 3

    if average >= 150:

        quality_score = 80
        status = "GOOD"
        spoilage_risk = "LOW"

    elif average >= 80:

        quality_score = 60
        status = "CAUTION"
        spoilage_risk = "MEDIUM"

    else:

        quality_score = 40
        status = "TEST REQUIRED"
        spoilage_risk = "HIGH"

    return {
        "quality_score": quality_score,
        "status": status,
        "milk_status": status,
        "spoilage_risk": spoilage_risk
    }


# =========================================================
# MILK TEST
# =========================================================

@app.post("/api/milk-test")
def milk_test(
    request: MilkTestRequest
):

    global latest_reading

    # -----------------------------------------------------
    # STORE LATEST SENSOR READING
    # -----------------------------------------------------

    latest_reading = {
        "farmer_id": request.farmer_id,
        "batch_id": request.batch_id,
        "red": request.red,
        "green": request.green,
        "blue": request.blue,
        "temperature": request.temperature
    }

    # -----------------------------------------------------
    # COLOUR ANALYSIS
    # -----------------------------------------------------

    colour_result = analyze_colour(
        request.red,
        request.green,
        request.blue
    )

    quality_score = colour_result[
        "quality_score"
    ]

    status = colour_result[
        "status"
    ]

    spoilage_risk = colour_result[
        "spoilage_risk"
    ]

    # -----------------------------------------------------
    # SHELF LIFE
    # -----------------------------------------------------

    shelf_result = predict_shelf_life(
        temperature=request.temperature,
        red=request.red,
        green=request.green,
        blue=request.blue,
        quality_score=quality_score
    )

    # -----------------------------------------------------
    # ROUTING
    # -----------------------------------------------------

    routing_result = recommend_milk_routing(
        quality_score=quality_score,
        spoilage_risk=spoilage_risk,
        temperature=request.temperature
    )

    # -----------------------------------------------------
    # AI RECOMMENDATION
    # -----------------------------------------------------

    ai_result = generate_ai_recommendation(
        quality_score=quality_score,
        spoilage_risk=spoilage_risk,
        temperature=request.temperature,
        red=request.red,
        green=request.green,
        blue=request.blue
    )

    # -----------------------------------------------------
    # RETURN RESULT
    # -----------------------------------------------------

    return {
        "farmer_id": request.farmer_id,

        "batch_id": request.batch_id,

        "red": request.red,

        "green": request.green,

        "blue": request.blue,

        "temperature": request.temperature,

        "quality_score": quality_score,

        "status": status,

        "milk_status": status,

        "spoilage_risk": spoilage_risk,

        "estimated_shelf_life_hours":
            shelf_result[
                "estimated_shelf_life_hours"
            ],

        "shelf_life_risk":
            shelf_result[
                "shelf_life_risk"
            ],

        "recommendation":
            shelf_result[
                "recommendation"
            ],

        "shelf_life_recommendation":
            shelf_result[
                "shelf_life_recommendation"
            ],

        "milk_routing":
            routing_result[
                "milk_routing"
            ],

        "routing_priority":
            routing_result[
                "routing_priority"
            ],

        "routing_reason":
            routing_result[
                "routing_reason"
            ],

        "ai_recommendation":
            ai_result[
                "ai_recommendation"
            ],

        "recommended_action":
            ai_result[
                "recommended_action"
            ],

        "recommendation_count":
            ai_result[
                "recommendation_count"
            ],

        "recommendations":
            ai_result[
                "recommendations"
            ],

        "note": (
            "Quality, shelf-life and recommendation "
            "values are prototype rule-based outputs "
            "and are not scientifically validated."
        )
    }


# =========================================================
# LATEST SENSOR READING
# =========================================================

@app.get("/api/latest-reading")
def get_latest_reading():

    return latest_reading


# =========================================================
# SAVE MILK TEST
# =========================================================

@app.post("/api/save-test")
def save_test(
    request: SaveTestRequest
):

    db = SessionLocal()

    try:

        test = MilkTest(

            farmer_id=request.farmer_id,

            batch_id=request.batch_id,

            red=request.red,

            green=request.green,

            blue=request.blue,

            temperature=request.temperature,

            quality_score=request.quality_score,

            status=request.status,

            spoilage_risk=request.spoilage_risk,

            mbrt_time_seconds=request.mbrt_time_seconds,

            mbrt_blue_score=request.mbrt_blue_score,

            mbrt_status=request.mbrt_status,

            mbrt_image_path=request.mbrt_image_path,

            # Current hardware does not perform
            # adulteration testing.
            adulteration_status="NOT TESTED"
        )

        db.add(test)

        db.commit()

        db.refresh(test)

        return {
            "message": "Milk test saved successfully",

            "id": test.id,

            "farmer_id": test.farmer_id,

            "batch_id": test.batch_id
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        db.close()


# =========================================================
# GET ALL TESTS
# =========================================================

@app.get("/api/tests")
def get_tests():

    db = SessionLocal()

    try:

        tests = (
            db.query(MilkTest)
            .order_by(MilkTest.id.desc())
            .all()
        )

        return [

            {
                "id": test.id,

                "farmer_id": test.farmer_id,

                "batch_id": test.batch_id,

                "red": test.red,

                "green": test.green,

                "blue": test.blue,

                "temperature":
                    test.temperature,

                "quality_score":
                    test.quality_score,

                "status":
                    test.status,

                "spoilage_risk":
                    test.spoilage_risk,

                "mbrt_time_seconds":
                    test.mbrt_time_seconds,

                "mbrt_blue_score":
                    test.mbrt_blue_score,

                "mbrt_status":
                    test.mbrt_status,

                "mbrt_image_path":
                    test.mbrt_image_path,

                "adulteration_status":
                    test.adulteration_status
            }

            for test in tests
        ]

    finally:

        db.close()


# =========================================================
# GET TESTS FOR A BATCH
# =========================================================

@app.get("/api/tests/{batch_id}")
def get_batch_tests(
    batch_id: str
):

    db = SessionLocal()

    try:

        tests = (
            db.query(MilkTest)
            .filter(
                MilkTest.batch_id == batch_id
            )
            .order_by(MilkTest.id.asc())
            .all()
        )

        return [

            {
                "id": test.id,

                "farmer_id": test.farmer_id,

                "batch_id": test.batch_id,

                "red": test.red,

                "green": test.green,

                "blue": test.blue,

                "temperature":
                    test.temperature,

                "quality_score":
                    test.quality_score,

                "status":
                    test.status,

                "spoilage_risk":
                    test.spoilage_risk,

                "mbrt_time_seconds":
                    test.mbrt_time_seconds,

                "mbrt_blue_score":
                    test.mbrt_blue_score,

                "mbrt_status":
                    test.mbrt_status,

                "mbrt_image_path":
                    test.mbrt_image_path,

                "adulteration_status":
                    test.adulteration_status
            }

            for test in tests
        ]

    finally:

        db.close()


# =========================================================
# CAMERA - FRESH IMAGE REQUEST
# =========================================================

def request_fresh_camera_image():

    headers = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Expires": "0"
    }

    response = requests.get(
        CAMERA_URL,
        headers=headers,
        timeout=(5, 20)
    )

    response.raise_for_status()

    image_bytes = response.content

    if len(image_bytes) < 1000:

        raise RuntimeError(
            "Camera returned an unexpectedly small image."
        )

    return image_bytes


# =========================================================
# CAMERA CAPTURE
# =========================================================

@app.get("/api/camera/capture")
def camera_capture():

    last_error = None

    for attempt in range(3):

        try:

            image_bytes = request_fresh_camera_image()

            return {
                "success": True,

                "image_size":
                    len(image_bytes),

                "attempt":
                    attempt + 1
            }

        except Exception as e:

            last_error = str(e)

            time.sleep(1)

    raise HTTPException(
        status_code=502,
        detail=(
            "Unable to capture fresh image "
            f"from ESP32-CAM: {last_error}"
        )
    )


# =========================================================
# CAMERA CAPTURE + SAVE
# =========================================================

@app.get("/api/camera/save")
def camera_save():

    last_error = None

    for attempt in range(3):

        try:

            image_bytes = request_fresh_camera_image()

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S_%f"
            )

            unique_path = (
                UPLOAD_DIR
                / f"milk_sample_{timestamp}.jpg"
            )

            unique_path.write_bytes(
                image_bytes
            )

            # Compatibility image
            latest_path = (
                UPLOAD_DIR
                / "milk_sample.jpg"
            )

            latest_path.write_bytes(
                image_bytes
            )

            return {

                "success": True,

                "image_path":
                    str(unique_path),

                "latest_image_path":
                    str(latest_path),

                "image_size":
                    len(image_bytes),

                "attempt":
                    attempt + 1
            }

        except Exception as e:

            last_error = str(e)

            time.sleep(1)

    raise HTTPException(
        status_code=502,
        detail=(
            "Unable to capture and save "
            f"camera image: {last_error}"
        )
    )


# =========================================================
# MBRT - CAPTURE FRESH IMAGE
# =========================================================

def capture_fresh_mbrt_image():

    image_bytes = request_fresh_camera_image()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    image_path = (
        MBRT_DIR
        / f"mbrt_{timestamp}.jpg"
    )

    image_path.write_bytes(
        image_bytes
    )

    return (
        image_path,
        image_bytes
    )


# =========================================================
# MBRT - IMAGE ANALYSIS
# =========================================================

def analyze_mbrt_image(
    image_path
):

    try:

        image = Image.open(
            image_path
        ).convert("RGB")

        width, height = image.size

        # -------------------------------------------------
        # CENTRAL REGION
        # -------------------------------------------------

        left = int(
            width * 0.30
        )

        right = int(
            width * 0.70
        )

        top = int(
            height * 0.20
        )

        bottom = int(
            height * 0.85
        )

        cropped = image.crop(
            (
                left,
                top,
                right,
                bottom
            )
        )

        cropped.thumbnail(
            (160, 160)
        )

        pixels = list(
            cropped.getdata()
        )

        if not pixels:

            raise RuntimeError(
                "No image pixels available."
            )

        # -------------------------------------------------
        # AVERAGE RGB
        # -------------------------------------------------

        avg_r = (
            sum(
                pixel[0]
                for pixel in pixels
            )
            / len(pixels)
        )

        avg_g = (
            sum(
                pixel[1]
                for pixel in pixels
            )
            / len(pixels)
        )

        avg_b = (
            sum(
                pixel[2]
                for pixel in pixels
            )
            / len(pixels)
        )

        # -------------------------------------------------
        # BLUE SCORE
        # -------------------------------------------------

        blue_score = (
            avg_b
            - (
                avg_r + avg_g
            ) / 2
        )

        return {

            "red": avg_r,

            "green": avg_g,

            "blue": avg_b,

            "blue_score":
                blue_score,

            "image_size":
                (
                    width,
                    height
                )
        }

    except Exception as e:

        raise RuntimeError(
            f"MBRT image analysis failed: {e}"
        )


# =========================================================
# MBRT MONITORING THREAD
# =========================================================

def mbrt_monitor():

    global MBRT_RUNNING
    global MBRT_START_TIME
    global MBRT_RESULTS

    MBRT_START_TIME = time.time()

    while MBRT_RUNNING:

        elapsed = (
            time.time()
            - MBRT_START_TIME
        )

        # -------------------------------------------------
        # MAXIMUM DURATION
        # -------------------------------------------------

        if elapsed >= MBRT_MAX_DURATION_SECONDS:

            MBRT_RUNNING = False

            break

        # -------------------------------------------------
        # CAPTURE FRESH IMAGE
        # -------------------------------------------------

        try:

            image_path, image_bytes = (
                capture_fresh_mbrt_image()
            )

            colour = analyze_mbrt_image(
                image_path
            )

            # -------------------------------------------------
            # MBRT PROTOTYPE RESULT
            # -------------------------------------------------

            mbrt_result = analyze_mbrt_result(
    elapsed_seconds=elapsed,
    blue_score=colour["blue_score"]
)

            result = {

                "timestamp":
                    datetime.now().isoformat(),

                "elapsed_seconds":
                    elapsed,

                "elapsed_minutes":
                    elapsed / 60,

                "image_path":
                    str(image_path),

                "colour":
                    colour,

                "mbrt":
                    mbrt_result
            }

            MBRT_RESULTS.append(
                result
            )

            # Keep memory bounded

            if len(MBRT_RESULTS) > MBRT_MAX_RESULTS:

                MBRT_RESULTS = (
                    MBRT_RESULTS[
                        -MBRT_MAX_RESULTS:
                    ]
                )

        except Exception as e:

            MBRT_RESULTS.append({

                "timestamp":
                    datetime.now().isoformat(),

                "elapsed_seconds":
                    elapsed,

                "elapsed_minutes":
                    elapsed / 60,

                "error":
                    str(e)
            })

        # -------------------------------------------------
        # WAIT FOR NEXT FRESH IMAGE
        # -------------------------------------------------

        for _ in range(
            MBRT_INTERVAL_SECONDS
        ):

            if not MBRT_RUNNING:

                break

            time.sleep(1)


# =========================================================
# START MBRT
# =========================================================

@app.post("/api/mbrt/start")
def start_mbrt(
    request: Optional[MBRTStartRequest] = None
):

    global MBRT_RUNNING
    global MBRT_START_TIME
    global MBRT_THREAD
    global MBRT_RESULTS

    if MBRT_RUNNING:

        return {

            "message":
                "MBRT monitoring is already running",

            "running":
                True,

            "interval_seconds":
                MBRT_INTERVAL_SECONDS
        }

    # Clear previous monitoring results

    MBRT_RESULTS = []

    MBRT_RUNNING = True

    MBRT_START_TIME = time.time()

    MBRT_THREAD = threading.Thread(
        target=mbrt_monitor,
        daemon=True
    )

    MBRT_THREAD.start()

    return {

        "message":
            "MBRT monitoring started",

        "running":
            True,

        "interval_seconds":
            MBRT_INTERVAL_SECONDS,

        "maximum_duration_minutes":
            MBRT_MAX_DURATION_SECONDS / 60,

        "farmer_id":
            request.farmer_id
            if request else None,

        "batch_id":
            request.batch_id
            if request else None
    }


# =========================================================
# STOP MBRT
# =========================================================

@app.post("/api/mbrt/stop")
def stop_mbrt():

    global MBRT_RUNNING

    MBRT_RUNNING = False

    return {

        "message":
            "MBRT monitoring stopped",

        "running":
            False,

        "images_captured":
            len(MBRT_RESULTS)
    }


# =========================================================
# MBRT STATUS
# =========================================================

@app.get("/api/mbrt/status")
def mbrt_status():

    elapsed = 0

    if MBRT_START_TIME is not None:

        elapsed = (
            time.time()
            - MBRT_START_TIME
        )

    latest = None

    if MBRT_RESULTS:

        latest = MBRT_RESULTS[-1]

    return {

        "running":
            MBRT_RUNNING,

        "elapsed_seconds":
            elapsed,

        "elapsed_minutes":
            elapsed / 60,

        "images_captured":
            len(MBRT_RESULTS),

        "latest":
            latest,

        "results":
            MBRT_RESULTS[-20:]
    }


# =========================================================
# FARMER RECORDS
# =========================================================

@app.get("/api/farmers")
def get_farmers():

    db = SessionLocal()

    try:

        tests = (
            db.query(MilkTest)
            .order_by(MilkTest.id.asc())
            .all()
        )

        farmer_ids = []

        for test in tests:

            if (
                test.farmer_id
                and test.farmer_id
                not in farmer_ids
            ):

                farmer_ids.append(
                    test.farmer_id
                )

        return [

            {
                "farmer_id":
                    farmer_id
            }

            for farmer_id
            in farmer_ids
        ]

    finally:

        db.close()