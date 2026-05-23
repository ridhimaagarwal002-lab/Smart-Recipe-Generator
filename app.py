import streamlit as st
from gemini_helper import generate_recipe
from utils import parse_ingredients, display_recipe_card, apply_custom_css

# ── Session State Initialization ──────────────────────────────────────────────
if "selected_pantry" not in st.session_state:
    st.session_state.selected_pantry = set()
if "recipe_book" not in st.session_state:
    st.session_state.recipe_book = []
if "current_recipe" not in st.session_state:
    st.session_state.current_recipe = None
if "focus_step_index" not in st.session_state:
    st.session_state.focus_step_index = 0

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Recipe Generator",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    api_key = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        placeholder="Enter your Gemini API key...",
        help="Get your key at https://makersuite.google.com/app/apikey",
    )

    st.markdown("---")
    st.markdown("### 🎯 Recipe Preferences")

    cuisine_type = st.selectbox(
        "Cuisine Style",
        ["Any", "Italian", "Indian", "Chinese", "Mexican", "Mediterranean",
         "Japanese", "American", "French", "Thai"],
    )

    meal_type = st.selectbox(
        "Meal Type",
        ["Any", "Breakfast", "Lunch", "Dinner", "Snack", "Dessert"],
    )

    dietary_pref = st.multiselect(
        "Dietary Preferences",
        ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free",
         "Nut-Free", "Low-Carb", "High-Protein"],
    )

    serving_size = st.slider("Serving Size (people)", 1, 10, 2)

    difficulty = st.radio(
        "Difficulty Level",
        ["Easy", "Medium", "Advanced"],
        horizontal=True,
    )

    # ── Sidebar Recipe Book Log ──
    if st.session_state.recipe_book:
        st.markdown("---")
        st.markdown("### 📚 Session Recipe Book")
        for idx, recipe in enumerate(st.session_state.recipe_book):
            name = recipe.get("recipe_name", f"Recipe {idx+1}")
            if st.button(f"🍽️ {name}", key=f"hist_{idx}", use_container_width=True):
                st.session_state.current_recipe = recipe
                st.session_state.focus_step_index = 0
                st.rerun()

    st.markdown("---")
    st.caption("Powered by Google Gemini ✨")

# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🍳 Smart Recipe Generator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Drop your ingredients → Get a full recipe with nutrition insights</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

col1, col2 = st.columns([1.8, 1], gap="large")

with col1:
    st.markdown("### 🥗 Add ingredients from your kitchen")
    raw_ingredients = st.text_area(
        label="Type custom ingredients",
        placeholder="Type custom ingredients (e.g. olive oil, salt, steak, pork...) separated by commas or newlines...",
        height=100,
        label_visibility="collapsed",
    )

    st.markdown("**Or select from our visual pantry presets:**")
    PANTRY_PRESETS = {
        "Eggs": "🍳", "Chicken": "🍗", "Rice": "🌾", "Pasta": "🍝",
        "Tomatoes": "🍅", "Onion": "🧅", "Garlic": "🧄", "Potato": "🥔",
        "Spinach": "🥬", "Cheese": "🧀", "Milk": "🥛", "Butter": "🧈",
        "Lemon": "🍋", "Bread": "🍞", "Mushrooms": "🍄", "Beef": "🥩",
        "Fish": "🐟", "Shrimp": "🍤", "Broccoli": "🥦", "Avocado": "🥑",
    }
    
    # Render in rows of 4 columns
    preset_names = list(PANTRY_PRESETS.keys())
    cols_per_row = 4
    for i in range(0, len(preset_names), cols_per_row):
        row_names = preset_names[i:i+cols_per_row]
        cols = st.columns(cols_per_row)
        for col, name in zip(cols, row_names):
            emoji = PANTRY_PRESETS[name]
            is_selected = name in st.session_state.selected_pantry
            btn_label = f"✅ {emoji} {name}" if is_selected else f"{emoji} {name}"
            
            with col:
                if st.button(btn_label, key=f"preset_{name}", use_container_width=True):
                    if is_selected:
                        st.session_state.selected_pantry.remove(name)
                    else:
                        st.session_state.selected_pantry.add(name)
                    st.rerun()

    # Clear pantry presets button
    if st.session_state.selected_pantry:
        st.write("")
        if st.button("🧹 Clear Pantry Selections", use_container_width=True):
            st.session_state.selected_pantry.clear()
            st.rerun()

with col2:
    st.markdown("### 📋 Summary")
    all_ingredients = parse_ingredients(raw_ingredients, list(st.session_state.selected_pantry))

    if all_ingredients:
        st.success(f"✅ **{len(all_ingredients)} ingredient(s)** detected")
        # Visual ingredient pills representation
        pills_html = "".join([f'<span style="background:rgba(249,115,22,0.15); border:1px solid rgba(249,115,22,0.3); color:#f97316; border-radius:10px; padding:4px 8px; margin:4px; display:inline-block; font-size:0.9rem;">{ing}</span>' for ing in all_ingredients])
        st.markdown(f'<div style="margin-top:10px; line-height:1.8;">{pills_html}</div>', unsafe_allow_html=True)
    else:
        st.info("Add ingredients to get started!")

st.markdown("---")

# ── Generate Button ───────────────────────────────────────────────────────────
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    generate_btn = st.button(
        "🚀 Generate My Recipe",
        use_container_width=True,
        type="primary",
    )

# ── Output ────────────────────────────────────────────────────────────────────
if generate_btn:
    if not api_key:
        st.error("🔑 Please enter your Gemini API key in the sidebar.")
    elif not all_ingredients:
        st.warning("🥕 Please add at least one ingredient!")
    else:
        with st.spinner("🤖 Gemini is crafting your perfect recipe..."):
            recipe_output = generate_recipe(
                api_key=api_key,
                ingredients=all_ingredients,
                cuisine=cuisine_type,
                meal_type=meal_type,
                dietary_prefs=dietary_pref,
                servings=serving_size,
                difficulty=difficulty,
            )

        if recipe_output.get("error"):
            st.error(f"❌ Error: {recipe_output['error']}")
        else:
            # Check if this recipe is already in our history book, if not append
            name = recipe_output.get("recipe_name", "Gourmet Creation")
            existing_names = [r.get("recipe_name") for r in st.session_state.recipe_book]
            if name not in existing_names:
                st.session_state.recipe_book.append(recipe_output)
            
            st.session_state.current_recipe = recipe_output
            st.session_state.focus_step_index = 0
            st.rerun()

# Render current recipe card below
if st.session_state.current_recipe:
    display_recipe_card(st.session_state.current_recipe)
