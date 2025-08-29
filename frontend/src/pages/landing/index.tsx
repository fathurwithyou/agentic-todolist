// src/pages/landing/index.tsx
import { Button } from "@/shared/components/ui/button";
import { Card } from "@/shared/components/ui/card";
import { useAuth } from "@/shared/hooks/use-auth";
import { cn } from "@/shared/lib/utils";
import {
  ArrowRight,
  Calendar,
  Check,
  //   ChevronRight,
  Clock,
  Globe,
  Sparkles,
  Users,
  Shield,
  Bot,
} from "lucide-react";
import React, { useEffect, useState } from "react";

export default function LandingPage() {
  const { loginWithGoogle } = useAuth();

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
          }
        });
      },
      { threshold: 0.1 }
    );

    const elements = document.querySelectorAll(".fade-in-on-scroll");
    elements.forEach((el) => observer.observe(el));

    return () => elements.forEach((el) => observer.unobserve(el));
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Navbar loginAction={loginWithGoogle} />
      <main>
        <HeroSection loginAction={loginWithGoogle} />
        <hr className="border-dashed border-1 border-muted" /> <LogoCloud />
        <FeaturesSection />
        <hr className="border-dashed border-1 border-muted" />
        <TestimonialsSection />
      </main>
      <Footer />
    </div>
  );
}

// Navbar Component
const Navbar = ({ loginAction }: { loginAction: () => void }) => {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header className={cn("fixed top-0 left-0 right-0 z-50 transition-all duration-300", isScrolled ? "py-2" : "py-4")}>
      <nav
        className={cn(
          "mx-auto transition-all duration-300",
          isScrolled
            ? "max-w-4xl px-6 bg-background/95 backdrop-blur-xl border border-border rounded-2xl shadow-soft"
            : "container-width"
        )}>
        <div className="flex h-14 items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 bg-primary rounded-xl flex items-center justify-center">
              <Calendar className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-semibold text-lg">CalendarAI</span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Features
            </a>
            <a href="#how-it-works" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              How it Works
            </a>
            <a href="#testimonials" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Testimonials
            </a>
          </div>

          <div className="flex items-center gap-4">
            <Button variant="ghost" className="hidden md:inline-flex">
              Sign In
            </Button>
            <Button onClick={loginAction} className="shadow-sm">
              Get Started
              <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      </nav>
    </header>
  );
};

// Hero Section
const HeroSection = ({ loginAction }: { loginAction: () => void }) => (
  <section className="relative pt-32 pb-20 md:pt-40 md:pb-28 overflow-hidden">
    {/* Background decoration */}
    <div className="absolute inset-0 -z-10">
      <div className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-10 w-96 h-96 bg-primary/3 rounded-full blur-3xl" />
    </div>

    <div className="container-width">
      <div className="max-w-5xl mx-auto text-center space-y-8">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/5 border border-primary/10 rounded-full text-sm animate-in">
          <Sparkles className="w-4 h-4 text-primary" />
          <span>AI-Powered Calendar Management</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-bold tracking-tighter animate-in" style={{ animationDelay: "100ms" }}>
          Transform text into
          <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary via-primary/80 to-primary/60">
            perfectly organized events
          </span>
        </h1>

        <p className="text-xl text-muted-foreground max-w-2xl mx-auto animate-in" style={{ animationDelay: "200ms" }}>
          Stop manually creating calendar events. Just paste your text and let AI handle the rest—dates, times, attendees, all
          automated.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4 animate-in" style={{ animationDelay: "300ms" }}>
          <Button onClick={loginAction} size="lg" className="h-14 px-8 text-base shadow-lg hover:shadow-xl">
            Start Free with Google
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
          <Button variant="outline" size="lg" className="h-14 px-8 text-base">
            Watch Demo
          </Button>
        </div>

        <div
          className="flex items-center justify-center gap-8 pt-8 text-sm text-muted-foreground animate-in"
          style={{ animationDelay: "400ms" }}>
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-600" />
            <span>No credit card required</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-600" />
            <span>Free forever plan</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-600" />
            <span>Setup in 30 seconds</span>
          </div>
        </div>
      </div>

      {/* Hero Image/Demo */}
      <div className="mt-16 relative">
        <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent z-10 pointer-events-none" />
        <Card className="mx-auto max-w-4xl overflow-hidden border-border/50 shadow-2xl fade-in-on-scroll">
          <div className="aspect-[16/9] bg-gradient-to-br from-muted/50 to-muted/30 flex items-center justify-center">
            <div className="text-center space-y-4 p-12">
              <div className="w-20 h-20 mx-auto bg-primary/10 rounded-2xl flex items-center justify-center">
                <Calendar className="w-10 h-10 text-primary" />
              </div>
              <p className="text-muted-foreground">Interactive Demo Coming Soon</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </section>
);

// Logo Cloud
const LogoCloud = () => (
  <section className="py-12 border-y border-border/50">
    <div className="container-width">
      <p className="text-center text-sm text-muted-foreground mb-8">Trusted by teams at</p>
      <div className="flex items-center justify-center gap-12 opacity-60 grayscale">
        {["Google", "Microsoft", "Slack", "Notion", "Linear"].map((company) => (
          <div key={company} className="text-lg font-semibold">
            {company}
          </div>
        ))}
      </div>
    </div>
  </section>
);

