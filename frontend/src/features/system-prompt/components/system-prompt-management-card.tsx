import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "../../../shared/components/ui/card";
import { SystemPromptForm } from "./system-prompt-form";

export function SystemPromptManagementCard() {
	return (
		<Card>
			<CardHeader>
				<CardTitle>System Prompt</CardTitle>
				<CardDescription>
					Set up general knowledge and context that will be used when parsing your timeline. 
					This can include contact information, common locations, and other references you frequently use.
				</CardDescription>
			</CardHeader>
			<CardContent>
				<SystemPromptForm />
			</CardContent>
		</Card>
	);
}