"""
app/services/ai_service.py — Gemini AI integration for personalized recommendations.

Generates context-aware mental health tips and recommendations using
Google Gemini. Falls back to rule-based recommendations if the API key
is not configured or the call fails.
"""
from __future__ import annotations

import json
from config import GEMINI_API_KEY

# Lazy-load the Gemini client only when needed
_gemini_model = None


def _get_gemini_model():
    """Initialize Gemini model lazily."""
    global _gemini_model
    if _gemini_model is None and GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            _gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        except Exception as e:
            print(f"[AI Service] Failed to initialize Gemini: {e}")
            _gemini_model = None
    return _gemini_model


def _build_context_string(
    sleep: float,
    stress: float,
    social: float,
    workload: float,
    screen_time: float,
    exercise: float,
    anxiety_probability: float,
    depression_probability: float,
    risk_score: float,
) -> str:
    """Build a human-readable context string for Gemini prompts."""
    return (
        f"- Sleep quality: {sleep:.1f}/10 ({'Poor' if sleep < 4 else 'Fair' if sleep < 7 else 'Good'})\n"
        f"- Stress level: {stress:.1f}/10 ({'Low' if stress < 4 else 'Moderate' if stress < 7 else 'High'})\n"
        f"- Social engagement: {social:.1f}/10 ({'Low' if social < 4 else 'Moderate' if social < 7 else 'Good'})\n"
        f"- Workload: {workload:.1f}/10 ({'Light' if workload < 4 else 'Moderate' if workload < 7 else 'Heavy'})\n"
        f"- Screen time: {screen_time:.1f}/10 ({'Low' if screen_time < 4 else 'Moderate' if screen_time < 7 else 'Excessive'})\n"
        f"- Exercise: {exercise:.1f}/10 ({'Sedentary' if exercise < 4 else 'Moderate' if exercise < 7 else 'Active'})\n"
        f"- Anxiety probability: {anxiety_probability:.0%}\n"
        f"- Depression probability: {depression_probability:.0%}\n"
        f"- Overall risk score: {risk_score:.0%}"
    )


async def generate_dashboard_tips(
    sleep: float,
    stress: float,
    social: float,
    workload: float,
    screen_time: float,
    exercise: float,
    anxiety_probability: float,
    depression_probability: float,
    risk_score: float,
) -> list[str]:
    """
    Generate 3 short, actionable mental health tips for the dashboard.
    Returns a list of tip strings.
    """
    model = _get_gemini_model()
    if not model:
        return _fallback_tips(sleep, stress, social, workload, screen_time, exercise)

    context = _build_context_string(
        sleep, stress, social, workload, screen_time, exercise,
        anxiety_probability, depression_probability, risk_score,
    )

    prompt = f"""You are a compassionate mental health advisor. Based on the following user metrics:

{context}

Generate exactly 3 short, actionable mental health tips. Each tip should be:
- One sentence (max 20 words)
- Specific to the user's current metrics (not generic)
- Actionable (something they can do right now)
- Start with an appropriate emoji

Focus on the most concerning metrics first. If the user is doing well, reinforce positive habits.

Return ONLY a JSON array of 3 strings, no other text. Example format:
["🧘 tip1", "💤 tip2", "🏃 tip3"]"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Extract JSON from response
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        tips = json.loads(text)
        if isinstance(tips, list) and len(tips) >= 1:
            return tips[:3]
    except Exception as e:
        print(f"[AI Service] Gemini tips failed: {e}")

    return _fallback_tips(sleep, stress, social, workload, screen_time, exercise)


async def generate_insights_recommendations(
    sleep: float,
    stress: float,
    social: float,
    workload: float,
    screen_time: float,
    exercise: float,
    anxiety_probability: float,
    depression_probability: float,
    risk_score: float,
) -> dict:
    """
    Generate detailed recommendations for the insights page.
    Returns a dict with 'summary' (paragraph) and 'actions' (list of strings).
    """
    model = _get_gemini_model()
    if not model:
        return _fallback_recommendations(sleep, stress, social, workload, screen_time, exercise, risk_score)

    context = _build_context_string(
        sleep, stress, social, workload, screen_time, exercise,
        anxiety_probability, depression_probability, risk_score,
    )

    prompt = f"""You are an expert mental health advisor. Based on the following user biometric data:

{context}

Generate a personalized mental health assessment with:
1. A "summary" paragraph (2-3 sentences) analyzing the user's current state — be specific about which metrics are concerning and why
2. An "insight" sentence about a pattern you notice in the data
3. A list of 3 "actions" — each is a specific, actionable recommendation (1-2 sentences each, start with an emoji)

Be empathetic but direct. Don't be generic — reference the actual numbers.

