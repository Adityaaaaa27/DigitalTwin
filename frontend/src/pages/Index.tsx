import { Link } from "react-router-dom";
import Navbar from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { useAppState } from "@/context/AppContext";

const quotes = [
  {
    text: "The wound is the place where the Light enters you.",
    author: "Rumi",
  },
  {
    text: "You don't have to control your thoughts. You just have to stop letting them control you.",
    author: "Dan Millman",
  },
  {
    text: "Mental health is not a destination, but a process. It's about how you drive, not where you're going.",
    author: "Noam Shpancer",
  },
  {
    text: "There is hope, even when your brain tells you there isn't.",
    author: "John Green",
  },
  {
    text: "Self-care is how you take your power back.",
    author: "Lalah Delia",
  },
];

// Choose a quote based on the day of the year for variety
const todayQuote = quotes[new Date().getDate() % quotes.length];

const Index = () => {
  const { isAuthenticated } = useAppState();

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero */}
      <section className="text-center py-16 px-6">
        <span className="inline-block px-4 py-1.5 rounded-full border border-border text-xs font-semibold tracking-wide text-muted-foreground mb-6">
          YOUR PERSONAL GUARDIAN
        </span>
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-foreground mb-4">
          Meet Your <span className="text-primary italic">Digital Mirror</span>
        </h1>
        <p className="text-muted-foreground max-w-lg mx-auto text-base leading-relaxed mb-8">
          A conscious interface designed to harmonize your digital existence with
          your mental well-being. Reflect, recover, and grow in your private
          sanctuary.
        </p>

        {/* Auth buttons */}
        <div className="flex items-center justify-center gap-4">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard">
                <Button size="lg" className="rounded-full px-8">
                  Go to Dashboard
                </Button>
              </Link>
              <Link to="/insights">
                <Button
                  variant="outline"
                  size="lg"
                  className="rounded-full px-8"
                >
                  View Insights
                </Button>
              </Link>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button size="lg" className="rounded-full px-8">
                  Sign In
                </Button>
              </Link>
              <Link to="/signup">
                <Button
                  variant="outline"
                  size="lg"
                  className="rounded-full px-8"
                >
                  Sign Up
                </Button>
              </Link>
            </>
          )}
        </div>
      </section>

      {/* Inspirational Quote */}
      <section className="max-w-[900px] mx-auto px-6 pb-32">
        <div className="relative rounded-3xl bg-gradient-to-br from-sanctuary-teal-dark via-primary to-sanctuary-teal-dark p-1">
          <div className="rounded-[22px] bg-gradient-to-br from-sanctuary-teal-dark/95 to-primary/90 px-10 py-16 md:px-16 md:py-20 text-center">
            {/* Decorative quotes */}
            <span className="text-7xl md:text-8xl leading-none text-primary-foreground/15 font-serif select-none block -mb-6">
              "
            </span>
            <blockquote className="text-2xl md:text-3xl lg:text-4xl font-bold text-primary-foreground leading-snug tracking-tight max-w-2xl mx-auto">
              {todayQuote.text}
            </blockquote>
            <div className="mt-6 flex items-center justify-center gap-3">
              <span className="w-8 h-px bg-primary-foreground/30" />
              <p className="text-primary-foreground/70 text-sm font-medium tracking-wide uppercase">
                {todayQuote.author}
              </p>
              <span className="w-8 h-px bg-primary-foreground/30" />
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
