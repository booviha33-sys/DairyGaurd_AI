# =========================================================
# DAIRYGUARD AI - PROTOTYPE MODELS
# =========================================================


# =========================================================
# SHELF-LIFE PREDICTION
# =========================================================

def predict_shelf_life(
    temperature,
    red,
    green,
    blue,
    quality_score
):
    """
    Prototype shelf-life prediction.

    This is a demonstration model and is NOT
    scientifically validated for commercial
    expiry-date determination.
    """

    rgb_average = (
        red + green + blue
    ) / 3


    # Base prototype shelf life
    shelf_life = 24.0


    # Temperature effect
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


    # Quality effect
    if quality_score >= 80:

        shelf_life += 6

    elif quality_score >= 60:

        shelf_life += 2

    else:

        shelf_life -= 6


    # Colour indication
    if rgb_average >= 150:

        shelf_life += 2

    elif rgb_average < 80:

        shelf_life -= 4


    # Keep within prototype range
    shelf_life = max(
        2,
        min(shelf_life, 48)
    )


    # Shelf-life risk
    if shelf_life >= 30:

        risk = "LOW"

    elif shelf_life >= 15:

        risk = "MEDIUM"

    else:

        risk = "HIGH"


    # Basic recommendation
    if risk == "LOW":

        recommendation = (
            "Milk appears suitable for normal "
            "processing and storage."
        )

    elif risk == "MEDIUM":

        recommendation = (
            "Prioritize this batch for processing "
            "and maintain proper cold-chain conditions."
        )

    else:

        recommendation = (
            "Prioritize this batch immediately "
            "and verify milk quality using the "
            "appropriate laboratory test."
        )


    return {

        "estimated_shelf_life_hours":
            round(shelf_life, 1),

        "shelf_life_risk":
            risk,

        "recommendation":
            recommendation
    }


# =========================================================
# SMART MILK ROUTING
# =========================================================

def recommend_milk_routing(
    quality_score,
    spoilage_risk,
    temperature
):

    if (
        quality_score >= 80
        and spoilage_risk == "LOW"
    ):

        return {

            "route":
                "NORMAL PROCESSING",

            "priority":
                "LOW",

            "reason":
                "Batch shows good prototype "
                "quality indicators."
        }


    elif (
        quality_score >= 60
        and spoilage_risk in [
            "LOW",
            "MEDIUM"
        ]
    ):

        return {

            "route":
                "PRIORITY PROCESSING",

            "priority":
                "MEDIUM",

            "reason":
                "Process this batch before "
                "lower-priority batches."
        }


    else:

        return {

            "route":
                "QUALITY VERIFICATION",

            "priority":
                "HIGH",

            "reason":
                "Batch requires additional "
                "quality verification before routing."
        }


# =========================================================
# AI RECOMMENDATIONS
# =========================================================

def generate_ai_recommendation(
    temperature,
    quality_score,
    spoilage_risk,
    shelf_life_hours,
    routing_priority
):
    """
    Prototype recommendation engine.

    This uses rule-based logic for the prototype.
    It is not a clinically or commercially validated
    AI decision system.
    """


    recommendations = []


    # -----------------------------------------------------
    # Temperature
    # -----------------------------------------------------

    if temperature > 20:

        recommendations.append(
            "Temperature is high. "
            "Move the batch to appropriate "
            "cold-chain storage and verify "
            "the milk condition."
        )

    elif temperature > 8:

        recommendations.append(
            "Maintain stronger temperature "
            "control and prioritize monitoring."
        )

    else:

        recommendations.append(
            "Temperature is within the "
            "prototype monitoring range."
        )


    # -----------------------------------------------------
    # Quality score
    # -----------------------------------------------------

    if quality_score >= 80:

        recommendations.append(
            "Prototype quality indicators are good."
        )

    elif quality_score >= 60:

        recommendations.append(
            "Quality indicators require "
            "closer monitoring."
        )

    else:

        recommendations.append(
            "Perform additional milk-quality "
            "verification before normal processing."
        )


    # -----------------------------------------------------
    # Spoilage risk
    # -----------------------------------------------------

    if spoilage_risk == "HIGH":

        recommendations.append(
            "High spoilage risk: prioritize "
            "additional quality verification."
        )

    elif spoilage_risk == "MEDIUM":

        recommendations.append(
            "Medium spoilage risk: prioritize "
            "the batch for processing."
        )

    else:

        recommendations.append(
            "Low prototype spoilage risk."
        )


    # -----------------------------------------------------
    # Shelf life
    # -----------------------------------------------------

    if shelf_life_hours < 12:

        recommendations.append(
            "Estimated remaining shelf life is short. "
            "Prioritize this batch."
        )

    elif shelf_life_hours < 24:

        recommendations.append(
            "Estimated shelf life is limited. "
            "Avoid unnecessary storage delays."
        )

    else:

        recommendations.append(
            "Estimated shelf life is relatively longer "
            "under the current prototype model."
        )


    # -----------------------------------------------------
    # Routing priority
    # -----------------------------------------------------

    if routing_priority == "HIGH":

        action = (
            "Recommended action: "
            "send the batch for quality verification."
        )

    elif routing_priority == "MEDIUM":

        action = (
            "Recommended action: "
            "prioritize the batch for processing."
        )

    else:

        action = (
            "Recommended action: "
            "continue normal processing while "
            "maintaining proper storage conditions."
        )


    # -----------------------------------------------------
    # Final recommendation
    # -----------------------------------------------------

    final_recommendation = " ".join(
        recommendations
    )


    return {

        "recommendation":
            final_recommendation,

        "recommended_action":
            action,

        "number_of_recommendations":
            len(recommendations)
    }