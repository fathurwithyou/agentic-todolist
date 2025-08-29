import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import type { Calendar, CalendarEvent } from "@/shared/types";
import { useState } from "react";
import PreviewTimelineCard from "./preview-timeline-card";
import PreviewTimelineForm from "./preview-timeline-form";
import { Sparkles } from "lucide-react";

export default function TextToCalendarCard() {
	const [createdEvents, setCreatedEvents] = useState<CalendarEvent[]>([]);
	const [selectedTargetCalendarId, setSelectedTargetCalendarId] = useState<
		Calendar["id"]
	>("primary");

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
						setCreatedEvents(events);
						setSelectedTargetCalendarId(targetCalendarId);
					}}
				/>

				{createdEvents.length > 0 && (
					<div className="animate-in">
						<PreviewTimelineCard
							events={createdEvents}
							targetCalendarId={selectedTargetCalendarId}
							onCancel={() => {
								setCreatedEvents([]);
								setSelectedTargetCalendarId("primary");
							}}
						/>
					</div>
				)}
			</CardContent>
		</Card>
	);
}