
import ApiKeyManagementCard from "@/features/api-key-management/components/api-key-management-card";
import { SystemPromptManagementCard } from "@/features/system-prompt/components/system-prompt-management-card";
import TextToCalendarCard from "@/features/text-to-calendar/components/text-to-calendar-card";
import TextToTasksCard from "@/features/task-management/components/text-to-tasks-card";
import Header from "@/shared/components/header";
import {
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@/shared/components/ui/tabs";
import { useAuth } from "@/shared/hooks/use-auth";
import { Calendar, CheckSquare, Key, Settings } from "lucide-react";
import LandingPage from "../landing";
import LoginPage from "../login"; // Import the login page

export default function AppPages() {
	const { isAuthenticated, isLoading } = useAuth();
	const isLoginPage = window.location.pathname === '/login';

	if (isLoading) {
		return (
			<div className="min-h-screen flex items-center justify-center bg-background relative">
				<div 
					className="absolute inset-0 opacity-[0.3] pointer-events-none" 
					style={{
						backgroundImage: 'radial-gradient(circle, rgb(0 0 0 / 0.3) 1px, transparent 1px)',
						backgroundSize: '18px 18px'
					}}
				/>
				<div className="animate-pulse">
					<div className="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center">
						<Calendar className="w-6 h-6 text-primary" />
					</div>
				</div>
			</div>
		);
	}

	if (isLoginPage) {
		return <LoginPage />;
	}

	if (!isAuthenticated) {
		return <LandingPage />;
	}

	return (
		<div className="min-h-screen relative">
			<div 
				className="absolute inset-0 opacity-[0.3] pointer-events-none" 
				style={{
					backgroundImage: 'radial-gradient(circle, rgb(0 0 0 / 0.3) 1px, transparent 1px)',
					backgroundSize: '18px 18px'
				}}
			/>
			<Header />
			<main className="container-width pb-8">
				<div className="animate-in">
					<Tabs defaultValue="convert" className="w-full space-y-8">
						<TabsList className="glass w-full sm:w-auto p-1 rounded-md">
							<TabsTrigger value="convert" className="gap-2 data-[state=active]:shadow-sm">
								<Calendar className="w-4 h-4" />
								<span className="hidden sm:inline">Events</span>
								<span className="sm:hidden">Events</span>
							</TabsTrigger>
							<TabsTrigger value="tasks" className="gap-2 data-[state=active]:shadow-sm">
								<CheckSquare className="w-4 h-4" />
								<span className="hidden sm:inline">Tasks</span>
								<span className="sm:hidden">Tasks</span>
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
							<TextToCalendarCard />
						</TabsContent>

						<TabsContent value="tasks" className="space-y-6 animate-in">
							<TextToTasksCard />
						</TabsContent>

						<TabsContent value="apikeys" className="space-y-6 animate-in">
							<ApiKeyManagementCard />
						</TabsContent>

						<TabsContent value="settings" className="space-y-6 animate-in">
							<SystemPromptManagementCard />
						</TabsContent>
					</Tabs>
				</div>
			</main>
		</div>
	);
}