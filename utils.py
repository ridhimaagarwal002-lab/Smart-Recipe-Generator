"""
utils.py
~~~~~~~~
Utility functions: ingredient parsing, recipe card rendering, custom CSS.
Includes dynamic quantity scaling and interactive focus mode slideshow.
"""

import re
import streamlit as st
from fractions import Fraction


# ── Ingredient Parser ─────────────────────────────────────────────────────────

def parse_ingredients(raw_text: str, quick_tags: list) -> list:
    """
    Combine free-text ingredients and quick-tag selections into a clean list.

    Args:
        raw_text: Comma/newline-separated ingredients from text area
        quick_tags: Selected items from multiselect widget

    Returns:
        Deduplicated list of cleaned ingredient strings
    """
    result = set()

    if raw_text.strip():
        # Split on commas or newlines
        parts = [p.strip() for p in raw_text.replace("\n", ",").split(",")]
        for p in parts:
            if p:
                result.add(p.lower().strip())

    for tag in quick_tags:
        result.add(tag.lower().strip())

    return sorted(list(result))


# ── Ingredient Portion Scaler ──────────────────────────────────────────────────

def scale_ingredient_quantity(qty_str: str, scale_factor: float) -> str:
    """
    Parses numeric, fractional, mixed fraction, or range quantity strings,
    scales them by a factor, and formats the output cleanly.
    """
    qty_str = qty_str.strip()
    if not qty_str:
        return ""
        
    # Case 1: Pure number (float/int)
    try:
        val = float(qty_str)
        scaled = val * scale_factor
        if scaled.is_integer():
            return str(int(scaled))
        return f"{scaled:.2f}".rstrip('0').rstrip('.')
    except ValueError:
        pass
        
    # Case 2: Simple Fraction (e.g. "1/2")
    fraction_pattern = r"^(\d+)/(\d+)$"
    match = re.match(fraction_pattern, qty_str)
    if match:
        num = int(match.group(1))
        denom = int(match.group(2))
        scaled = (num / denom) * scale_factor
        if scaled.is_integer():
            return str(int(scaled))
        try:
            frac = Fraction(scaled).limit_denominator(8)
            if frac.denominator in [2, 3, 4, 8]:
                return str(frac)
        except Exception:
            pass
        return f"{scaled:.2f}".rstrip('0').rstrip('.')
        
    # Case 3: Mixed Fraction (e.g. "1 1/2")
    mixed_pattern = r"^(\d+)\s+(\d+)/(\d+)$"
    match = re.match(mixed_pattern, qty_str)
    if match:
        whole = int(match.group(1))
        num = int(match.group(2))
        denom = int(match.group(3))
        val = whole + (num / denom)
        scaled = val * scale_factor
        if scaled.is_integer():
            return str(int(scaled))
        try:
            frac = Fraction(scaled - int(scaled)).limit_denominator(8)
            if frac.denominator in [2, 3, 4, 8]:
                if int(scaled) > 0:
                    return f"{int(scaled)} {frac}"
                return str(frac)
        except Exception:
            pass
        return f"{scaled:.2f}".rstrip('0').rstrip('.')
        
    # Case 4: Range (e.g. "1-2")
    range_pattern = r"^(\d+)-(\d+)$"
    match = re.match(range_pattern, qty_str)
    if match:
        low = int(match.group(1)) * scale_factor
        high = int(match.group(2)) * scale_factor
        low_str = str(int(low)) if low.is_integer() else f"{low:.1f}"
        high_str = str(int(high)) if high.is_integer() else f"{high:.1f}"
        return f"{low_str}-{high_str}"
        
    # Case 5: Text (e.g. "to taste", "pinch")
    return qty_str


# ── Recipe Card Display ───────────────────────────────────────────────────────

