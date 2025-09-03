import { Button } from "@/shared/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import { Form } from "@/shared/components/ui/form";
import { CheckSquare, Sparkles } from "lucide-react";
import { useCreateTasksFromTimelineForm } from "../hooks/use-create-tasks-from-timeline-form";
import PreviewTasksCard from "./preview-tasks-card";
import PreviewTasksForm from "./preview-tasks-form";

export default function TextToTasksCard() {
	const form = useCreateTasksFromTimelineForm();

	return (
		<Card className="border-0 shadow-soft overflow-visible relative">
			<CardHeader className="border-b border-border/40 bg-gradient-to-r from-muted/10 to-muted/20 px-8 py-6 relative">
				<div className="flex items-start justify-between">
					<div className="space-y-1.5">
						<CardTitle className="flex items-center gap-2.5 text-2xl font-medium">
							<CheckSquare className="w-5 h-5 text-primary/70" />
							Convert Text to Tasks
						</CardTitle>
						<CardDescription className="text-muted-foreground">
							Paste your timeline text and let AI create tasks in Google Tasks
						</CardDescription>
					</div>
				</div>
			</CardHeader>

			<CardContent className="px-8 py-6 space-y-6">
				<Form {...form}>
					<form className="space-y-6">
						<PreviewTasksForm />

						{form.getValues("tasks")?.length > 0 && (
							<PreviewTasksCard />
						)}
					</form>
				</Form>
			</CardContent>
		</Card>
	);
}