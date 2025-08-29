// src/pages/landing/index.tsx
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { useAuth } from "@/shared/hooks/use-auth";
import { cn } from "@/shared/lib/utils";
import { ArrowRight, Calendar, Check, Menu, X, Zap } from "lucide-react";
import React, { useEffect, useState } from "react";

// Main Landing Page Component
export default function LandingPage() {
	const { loginWithGoogle } = useAuth();

	// Simple scroll-in animation hook
	useEffect(() => {
		const observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting) {
						entry.target.classList.add("is-visible");
					}
				});
			},
			{ threshold: 0.1 },
		);

		const elements = document.querySelectorAll(".fade-in-on-scroll");
		elements.forEach((el) => observer.observe(el));

		return () => elements.forEach((el) => observer.unobserve(el));
	}, []);

	return (
		<div className="bg-background text-foreground">
			<Navbar loginAction={loginWithGoogle} />
			<main>
				<HeroSection loginAction={loginWithGoogle} />
				<hr className="border-dashed border-1 border-muted" />
				<FeaturesSection />
				<hr className="border-dashed border-1 border-muted" />
				<TestimonialsSection />
			</main>
			<Footer />
		</div>
	);
}

// Sticky, translucent Navbar with scroll and mobile responsive effects
const Navbar = ({ loginAction }: { loginAction: () => void }) => {
	const [isScrolled, setIsScrolled] = useState(false);
	const [isMenuOpen, setIsMenuOpen] = useState(false);

	useEffect(() => {
		const handleScroll = () => {
			setIsScrolled(window.scrollY > 20);
		};
		window.addEventListener("scroll", handleScroll);
		return () => window.removeEventListener("scroll", handleScroll);
	}, []);

	return (
		<div
			className={cn(
				"fixed top-0 left-0 right-0 z-50 transition-all duration-300 ease-in-out",
				isScrolled && "pt-4", // Add padding to the container when scrolled
			)}
		>
			<header
				className={cn(
					"glass transition-all duration-300 ease-in-out relative",
					isScrolled
						? "mx-auto max-w-4xl rounded-lg border shadow-soft" // Contained width, rounded pill shape
						: "border-b border-border", // Full width, only bottom border
				)}
			>
				<div className="container-width flex h-16 items-center justify-between">
					<div className="flex items-center gap-2">
						<div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center shadow-sm">
							<Calendar className="w-4 h-4 text-primary-foreground" />
						</div>
						<h1 className="text-lg font-bold tracking-tighter">CalendarAI</h1>
					</div>
					
					{/* Desktop Navigation */}
					<nav className="hidden md:flex items-center gap-6 text-sm font-medium">
						<a href="#features" className="text-muted-foreground hover:text-foreground transition-colors">Features</a>
						<a href="#testimonials" className="text-muted-foreground hover:text-foreground transition-colors">Testimonials</a>
					</nav>
					<Button onClick={loginAction} className="hidden md:flex">
						Get Started
						<ArrowRight className="w-4 h-4 ml-2" />
					</Button>

					{/* Mobile Menu Button */}
					<div className="md:hidden">
						<Button onClick={() => setIsMenuOpen(!isMenuOpen)} variant="ghost" size="icon">
							{isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
						</Button>
					</div>
				</div>

				{/* Mobile Menu Dropdown */}
				{isMenuOpen && (
					<div className="md:hidden absolute top-full left-0 right-0 p-4">
						<div className="bg-background border rounded-2xl shadow-lg p-4 space-y-4 animate-in fade-in-20">
							<nav className="flex flex-col gap-4 text-center">
								<a href="#features" onClick={() => setIsMenuOpen(false)} className="text-muted-foreground hover:text-foreground transition-colors py-2">Features</a>
								<a href="#testimonials" onClick={() => setIsMenuOpen(false)} className="text-muted-foreground hover:text-foreground transition-colors py-2">Testimonials</a>
							</nav>
							<Button onClick={loginAction} className="w-full">
								Get Started
								<ArrowRight className="w-4 h-4 ml-2" />
							</Button>
						</div>
					</div>
				)}
			</header>
		</div>
	);
};


// Hero Section with a clear value proposition
const HeroSection = ({ loginAction }: { loginAction: () => void }) => (
	<section className="pt-32 pb-20 md:pt-40 md:pb-32">
		<div className="container-width grid md:grid-cols-2 gap-12 items-center">
			<div className="space-y-6 text-center md:text-left">
				<h1 className="text-4xl md:text-6xl font-bold tracking-tighter animate-in">
					Turn any text into a structured calendar
				</h1>
				<p className="text-lg text-muted-foreground max-w-xl mx-auto md:mx-0 animate-in" style={{ animationDelay: "100ms" }}>
					CalendarAI uses AI to parse your notes, emails, and documents, automatically creating organized events in your Google Calendar.
				</p>
				<div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start animate-in" style={{ animationDelay: "200ms" }}>
					<Button onClick={loginAction} size="lg" className="h-12 text-base">
						Get Started for Free
					</Button>
					<Button variant="outline" size="lg" className="h-12 text-base">
						Learn More
					</Button>
				</div>
			</div>
			<div className="w-full h-64 md:h-96 bg-muted rounded-2xl border flex items-center justify-center fade-in-on-scroll">
				<p className="text-muted-foreground">
					[Clean Illustration / Screenshot Mockup]
				</p>
			</div>
		</div>
	</section>
);

// Features Section in a grid layout
const FeaturesSection = () => (
	<section id="features" className="py-20">
		<div className="container-width">
			<div className="text-center space-y-3 mb-12">
				<h2 className="text-3xl font-bold fade-in-on-scroll">Powerful Features, Effortless Scheduling</h2>
				<p className="text-muted-foreground max-w-2xl mx-auto fade-in-on-scroll" style={{ animationDelay: "100ms" }}>
					From messy notes to perfectly planned events, see how CalendarAI can streamline your workflow.
				</p>
			</div>
			<div className="grid md:grid-cols-3 gap-8">
				<FeatureCard
					icon={<Zap className="w-6 h-6 text-primary" />}
					title="AI-Powered Parsing"
					description="Our smart AI understands natural language to extract event details like titles, dates, times, and attendees."
				/>
				<FeatureCard
					icon={<Calendar className="w-6 h-6 text-primary" />}
					title="Direct Google Calendar Sync"
					description="Seamlessly create and update events in your primary or shared Google Calendars without leaving the app."
				/>
				<FeatureCard
					icon={<Check className="w-6 h-6 text-primary" />}
					title="Secure & Private"
					description="Your data is your own. We use secure API key management and never store your event content."
				/>
			</div>
		</div>
	</section>
);

const FeatureCard = ({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) => (
	<Card className="rounded-2xl shadow-soft fade-in-on-scroll">
		<CardHeader className="flex flex-row items-start gap-4 space-y-0">
			<div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
				{icon}
			</div>
			<CardTitle className="text-lg font-semibold pt-3">{title}</CardTitle>
		</CardHeader>
		<CardContent>
			<p className="text-muted-foreground">{description}</p>
		</CardContent>
	</Card>
);

// Testimonials Section
const TestimonialsSection = () => (
	<section id="testimonials" className="py-20">
		<div className="container-width">
			<div className="text-center space-y-3 mb-12">
				<h2 className="text-3xl font-bold fade-in-on-scroll">Loved by Professionals</h2>
				<p className="text-muted-foreground fade-in-on-scroll" style={{ animationDelay: "100ms" }}>See what our users are saying about CalendarAI.</p>
			</div>
			<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
				<TestimonialCard
					quote="This app is a game-changer. I've saved hours of manual data entry for my project timelines."
					author="Alice L."
					role="Project Manager"
				/>
				<TestimonialCard
					quote="Finally, a tool that understands my messy meeting notes and turns them into actual calendar events."
					author="Mark R."
					role="Freelance Consultant"
				/>
				<TestimonialCard
					quote="The Google Calendar integration is seamless. I can manage my team's schedule from a single source of truth."
					author="Samantha C."
					role="Team Lead"
				/>
			</div>
		</div>
	</section>
);

const TestimonialCard = ({ quote, author, role }: { quote: string, author: string, role: string }) => (
	<Card className="rounded-2xl shadow-soft fade-in-on-scroll">
		<CardContent className="pt-6">
			<p className="mb-4">"{quote}"</p>
			<div className="flex items-center gap-3">
				<div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
					<span className="font-bold">{author.charAt(0)}</span>
				</div>
				<div>
					<p className="font-semibold">{author}</p>
					<p className="text-sm text-muted-foreground">{role}</p>
				</div>
			</div>
		</CardContent>
	</Card>
);

// Minimal Footer
const Footer = () => (
	<footer className="py-12 border-t">
		<div className="container-width flex flex-col md:flex-row justify-between items-center gap-6">
			<div className="flex items-center gap-2">
				<div className="w-8 h-8 bg-foreground rounded-lg flex items-center justify-center">
					<Calendar className="w-4 h-4 text-background" />
				</div>
				<p className="text-sm text-muted-foreground">&copy; {new Date().getFullYear()} CalendarAI. All rights reserved.</p>
			</div>
			<div className="flex items-center gap-6 text-sm font-medium">
				<a href="#" className="text-muted-foreground hover:text-foreground">Privacy</a>
				<a href="#" className="text-muted-foreground hover:text-foreground">Terms</a>
			</div>
		</div>
	</footer>
);