def display_recipe_card(recipe: dict):
    """Render an interactive, tabbed gourmet recipe card."""

    st.markdown("---")
    st.markdown(f'<div class="recipe-title">🍽️ {recipe.get("recipe_name", "Your Recipe")}</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="recipe-tagline">✨ {recipe.get("tagline", "")}</div>',
                unsafe_allow_html=True)

    # Original servings for portion scaling
    original_servings = int(recipe.get("servings", 2))

    # ── Meta Row Cards
    meta_cols = st.columns(5)
    meta_items = [
        ("⏱️ Prep", recipe.get("prep_time", "—")),
        ("🔥 Cook", recipe.get("cook_time", "—")),
        ("⌛ Total", recipe.get("total_time", "—")),
        ("👥 Serves", f"{original_servings} people"),
        ("🎯 Level", recipe.get("difficulty", "—")),
    ]
    for col, (label, value) in zip(meta_cols, meta_items):
        with col:
            st.markdown(f'<div class="meta-box"><span class="meta-label">{label}</span>'
                        f'<span class="meta-value">{value}</span></div>',
                        unsafe_allow_html=True)

    st.markdown("---")

    # ── Interactive Tabs Layout
    tab_overview, tab_ingredients, tab_cooking, tab_tips = st.tabs([
        "🍽️ Overview & Flavor",
        "🧺 Ingredients & Nutrition",
        "👩‍🍳 Cooking Focus Mode",
        "💡 Chef's Secret & Twists"
    ])

    # ── Tab 1: Overview & Flavor Alchemy
    with tab_overview:
        col_desc, col_flav = st.columns([1.2, 1], gap="large")
        with col_desc:
            st.markdown("### 📝 Chef's Vision")
            st.write(recipe.get("tagline", ""))
            
            # Simple metadata summary bullet points
            st.markdown(f"""
            - **Cuisine Style:** {recipe.get('cuisine', 'Any')}
            - **Portion Size:** Designed for {original_servings} people (can be scaled in the next tab)
            - **Difficulty Level:** {recipe.get('difficulty', 'Medium')}
            - **Active Preparation Time:** {recipe.get('prep_time', '—')}
            - **Cooking Time:** {recipe.get('cook_time', '—')}
            """)
            
        with col_flav:
            st.markdown("### 🎨 Flavor Alchemy Profile")
            fp = recipe.get("flavor_profile", {})
            if fp:
                st.markdown(f"**Dominant Element:** {fp.get('dominant', '—')}")
                
                # Flavor notes representation
                notes = fp.get("notes", [])
                if notes:
                    notes_pills = "".join([f'<span class="flavor-pill">{note}</span>' for note in notes])
                    st.markdown(f'<div style="margin: 10px 0;">{notes_pills}</div>', unsafe_allow_html=True)
                
                pairs = fp.get("pairs_well_with", "")
                if pairs:
                    st.markdown(f'<div style="background: rgba(139, 92, 246, 0.05); border-left: 3px solid #8b5cf6; padding: 10px 12px; border-radius: 0 8px 8px 0;">'
                                f'🍹 <b>Pairs Well With:</b> {pairs}</div>', unsafe_allow_html=True)

    # ── Tab 2: Ingredients Checklist & Nutrition
    with tab_ingredients:
        col_left, col_right = st.columns([1, 1], gap="large")

        with col_left:
            st.markdown("### 🧺 Ingredients Checklist")
            
            # Interactive serving scaler slider
            portion_scale = st.slider("Scale Portion (Servings)", min_value=1, max_value=20, value=original_servings, step=1)
            scale_factor = portion_scale / original_servings
            
            if scale_factor != 1.0:
                st.info(f"🔄 Ingredient portions scaled **{scale_factor:.1f}x** (adjusted for **{portion_scale} servings**)")
                
            st.write("Check items off as you prepare your station:")
            for idx, ing in enumerate(recipe.get("ingredients_used", [])):
                qty  = ing.get("quantity", "")
                unit = ing.get("unit", "")
                item = ing.get("item", "")
                
                # Calculate scaled quantity
                scaled_qty = scale_ingredient_quantity(qty, scale_factor)
                
                # Format string representation
                display_text = f"**{scaled_qty} {unit}** {item}".strip() if scaled_qty else item
                
                st.checkbox(display_text, key=f"check_{idx}_{hash(display_text)}")

            optional = recipe.get("missing_but_recommended", [])
            if optional:
                st.markdown("#### 💡 Recommended additions to elevate:")
                for opt in optional:
                    st.markdown(f"- _{opt}_")

        with col_right:
            st.markdown("### 🥗 Nutrition Insights (Per Serving)")
            nutrition = recipe.get("nutrition_per_serving", {})
            if nutrition:
                n_cols = st.columns(3)
                n_data = [
                    ("🔥 Calories", nutrition.get("calories", "—")),
                    ("💪 Protein",  nutrition.get("protein", "—")),
                    ("🍞 Carbs",    nutrition.get("carbohydrates", "—")),
                    ("🧈 Fats",     nutrition.get("fats", "—")),
                    ("🌾 Fiber",    nutrition.get("fiber", "—")),
                    ("🧂 Sodium",   nutrition.get("sodium", "—")),
                ]
                for i, (label, val) in enumerate(n_data):
                    with n_cols[i % 3]:
                        st.markdown(f'<div class="nutrition-box">'
                                    f'<div class="n-label">{label}</div>'
                                    f'<div class="n-val">{val}</div>'
                                    f'</div>', unsafe_allow_html=True)

                vitamins = nutrition.get("key_vitamins_minerals", [])
                if vitamins:
                    st.write("")
                    st.markdown(f"🌟 **Vitamins & Minerals:** {', '.join(vitamins)}")

            nutrition_tips = recipe.get("nutrition_tips", [])
            if nutrition_tips:
                st.markdown("#### 🩺 Nutrition Science Tips")
                for tip in nutrition_tips:
                    st.info(f"💚 {tip}")

    # ── Tab 3: Cooking Focus Mode
    with tab_cooking:
        st.markdown("### 👨🍳 Instructions & Science")
        
        # Interactive mode selector toggle
        focus_mode = st.toggle("🔍 Enable Kitchen Focus Mode (Slideshow View)", value=False)
        method_steps = recipe.get("method", [])
        
        if not method_steps:
            st.warning("No instructions found.")
        elif not focus_mode:
            # Standard vertical list layout
            for step in method_steps:
                num    = step.get("step_number", "")
                action = step.get("action", "")
                note   = step.get("technique_note", "")
                st.markdown(
                    f'<div class="step-card">'
                    f'<span class="step-num">Step {num}</span>'
                    f'<div class="step-action">{action}</div>'
                    f'<div class="step-note">🔬 {note}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            # Slideshow slideshow view
            total_steps = len(method_steps)
            
            # Bound focus step index
            if st.session_state.focus_step_index >= total_steps:
                st.session_state.focus_step_index = 0
            elif st.session_state.focus_step_index < 0:
                st.session_state.focus_step_index = total_steps - 1
                
            current_step = method_steps[st.session_state.focus_step_index]
            
            # Progress bar representation
            progress_val = (st.session_state.focus_step_index + 1) / total_steps
            st.progress(progress_val)
            st.write(f"**Step {st.session_state.focus_step_index + 1} of {total_steps}**")
            
            # Render highlighted step text
            st.markdown(f"""
            <div style="background: rgba(249, 115, 22, 0.05); border-left: 5px solid #f97316; padding: 25px; border-radius: 0 16px 16px 0; margin: 15px 0;">
                <h4 style="margin:0 0 10px 0; color:#f97316;">Step {current_step.get('step_number', '')} Action:</h4>
                <p style="font-size:1.3rem; font-weight:400; line-height:1.6; color:#f1f5f9;">{current_step.get('action', '')}</p>
                <div style="margin-top:15px; background:rgba(148, 163, 184, 0.1); border:1px dashed rgba(148,163,184,0.3); padding:12px; border-radius:8px; font-size:0.95rem; color:#94a3b8; font-style:italic;">
                    🔬 <b>Culinary Science:</b> {current_step.get('technique_note', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Step Navigation controls
            col_back, col_middle, col_next = st.columns([1, 2, 1])
            with col_back:
                if st.button("⬅️ Previous Step", use_container_width=True):
                    st.session_state.focus_step_index -= 1
                    st.rerun()
            with col_middle:
                st.markdown(f"<div style='text-align:center; padding-top:10px; font-weight:600; color:#94a3b8;'>Use buttons to navigate</div>", unsafe_allow_html=True)
            with col_next:
                if st.button("Next Step ➡️", use_container_width=True):
                    st.session_state.focus_step_index += 1
                    st.rerun()

    # ── Tab 4: Chef's Secret & Twists
    with tab_tips:
        col_tips, col_var = st.columns([1, 1], gap="large")

        with col_tips:
            st.markdown("### 🎩 Chef's Professional Secrets")
            for tip in recipe.get("chef_tips", []):
                st.success(f"⭐ {tip}")

            allergens = recipe.get("allergens", [])
            # Strip list if contains None
            clean_allergens = [a for a in allergens if a and a.lower() != "none"]
            if clean_allergens:
                st.warning(f"⚠️ **Allergens Present:** {', '.join(clean_allergens)}")
            else:
                st.info("🥦 **Allergen Free:** No major allergens flagged for this recipe.")

        with col_var:
            variation = recipe.get("variation", {})
            if variation:
                v_name = variation.get("name", "Variation")
                v_desc = variation.get("description", "")
                st.markdown("### 🔀 Culinary Fusion Twist")
                st.markdown(f"""
                <div style="background: rgba(236, 72, 153, 0.05); border: 1px dashed rgba(236,72,153,0.3); padding: 20px; border-radius: 16px;">
                    <h4 style="margin:0 0 8px 0; color:#ec4899;">🔄 {v_name}</h4>
                    <p style="margin:0; line-height:1.6; color:#e2e8f0;">{v_desc}</p>
                </div>
                """, unsafe_allow_html=True)


# ── Custom CSS ────────────────────────────────────────────────────────────────

def apply_custom_css():
    import base64
    import os

    bg_path = os.path.join(os.path.dirname(__file__), "kitchen_bg.png")
    bg_style = ""
    if os.path.exists(bg_path):
        try:
            with open(bg_path, "rb") as f:
                data = f.read()
            b64_str = base64.b64encode(data).decode()
            bg_style = f"background: linear-gradient(rgba(15, 23, 42, 0.35), rgba(15, 23, 42, 0.35)), url(data:image/png;base64,{b64_str}) !important;"
        except Exception:
            pass

    if not bg_style:
        bg_style = "background: radial-gradient(circle at 80% 20%, #1e1e38 0%, #0f172a 65%) !important;"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500;700&display=swap');

    html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}

    /* Elegant Kitchen Background */
    .stApp {{
        {bg_style}
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    /* Make View Containers transparent to let stApp background show everywhere */
    div[data-testid="stAppViewContainer"], 
    div[data-testid="stMainViewContainer"],
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* Glassmorphic Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: rgba(15, 23, 42, 0.45) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }}

    section[data-testid="stSidebar"] > div {{
        background: transparent !important;
    }}

    /* Force high contrast text colors for labels, paragraphs, list items */
    h1, h2, h3, h4, h5, h6 {{
        color: #ffffff !important;
    }}

    /* Targets all widget labels, dropdown texts, radio button texts, headers */
    label[data-testid="stWidgetLabel"],
    div[data-testid="stWidgetLabel"] p,
    span[data-testid="stWidgetLabel"] p,
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {{
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }}

    /* Animations Keyframes */
    @keyframes fadeInSlideUp {{
        0% {{ opacity: 0; transform: translateY(20px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 4px 10px rgba(249,115,22,0.15); }}
        50% {{ box-shadow: 0 4px 20px rgba(249,115,22,0.35); }}
        100% {{ box-shadow: 0 4px 10px rgba(249,115,22,0.15); }}
    }}

    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Style Streamlit Alerts to have clear, high contrast text */
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] li,
    div[data-testid="stAlert"] span {{
        color: #ffffff !important;
        font-weight: 500 !important;
    }}

    /* Caption text style */
    .stMarkdown caption,
    section[data-testid="stSidebar"] .stCaption,
    div.stCaption p {{
        color: #94a3b8 !important;
    }}

    /* Custom scrollbars */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: #0f172a;
    }}
    ::-webkit-scrollbar-thumb {{
        background: #1e293b;
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #334155;
    }}

    .hero-title {{
        font-family: 'Playfair Display', serif;
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #f97316, #ec4899, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.3rem;
        animation: fadeInSlideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    .hero-sub {{
        text-align: center;
        font-size: 1.15rem;
        color: #e2e8f0; /* brighter for visibility */
        margin-bottom: 1.5rem;
        animation: fadeInSlideUp 1s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    .recipe-title {{
        font-family: 'Playfair Display', serif;
        font-size: 2.6rem;
        font-weight: 700;
        color: #f97316;
        margin-bottom: 0.2rem;
        animation: fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    .recipe-tagline {{
        font-size: 1.1rem;
        color: #cbd5e1; /* brighter for visibility */
        font-style: italic;
        margin-bottom: 1.5rem;
        animation: fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    .meta-box {{
        background: #1e293b;
        border-radius: 14px;
        padding: 14px 10px;
        text-align: center;
        margin-bottom: 8px;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        animation: fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    .meta-box:hover {{
        transform: translateY(-4px) scale(1.02) !important;
        border-color: rgba(249,115,22,0.3) !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2) !important;
    }}
    .meta-label {{ display: block; font-size: 0.75rem; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.5px; }}
    .meta-value {{ display: block; font-size: 1.05rem; font-weight: 600; color: #ffffff; margin-top: 3px; }}

    .nutrition-box {{
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        animation: fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    .nutrition-box:hover {{
        transform: translateY(-3px) scale(1.03) !important;
        border-color: rgba(52, 211, 153, 0.3) !important;
        box-shadow: 0 8px 16px rgba(52, 211, 153, 0.1) !important;
    }}
    .n-label {{ font-size: 0.8rem; color: #cbd5e1; font-weight: 500; }}
    .n-val   {{ font-size: 1.15rem; font-weight: 700; color: #34d399; margin-top: 4px; }}

    .step-card {{
        background: #0f172a;
        border-left: 4px solid #f97316;
        border-radius: 0 14px 14px 0;
        padding: 18px 24px;
        margin-bottom: 14px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        transition: border-color 0.25s ease !important;
        animation: fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    .step-card:hover {{
        border-left-color: #ec4899 !important;
    }}
    .step-num    {{ font-size: 0.8rem; color: #f97316; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }}
    .step-action {{ font-size: 1.05rem; color: #ffffff; margin: 8px 0; line-height: 1.6; }}
    .step-note   {{ font-size: 0.9rem; color: #cbd5e1; font-style: italic; background: rgba(255,255,255,0.02); padding: 8px 12px; border-radius: 6px; border-left: 2px solid #64748b; margin-top: 6px;}}

    .flavor-pill {{
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
        border-radius: 12px;
        padding: 4px 12px;
        margin-right: 6px;
        margin-bottom: 6px;
        display: inline-block;
        font-size: 0.88rem;
        font-weight: 500;
    }}

    /* Style enhancements for all widgets */
    .stButton > button {{
        background: linear-gradient(135deg, #f97316, #ec4899, #8b5cf6, #f97316) !important;
        background-size: 300% 300% !important;
        color: white !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        animation: gradientShift 6s ease infinite, pulseGlow 2.5s infinite !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
    }}

    /* Styling secondary type buttons specifically (like presets and clear buttons) */
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stSidebar"] button,
    .stButton button[key*="preset"],
    .stButton button[key*="hist"] {{
        background: #1e293b !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        box-shadow: none !important;
        transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }}
    div[data-testid="stSidebar"] button:hover {{
        background: #334155 !important;
        border-color: rgba(236,72,153,0.3) !important;
        transform: translateX(4px) !important;
    }}
    .stButton button[key*="preset"]:hover,
    .stButton button[key*="hist"]:hover {{
        background: #334155 !important;
        border-color: rgba(249,115,22,0.4) !important;
        transform: translateY(-3px) scale(1.03) !important;
        box-shadow: 0 5px 15px rgba(249,115,22,0.15) !important;
    }}
    .stButton button[key*="preset"]:active {{
        transform: translateY(-1px) scale(0.98) !important;
    }}

    /* Styling tabs specifically */
    button[data-baseweb="tab"] {{
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #cbd5e1 !important;
        padding: 10px 16px !important;
        border-bottom: 2px solid transparent !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: #f97316 !important;
        border-bottom-color: #f97316 !important;
    }}
    </style>
    """, unsafe_allow_html=True)
