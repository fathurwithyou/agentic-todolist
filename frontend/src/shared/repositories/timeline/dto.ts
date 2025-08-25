import z from "zod";
import type { CalendarEvent } from "../../types";

export type GetTimelineProvidersResponse = {
	available_providers: string[];
	provider_models: {
		[provider: string]: string[];
	};
};

export const PreviewTimelineSchema = z.object({
	timeline_text: z.string().min(1),
	flexible: z.boolean(),
	llm_provider: z.string().min(1),
	llm_model: z.string().min(1),
});

export type PreviewTimelineRequest = z.infer<typeof PreviewTimelineSchema>;

export type PreviewTimelineResponse = {
  processing_time_ms: number;
  total_events: number;
  used_model: string;
  used_provider: string;
	parsed_events: CalendarEvent[];
};

export const CreateEventsFromTimelineSchema = z.object({
	events: z.array(
		z.object({
			title: z.string().min(1),
			description: z.string().min(1),
			start_date: z.string().min(1),
			end_date: z.string().min(1),
			start_time: z.string().nullable(),
			end_time: z.string().nullable(),
			attendees: z.array(z.email()),
			location: z.string().nullable(),
			all_day: z.boolean(),
		}),
	),
});

export type CreateEventsFromTimelineRequest = z.infer<
	typeof CreateEventsFromTimelineSchema
>;
