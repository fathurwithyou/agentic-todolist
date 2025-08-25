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
		<Card>
			<CardHeader>
				<CardTitle>API Key Management</CardTitle>
				<CardDescription>
					Manage your AI provider API keys securely
				</CardDescription>
			</CardHeader>
			<CardContent className="space-y-4">
				<ApiKeyStatusCard />

				<ManageApiKeyForm />

				<HowToGetApiKeysCard />
			</CardContent>
		</Card>
	);
}
