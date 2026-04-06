const API_BASE = "http://localhost:8000";

// ══════════════════════════════════════════════════════════════════════════════
// Type definitions
// ══════════════════════════════════════════════════════════════════════════════

export interface PredictionInput {
  user_id: string;
  sleep: number;
  stress: number;
  social: number;
  workload: number;
  screen_time: number;
  exercise: number;
}

export interface PredictionResult {
  risk_score: number;
  anxiety_probability: number;
  depression_probability: number;
  alerts: string[];
  recommendations: string[];
  factors: { name: string; contribution: number }[];
  // Raw 0-10 inputs (stored for AI tips context)
  inputs?: {
    sleep: number;
    stress: number;
    social: number;
    workload: number;
    screen_time: number;
    exercise: number;
  };
}

export interface HistoryRecord {
  id: string;
  cognitive_state: string;
  neural_symmetry: number;
  date: string;
  trend: "up" | "down" | "stable";
  risk_score: number;
  anxiety_probability: number;
  depression_probability: number;
  stress: number;
  sleep: number;
  social: number;
  workload: number;
  screen_time: number;
  exercise: number;
}

export interface FuturePrediction {
  dates: string[];
  risk_values: number[];
  focus_probability: number;
  stress_resistance: number;
  trend_direction: string;
}

export interface AuthUser {
  id: number;
  name: string;
  email: string;
}

export interface AITips {
  tips: string[];
}

export interface AIRecommendations {
  summary: string;
  insight: string;
  actions: string[];
}

// ══════════════════════════════════════════════════════════════════════════════
// Utilities
// ══════════════════════════════════════════════════════════════════════════════

function titleCase(str: string) {
  return str
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function formatDate(isoString: string) {
  const date = new Date(isoString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// Auth APIs
// ══════════════════════════════════════════════════════════════════════════════

export async function authSignup(
  name: string,
  email: string,
  password: string
): Promise<AuthUser> {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Signup failed" }));
    throw new Error(err.detail || "Signup failed");
  }
  return res.json();
}

export async function authLogin(
  email: string,
  password: string
): Promise<AuthUser> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(err.detail || "Invalid email or password");
  }
  return res.json();
}

// ══════════════════════════════════════════════════════════════════════════════
// Prediction API
// ══════════════════════════════════════════════════════════════════════════════

