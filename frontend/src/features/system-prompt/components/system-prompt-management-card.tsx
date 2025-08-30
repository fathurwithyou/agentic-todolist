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
		<Card className="border-0 shadow-soft">
			<CardHeader className="border-b border-border/40 bg-muted/20 px-8 py-6">
				<div className="flex items-start gap-4">
					<div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
						<Settings2 className="w-5 h-5 text-primary/70" />
					</div>
					<div className="space-y-1.5">
						<CardTitle className="text-2xl font-medium">System Prompt Configuration</CardTitle>
						<CardDescription className="text-muted-foreground leading-relaxed">
							Define context and references that will be used when parsing your timelines.
							Include contacts, locations, and common abbreviations for better accuracy.
						</CardDescription>
					</div>
				</div>
			</CardHeader>
			<CardContent className="p-8">
				<SystemPromptForm />
			</CardContent>
		</Card>
	);
}