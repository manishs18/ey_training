from fastapi import FastAPI
from app.graph.nutriguard_graph import graph
from app.llm.gemini_client import gemini_client
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

app = FastAPI(title="NutriGuard AI Orchestrator")


class ProcessMealInput(BaseModel):
    meal_log_id: int
    user_id: int
    meal_text: str
    meal_type: Optional[str] = None
    meal_time: Optional[str] = None
    previous_meal_text: Optional[str] = None
    previous_meal_time: Optional[str] = None
    minutes_since_previous_meal: Optional[int] = None
    day_meals: Optional[List[Dict[str, Any]]] = None
    goal: str
    goals: Optional[List[str]] = None
    health_conditions: Optional[List[str]] = None
    deficiencies: Optional[List[str]] = None
    supplements: Optional[List[str]] = None
    health_report_text: Optional[str] = None


class NutritionQueryInput(BaseModel):
    query: str
    goal: Optional[str] = None
    goals: Optional[List[str]] = None
    diet_type: Optional[str] = None
    health_conditions: Optional[List[str]] = None
    deficiencies: Optional[List[str]] = None
    supplements: Optional[List[str]] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    day_meals: Optional[List[Dict[str, Any]]] = None


def _format_profile_summary(payload: NutritionQueryInput) -> str:
    lines = []
    if payload.gender:
        lines.append(f"Gender: {payload.gender}")
    if payload.age:
        lines.append(f"Age: {payload.age} years")
    if payload.weight_kg:
        lines.append(f"Weight: {payload.weight_kg} kg")
    if payload.diet_type:
        lines.append(f"Diet type: {payload.diet_type}")
    if payload.goals:
        lines.append(f"Goals: {', '.join(payload.goals)}")
    if payload.health_conditions:
        lines.append(f"Conditions: {', '.join(payload.health_conditions)}")
    if payload.deficiencies:
        lines.append(f"Deficiencies: {', '.join(payload.deficiencies)}")
    if payload.supplements:
        lines.append(f"Supplements: {', '.join(payload.supplements)}")
    return "\n".join(lines)


def _build_nutrition_query_prompt(payload: NutritionQueryInput) -> str:
    profile_summary = _format_profile_summary(payload)
    day_meals = payload.day_meals or []
    meal_lines = []
    for meal in day_meals:
        meal_lines.append(
            f"{meal.get('meal_type', 'Meal').title()} at {meal.get('meal_time')}: {meal.get('meal_text')}"
        )

    return f"""
You are an expert nutrition assistant for a personal health app.
Provide a clear, practical response focused on:
- a user-friendly nutrition plan
- protein guidance for the user's body metrics
- pros and cons of foods and meal choices
- healthy meal timing, portion quality, and balanced diet advice
- references to the user's profile and food log when available

Use a supportive tone. Do not diagnose or prescribe.

User profile:
{profile_summary}

Logged day meals:
{chr(10).join(meal_lines) if meal_lines else 'No meals logged.'}

User query:
{payload.query}

Answer directly and include a short recommendation and any protein guidance relevant to the user's body metrics.
""".strip()


def _fallback_nutrition_query(payload: NutritionQueryInput) -> str:
    profile_summary = _format_profile_summary(payload)
    weight = payload.weight_kg
    protein_guidance = ""
    if weight:
        min_target = weight * 0.8
        moderate_target = weight * 1.0
        active_target = weight * 1.2
        protein_guidance = (
            f"For your weight, a daily protein range of about {min_target:.0f}-{active_target:.0f} g is reasonable. "
            f"A moderate target is around {moderate_target:.0f} g."
        )
    else:
        protein_guidance = "A scalable protein target is about 0.8-1.2 g per kg of body weight."

    response_lines = [
        "Nutrition AI response:",
        profile_summary if profile_summary else "Profile details are not available.",
        protein_guidance,
        "Focus on lean proteins, whole grains, vegetables, and healthy fats.",
        "Curd is a good dairy source, but 50 ml is a light portion for protein, so pair it with larger protein items like chicken, lentils, paneer, or eggs.",
        "Use meals with a mix of proteins, carbs, and fiber, and minimize too much processed starch alone.",
        "Pros: good protein sources support muscle and recovery. Cons: watch portion sizes, and avoid drinking tea/coffee right with iron-rich meals if you have absorption concerns.",
    ]
    return "\n\n".join(line for line in response_lines if line)


@app.post("/process-meal")
def process_meal(payload: ProcessMealInput):
    result = graph.invoke(
        {
            "meal_log_id": payload.meal_log_id,
            "user_id": payload.user_id,
            "meal_text": payload.meal_text,
            "meal_type": payload.meal_type,
            "meal_time": payload.meal_time,
            "previous_meal_text": payload.previous_meal_text,
            "previous_meal_time": payload.previous_meal_time,
            "minutes_since_previous_meal": payload.minutes_since_previous_meal,
            "day_meals": payload.day_meals or [],
            "goal": payload.goal,
            "goals": payload.goals or ([payload.goal] if payload.goal else []),
            "health_conditions": payload.health_conditions or [],
            "deficiencies": payload.deficiencies or [],
            "supplements": payload.supplements or [],
            "health_report_text": payload.health_report_text or "",
            "meal_analysis": None,
            "risk_flags": [],
            "report": None,
        }
    )
    return {
        "meal_analysis": result.get("meal_analysis") or {},
        "risk_flags": result.get("risk_flags") or [],
        "report": result.get("report") or "",
    }


@app.post("/nutrition-query")
def nutrition_query(payload: NutritionQueryInput):
    prompt = _build_nutrition_query_prompt(payload)
    if gemini_client.enabled:
        try:
            response_text = gemini_client.generate_text(prompt)
        except Exception:
            response_text = _fallback_nutrition_query(payload)
    else:
        response_text = _fallback_nutrition_query(payload)
    return {"response": response_text}


@app.get("/health")
def health():
    return {"status": "ok"}
