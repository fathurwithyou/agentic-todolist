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
		<div className="rounded-xl border border-green-600/20 bg-green-50/50 dark:bg-green-950/10 p-6 space-y-4 transition-all duration-200">
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-3">
					<div className="w-9 h-9 rounded-xl bg-green-600/10 dark:bg-green-400/10 flex items-center justify-center">
						<Check className="w-4.5 h-4.5 text-green-600 dark:text-green-400" />
					</div>
					<div>
						<h3 className="font-medium text-foreground">Preview Events</h3>
						<p className="text-sm text-muted-foreground">
							{events.length} event{events.length !== 1 ? 's' : ''} ready to add
						</p>
					</div>
				</div>
			</div>
			
			<div className="space-y-3 max-h-96 overflow-y-auto pr-2">
				{events.map((event, index) => (
					<Card key={index} className="border-border/40 shadow-none hover:shadow-soft transition-all duration-150">
						<CardHeader className="pb-3 px-5 pt-5">
							<CardTitle className="text-base flex items-center gap-2 font-medium">
								<CalendarIcon className="w-4 h-4 text-primary/60" />
								{event.title}
							</CardTitle>
							{event.description && (
								<CardDescription className="text-sm mt-1.5 text-muted-foreground">
									{event.description}
								</CardDescription>
							)}
						</CardHeader>
						<CardContent className="space-y-2.5 text-sm px-5 pb-5">
							<div className="flex items-center gap-2.5 text-muted-foreground">
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
								<div className="flex items-center gap-2.5 text-muted-foreground">
									<MapPin className="w-3.5 h-3.5" />
									<span>{event.location}</span>
								</div>
							)}
							
							{event.attendees && event.attendees.length > 0 && (
								<div className="flex items-center gap-2.5 text-muted-foreground">
									<Users className="w-3.5 h-3.5" />
									<span>{event.attendees.join(", ")}</span>
								</div>
							)}
						</CardContent>
					</Card>
				))}
			</div>
			
			<div className="flex gap-3 pt-3">
				<Button 
					variant="outline" 
					onClick={onCancel}
					className="flex-1 transition-all duration-150 hover:bg-muted/50"
				>
					Cancel
				</Button>
				<Button
					onClick={onSubmitHandler}
					disabled={isCreateEventsFromTimelinePending}
					className="flex-1 transition-all duration-150"
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