export async function predict(
  data: PredictionInput
): Promise<PredictionResult> {
  try {
    const normalised = {
      ...data,
      sleep: data.sleep / 10,
      stress: data.stress / 10,
      social: data.social / 10,
      workload: data.workload / 10,
      screen_time: data.screen_time / 10,
      exercise: data.exercise / 10,
    };

    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(normalised),
    });
    if (!res.ok) throw new Error("Prediction failed");
    const json = await res.json();

    return {
      risk_score: Math.round(json.risk_score * 100),
      anxiety_probability: Math.round(json.anxiety_probability * 100),
      depression_probability: Math.round(json.depression_probability * 100),
      alerts: json.alerts,
      recommendations: json.recommendations,
      factors: Object.entries(json.explanation || {}).map(
        ([name, contribution]) => ({
          name: titleCase(name),
          contribution: Math.round((contribution as number) * 100),
        })
      ),
      inputs: {
        sleep: data.sleep / 10,
        stress: data.stress / 10,
        social: data.social / 10,
        workload: data.workload / 10,
        screen_time: data.screen_time / 10,
        exercise: data.exercise / 10,
      },
    };
  } catch (e) {
    console.error("API Error:", e);
    throw new Error("Failed to connect to the backend.");
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// History API
// ══════════════════════════════════════════════════════════════════════════════

export async function getHistory(userId: string): Promise<HistoryRecord[]> {
  try {
    const res = await fetch(`${API_BASE}/history/${userId}`);
    if (!res.ok) throw new Error("Failed to fetch history");
    const json = await res.json();

    return json.records
      .map((r: any, idx: number) => {
        const isUp =
          idx > 0
            ? r.risk_score > json.records[idx - 1].risk_score
            : false;
        const isDown =
          idx > 0
            ? r.risk_score < json.records[idx - 1].risk_score
            : false;
        return {
          id: `#DT-${r.id.toString().padStart(4, "0")}`,
          cognitive_state:
            r.risk_score > 0.6
              ? "Acute Stress"
              : r.risk_score > 0.3
                ? "Balanced"
                : "Deep Focus",
          neural_symmetry: Math.round(100 - r.risk_score * 100),
          date: formatDate(r.date),
          trend: isUp ? "up" : isDown ? "down" : "stable",
          risk_score: Math.round(r.risk_score * 100),
          anxiety_probability: Math.round(
            (r.anxiety_probability || 0) * 100
          ),
          depression_probability: Math.round(
            (r.depression_probability || 0) * 100
          ),
          stress: Math.round(r.stress * 10),
          sleep: Math.round(r.sleep * 10),
          social: Math.round((r.social || 0) * 10),
          workload: Math.round((r.workload || 0) * 10),
          screen_time: Math.round((r.screen_time || 0) * 10),
          exercise: Math.round((r.exercise || 0) * 10),
        };
      })
      .reverse(); // Latest first
  } catch (e) {
    console.error("History fetch error:", e);
    return [];
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// Future Prediction API
// ══════════════════════════════════════════════════════════════════════════════

export async function getFuture(userId: string): Promise<FuturePrediction> {
  try {
    const res = await fetch(`${API_BASE}/future/${userId}`);
    if (!res.ok) throw new Error("Failed to fetch future");
    const json = await res.json();

    const dates = json.future_risk.map((_: any, i: number) => {
      const d = new Date();
      d.setDate(d.getDate() + (i + 1) * 7);
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    });

    return {
      dates,
      risk_values: json.future_risk.map((v: number) => Math.round(v * 100)),
      focus_probability: Math.round(100 - json.future_risk[0] * 100),
      stress_resistance: Math.round(100 - json.future_risk[0] * 50),
      trend_direction: json.trend_direction || "stable",
    };
  } catch (e) {
    console.error("Future fetch error:", e);
    return {
      dates: [],
      risk_values: [],
      focus_probability: 50,
      stress_resistance: 50,
      trend_direction: "stable",
    };
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// AI Recommendation APIs
// ══════════════════════════════════════════════════════════════════════════════

export async function getAITips(
  inputs: PredictionResult["inputs"],
  anxiety: number,
  depression: number,
  risk: number
): Promise<string[]> {
  if (!inputs) return [];
  try {
    const res = await fetch(`${API_BASE}/ai/tips`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sleep: inputs.sleep,
        stress: inputs.stress,
        social: inputs.social,
        workload: inputs.workload,
        screen_time: inputs.screen_time,
        exercise: inputs.exercise,
        anxiety_probability: anxiety / 100,
        depression_probability: depression / 100,
        risk_score: risk / 100,
      }),
    });
    if (!res.ok) throw new Error("Tips fetch failed");
    const json = await res.json();
    return json.tips || [];
  } catch (e) {
    console.error("AI Tips error:", e);
    return [];
  }
}

export async function getAIRecommendations(
  inputs: PredictionResult["inputs"],
  anxiety: number,
  depression: number,
  risk: number
): Promise<AIRecommendations | null> {
  if (!inputs) return null;
  try {
    const res = await fetch(`${API_BASE}/ai/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sleep: inputs.sleep,
        stress: inputs.stress,
        social: inputs.social,
        workload: inputs.workload,
        screen_time: inputs.screen_time,
        exercise: inputs.exercise,
        anxiety_probability: anxiety / 100,
        depression_probability: depression / 100,
        risk_score: risk / 100,
      }),
    });
    if (!res.ok) throw new Error("Recommendations fetch failed");
    return res.json();
  } catch (e) {
    console.error("AI Recommendations error:", e);
    return null;
  }
}
