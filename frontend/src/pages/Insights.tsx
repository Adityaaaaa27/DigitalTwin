import Navbar from "@/components/Navbar";
import AppSidebar from "@/components/AppSidebar";
import { useAppState } from "@/context/AppContext";
import { useNavigate } from "react-router-dom";
import { predict, getAIRecommendations, AIRecommendations } from "@/services/api";
import { useState, useEffect } from "react";
import {
  Moon,
  Zap,
  Users,
  Clock,
  Timer,
  Dumbbell,
  Sparkles,
  ArrowRight,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { toast } from "sonner";

const Insights = () => {
  const { predictionResult, setPredictionResult, userId } = useAppState();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  // AI recommendations
  const [aiRecs, setAiRecs] = useState<AIRecommendations | null>(null);
  const [recsLoading, setRecsLoading] = useState(false);

  // Fetch AI recommendations when prediction result changes
  useEffect(() => {
    if (predictionResult?.inputs) {
      setRecsLoading(true);
      getAIRecommendations(
        predictionResult.inputs,
        predictionResult.anxiety_probability,
        predictionResult.depression_probability,
        predictionResult.risk_score
      )
        .then((recs) => {
          if (recs) setAiRecs(recs);
        })
        .finally(() => setRecsLoading(false));
    }
  }, [predictionResult]);

  // If no result, run a default prediction
  const runDefault = async () => {
    setLoading(true);
    try {
      const result = await predict({
        user_id: userId,
        sleep: 75,
        stress: 42,
        social: 80,
        workload: 70,
        screen_time: 52,
        exercise: 35,
      });
      setPredictionResult(result);
    } catch {
      toast.error("Analysis failed. Please check if the backend is running.");
    }
    setLoading(false);
  };

  if (!predictionResult) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="flex">
          <AppSidebar />
          <main className="flex-1 p-8 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-foreground mb-3">
                No Assessment Data Yet
              </h2>
              <p className="text-muted-foreground mb-6">
                Complete an assessment to view your biometric synthesis.
              </p>
              <div className="flex gap-3 justify-center">
                <Button
                  onClick={() => navigate("/dashboard")}
                  variant="outline"
                  className="rounded-full"
                >
                  Go to Assessment
                </Button>
                <Button
                  onClick={runDefault}
                  className="rounded-full"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />{" "}
                      Analyzing...
                    </>
                  ) : (
                    "Quick Analysis"
                  )}
                </Button>
              </div>
            </div>
          </main>
        </div>
      </div>
    );
  }

  const r = predictionResult;
  const riskLabel =
    r.risk_score <= 25
      ? "OPTIMAL"
      : r.risk_score <= 50
        ? "MODERATE"
        : "ELEVATED";
  const gaugeAngle = (r.risk_score / 100) * 180;

  const factorIcons: Record<string, typeof Moon> = {
    Sleep: Moon,
    Stress: Zap,
    Social: Users,
    Workload: Clock,
    "Screen Time": Timer,
    Exercise: Dumbbell,
  };

  // Dynamic aura gradient based on risk
  const auraGradient =
    r.risk_score <= 25
      ? "from-green-200 via-emerald-100 to-green-50"
      : r.risk_score <= 50
        ? "from-blue-200 via-sky-100 to-blue-50"
        : r.risk_score <= 75
          ? "from-yellow-200 via-orange-100 to-amber-50"
          : "from-red-200 via-rose-100 to-red-50";

  const auraInner =
    r.risk_score <= 25
      ? "from-green-400/30 to-emerald-300/20"
      : r.risk_score <= 50
        ? "from-blue-400/30 to-sky-300/20"
        : r.risk_score <= 75
          ? "from-orange-400/30 to-amber-300/20"
          : "from-red-400/30 to-rose-300/20";

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="flex">
        <AppSidebar />
        <main className="flex-1 p-8 max-w-[1100px] mx-auto">
          <h1 className="text-4xl font-extrabold tracking-tight text-foreground mb-2">
            Biometric <span className="text-primary italic">Synthesis</span>
          </h1>
          <p className="text-muted-foreground max-w-lg mb-8">
            Your Digital Twin has analyzed your recent physiological markers.
            Here is your clarity for today.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            {/* Integrative Risk Assessment */}
            <div className="md:col-span-3 bg-sanctuary-blue-light rounded-2xl p-8 text-center">
              <h3 className="text-lg font-bold text-foreground mb-6 text-left">
                Integrative Risk Assessment
              </h3>

              {/* Gauge */}
              <div className="relative w-48 h-24 mx-auto mb-4 overflow-hidden">
                <div className="absolute inset-0 border-[12px] border-border rounded-t-full border-b-0" />
                <div
                  className="absolute inset-0 border-[12px] border-primary rounded-t-full border-b-0"
                  style={{
                    clipPath: `polygon(0 100%, 0 0, ${Math.min(100, gaugeAngle / 1.8)}% 0, 50% 100%)`,
                  }}
                />
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center">
                  <p className="text-4xl font-extrabold text-foreground">
                    {r.risk_score}
                  </p>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    {riskLabel}
                  </p>
                </div>
              </div>

              <p className="text-sm text-muted-foreground max-w-sm mx-auto mb-4">
                {aiRecs?.summary ||
                  `Your current score indicates ${riskLabel.toLowerCase()} resilience. Continue to maintain balanced metrics for optimal well-being.`}
              </p>

              <div className="flex justify-center gap-3">
                <span className="px-4 py-1.5 rounded-full bg-sanctuary-green-light text-sanctuary-green text-xs font-semibold">
                  {r.risk_score <= 30 ? "Stable Baseline" : "Active Monitoring"}
                </span>
                <span className="px-4 py-1.5 rounded-full bg-sanctuary-blue-light text-primary text-xs font-semibold border border-primary/20">
                  {r.risk_score <= 50 ? "High Coherence" : "Needs Attention"}
                </span>
              </div>
            </div>

            {/* Right column — Anxiety & Depression (values rounded, no floating) */}
            <div className="md:col-span-2 flex flex-col gap-6">
              <div className="bg-card rounded-2xl border border-border p-6">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-sm text-muted-foreground">
                    Anxiety Propensity
                  </p>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-extrabold text-foreground">
                    {r.anxiety_probability}%
                  </span>
                  <span className="text-sm text-muted-foreground">
                    {r.anxiety_probability < 20
                      ? "Low Probability"
                      : r.anxiety_probability < 50
                        ? "Moderate"
                        : "Elevated"}
                  </span>
                </div>
                <div className="w-full bg-muted rounded-full h-1.5 mt-3">
                  <div
                    className="bg-primary rounded-full h-1.5 transition-all duration-500"
                    style={{ width: `${Math.min(r.anxiety_probability, 100)}%` }}
                  />
                </div>
              </div>

              <div className="bg-card rounded-2xl border border-border p-6">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-sm text-muted-foreground">
                    Depression Risk
                  </p>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-extrabold text-foreground">
                    {r.depression_probability}%
                  </span>
                  <span className="text-sm text-muted-foreground">
                    {r.depression_probability < 15
                      ? "Minimal Risk"
                      : r.depression_probability < 40
                        ? "Notable"
                        : "Significant"}
                  </span>
                </div>
                <div className="w-full bg-muted rounded-full h-1.5 mt-3">
                  <div
                    className="bg-primary rounded-full h-1.5 transition-all duration-500"
                    style={{
                      width: `${Math.min(r.depression_probability, 100)}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Why This Matters + AI Recommendations */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mt-6">
            <div className="md:col-span-3 bg-card rounded-2xl border border-border p-6">
              <h3 className="text-lg font-bold text-foreground mb-6">
                Why This Matters
              </h3>
              <div className="space-y-5">
                {r.factors.slice(0, 3).map((f) => {
                  const Icon = factorIcons[f.name] || Zap;
                  return (
                    <div key={f.name}>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Icon className="w-4 h-4 text-primary" />
                          <span className="font-semibold text-sm text-foreground">
                            {f.name}
                          </span>
                        </div>
                        <span className="text-sm text-primary font-medium">
                          {f.contribution}% Influence
                        </span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-3">
                        <div
                          className="bg-primary rounded-full h-3 transition-all duration-500"
                          style={{ width: `${Math.min(f.contribution, 100)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* AI Recommendations */}
            <div className="md:col-span-2 bg-gradient-to-br from-sanctuary-teal-dark to-primary rounded-2xl p-6 text-primary-foreground relative">
              <div className="flex items-center justify-between mb-3">
                <div className="w-9 h-9 rounded-full bg-primary-foreground/20 flex items-center justify-center">
                  <Sparkles className="w-4 h-4" />
                </div>
                {recsLoading && (
                  <Loader2 className="w-4 h-4 animate-spin text-primary-foreground/60" />
                )}
              </div>
              <h3 className="text-xl font-bold mb-2">Recommended Action</h3>
              <p className="text-sm text-primary-foreground/80 leading-relaxed mb-5">
                {aiRecs?.insight ||
                  "Complete an analysis to receive personalized, AI-generated recommendations."}
              </p>
              <div className="space-y-2 mb-5">
                {(aiRecs?.actions || r.recommendations.slice(0, 2)).map(
                  (rec, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-2 bg-primary-foreground/10 rounded-lg px-3 py-2"
                    >
                      <Timer className="w-4 h-4 shrink-0 mt-0.5" />
                      <span className="text-sm font-medium">{rec}</span>
                    </div>
                  )
                )}
              </div>
              <Button
                variant="outline"
                className="w-full rounded-full border-primary-foreground/30 text-primary-foreground hover:bg-primary-foreground/10 bg-transparent"
                onClick={() =>
                  toast.success("Focus Session Started", {
                    description: "Biometric tracking active.",
                  })
                }
              >
                Start Session
              </Button>
            </div>
          </div>

          {/* Cognitive Ease Insight + Dynamic Aura */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mt-6 mb-12">
            <div className="md:col-span-3">
              <h3 className="text-2xl font-extrabold text-foreground mb-2">
                Cognitive Ease Insight
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                {aiRecs?.summary ||
                  "Your Digital Twin is analyzing patterns in your data. Complete more assessments to unlock deeper cognitive insights and personalized guidance."}
              </p>
              <Link
                to="/history"
                className="flex items-center gap-1 text-sm text-primary font-medium hover:underline"
              >
                View complete history <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            {/* Dynamic Digital Twin Live Aura */}
            <div className="md:col-span-2 bg-card rounded-2xl border border-border p-6 flex flex-col items-center">
              <div
                className={`w-32 h-32 rounded-full bg-gradient-to-br ${auraGradient} flex items-center justify-center transition-all duration-700`}
                style={{
                  animation: "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                }}
              >
                <div
                  className={`w-16 h-16 rounded-full bg-gradient-to-br ${auraInner} transition-all duration-700`}
                />
              </div>
              <p className="text-sm text-muted-foreground mt-3 flex items-center gap-1.5">
                <span
                  className={`w-2 h-2 rounded-full inline-block ${
                    r.risk_score <= 30
                      ? "bg-sanctuary-green"
                      : r.risk_score <= 60
                        ? "bg-primary"
                        : "bg-sanctuary-orange"
                  }`}
                  style={{
                    animation:
                      "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                  }}
                />
                Digital Twin Live Aura
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Risk: {r.risk_score}% | Anxiety: {r.anxiety_probability}% |
                Depression: {r.depression_probability}%
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Insights;