Return ONLY valid JSON in this exact format, no other text:
{{
  "summary": "Your analysis paragraph here...",
  "insight": "A pattern insight sentence...",
  "actions": ["🧘 Action 1...", "💤 Action 2...", "🏃 Action 3..."]
}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text)
        if isinstance(result, dict) and "summary" in result and "actions" in result:
            return result
    except Exception as e:
        print(f"[AI Service] Gemini recommendations failed: {e}")

    return _fallback_recommendations(sleep, stress, social, workload, screen_time, exercise, risk_score)


# ══════════════════════════════════════════════════════════════════════════════
# Fallback rule-based generators (used when Gemini is unavailable)
# ══════════════════════════════════════════════════════════════════════════════

def _fallback_tips(
    sleep: float, stress: float, social: float,
    workload: float, screen_time: float, exercise: float,
) -> list[str]:
    """Rule-based tips when Gemini is not available."""
    tips = []

    if sleep < 4:
        tips.append("💤 Your sleep is critically low — try setting a consistent bedtime tonight.")
    elif sleep < 6:
        tips.append("🌙 Improve your sleep by avoiding screens 1 hour before bed.")

    if stress > 7:
        tips.append("🧘 High stress detected — take 5 deep breaths right now to reset.")
    elif stress > 5:
        tips.append("🧘 Try a 10-minute meditation break to manage your stress levels.")

    if exercise < 3:
        tips.append("🏃 A 15-minute walk can boost your mood significantly — try one today.")

    if social < 4:
        tips.append("👥 Reach out to a friend today — even a short text can boost your mood.")

    if screen_time > 7:
        tips.append("📵 Screen time is high — apply the 20-20-20 rule for eye and mind rest.")

    if workload > 7:
        tips.append("📋 Break your workload into smaller tasks using 25-min focus blocks.")

    if not tips:
        tips = [
            "✅ Great job maintaining balance — keep up your healthy routine!",
            "🌟 Your metrics look strong — consider mentoring others on wellness.",
            "🎯 Stay consistent with your current habits for long-term benefits.",
        ]

    return tips[:3]


def _fallback_recommendations(
    sleep: float, stress: float, social: float,
    workload: float, screen_time: float, exercise: float,
    risk_score: float,
) -> dict:
    """Rule-based recommendations when Gemini is not available."""
    if risk_score > 0.6:
        level = "elevated"
    elif risk_score > 0.3:
        level = "moderate"
    else:
        level = "low"

    # Build summary
    concerns = []
    if sleep < 4:
        concerns.append("critically low sleep quality")
    if stress > 7:
        concerns.append("high stress levels")
    if exercise < 3:
        concerns.append("insufficient physical activity")
    if social < 4:
        concerns.append("limited social engagement")

    if concerns:
        summary = f"Your current risk level is {level}. Key concerns include {', '.join(concerns)}. Addressing these areas can significantly improve your overall mental wellness."
    else:
        summary = f"Your current risk level is {level}. Your metrics are generally well-balanced. Continue maintaining your current healthy habits for sustained well-being."

    # Build insight
    if sleep < 5 and stress > 6:
        insight = "Your stress resilience drops significantly when sleep quality is below 5. Prioritizing rest could break this cycle."
    elif exercise < 3 and stress > 5:
        insight = "Research shows that even moderate exercise reduces stress hormones. Your current exercise level may be limiting your stress recovery."
    else:
        insight = "Your Digital Twin notices your best mental performance days correlate with balanced sleep and social connection."

    # Build actions
    actions = []
    if sleep < 5:
        actions.append("🛌 Implement a strict 10 PM wind-down routine: dim lights, no screens, and light stretching to improve sleep from your current level.")
    if stress > 6:
        actions.append("🧘 Practice progressive muscle relaxation for 10 minutes twice daily — this can reduce your cortisol response by up to 25%.")
    if exercise < 4:
        actions.append("🏃 Start with just 20 minutes of brisk walking daily. Your low exercise score is one of the biggest levers for mood improvement.")
    if social < 4:
        actions.append("👥 Schedule one meaningful social interaction today — even a 10-minute call with a friend can boost oxytocin levels.")
    if screen_time > 7:
        actions.append("📵 Reduce screen exposure by replacing 30 minutes of phone time with an offline hobby. Your eyes and stress levels will thank you.")

    if not actions:
        actions = [
            "✅ Keep up your excellent habits — consistency is the key to long-term mental wellness.",
            "🎯 Consider setting a new wellness goal, like trying meditation or journaling, to continue your upward trajectory.",
            "🌟 Share your positive habits with others — social support networks strengthen everyone's resilience.",
        ]

    return {
        "summary": summary,
        "insight": insight,
        "actions": actions[:3],
    }
