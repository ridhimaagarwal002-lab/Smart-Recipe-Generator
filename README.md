<div align="center">

# 🍳 Smart Recipe Generator

**AI-powered kitchen companion — drop your ingredients, get a gourmet recipe.**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com)
[![MIT License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

</div>

---

## What It Does

Enter the ingredients you have at home. **Chef·AI** — built on Google Gemini — returns a complete recipe with step-by-step instructions, culinary science notes, macronutrient breakdown, chef tips, and a creative fusion twist.

---

## Features

| | |
|---|---|
| 🧠 **Antigravity Prompt** | 4-layer engineered prompt — role anchor, mission brief, constraint weave, JSON output sculpture |
| 🔄 **Auto Model Fallback** | Tries `gemini-2.5-flash` → `2.0-flash` → `1.5-flash` automatically |
| 🧺 **Ingredient Chips** | Click pantry presets or type freely — auto-deduplicated |
| ⚖️ **Portion Scaler** | Scales fractions, ranges, and decimals for 1–10 servings |
| 🔬 **Slideshow Mode** | Step-by-step kitchen focus view with science notes |
| 🥗 **Nutrition Panel** | Calories, protein, carbs, fats, fiber, sodium + tips |
| 🎨 **Glassmorphic UI** | Dark theme, gradient accents, smooth micro-animations |

---

## Quick Start

```bash
git clone https://github.com/your-username/smart-recipe-generator.git
cd smart-recipe-generator
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`, paste your **Gemini API key** in the sidebar, and cook.

> Get a free API key at [aistudio.google.com](https://aistudio.google.com/app/apikey)

---

## Project Structure

```
app.py              → Streamlit UI & session state
gemini_helper.py    → Gemini API + Antigravity Prompt
utils.py            → Parser, scaler, CSS, recipe card
style.css           → Glassmorphic styles & animations
requirements.txt    → Dependencies
```

---

## Stack

`Streamlit` · `Google Gemini API` · `google-generativeai` · `Custom CSS`

---

<div align="center">
Built with ❤️ — give it a ⭐ if it helped you!
</div>
