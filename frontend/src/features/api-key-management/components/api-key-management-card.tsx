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
		<Card className="overflow-hidden">
			<CardHeader className="border-b border-border/50 bg-muted/30">
				<CardTitle>API Configuration</CardTitle>
				<CardDescription>
					Connect your AI provider accounts to enable text processing
				</CardDescription>
			</CardHeader>
			<CardContent className="space-y-6 p-6">
				<ApiKeyStatusCard />
				<ManageApiKeyForm />
				<HowToGetApiKeysCard />
			</CardContent>
		</Card>
	);
}