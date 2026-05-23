"""
gemini_helper.py
~~~~~~~~~~~~~~~~
Core Gemini API integration for Smart Recipe Generator.
Contains the ANTIGRAVITY PROMPT — a multi-layered, structured prompt
engineered for maximum recipe quality and nutrition depth.
Includes dynamic model resolution to handle 404 deprecations of older models.
"""

import json
import re
import google.generativeai as genai


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      🚀  ANTIGRAVITY PROMPT TEMPLATE                       ║
# ║  A prompt engineered to "float above" generic AI output — using layered    ║
# ║  context injection, role anchoring, constraint weaving, and output         ║
# ║  sculpting to produce deeply structured, expert-quality recipes.           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

ANTIGRAVITY_PROMPT = """
═══════════════════════════════════════════════════════════
🧠 ROLE ANCHOR  (Layer 1 — Identity Injection)
═══════════════════════════════════════════════════════════
You are CHEF·AI — a Michelin-trained culinary genius fused with
a certified nutritionist and a food scientist. You don't just
"suggest recipes"; you engineer edible experiences backed by
macronutrient logic, flavor chemistry, and cultural authenticity.

You think in layers:
  → FLAVOR LAYER   : balance of sweet, sour, salt, umami, bitter, fat
  → TEXTURE LAYER  : crunch vs silk vs chew
  → NUTRITION LAYER: macro targets, micronutrient density, GI index
  → TECHNIQUE LAYER: why each step works (Maillard, emulsification, etc.)

═══════════════════════════════════════════════════════════
🎯 MISSION BRIEF  (Layer 2 — Task Definition)
═══════════════════════════════════════════════════════════
Create ONE complete, original recipe using the ingredients below.
The recipe must feel INTENTIONAL — not like leftovers thrown together.

📦 INGREDIENTS PROVIDED : {ingredients}
🍽️  CUISINE STYLE        : {cuisine}
🕐  MEAL TYPE            : {meal_type}
🌿  DIETARY RESTRICTIONS : {dietary_prefs}
👥  SERVING SIZE         : {servings} person(s)
🎯  DIFFICULTY LEVEL     : {difficulty}

═══════════════════════════════════════════════════════════
🔬 CONSTRAINT WEAVE  (Layer 3 — Hard Rules)
═══════════════════════════════════════════════════════════
MUST follow these without exception:
  ✅ Use ONLY the listed ingredients (add salt, pepper, water, oil as basics)
  ✅ Every step must have a WHY (brief technique note in parentheses)
  ✅ Nutrition section must include estimated values per serving
  ✅ Include at least 2 pro chef tips that elevate the dish
  ✅ Flag any allergens clearly
  ✅ Suggest 1 creative variation or fusion twist
  ✅ Keep language warm, confident, and inspiring — not robotic

═══════════════════════════════════════════════════════════
📐 OUTPUT SCULPTURE  (Layer 4 — Strict JSON Schema)
═══════════════════════════════════════════════════════════
Respond ONLY with valid JSON. No markdown fences, no preamble.
Use this EXACT structure:

{{
  "recipe_name": "Creative, evocative dish name",
  "tagline": "One-line poetic description of the dish",
  "difficulty": "{difficulty}",
  "cuisine": "{cuisine}",
  "prep_time": "X minutes",
  "cook_time": "X minutes",
  "total_time": "X minutes",
  "servings": {servings},

  "ingredients_used": [
    {{"item": "ingredient name", "quantity": "amount", "unit": "grams/cups/etc"}}
  ],

  "missing_but_recommended": [
    "Optional ingredient that would elevate the dish (not required)"
  ],

  "method": [
    {{
      "step_number": 1,
      "action": "What to do",
      "technique_note": "Why this step works scientifically/culinarily"
    }}
  ],

  "nutrition_per_serving": {{
    "calories": "~XXX kcal",
    "protein": "XXg",
    "carbohydrates": "XXg",
    "fats": "XXg",
    "fiber": "XXg",
    "sodium": "XXmg",
    "key_vitamins_minerals": ["Vitamin C", "Iron", "Calcium"]
  }},

  "nutrition_tips": [
    "Actionable tip to boost nutrition or improve absorption"
  ],

  "chef_tips": [
    "Pro tip 1 to elevate the dish",
    "Pro tip 2 — a secret technique or flavor trick"
  ],

  "allergens": ["list any present allergens, e.g. Eggs, Gluten, Dairy"],

  "variation": {{
    "name": "Creative variation name",
    "description": "How to twist this dish into something new"
  }},

  "flavor_profile": {{
    "dominant": "e.g. Savory-Umami",
    "notes": ["earthy", "bright", "creamy"],
    "pairs_well_with": "Suggested drink or side"
  }}
}}
═══════════════════════════════════════════════════════════
Now generate the recipe. Be brilliant. Be CHEF·AI.
═══════════════════════════════════════════════════════════
"""


