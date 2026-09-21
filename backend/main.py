# =========================================================
# DAIRYGUARD AI - FASTAPI BACKEND
# =========================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path

import requests
import time

from backend.database import SessionLocal, MilkTest

from backend.model import (
    predict_shelf_life,
    recommend_milk_routing,
    generate_ai_recommendation
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="DairyGuard AI API",
    description="Intelligent Milk Quality Assessment System",
    version="1.0.0"
)


# =========================================================
# CAMERA CONFIGURATION
# =========================================================

CAMERA_URL = "http://10.25.58.1/capture"

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# LATEST SENSOR READING
# =========================================================

latest_reading = {
    "farmer_id": "F001",
    "batch_id": "B001",
    "red": 0,
    "green": 0,
    "blue": 0,
    "temperature": 0.0
}


# =========================================================
# REQUEST MODEL
# =========================================================

class MilkTestRequest(BaseModel):

    farmer_id: str
    batch_id: str

    red: float
    green: float
    blue: float

    temperature: float


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "DairyGuard AI Backend is running",
        "status": "online"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# COLOUR ANALYSIS
# =========================================================

def analyze_colour(red, green, blue):

    average_rgb = (
        red +
        green +
        blue
    ) / 3

    # -----------------------------------------------------
    # PROTOTYPE DEMO LOGIC
    # -----------------------------------------------------

    if average_rgb >= 150:

        quality_score = 80
        status = "GOOD"
        spoilage_risk = "LOW"

    elif average_rgb >= 80:

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
        "spoilage_risk": spoilage_risk
    }


# =========================================================
# MILK TEST
# =========================================================

@app.post("/api/milk-test")
def milk_test(data: MilkTestRequest):

    global latest_reading

    # -----------------------------------------------------
    # SAVE LATEST SENSOR READING
    # -----------------------------------------------------

    latest_reading = {
        "farmer_id": data.farmer_id,
        "batch_id": data.batch_id,
        "red": data.red,
        "green": data.green,
        "blue": data.blue,
        "temperature": data.temperature
    }

    # -----------------------------------------------------
    # COLOUR ANALYSIS
    # -----------------------------------------------------

    colour_result = analyze_colour(
        data.red,
        data.green,
        data.blue
    )

    quality_score = colour_result["quality_score"]
    status = colour_result["status"]
    spoilage_risk = colour_result["spoilage_risk"]

    # -----------------------------------------------------
    # SHELF LIFE
    # -----------------------------------------------------

    shelf_life_result = predict_shelf_life(
        temperature=data.temperature,
        red=data.red,
        green=data.green,
        blue=data.blue,
        quality_score=quality_score
    )

    shelf_life_hours = (
        shelf_life_result[
            "estimated_shelf_life_hours"
        ]
    )

    shelf_life_risk = (
        shelf_life_result[
            "shelf_life_risk"
        ]
    )

    shelf_life_recommendation = (
        shelf_life_result[
            "recommendation"
        ]
    )

    # -----------------------------------------------------
    # SMART MILK ROUTING
    # -----------------------------------------------------

    routing_result = recommend_milk_routing(
        quality_score=quality_score,
        spoilage_risk=spoilage_risk,
        temperature=data.temperature
    )

    routing = routing_result["route"]
    routing_priority = routing_result["priority"]
    routing_reason = routing_result["reason"]

    # -----------------------------------------------------
    # AI RECOMMENDATION
    # -----------------------------------------------------

    ai_result = generate_ai_recommendation(
        temperature=data.temperature,
        quality_score=quality_score,
        spoilage_risk=spoilage_risk,
        shelf_life_hours=shelf_life_hours,
        routing_priority=routing_priority
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "status": "success",

        "farmer_id": data.farmer_id,

        "batch_id": data.batch_id,

        "red": data.red,

        "green": data.green,

        "blue": data.blue,

        "temperature": data.temperature,

        "quality_score": quality_score,

        "milk_status": status,

        "spoilage_risk": spoilage_risk,

        "estimated_shelf_life_hours":
            shelf_life_hours,

        "shelf_life_risk":
            shelf_life_risk,

        "shelf_life_recommendation":
            shelf_life_recommendation,

        "milk_routing":
            routing,

        "routing_priority":
            routing_priority,

        "routing_reason":
            routing_reason,

        "ai_recommendation":
            ai_result["recommendation"],

        "recommended_action":
            ai_result["recommended_action"],

        "recommendation_count":
            ai_result["number_of_recommendations"]
    }


