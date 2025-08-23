import "@/shared/styles/globals.css";
import { Button } from "@/shared/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import { Toaster } from "@/shared/components/ui/sonner";
import {
	QueryClient,
	QueryClientProvider,
	useMutation,
} from "@tanstack/react-query";
import { Brain, Calendar, Sparkles } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Input } from "./shared/components/ui/input";
import { Label } from "./shared/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "./shared/components/ui/select";
import { Textarea } from "./shared/components/ui/textarea";

const queryClient = new QueryClient();

function ReactQueryProvider({ children }: { children: React.ReactNode }) {
	return (
		<QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
	);
}

function Providers({ children }: { children: React.ReactNode }) {
	return (
		<ReactQueryProvider>
			{children}
			<Toaster richColors />
		</ReactQueryProvider>
	);
}

function Layout({ children }: { children: React.ReactNode }) {
	return <Providers>{children}</Providers>;
}

export default function AppWrapper() {
	return (
		<Layout>
			<App />
		</Layout>
	);
}

function App() {
	const [selectedProvider, setSelectedProvider] = useState<string>("");
	const [apiKey, setApiKey] = useState("");
	const [textInput, setTextInput] = useState("");
	const [isProcessing, setIsProcessing] = useState(false);

	const aiProviders = [
		{
			id: "openai",
			name: "OpenAI",
			description: "GPT-4 and GPT-3.5 models",
			placeholder: "sk-...",
		},
		{
			id: "gemini",
			name: "Google Gemini",
			description: "Gemini Pro and Ultra models",
			placeholder: "AIza...",
		},
		{
			id: "claude",
			name: "Anthropic Claude",
			description: "Claude 3 Opus, Sonnet, and Haiku",
			placeholder: "sk-ant-...",
		},
	];

	const handleProcessText = async () => {
		setIsProcessing(true);
		await new Promise((resolve) => setTimeout(resolve, 2000));
		setIsProcessing(false);
	};

	const handleProviderChange = (providerId: string) => {
		setSelectedProvider(providerId);
		setApiKey("");
	};

	const selectedProviderInfo = aiProviders.find(
		(p) => p.id === selectedProvider,
	);

	const searchParams = new URLSearchParams(window.location.search);
	const token = searchParams.get("token");

	if (token) {
		localStorage.setItem("token", token);
		window.location.href = "/";
	}

	const isLogin = token || localStorage.getItem("token");

	if (!isLogin) {
		return <LoginCard />;
	}

	return (
		<div className="min-h-screen bg-background flex items-center justify-center p-4">
			<div className="w-full max-w-2xl space-y-6">
				{/* Hero Header */}
				<div className="text-center space-y-4">
					<div className="mx-auto w-20 h-20 bg-accent rounded-full flex items-center justify-center">
						<Calendar className="w-10 h-10 text-accent-foreground" />
					</div>
					<div>
						<h1 className="text-4xl font-bold font-geist mb-2">CalendarAI</h1>
						<p className="text-xl text-muted-foreground font-manrope">
							Transform your text into calendar events automatically
						</p>
					</div>
				</div>

				{/* Main Card */}
				<Card className="w-full">
					<CardHeader>
						<CardTitle className="flex items-center justify-center font-geist text-xl">
							<Sparkles className="w-6 h-6 mr-2 text-accent" />
							Convert Text to Calendar Events
						</CardTitle>
						<CardDescription className="text-center font-manrope">
							Choose your AI provider, add your API key, and paste your text to
							get started
						</CardDescription>
					</CardHeader>
					<CardContent className="space-y-6">
						{/* AI Provider Selection */}
						<div className="space-y-3">
							<Label
								htmlFor="provider-select"
								className="flex items-center font-manrope"
							>
								<Brain className="w-4 h-4 mr-2" />
								AI Provider
							</Label>
							<Select
								value={selectedProvider}
								onValueChange={handleProviderChange}
							>
								<SelectTrigger className="font-manrope">
									<SelectValue placeholder="Select an AI provider..." />
								</SelectTrigger>
								<SelectContent>
									{aiProviders.map((provider) => (
										<SelectItem
											key={provider.id}
											value={provider.id}
											className="font-manrope"
										>
											<div className="flex flex-col">
												<span className="font-medium">{provider.name}</span>
												<span className="text-xs text-muted-foreground">
													{provider.description}
												</span>
											</div>
										</SelectItem>
									))}
								</SelectContent>
							</Select>
						</div>

						{/* API Key Input */}
						{selectedProvider && (
							<div className="space-y-3">
								<Label htmlFor="api-key" className="font-manrope">
									{selectedProviderInfo?.name} API Key
								</Label>
								<Input
									id="api-key"
									type="password"
									placeholder={
										selectedProviderInfo?.placeholder || "Enter your API key..."
									}
									value={apiKey}
									onChange={(e) => setApiKey(e.target.value)}
									className="font-manrope"
								/>
								<p className="text-xs text-muted-foreground font-manrope">
									Your API key is stored securely and never shared
								</p>
							</div>
						)}

						{/* Text Input */}
						<div className="space-y-3">
							<Label htmlFor="text-input" className="font-manrope">
								Event Text
							</Label>
							<Textarea
								id="text-input"
								placeholder="Example: Team meeting tomorrow at 10am in conference room A with Alice and Bob. Also schedule project review on Friday at 2pm online with the manager..."
								value={textInput}
								onChange={(e) => setTextInput(e.target.value)}
								rows={6}
								className="font-manrope"
							/>
						</div>

						{/* Process Button */}
						<Button
							onClick={handleProcessText}
							disabled={
								!textInput.trim() ||
								!selectedProvider ||
								!apiKey ||
								isProcessing
							}
							className="w-full bg-accent hover:bg-accent/90 text-accent-foreground font-manrope"
							size="lg"
						>
							{isProcessing ? (
								<>
									<div className="w-4 h-4 mr-2 border-2 border-accent-foreground/30 border-t-accent-foreground rounded-full animate-spin" />
									Processing with {selectedProviderInfo?.name}...
								</>
							) : (
								<>
									<Calendar className="w-4 h-4 mr-2" />
									Convert to Calendar Events
								</>
							)}
						</Button>

						{/* Status Message */}
						{selectedProvider && apiKey && (
							<div className="flex items-center justify-center space-x-2 p-3 bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800 rounded-lg">
								<div className="w-2 h-2 bg-green-500 rounded-full" />
								<span className="text-sm text-green-700 dark:text-green-300 font-manrope">
									Ready to process with {selectedProviderInfo?.name}
								</span>
							</div>
						)}
					</CardContent>
				</Card>
			</div>
		</div>
	);
}

