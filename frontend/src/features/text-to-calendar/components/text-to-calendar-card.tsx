import { Button } from "@/shared/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import { Form } from "@/shared/components/ui/form";
import { Check, Sparkles } from "lucide-react";
import { useCreateEventsFromTimelineForm } from "../hooks/use-create-events-from-timeline-form";
import PreviewTimelineCard from "./preview-timeline-card";
import PreviewTimelineForm from "./preview-timeline-form";

export default function TextToCalendarCard() {
	const form = useCreateEventsFromTimelineForm();

	return (
		<Card className="border-0 shadow-soft overflow-visible">
			<CardHeader className="border-b border-border/40 bg-gradient-to-r from-muted/10 to-muted/20 px-8 py-6">
				<div className="flex items-start justify-between">
					<div className="space-y-1.5">
						<CardTitle className="flex items-center gap-2.5 text-2xl font-medium">
							<Sparkles className="w-5 h-5 text-primary/70" />
							Convert Text to Events
						</CardTitle>
						<CardDescription className="text-muted-foreground">
							Paste your timeline text and let AI create calendar events
						</CardDescription>
					</div>
				</div>
			</CardHeader>
			<CardContent className="p-8 space-y-6">
				<PreviewTimelineForm
					onSuccess={(events, targetCalendarId) => {
						form.setValue("events", events);
						form.setValue("target_calendar_id", targetCalendarId);
					}}
				/>

				{form.eventsFieldArray.fields.length > 0 && (
					<Form {...form}>
						<form className="animate-in" onSubmit={form.onSubmitHandler}>
							<div className="rounded-xl border border-green-600/20 bg-green-50/50 dark:bg-green-950/10 p-6 space-y-4 transition-all duration-200">
								<div className="flex items-center justify-between">
									<div className="flex items-center gap-3">
										<div className="w-9 h-9 rounded-xl bg-green-600/10 dark:bg-green-400/10 flex items-center justify-center">
											<Check className="w-4.5 h-4.5 text-green-600 dark:text-green-400" />
										</div>
										<div>
											<h3 className="font-medium text-foreground">
												Preview Events
											</h3>
											<p className="text-sm text-muted-foreground">
												{form.eventsFieldArray.fields.length} event
												{form.eventsFieldArray.fields.length !== 1 ? "s" : ""}{" "}
												ready to add
											</p>
										</div>
									</div>
								</div>

								<div className="space-y-3">
									{form.eventsFieldArray.fields.map((event, idx) => (
										<PreviewTimelineCard key={event.id} idx={idx} />
									))}
								</div>

								<div className="flex gap-3 pt-3">
									<Button
										type="button"
										variant="outline"
										onClick={() => form.reset()}
										className="flex-1 transition-all duration-150 hover:bg-muted/50"
									>
										Cancel
									</Button>
									<Button
										type="submit"
										disabled={form.isCreateEventsFromTimelinePending}
										className="flex-1 transition-all duration-150"
									>
										{form.isCreateEventsFromTimelinePending ? (
											<div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
										) : (
											<>Add to Calendar</>
										)}
									</Button>
								</div>
							</div>
						</form>
					</Form>
				)}
			</CardContent>
		</Card>
	);
}
