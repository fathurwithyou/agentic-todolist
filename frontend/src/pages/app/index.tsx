import ApiKeyManagementCard from "@/features/api-key-management/components/api-key-management-card";
import LoginCard from "@/features/auth/components/login-card";
import TextToCalendarCard from "@/features/text-to-calendar/components/text-to-calendar-card";
import { SystemPromptManagementCard } from "@/features/system-prompt/components/system-prompt-management-card";
import Header from "@/shared/components/header";
import {
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@/shared/components/ui/tabs";
import { useAuth } from "@/shared/hooks/use-auth";
import { Calendar, Key, Settings } from "lucide-react";

export default function AppPages() {
	const { isAuthenticated, isLoading } = useAuth();

	if (isLoading) {
		return (
			<div className="min-h-screen flex items-center justify-center">
				<div className="animate-pulse">
					<div className="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center">
						<Calendar className="w-6 h-6 text-primary" />
					</div>
				</div>
			</div>
		);
	}

	if (!isAuthenticated) {
		return <LoginCard />;
	}

	return (
		<div className="min-h-screen">
			<Header />
			
			<main className="container-width pb-20">
				<div className="animate-in">
					<Tabs defaultValue="convert" className="w-full space-y-8">
						<TabsList className="glass w-full sm:w-auto p-1 rounded-lg">
							<TabsTrigger value="convert" className="gap-2 data-[state=active]:shadow-sm">
								<Calendar className="w-4 h-4" />
								<span className="hidden sm:inline">Convert</span>
								<span className="sm:hidden">AI</span>
							</TabsTrigger>
							<TabsTrigger value="apikeys" className="gap-2 data-[state=active]:shadow-sm">
								<Key className="w-4 h-4" />
								<span className="hidden sm:inline">API Keys</span>
								<span className="sm:hidden">Keys</span>
							</TabsTrigger>
							<TabsTrigger value="settings" className="gap-2 data-[state=active]:shadow-sm">
								<Settings className="w-4 h-4" />
								<span className="hidden sm:inline">Settings</span>
								<span className="sm:hidden">Settings</span>
							</TabsTrigger>
						</TabsList>

						<TabsContent value="convert" className="space-y-6 animate-in">
							<div className="grid gap-6">
								<div className="space-y-2">
									<h2 className="text-2xl font-semibold tracking-tight">AI Text to Calendar</h2>
									<p className="text-muted-foreground">
										Transform your text into calendar events automatically using AI
									</p>
								</div>
								<TextToCalendarCard />
							</div>
						</TabsContent>

						<TabsContent value="apikeys" className="space-y-6 animate-in">
							<div className="grid gap-6">
								<div className="space-y-2">
									<h2 className="text-2xl font-semibold tracking-tight">API Key Management</h2>
									<p className="text-muted-foreground">
										Configure your AI provider API keys for text processing
									</p>
								</div>
								<ApiKeyManagementCard />
							</div>
						</TabsContent>

						<TabsContent value="settings" className="space-y-6 animate-in">
							<div className="grid gap-6">
								<div className="space-y-2">
									<h2 className="text-2xl font-semibold tracking-tight">Settings</h2>
									<p className="text-muted-foreground">
										Customize your system prompt and preferences
									</p>
								</div>
								<SystemPromptManagementCard />
							</div>
						</TabsContent>
					</Tabs>
				</div>
			</main>
		</div>
	);
}