// Features Section
const FeaturesSection = () => (
  <section id="features" className="py-24">
    <div className="container-width">
      <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
        <h2 className="text-4xl font-bold tracking-tight fade-in-on-scroll">Everything you need to automate your calendar</h2>
        <p className="text-lg text-muted-foreground fade-in-on-scroll">
          Powerful features that save hours of manual scheduling work
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <FeatureCard
          icon={<Bot className="w-6 h-6" />}
          title="AI Text Parsing"
          description="Advanced NLP understands any format—emails, meeting notes, chat messages, or documents"
          gradient="from-blue-600/20 to-cyan-600/20"
        />
        <FeatureCard
          icon={<Globe className="w-6 h-6" />}
          title="Multi-Provider Support"
          description="Works with OpenAI GPT-4, Google Gemini, and more AI providers for maximum flexibility"
          gradient="from-purple-600/20 to-pink-600/20"
        />
        <FeatureCard
          icon={<Calendar className="w-6 h-6" />}
          title="Direct Calendar Sync"
          description="Seamlessly creates events in Google Calendar with proper formatting and notifications"
          gradient="from-green-600/20 to-emerald-600/20"
        />
        <FeatureCard
          icon={<Users className="w-6 h-6" />}
          title="Smart Attendee Detection"
          description="Automatically identifies and adds attendees from email addresses in your text"
          gradient="from-orange-600/20 to-red-600/20"
        />
        <FeatureCard
          icon={<Clock className="w-6 h-6" />}
          title="Flexible Date Parsing"
          description="Understands relative dates, recurring events, and complex time expressions"
          gradient="from-indigo-600/20 to-blue-600/20"
        />
        <FeatureCard
          icon={<Shield className="w-6 h-6" />}
          title="Enterprise Security"
          description="Your data is encrypted, never stored, and API keys are secured with industry standards"
          gradient="from-slate-600/20 to-gray-600/20"
        />
      </div>
    </div>
  </section>
);

const FeatureCard = ({
  icon,
  title,
  description,
  gradient,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  gradient: string;
}) => (
  <Card className="group relative overflow-hidden border-border/50 hover:border-border hover:shadow-soft-lg transition-all duration-300 fade-in-on-scroll">
    <div
      className={cn(
        "absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-br",
        gradient
      )}
    />
    <div className="relative p-6 space-y-4">
      <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary">{icon}</div>
      <h3 className="font-semibold text-lg">{title}</h3>
      <p className="text-muted-foreground text-sm leading-relaxed">{description}</p>
    </div>
  </Card>
);

// Testimonials Section
const TestimonialsSection = () => (
  <section id="testimonials" className="py-24">
    <div className="container-width">
      <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
        <h2 className="text-4xl font-bold tracking-tight fade-in-on-scroll">Loved by busy professionals</h2>
        <p className="text-lg text-muted-foreground fade-in-on-scroll">Join thousands who've simplified their scheduling</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <TestimonialCard
          quote="This tool saved me hours every week. I just forward emails to myself with event details and CalendarAI does the rest."
          author="Sarah Chen"
          role="Product Manager at Meta"
          avatar="SC"
        />
        <TestimonialCard
          quote="Game-changer for managing conference schedules. Paste the agenda, and boom—everything's in my calendar perfectly."
          author="Michael Torres"
          role="Event Coordinator"
          avatar="MT"
        />
        <TestimonialCard
          quote="As a consultant juggling multiple clients, this is invaluable. It catches every detail I might miss manually."
          author="Emma Williams"
          role="Strategy Consultant"
          avatar="EW"
        />
      </div>
    </div>
  </section>
);

const TestimonialCard = ({ quote, author, role, avatar }: { quote: string; author: string; role: string; avatar: string }) => (
  <Card className="p-6 border-border/50 fade-in-on-scroll">
    <div className="space-y-4">
      <div className="flex gap-1">
        {[...Array(5)].map((_, i) => (
          <svg key={i} className="w-5 h-5 text-yellow-500 fill-current" viewBox="0 0 20 20">
            <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
          </svg>
        ))}
      </div>
      <p className="text-muted-foreground italic">"{quote}"</p>
      <div className="flex items-center gap-3 pt-2">
        <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center font-semibold text-sm">
          {avatar}
        </div>
        <div>
          <p className="font-medium">{author}</p>
          <p className="text-sm text-muted-foreground">{role}</p>
        </div>
      </div>
    </div>
  </Card>
);

// Footer
const Footer = () => (
  <footer className="py-16 border-t">
    <div className="container-width">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
        <div className="col-span-2 md:col-span-1">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-9 h-9 bg-primary rounded-xl flex items-center justify-center">
              <Calendar className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-semibold text-lg">CalendarAI</span>
          </div>
          <p className="text-sm text-muted-foreground">Transform text into calendar events with AI</p>
        </div>

        <div>
          <h4 className="font-medium mb-4">Product</h4>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>
              <a href="#" className="hover:text-foreground transition-colors">
                Features
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-foreground transition-colors">
                Pricing
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-foreground transition-colors">
                API
              </a>
            </li>
          </ul>
        </div>

        <div>
          <h4 className="font-medium mb-4">Company</h4>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>
              <a href="#" className="hover:text-foreground transition-colors">
                About
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-foreground transition-colors">
                Blog
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-foreground transition-colors">
                Careers
              </a>
            </li>
          </ul>
        </div>

        <div>
          <h4 className="font-medium mb-4">Legal</h4>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>
              <a href="#" className="hover:text-foreground transition-colors">
                Privacy
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-foreground transition-colors">
                Terms
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-foreground transition-colors">
                Security
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="pt-8 border-t flex flex-col md:flex-row justify-between items-center gap-4">
        <p className="text-sm text-muted-foreground">© {new Date().getFullYear()} CalendarAI. All rights reserved.</p>
        <div className="flex gap-6">
          <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
            </svg>
          </a>
          <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  </footer>
);
