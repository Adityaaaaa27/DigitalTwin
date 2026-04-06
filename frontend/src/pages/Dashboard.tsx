import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import AppSidebar from "@/components/AppSidebar";
import { Slider } from "@/components/ui/slider";
import { Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { useAppState } from "@/context/AppContext";
import { predict, getAITips } from "@/services/api";

const Dashboard = () => {
  const { userId, setPredictionResult, predictionResult } = useAppState();
  const [sleep, setSleep] = useState([75]);
  const [stress, setStress] = useState([42]);
  const [social, setSocial] = useState([80]);
  const [workload, setWorkload] = useState([70]);
  const [screenTime, setScreenTime] = useState([52]);
  const [exercise, setExercise] = useState([35]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // AI-generated tips
  const [aiTips, setAiTips] = useState<string[]>([]);
  const [tipsLoading, setTipsLoading] = useState(false);

  const getLevelLabel = (val: number) =>
    val < 30 ? "Low" : val < 70 ? "Mod." : "High";

  // Fetch AI tips after prediction
  useEffect(() => {
    if (predictionResult?.inputs) {
      setTipsLoading(true);
      getAITips(
        predictionResult.inputs,
        predictionResult.anxiety_probability,
        predictionResult.depression_probability,
        predictionResult.risk_score
      )
        .then((tips) => {
          if (tips.length > 0) setAiTips(tips);
        })
        .finally(() => setTipsLoading(false));
    }
  }, [predictionResult]);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const result = await predict({
        user_id: userId,
        sleep: sleep[0],
        stress: stress[0],
        social: social[0],
        workload: workload[0],
        screen_time: screenTime[0],
        exercise: exercise[0],
      });

      setPredictionResult(result);
      toast.success("Twin Analysis Complete", {
        description: `Risk Score: ${result.risk_score}% | ${result.alerts.length ? result.alerts[0] : "State looks stable."}`,
      });
    } catch (e) {
      toast.error("Analysis Failed", {
        description: "Could not connect to the backend. Make sure the server is running.",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="flex">
        <AppSidebar />
        <main className="flex-1 p-8 max-w-[1100px] mx-auto">
          <h1 className="text-4xl font-extrabold tracking-tight text-foreground mb-2">
            Map Your <span className="text-primary italic">Digital Twin</span>
          </h1>
          <p className="text-muted-foreground mb-8 max-w-lg">
            Your emotional aura is dynamic. Adjust the indicators below to
            synchronize your physical state with your mindful guardian.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            {/* Vital Rhythms — 3 cols */}
            <div className="md:col-span-3 bg-card rounded-2xl border border-border p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-foreground">
                  Vital Rhythms
                </h3>
                <span className="text-xs font-semibold text-primary px-3 py-1 rounded-full border border-primary/20 bg-sanctuary-blue-light uppercase tracking-wider">
                  Core Metrics
                </span>
              </div>

              <div className="space-y-8">
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <div>
                      <p className="font-semibold text-foreground">Sleep</p>
                      <p className="text-xs text-muted-foreground">
                        Restorative hours per night
                      </p>
                    </div>
                    <p className="text-2xl font-bold text-primary">
                      {(sleep[0] / 10).toFixed(1)}
                      <span className="text-sm font-normal text-muted-foreground ml-0.5">
                        hrs
                      </span>
                    </p>
                  </div>
                  <Slider
                    value={sleep}
                    onValueChange={setSleep}
                    max={100}
                    className="w-full"
                  />
                </div>

                <div>
                  <div className="flex justify-between items-end mb-2">
                    <div>
                      <p className="font-semibold text-foreground">Stress</p>
                      <p className="text-xs text-muted-foreground">
                        Daily cognitive load level
                      </p>
                    </div>
                    <p className="text-2xl font-bold text-primary">
                      {stress[0]}
                      <span className="text-sm font-normal text-muted-foreground ml-0.5">
                        %
                      </span>
                    </p>
                  </div>
                  <Slider
                    value={stress}
                    onValueChange={setStress}
                    max={100}
                    className="w-full"
                  />
                </div>

                <div>
                  <div className="flex justify-between items-end mb-2">
                    <div>
                      <p className="font-semibold text-foreground">Social</p>
                      <p className="text-xs text-muted-foreground">
                        Quality of human connection
                      </p>
                    </div>
                    <p className="text-2xl font-bold text-primary">
                      {Math.round(social[0] / 10)
                        .toString()
                        .padStart(2, "0")}
                      <span className="text-sm font-normal text-muted-foreground ml-0.5">
                        /10
                      </span>
                    </p>
                  </div>
                  <Slider
                    value={social}
                    onValueChange={setSocial}
                    max={100}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            {/* Real-Time Aura — 2 cols (FIXED: now properly in the grid) */}
            <div className="md:col-span-2 bg-card rounded-2xl border border-border p-6 flex flex-col items-center justify-center">
              <p className="text-xs font-semibold text-primary uppercase tracking-wider mb-4">
                Real-Time Aura
              </p>
              {(() => {
                const r = predictionResult;
                const auraLabel = !r
                  ? "Stable Resonance"
                  : r.risk_score <= 25
                    ? "Radiant Calm"
                    : r.risk_score <= 50
                      ? "Balanced Harmony"
                      : r.risk_score <= 75
                        ? "Mild Tension"
                        : "Acute Stress";
                const alignment = !r
                  ? 88
                  : Math.round(100 - r.risk_score);
                const resilience = !r
                  ? "High"
                  : r.risk_score <= 30
                    ? "High"
                    : r.risk_score <= 60
                      ? "Moderate"
                      : "Low";
                const auraColor = !r
                  ? "from-muted to-border"
                  : r.risk_score <= 25
                    ? "from-green-100 to-green-200"
                    : r.risk_score <= 50
                      ? "from-blue-100 to-blue-200"
                      : r.risk_score <= 75
                        ? "from-yellow-100 to-orange-200"
                        : "from-red-100 to-red-200";
                return (
                  <>
                    <div
                      className={`w-36 h-36 mx-auto rounded-full bg-gradient-to-b ${auraColor} flex items-center justify-center mb-4 transition-all duration-700 ${r ? "animate-pulse" : ""}`}
                    >
                      <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-primary-foreground" />
                      </div>
                    </div>
                    <p className="text-primary font-semibold text-sm mb-4">
                      {auraLabel}
                    </p>
                    <div className="flex gap-4">
                      <div className="bg-muted rounded-xl px-5 py-3 text-center">
                        <p className="text-xs text-muted-foreground uppercase tracking-wide">
                          Alignment
                        </p>
                        <p className="text-xl font-bold text-foreground">
                          {alignment}%
                        </p>
                      </div>
                      <div className="bg-muted rounded-xl px-5 py-3 text-center">
                        <p className="text-xs text-muted-foreground uppercase tracking-wide">
                          Resilience
                        </p>
                        <p className="text-xl font-bold text-foreground">
                          {resilience}
                        </p>
                      </div>
                    </div>
                  </>
                );
              })()}
            </div>
          </div>

          {/* External Impact + AI Tips */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mt-6">
            <div className="md:col-span-3 bg-card rounded-2xl border border-border p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-foreground">
                  External Impact
                </h3>
                <span className="text-xs font-semibold text-sanctuary-green px-3 py-1 rounded-full border border-sanctuary-green/20 bg-sanctuary-green-light uppercase tracking-wider">
                  Environmental
                </span>
              </div>
              <div className="space-y-8">
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <div>
                      <p className="font-semibold text-foreground">Workload</p>
                      <p className="text-xs text-muted-foreground">
                        Volume of professional output
                      </p>
                    </div>
                    <p className="text-2xl font-bold text-primary">
                      {getLevelLabel(workload[0])}
                    </p>
                  </div>
                  <Slider
                    value={workload}
                    onValueChange={setWorkload}
                    max={100}
                    className="w-full"
                  />
                </div>
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <div>
                      <p className="font-semibold text-foreground">
                        Screen Time
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Digital exposure duration
                      </p>
                    </div>
                    <p className="text-2xl font-bold text-primary">
                      {(screenTime[0] / 10).toFixed(1)}
                      <span className="text-sm font-normal text-muted-foreground ml-0.5">
                        hrs
                      </span>
                    </p>
                  </div>
                  <Slider
                    value={screenTime}
                    onValueChange={setScreenTime}
                    max={100}
                    className="w-full"
                  />
                </div>
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <div>
                      <p className="font-semibold text-foreground">Exercise</p>
                      <p className="text-xs text-muted-foreground">
                        Physical activity intensity
                      </p>
                    </div>
                    <p className="text-2xl font-bold text-primary">
                      {getLevelLabel(exercise[0])}
                    </p>
                  </div>
                  <Slider
                    value={exercise}
                    onValueChange={setExercise}
                    max={100}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            <div className="md:col-span-2 flex flex-col gap-6">
              {/* AI Aura Tips */}
              <div className="bg-gradient-to-br from-sanctuary-teal-dark to-primary rounded-2xl p-6 text-primary-foreground">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-bold">Aura Tips</h3>
                  {tipsLoading && (
                    <Loader2 className="w-4 h-4 animate-spin text-primary-foreground/60" />
                  )}
                </div>
                {aiTips.length > 0 ? (
                  <div className="space-y-3">
                    {aiTips.map((tip, i) => (
                      <p
                        key={i}
                        className="text-sm text-primary-foreground/85 leading-relaxed"
                      >
                        {tip}
                      </p>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-primary-foreground/80 leading-relaxed">
                    Run an analysis to get personalized AI-powered tips based on
                    your current metrics.
                  </p>
                )}
              </div>

              {/* Recent Milestones */}
              <div className="bg-card rounded-2xl border border-border p-6">
                <h3 className="text-base font-bold text-foreground mb-3">
                  Recent Milestones
                </h3>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-sanctuary-green inline-block" />
                    {predictionResult
                      ? predictionResult.risk_score <= 30
                        ? "Aura in Radiant Calm state"
                        : "Analysis completed successfully"
                      : "Awaiting first analysis"}
                  </p>
                  <p className="text-sm text-muted-foreground flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-primary inline-block" />
                    Digital Twin synchronization active
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Analyze Button */}
          <div className="text-center mt-10 mb-8">
            <Button
              size="lg"
              className="rounded-full px-10 gap-2"
              onClick={handleAnalyze}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Syncing...
                </>
              ) : (
                <>
                  Analyze My Twin <Sparkles className="w-4 h-4" />
                </>
              )}
            </Button>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