def build_prompt(ingredients, cuisine, meal_type, dietary_prefs, servings, difficulty):
    """Inject all variables into the Antigravity Prompt template."""
    dietary_str = ", ".join(dietary_prefs) if dietary_prefs else "None"
    ingredients_str = ", ".join(ingredients)

    return ANTIGRAVITY_PROMPT.format(
        ingredients=ingredients_str,
        cuisine=cuisine,
        meal_type=meal_type,
        dietary_prefs=dietary_str,
        servings=servings,
        difficulty=difficulty,
    )


def generate_recipe(api_key, ingredients, cuisine, meal_type,
                    dietary_prefs, servings, difficulty):
    """
    Call the Gemini API with the Antigravity Prompt and return parsed JSON.
    Implements self-healing model resolution to prevent 404 errors.

    Returns:
        dict: Parsed recipe data or {"error": "message"}
    """
    try:
        # Configure Gemini API Key
        genai.configure(api_key=api_key)

        # Build the chef prompt
        prompt = build_prompt(
            ingredients=ingredients,
            cuisine=cuisine,
            meal_type=meal_type,
            dietary_prefs=dietary_prefs,
            servings=servings,
            difficulty=difficulty,
        )

        # Order of fallback model candidates to check
        candidate_models = [
            "gemini-2.5-flash", 
            "gemini-2.0-flash", 
            "gemini-1.5-flash", 
            "gemini-1.5-flash-latest"
        ]

        # Interrogate list_models to dynamically sort candidates based on availability
        try:
            available_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Extract models containing 'flash'
            flash_avail = [m.replace("models/", "") for m in available_list if "flash" in m.lower()]
            if flash_avail:
                # Sort descending to prefer 2.5 > 2.0 > 1.5
                flash_avail.sort(reverse=True)
                # Prepend available models, preserving uniqueness
                candidate_models = flash_avail + [c for c in candidate_models if c not in flash_avail]
        except Exception:
            # Fall back to default candidate sequence if API list call fails (e.g., restriction or billing delay)
            pass

        # Try models in priority order
        response_text = ""
        last_error = None

        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.85,       # Creative but not hallucinating
                        top_p=0.92,
                        top_k=40,
                        max_output_tokens=4096,
                    ),
                )
                response = model.generate_content(prompt)
                if response and response.text:
                    response_text = response.text.strip()
                    break
            except Exception as e:
                last_error = e
                # Proceed to try the next model candidate
                continue
        else:
            # If all candidates failed, raise the last exception
            if last_error:
                raise last_error
            else:
                raise Exception("No active Gemini model candidates succeeded.")

        # Strip any accidental markdown fences
        raw_text = re.sub(r"^```(?:json)?", "", response_text).strip()
        raw_text = re.sub(r"```$", "", raw_text).strip()

        recipe_data = json.loads(raw_text)
        return recipe_data

    except json.JSONDecodeError as e:
        return {"error": f"Could not parse recipe JSON: {str(e)}. Try again."}
    except Exception as e:
        return {"error": f"Gemini API Error: {str(e)}"}