function LoginCard() {
	const { mutate, isPending } = useMutation({
		mutationFn: async () => {
			return window.location.assign("/api/v1/auth/google");
		},
	});

	const handleGoogleLogin = () => {
		mutate(undefined, {
			onError: (error) => {
				toast.error("Failed to login with Google", {
					description: String(error),
				});
			},
		});
	};

	return (
		<div className="min-h-screen bg-background flex items-center justify-center p-4">
			<Card className="w-full max-w-md">
				<CardHeader className="text-center space-y-4">
					<div className="mx-auto w-16 h-16 bg-accent rounded-full flex items-center justify-center">
						<Calendar className="w-8 h-8" />
					</div>
					<div>
						<CardTitle className="text-2xl font-geist">CalendarAI</CardTitle>
						<CardDescription className="font-manrope">
							Transform your text into calendar events automatically
						</CardDescription>
					</div>
				</CardHeader>
				<CardContent className="space-y-4">
					<Button
						onClick={handleGoogleLogin}
						className="w-full"
						size="lg"
						disabled={isPending}
					>
						<svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
							<title>Google</title>
							<path
								fill="currentColor"
								d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
							/>
							<path
								fill="currentColor"
								d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
							/>
							<path
								fill="currentColor"
								d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
							/>
							<path
								fill="currentColor"
								d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
							/>
						</svg>
						Continue with Google
					</Button>
					<p className="text-xs text-center">
						Sign in to start converting your text to calendar events
					</p>
				</CardContent>
			</Card>
		</div>
	);
}
