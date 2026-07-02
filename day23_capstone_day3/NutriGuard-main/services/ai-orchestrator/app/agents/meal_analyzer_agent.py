from typing import Dict, Any

from app.llm.gemini_client import gemini_client


import re


def _extract_label_value(meal_text: str, label: str) -> list[str]:
    values = []
    for line in meal_text.splitlines():
        if line.lower().startswith(f"{label.lower()}:"):
            text = line.split(":", 1)[1].strip()
            if text and text.lower() != "not provided":
                raw_values = [item.strip() for item in re.split(r",| and |\+", text) if item.strip()]
                values.extend([item.lower() for item in raw_values])
    return values


def _fallback_meal_analysis(meal_text: str) -> Dict[str, Any]:
    foods = []
    beverages = []
    carb_sources = []
    protein_sources = []

    lowered = meal_text.lower()

    pattern_map = {
        "aloo paratha": "aloo paratha",
        "poha": "poha",
        "roti": "roti",
        "chapati": "chapati",
        "paratha": "paratha",
        "rice": "rice",
        "dal": "dal",
        "sabzi": "sabzi",
        "salad": "salad",
        "paneer": "paneer",
        "curd": "curd",
        "tofu": "tofu",
        "sprouts": "sprouts",
        "chana": "chana",
        "soy": "soy",
        "eggs": "eggs",
        "egg": "egg",
        "banana": "banana",
        "apple": "apple",
        "milk": "milk",
    }

    beverage_map = {
        "tea": "tea",
        "coffee": "coffee",
        "water": "water",
        "juice": "juice",
        "lassi": "lassi",
        "smoothie": "smoothie",
    }

    protein_map = {
        "paneer": "paneer",
        "tofu": "tofu",
        "sprouts": "sprouts",
        "chana": "chana",
        "eggs": "eggs",
        "egg": "egg",
        "dal": "dal",
        "fish": "fish",
        "chicken": "chicken",
        "soy": "soy",
        "yogurt": "yogurt",
    }

    carb_map = {
        "poha": "poha",
        "aloo paratha": "aloo paratha",
        "paratha": "paratha",
        "roti": "roti",
        "chapati": "chapati",
        "rice": "rice",
        "bread": "bread",
        "idli": "idli",
        "dosa": "dosa",
    }

    for key, name in pattern_map.items():
        if key in lowered and name not in foods:
            foods.append(name)
    for key, name in beverage_map.items():
        if key in lowered and name not in beverages:
            beverages.append(name)
    for key, name in carb_map.items():
        if key in lowered and name not in carb_sources:
            carb_sources.append(name)
    for key, name in protein_map.items():
        if key in lowered and name not in protein_sources:
            protein_sources.append(name)

    foods.extend(_extract_label_value(meal_text, "Foods"))
    beverages.extend(_extract_label_value(meal_text, "Drinks"))

    # Deduplicate while preserving order
    foods = list(dict.fromkeys(foods))
    beverages = list(dict.fromkeys(beverages))
    carb_sources = list(dict.fromkeys(carb_sources))
    protein_sources = list(dict.fromkeys(protein_sources))

    issues = []
    if not protein_sources:
        issues.append("This meal appears low in protein.")

    return {
        "foods": foods,
        "carb_sources": carb_sources,
        "protein_sources": protein_sources,
        "beverages": beverages,
        "possible_issues": issues,
    }


def meal_analyzer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    meal_text = state.get("meal_text", "")

    try:
        meal_analysis = gemini_client.generate_json(
            f"""
You are the Meal Analyzer Agent for NutriGuard.

Convert the user's meal text into structured food data.
Do not give medical advice.
Return only valid JSON with this shape:
{{
  "foods": ["food names"],
  "carb_sources": ["food names"],
  "protein_sources": ["food names"],
  "beverages": ["beverage names"],
  "possible_issues": ["short nutrition observations, no medical advice"]
}}

Meal text: {meal_text}
"""
        )
        if not any(
            meal_analysis.get(key)
            for key in ["foods", "carb_sources", "protein_sources", "beverages"]
        ):
            meal_analysis = _fallback_meal_analysis(meal_text)
    except Exception:
        meal_analysis = _fallback_meal_analysis(meal_text)

    return {
        **state,
        "meal_analysis": {
            "foods": meal_analysis.get("foods") or [],
            "carb_sources": meal_analysis.get("carb_sources") or [],
            "protein_sources": meal_analysis.get("protein_sources") or [],
            "beverages": meal_analysis.get("beverages") or [],
            "possible_issues": meal_analysis.get("possible_issues") or [],
        },
    }
