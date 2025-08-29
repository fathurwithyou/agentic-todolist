import { Button } from "@/shared/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import { useCreateEventsFromTimelineMutation } from "@/shared/repositories/timeline/query";
import type { Calendar, CalendarEvent } from "@/shared/types";
import { Calendar as CalendarIcon, MapPin, Users, Clock, Check } from "lucide-react";
import { toast } from "sonner";

type Props = {
	events: CalendarEvent[];
	targetCalendarId: Calendar["id"];
	onCancel: () => void;
};

export default function PreviewTimelineCard({
	events,
	targetCalendarId,
	onCancel,
}: Props) {
	const {
		mutate: createEventsFromTimeline,
		isPending: isCreateEventsFromTimelinePending,
	} = useCreateEventsFromTimelineMutation();

	const onSubmitHandler = () => {
		createEventsFromTimeline(
			{ events, target_calendar_id: targetCalendarId },
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
		<div className="rounded-xl border border-green-200 dark:border-green-900/50 bg-green-50 dark:bg-green-950/20 p-6 space-y-4">
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-2">
					<div className="w-8 h-8 rounded-lg bg-green-600/10 dark:bg-green-400/10 flex items-center justify-center">
						<Check className="w-4 h-4 text-green-600 dark:text-green-400" />
					</div>
					<div>
						<h3 className="font-semibold text-green-900 dark:text-green-100">Preview Events</h3>
						<p className="text-sm text-green-700 dark:text-green-400">
							{events.length} event{events.length !== 1 ? 's' : ''} ready to add
						</p>
					</div>
				</div>
			</div>
			
			<div className="space-y-3 max-h-96 overflow-y-auto pr-2">
				{events.map((event, index) => (
					<Card key={index} className="border-border/50">
						<CardHeader className="pb-3">
							<CardTitle className="text-base flex items-center gap-2">
								<CalendarIcon className="w-4 h-4 text-muted-foreground" />
								{event.title}
							</CardTitle>
							{event.description && (
								<CardDescription className="text-sm mt-1">
									{event.description}
								</CardDescription>
							)}
						</CardHeader>
						<CardContent className="space-y-2 text-sm">
							<div className="flex items-center gap-2 text-muted-foreground">
								<Clock className="w-3.5 h-3.5" />
								{event.start_date === event.end_date ? (
									<span>
										{new Date(event.start_date).toLocaleDateString("en-US", {
											weekday: "short",
											year: "numeric",
											month: "short",
											day: "numeric",
										})}
										{event.start_time && ` • ${event.start_time}`}
										{event.end_time && ` - ${event.end_time}`}
									</span>
								) : (
									<span>
										{new Date(event.start_date).toLocaleDateString("en-US", {
											month: "short",
											day: "numeric",
										})}
										{" - "}
										{new Date(event.end_date).toLocaleDateString("en-US", {
											month: "short",
											day: "numeric",
											year: "numeric",
										})}
									</span>
								)}
							</div>
							
							{event.location && (
								<div className="flex items-center gap-2 text-muted-foreground">
									<MapPin className="w-3.5 h-3.5" />
									<span>{event.location}</span>
								</div>
							)}
							
							{event.attendees && event.attendees.length > 0 && (
								<div className="flex items-center gap-2 text-muted-foreground">
									<Users className="w-3.5 h-3.5" />
									<span>{event.attendees.join(", ")}</span>
								</div>
							)}
						</CardContent>
					</Card>
				))}
			</div>
			
			<div className="flex gap-3 pt-2">
				<Button 
					variant="outline" 
					onClick={onCancel}
					className="flex-1"
				>
					Cancel
				</Button>
				<Button
					onClick={onSubmitHandler}
					disabled={isCreateEventsFromTimelinePending}
					className="flex-1"
				>
					{isCreateEventsFromTimelinePending ? (
						<div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
					) : (
						<>Add to Calendar</>
					)}
				</Button>
			</div>
		</div>
	);
}