import {
	type CreateEventsFromTimelineRequest,
	CreateEventsFromTimelineSchema,
} from "@/shared/repositories/timeline/dto";
import { useCreateEventsFromTimelineMutation } from "@/shared/repositories/timeline/query";
import { zodResolver } from "@hookform/resolvers/zod";
import { useFieldArray, useForm } from "react-hook-form";
import { toast } from "sonner";

export const useCreateEventsFromTimelineForm = () => {
	const form = useForm<CreateEventsFromTimelineRequest>({
		resolver: zodResolver(CreateEventsFromTimelineSchema),
		defaultValues: {
			events: [],
			target_calendar_id: "primary",
		},
	});

	const {
		mutate: createEventsFromTimeline,
		isPending: isCreateEventsFromTimelinePending,
	} = useCreateEventsFromTimelineMutation();

	const onSubmitHandler = form.handleSubmit((data) => {
		createEventsFromTimeline(data, {
			onSuccess: () => {
				toast.success(`Successfully created ${data.events.length} events`);
				form.reset();
			},
			onError: (err) => {
				toast.error(err.message || "Failed to create events");
			},
		});
	});

	const eventsFieldArray = useFieldArray({
		control: form.control,
		name: "events",
	});

	return {
		...form,
		eventsFieldArray,
		onSubmitHandler,
		isCreateEventsFromTimelinePending,
	};
};