# =========================================================
# GET LATEST SENSOR READING
# =========================================================

@app.get("/api/latest-reading")
def get_latest_reading():

    return latest_reading


# =========================================================
# SAVE MILK TEST
# =========================================================

@app.post("/api/save-test")
def save_test(data: MilkTestRequest):

    # -----------------------------------------------------
    # ANALYZE COLOUR
    # -----------------------------------------------------

    colour_result = analyze_colour(
        data.red,
        data.green,
        data.blue
    )

    quality_score = colour_result["quality_score"]
    status = colour_result["status"]
    spoilage_risk = colour_result["spoilage_risk"]

    # -----------------------------------------------------
    # SHELF LIFE
    # -----------------------------------------------------

    shelf_life_result = predict_shelf_life(
        temperature=data.temperature,
        red=data.red,
        green=data.green,
        blue=data.blue,
        quality_score=quality_score
    )

    shelf_life_hours = (
        shelf_life_result[
            "estimated_shelf_life_hours"
        ]
    )

    # -----------------------------------------------------
    # ROUTING
    # -----------------------------------------------------

    routing_result = recommend_milk_routing(
        quality_score=quality_score,
        spoilage_risk=spoilage_risk,
        temperature=data.temperature
    )

    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    db = SessionLocal()

    try:

        test = MilkTest(

            farmer_id=data.farmer_id,

            batch_id=data.batch_id,

            red=data.red,

            green=data.green,

            blue=data.blue,

            temperature=data.temperature,

            quality_score=quality_score,

            status=status,

            spoilage_risk=spoilage_risk

        )

        db.add(test)

        db.commit()

        db.refresh(test)

        return {

            "status": "success",

            "message": "Milk test saved successfully",

            "test_id": test.id,

            "farmer_id": data.farmer_id,

            "batch_id": data.batch_id,

            "quality_score": quality_score,

            "milk_status": status,

            "spoilage_risk": spoilage_risk,

            "temperature": data.temperature,

            "estimated_shelf_life_hours":
                shelf_life_hours,

            "milk_routing":
                routing_result["route"],

            "routing_priority":
                routing_result["priority"]

        }

    finally:

        db.close()


# =========================================================
# GET ALL TESTS
# =========================================================

@app.get("/api/tests")
def get_all_tests():

    db = SessionLocal()

    try:

        tests = (
            db.query(MilkTest)
            .order_by(MilkTest.id.desc())
            .all()
        )

        result = []

        for test in tests:

            result.append({

                "id": test.id,

                "farmer_id":
                    test.farmer_id,

                "batch_id":
                    test.batch_id,

                "red":
                    test.red,

                "green":
                    test.green,

                "blue":
                    test.blue,

                "temperature":
                    test.temperature,

                "quality_score":
                    test.quality_score,

                "status":
                    test.status,

                "spoilage_risk":
                    test.spoilage_risk

            })

        return result

    finally:

        db.close()


# =========================================================
# GET TESTS BY BATCH ID
# =========================================================

