import { Button } from "@/shared/components/ui/button";
import { Checkbox } from "@/shared/components/ui/checkbox";
import {
	Form,
	FormControl,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
	FormDescription,
} from "@/shared/components/ui/form";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/shared/components/ui/select";
import { Textarea } from "@/shared/components/ui/textarea";
import { capitalize } from "@/shared/lib/string";
import { useGetListWritableCalendarsQuery } from "@/shared/repositories/calendar/query";
import { useGetTimelineProvidersQuery } from "@/shared/repositories/timeline/query";
import type { CalendarEvent } from "@/shared/types";
import type { Calendar } from "@/shared/types";
import { Sparkles, CalendarDays, Loader2 } from "lucide-react";
import { usePreviewTimelineForm } from "../hooks/use-preview-timeline-form";

type Props = {
	onSuccess: (
		events: CalendarEvent[],
		targetCalendarId: Calendar["id"],
	) => void;
};

export default function PreviewTimelineForm({ onSuccess }: Props) {
	const { data: listProvidersRes } = useGetTimelineProvidersQuery();
	const { onSubmitHandler, isPreviewTimelinePending, llmProvider, ...form } =
		usePreviewTimelineForm({ onSuccess });
	const { data: listWritableCalendarsRes } = useGetListWritableCalendarsQuery();

	return (
		<Form {...form}>
			<form className="space-y-6" onSubmit={onSubmitHandler}>
				<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
					<FormField
						control={form.control}
						name="llm_provider"
						render={({ field }) => (
							<FormItem>
								<FormLabel>AI Provider</FormLabel>
								<Select
									onValueChange={field.onChange}
									value={field.value}
									defaultValue={field.value}
								>
									<FormControl>
										<SelectTrigger>
											<SelectValue placeholder="Select a provider" />
										</SelectTrigger>
									</FormControl>
									<SelectContent>
										{listProvidersRes?.available_providers.map((provider) => (
											<SelectItem key={provider} value={provider}>
												{capitalize(provider)}
											</SelectItem>
										))}
									</SelectContent>
								</Select>
								<FormMessage />
							</FormItem>
						)}
					/>
					{llmProvider && (
						<FormField
							control={form.control}
							name="llm_model"
							render={({ field }) => (
								<FormItem>
									<FormLabel>Model</FormLabel>
									<Select
										onValueChange={field.onChange}
										value={field.value}
										defaultValue={field.value}
									>
										<FormControl>
											<SelectTrigger>
												<SelectValue placeholder="Select a model" />
											</SelectTrigger>
										</FormControl>
										<SelectContent>
											{listProvidersRes?.provider_models[llmProvider].map(
												(model) => (
													<SelectItem key={model} value={model}>
														{model}
													</SelectItem>
												),
											)}
										</SelectContent>
									</Select>
									<FormMessage />
								</FormItem>
							)}
						/>
					)}
				</div>
				
				<FormField
					control={form.control}
					name="target_calendar_id"
					render={({ field }) => (
						<FormItem>
							<FormLabel className="flex items-center gap-2">
								<CalendarDays className="w-4 h-4" />
								Target Calendar
							</FormLabel>
							<Select
								onValueChange={field.onChange}
								value={field.value}
								defaultValue={field.value}
							>
								<FormControl>
									<SelectTrigger>
										<SelectValue placeholder="Select target calendar" />
									</SelectTrigger>
								</FormControl>
								<SelectContent>
									<SelectItem value="primary">
										<span className="font-medium">Primary Calendar</span>
									</SelectItem>
									{listWritableCalendarsRes?.map((calendar) => (
										<SelectItem key={calendar.id} value={calendar.id}>
											{calendar.summary}
										</SelectItem>
									))}
								</SelectContent>
							</Select>
							<FormMessage />
						</FormItem>
					)}
				/>
				
				<FormField
					control={form.control}
					name="timeline_text"
					render={({ field }) => (
						<FormItem>
							<FormLabel>Timeline Text</FormLabel>
							<FormDescription>
								Paste your schedule, timeline, or list of events below
							</FormDescription>
							<FormControl>
								<Textarea
									placeholder="Example:&#10;&#10;Project Timeline:&#10;&#10;July 1-10: Submit proposal&#10;August 11 - Sept 2: Review period&#10;Sept 8 at 10:00 AM: Finalist announcement&#10;Oct 27 9:00-17:00: Final presentation Day 1&#10;Oct 28 13:30-15:30: Final presentation&#10;&#10;Meetings:&#10;July 15 at 2:00 PM: Coordination meeting&#10;July 20 10:30-12:00: Progress review&#10;&#10;Attendees: Fathur, Bimo, Guntara"
									className="min-h-[180px] font-mono text-xs"
									{...field}
								/>
							</FormControl>
							<FormMessage />
						</FormItem>
					)}
				/>
				
				<FormField
					control={form.control}
					name="flexible"
					render={({ field }) => (
						<FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-lg border border-border/50 p-4 bg-muted/30">
							<FormControl>
								<Checkbox
									checked={field.value}
									onCheckedChange={field.onChange}
								/>
							</FormControl>
							<div className="space-y-1 leading-none">
								<FormLabel>
									Flexible Parsing Mode
								</FormLabel>
								<FormDescription>
									Enable AI to better understand various text formats and natural language
								</FormDescription>
							</div>
						</FormItem>
					)}
				/>
				
				<Button
					type="submit"
					className="w-full h-11 gap-2"
					size="lg"
					disabled={isPreviewTimelinePending}
				>
					{isPreviewTimelinePending ? (
						<Loader2 className="h-5 w-5 animate-spin" />
					) : (
						<Sparkles className="h-5 w-5" />
					)}
					Generate Calendar Events
				</Button>
			</form>
		</Form>
	);
}