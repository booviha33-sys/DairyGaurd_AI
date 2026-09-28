def predict_shelf_life(
    temperature,
    red,
    green,
    blue,
    quality_score
):

    rgb_average = (red + green + blue) / 3

    shelf_life = 24

    if temperature <= 4:
        shelf_life += 8
    elif temperature <= 8:
        shelf_life += 4
    elif temperature <= 12:
        shelf_life -= 2
    elif temperature <= 20:
        shelf_life -= 6
    else:
        shelf_life -= 10

    if quality_score >= 80:
        shelf_life += 6
    elif quality_score >= 60:
        shelf_life += 2
    else:
        shelf_life -= 6

    if rgb_average >= 150:
        shelf_life += 2
    elif rgb_average < 80:
        shelf_life -= 4

    shelf_life = max(
        2,
        min(48, shelf_life)
    )

    if shelf_life >= 30:
        risk = "LOW"
    elif shelf_life >= 15:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    if risk == "LOW":
        recommendation = (
            "Milk is currently in a lower prototype "
            "spoilage-risk range. Continue proper cold-chain "
            "handling and routine monitoring."
        )
    elif risk == "MEDIUM":
        recommendation = (
            "Milk should be monitored closely and processed "
            "with priority while maintaining temperature control."
        )
    else:
        recommendation = (
            "Milk requires additional quality verification "
            "and priority handling."
        )

    return {
        "estimated_shelf_life_hours": shelf_life,
        "shelf_life_risk": risk,
        "recommendation": recommendation,
        "shelf_life_recommendation": recommendation
    }


def recommend_milk_routing(
    quality_score,
    spoilage_risk,
    temperature
):

    if quality_score >= 80 and spoilage_risk == "LOW":

        route = "NORMAL PROCESSING"
        priority = "LOW"

        reason = (
            "Prototype quality indicators are within the "
            "normal processing range."
        )

    elif (
        quality_score >= 60
        and spoilage_risk in ["LOW", "MEDIUM"]
    ):

        route = "PRIORITY PROCESSING"
        priority = "MEDIUM"

        reason = (
            "Milk should receive closer monitoring and "
            "priority processing."
        )

    else:

        route = "QUALITY VERIFICATION"
        priority = "HIGH"

        reason = (
            "Milk requires additional quality verification "
            "before normal processing."
        )

    if temperature > 20:

        route = "QUALITY VERIFICATION"
        priority = "HIGH"

        reason = (
            "Temperature is high in the prototype monitoring "
            "logic. Verify cold-chain conditions before processing."
        )

    return {
        "milk_routing": route,
        "routing_priority": priority,
        "routing_reason": reason
    }


def generate_ai_recommendation(
    quality_score,
    spoilage_risk,
    temperature,
    red,
    green,
    blue
):

    recommendations = []

    rgb_average = (
        red + green + blue
    ) / 3

    if temperature > 20:
        recommendations.append(
            "Temperature is high. Check cold-chain conditions."
        )
    elif temperature > 8:
        recommendations.append(
            "Maintain stronger temperature control."
        )
    else:
        recommendations.append(
            "Temperature is within the prototype monitoring range."
        )

    if quality_score >= 80:
        recommendations.append(
            "Prototype quality score is in the higher range."
        )
    elif quality_score >= 60:
        recommendations.append(
            "Monitor the milk quality more closely."
        )
    else:
        recommendations.append(
            "Additional quality verification is recommended."
        )

    if spoilage_risk == "HIGH":
        recommendations.append(
            "High prototype spoilage risk detected. "
            "Perform additional verification."
        )
    elif spoilage_risk == "MEDIUM":
        recommendations.append(
            "Medium prototype spoilage risk. "
            "Prioritize processing."
        )
    else:
        recommendations.append(
            "Prototype spoilage risk is currently low."
        )

    if rgb_average >= 150:
        recommendations.append(
            "Colour sensor reading is in the prototype higher range."
        )
    elif rgb_average >= 80:
        recommendations.append(
            "Colour reading should be monitored."
        )
    else:
        recommendations.append(
            "Colour reading requires additional verification."
        )

    if spoilage_risk == "HIGH":

        recommended_action = (
            "Perform quality verification before processing."
        )

    elif temperature > 20:

        recommended_action = (
            "Improve cold-chain conditions and prioritize processing."
        )

    elif quality_score >= 80:

        recommended_action = (
            "Proceed with normal prototype processing workflow."
        )

    else:

        recommended_action = (
            "Prioritize processing and continue monitoring."
        )

    if spoilage_risk == "HIGH":

        ai_recommendation = (
            "Additional quality verification is recommended "
            "because the prototype indicates higher spoilage risk."
        )

    elif temperature > 20:

        ai_recommendation = (
            "Temperature control should be improved before "
            "continuing normal processing."
        )

    elif quality_score >= 80:

        ai_recommendation = (
            "Milk is currently within the higher prototype "
            "quality range."
        )

    else:

        ai_recommendation = (
            "Continue monitoring milk quality and process "
            "the batch with appropriate priority."
        )

    return {
        "recommendation": ai_recommendation,
        "ai_recommendation": ai_recommendation,
        "recommended_action": recommended_action,
        "recommendation_count": len(recommendations),
        "recommendations": recommendations
    }


def analyze_mbrt_result(
    elapsed_seconds,
    blue_score,
    initial_blue_score=None
):
    """
    Prototype microbial-activity estimate based on MBRT
    camera colour behaviour.

    IMPORTANT:
    This is NOT a validated CFU/mL measurement.
    Laboratory calibration is required for microbial counts.
    """

    if elapsed_seconds is None:
        return {
            "mbrt_status": "NOT AVAILABLE",
            "microbial_activity": "NOT AVAILABLE",
            "microbial_count": "NOT CALIBRATED",
            "basis": "No MBRT observation available"
        }

    # -----------------------------------------------------
    # Prototype activity classification
    # -----------------------------------------------------
    #
    # These categories are only for prototype demonstration.
    # They must not be interpreted as laboratory microbial
    # counts.
    #

    if elapsed_seconds >= 30 * 60:

        activity = "LOW"

    elif elapsed_seconds >= 15 * 60:

        activity = "MODERATE"

    else:

        activity = "HIGH"

    return {
        "mbrt_status": "MONITORING",

        "microbial_activity":
            activity,

        "microbial_count":
            "NOT CALIBRATED",

        "basis":
            "MBRT colour-change behaviour",

        "mbrt_time_seconds":
            elapsed_seconds,

        "mbrt_blue_score":
            blue_score
    }