@app.get("/api/tests/{batch_id}")
def get_tests_by_batch(batch_id: str):

    db = SessionLocal()

    try:

        tests = (
            db.query(MilkTest)
            .filter(
                MilkTest.batch_id == batch_id
            )
            .order_by(MilkTest.id.desc())
            .all()
        )

        if not tests:

            raise HTTPException(
                status_code=404,
                detail="Batch not found"
            )

        result = []

        for test in tests:

            result.append({

                "id": test.id,

                "farmer_id":
                    test.farmer_id,

                "batch_id":
                    test.batch_id,

                "red":
                    test.red,

                "green":
                    test.green,

                "blue":
                    test.blue,

                "temperature":
                    test.temperature,

                "quality_score":
                    test.quality_score,

                "status":
                    test.status,

                "spoilage_risk":
                    test.spoilage_risk

            })

        return result

    finally:

        db.close()


# =========================================================
# CAMERA CAPTURE
# =========================================================
#
# IMPORTANT:
# The ESP32-CAM connection can occasionally time out.
# Therefore we try up to 3 times.
#
# =========================================================

@app.get("/api/camera/capture")
def capture_camera():

    max_attempts = 3

    for attempt in range(
        1,
        max_attempts + 1
    ):

        try:

            print(
                f"Camera capture attempt "
                f"{attempt}/{max_attempts}"
            )

            response = requests.get(

                CAMERA_URL,

                timeout=(5, 20)
            )

            response.raise_for_status()

            print(
                "Camera capture successful: "
                f"{len(response.content)} bytes"
            )

            return {

                "status": "success",

                "camera_url":
                    CAMERA_URL,

                "image_size":
                    len(response.content)

            }

        except requests.exceptions.RequestException as e:

            print(
                f"Camera attempt "
                f"{attempt} failed: {e}"
            )

            if attempt < max_attempts:

                time.sleep(1)

    raise HTTPException(

        status_code=504,

        detail=(
            "ESP32-CAM did not respond "
            "after 3 attempts."
        )
    )


# =========================================================
# SAVE CAMERA IMAGE
# =========================================================

@app.get("/api/camera/save")
def save_camera_image():

    max_attempts = 3

    for attempt in range(
        1,
        max_attempts + 1
    ):

        try:

            print(
                f"Camera save attempt "
                f"{attempt}/{max_attempts}"
            )

            response = requests.get(

                CAMERA_URL,

                timeout=(5, 20)
            )

            response.raise_for_status()

            # -------------------------------------------------
            # IMAGE PATH
            # -------------------------------------------------

            image_path = (
                UPLOAD_DIR /
                "milk_sample.jpg"
            )

            # -------------------------------------------------
            # SAVE IMAGE
            # -------------------------------------------------

            with open(
                image_path,
                "wb"
            ) as file:

                file.write(
                    response.content
                )

            print(
                "Milk sample saved:"
                f" {image_path}"
            )

            return {

                "status": "success",

                "message":
                    "Milk sample image captured successfully",

                "image_path":
                    str(image_path),

                "image_size":
                    len(response.content)

            }

        except requests.exceptions.RequestException as e:

            print(
                f"Camera save attempt "
                f"{attempt} failed: {e}"
            )

            if attempt < max_attempts:

                time.sleep(1)

    raise HTTPException(

        status_code=504,

        detail=(
            "ESP32-CAM did not respond "
            "after 3 attempts."
        )
    )


# =========================================================
# GET FARMERS
# =========================================================

@app.get("/api/farmers")
def get_farmers():

    db = SessionLocal()

    try:

        tests = (
            db.query(MilkTest)
            .order_by(MilkTest.id.desc())
            .all()
        )

        farmers = {}

        for test in tests:

            farmer_id = test.farmer_id

            if farmer_id not in farmers:

                farmers[farmer_id] = {

                    "farmer_id":
                        farmer_id,

                    "total_tests":
                        0,

                    "latest_batch":
                        test.batch_id,

                    "latest_quality_score":
                        test.quality_score,

                    "latest_status":
                        test.status,

                    "latest_spoilage_risk":
                        test.spoilage_risk

                }

            farmers[
                farmer_id
            ]["total_tests"] += 1

        return list(
            farmers.values()
        )

    finally:

        db.close()