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

export default function AppPages() {
	const { isAuthenticated, isLoading } = useAuth();

	if (isLoading) {
		return null;
	}

	if (!isAuthenticated) {
		return <LoginCard />;
	}

	return (
		<div className="min-h-screen bg-background py-20 px-4">
			<div className="max-w-4xl mx-auto space-y-6">
				<Header />

				<Tabs defaultValue="convert" className="w-full">
					<TabsList className="flex items-center justify-start flex-wrap h-auto space-y-1 w-full">
						<TabsTrigger value="convert" className="font-manrope">
							AI Text to Calendar
						</TabsTrigger>
						<TabsTrigger value="apikeys" className="font-manrope">
							API Keys
						</TabsTrigger>
						<TabsTrigger value="settings" className="font-manrope">
							Settings
						</TabsTrigger>
					</TabsList>

					<TabsContent value="convert" className="space-y-4">
						<TextToCalendarCard />
					</TabsContent>

					<TabsContent value="apikeys" className="space-y-4">
						<ApiKeyManagementCard />
					</TabsContent>

					<TabsContent value="settings" className="space-y-4">
						<SystemPromptManagementCard />
					</TabsContent>
				</Tabs>
			</div>
		</div>
	);
}
