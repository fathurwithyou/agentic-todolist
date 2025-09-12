import {
	type PreviewTimelineRequest,
	PreviewTimelineSchema,
} from "@/shared/repositories/timeline/dto";
import { usePreviewTimelineMutation } from "@/shared/repositories/timeline/query";
import type { Calendar, CalendarEvent } from "@/shared/types";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, useWatch } from "react-hook-form";
import { toast } from "sonner";

type Props = {
	onSuccess: (
		events: CalendarEvent[],
		targetCalendarId: Calendar["id"],
	) => void;
};

export const usePreviewTimelineForm = ({ onSuccess }: Props) => {
	const { mutate: previewTimeline, isPending: isPreviewTimelinePending } =
		usePreviewTimelineMutation();

	const form = useForm<PreviewTimelineRequest>({
		resolver: zodResolver(PreviewTimelineSchema),
		defaultValues: {
			flexible: false,
			llm_provider: undefined,
			llm_model: "gemini-2.5-flash", // TODO: change to undefined when api models endpoint is fixed
			timeline_text: "",
			target_calendar_id: "primary",
		},
	});

	const [llmProvider] = useWatch({
		control: form.control,
		name: ["llm_provider"],
	});

	const onSubmitHandler = form.handleSubmit((data) => {
		previewTimeline(data, {
			onSuccess: (res) => {
				toast.success(
					`Successfully parsed ${res.total_events} events in ${res.processing_time_ms}ms using ${res.used_provider} (${res.used_model})`,
					{ duration: 5000 },
				);
				onSuccess(res.parsed_events, data.target_calendar_id);
			},
			onError: (err) => {
				console.error("Preview Timeline Error:", err);
				toast.error(err.message || "Failed to preview timeline");
			},
		});
	});

	return {
		...form,
		llmProvider,
		onSubmitHandler,
		isPreviewTimelinePending,
	};
};
