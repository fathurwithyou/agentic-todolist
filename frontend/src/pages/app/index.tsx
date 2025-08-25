import ApiKeyManagementCard from "@/features/api-key-management/components/api-key-management-card";
import LoginCard from "@/features/auth/components/login-card";
import MyCalendarCard from "@/features/my-calendars/components/my-calendar-card";
import TextToCalendarCard from "@/features/text-to-calendar/components/text-to-calendar-card";
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
						<TabsTrigger value="calendars" className="font-manrope">
							My Calendars
						</TabsTrigger>
						<TabsTrigger value="apikeys" className="font-manrope">
							API Keys
						</TabsTrigger>
					</TabsList>

					<TabsContent value="convert" className="space-y-4">
						<TextToCalendarCard />
					</TabsContent>

					<TabsContent value="calendars" className="space-y-4">
						<MyCalendarCard />
					</TabsContent>

					<TabsContent value="apikeys" className="space-y-4">
						<ApiKeyManagementCard />
					</TabsContent>
				</Tabs>
			</div>
		</div>
	);
}
