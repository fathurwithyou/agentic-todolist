import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import type { CalendarEvent } from "@/shared/types";
import { useState } from "react";
import PreviewTimelineCard from "./preview-timeline-card";
import PreviewTimelineForm from "./preview-timeline-form";

export default function TextToCalendarCard() {
	const [createdEvents, setCreatedEvents] = useState<CalendarEvent[]>([]);

	return (
		<Card>
			<CardHeader>
				<CardTitle>Convert Text to Calendar Events</CardTitle>
				<CardDescription>
					Select your AI provider and convert text to calendar events
				</CardDescription>
			</CardHeader>
			<CardContent className="space-y-4">
				<PreviewTimelineForm onSuccess={setCreatedEvents} />

				{createdEvents.length > 0 && (
					<PreviewTimelineCard
						events={createdEvents}
						onCancel={() => setCreatedEvents([])}
					/>
				)}
			</CardContent>
		</Card>
	);
}
