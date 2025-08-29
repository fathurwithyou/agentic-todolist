import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "../../../shared/components/ui/card";
import { SystemPromptForm } from "./system-prompt-form";
import { Settings2 } from "lucide-react";

export function SystemPromptManagementCard() {
	return (
		<Card className="overflow-hidden">
			<CardHeader className="border-b border-border/50 bg-muted/30">
				<div className="flex items-start gap-3">
					<div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
						<Settings2 className="w-5 h-5 text-primary" />
					</div>
					<div className="space-y-1">
						<CardTitle>System Prompt Configuration</CardTitle>
						<CardDescription>
							Define context and references that will be used when parsing your timelines.
							Include contacts, locations, and common abbreviations for better accuracy.
						</CardDescription>
					</div>
				</div>
			</CardHeader>
			<CardContent className="p-6">
				<SystemPromptForm />
			</CardContent>
		</Card>
	);
}