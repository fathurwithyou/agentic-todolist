import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import ApiKeyStatusCard from "./api-key-status-card";
import HowToGetApiKeysCard from "./how-to-get-api-keys-card";
import ManageApiKeyForm from "./manage-api-key-form";

export default function ApiKeyManagementCard() {
	return (
		<Card className="border-0 shadow-soft">
			<CardHeader className="border-b border-border/40 bg-muted/20 px-8 py-6">
				<CardTitle className="text-2xl font-medium">API Configuration</CardTitle>
				<CardDescription className="text-muted-foreground mt-1">
					Connect your AI provider accounts to enable text processing
				</CardDescription>
			</CardHeader>
			<CardContent className="p-8 space-y-6">
				<ApiKeyStatusCard />
				<ManageApiKeyForm />
				<HowToGetApiKeysCard />
			</CardContent>
		</Card>
	);
}