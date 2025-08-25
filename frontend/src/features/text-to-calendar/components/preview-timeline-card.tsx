import { Button } from "@/shared/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardFooter,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import { useCreateEventsFromTimelineMutation } from "@/shared/repositories/timeline/query";
import type { CalendarEvent } from "@/shared/types";
import { LoaderCircle } from "lucide-react";
import { toast } from "sonner";

type Props = {
	events: CalendarEvent[];
	onCancel: () => void;
};

export default function PreviewTimelineCard({ events, onCancel }: Props) {
	const {
		mutate: createEventsFromTimeline,
		isPending: isCreateEventsFromTimelinePending,
	} = useCreateEventsFromTimelineMutation();

	const onSubmitHandler = () => {
		console.log("Creating Events:", events);

		createEventsFromTimeline(
			{ events },
			{
				onSuccess: () => {
					toast.success(`Successfully created ${events.length} events`);
					onCancel();
				},
				onError: (err) => {
					toast.error(err.message || "Failed to create events");
				},
			},
		);
	};

	return (
		<Card className="bg-accent text-accent-foreground">
			<CardHeader>
				<CardTitle>📋 Preview Events</CardTitle>
				<CardDescription>{events.length} events created</CardDescription>
			</CardHeader>
			<CardContent className="space-y-2">
				{events.map((event, index) => (
					// biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
					<Card key={index}>
						<CardHeader>
							<CardTitle>{event.title}</CardTitle>
							<CardDescription>{event.description}</CardDescription>
						</CardHeader>
						<CardContent className="text-sm">
							<p>
								<strong>Start:</strong>{" "}
								{new Date(event.start_date).toLocaleDateString("en-US", {
									year: "numeric",
									month: "long",
									day: "numeric",
								})}
							</p>
							<p>
								<strong>End:</strong>{" "}
								{new Date(event.end_date).toLocaleDateString("en-US", {
									year: "numeric",
									month: "long",
									day: "numeric",
								})}
							</p>
							{event.start_time && (
								<p>
									<strong>Start Time:</strong> {event.start_time}
								</p>
							)}
							{event.end_time && (
								<p>
									<strong>End Time:</strong> {event.end_time}
								</p>
							)}
							{event.location && (
								<p>
									<strong>Location:</strong> {event.location}
								</p>
							)}
							{event.attendees && event.attendees.length > 0 && (
								<p>
									<strong>Attendees:</strong> {event.attendees.join(", ")}
								</p>
							)}
						</CardContent>
					</Card>
				))}
			</CardContent>
			<CardFooter className="grid grid-cols-1 md:grid-cols-2 gap-2 w-full">
				<Button variant="outline" className="flex-1" onClick={onCancel}>
					Cancel
				</Button>
				<Button
					className="flex-1"
					onClick={onSubmitHandler}
					disabled={isCreateEventsFromTimelinePending}
				>
					{isCreateEventsFromTimelinePending && (
						<LoaderCircle className="animate-spin" />
					)}
					Add {events.length} Events to Calendar
				</Button>
			</CardFooter>
		</Card>
	);
}
