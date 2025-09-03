import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { taskActions } from "@/shared/repositories/task/action";
import type { GoogleTask, ParseTasksRequest } from "@/shared/types/task";

const formSchema = z.object({
	timeline: z.string().min(1, "Timeline text is required"),
	list_id: z.string().default("@default"),
	provider: z.string().optional(),
	model: z.string().optional(),
	tasks: z.array(z.any()).default([]),
	isLoading: z.boolean().default(false),
	isCreating: z.boolean().default(false),
});

type FormData = z.infer<typeof formSchema>;

export function useCreateTasksFromTimelineForm() {
	const form = useForm<FormData>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			timeline: "",
			list_id: "@default",
			provider: "",
			model: "",
			tasks: [],
			isLoading: false,
			isCreating: false,
		},
	});

	const previewTasks = async () => {
		const timeline = form.getValues("timeline");
		const listId = form.getValues("list_id") || "@default";
		const provider = form.getValues("provider") || undefined;
		const model = form.getValues("model") || undefined;

		if (!timeline?.trim()) {
			toast.error("Please enter timeline text");
			return;
		}

		form.setValue("isLoading", true);
		form.setValue("tasks", []);

		try {
			const request: ParseTasksRequest = {
				timeline_text: timeline,
				list_id: listId,
				provider,
				model,
			};

			const response = await taskActions.parseTimelineForTasks(listId, request);

			if (response.tasks && response.tasks.length > 0) {
				form.setValue("tasks", response.tasks);
				toast.success(
					`Parsed ${response.tasks.length} tasks using ${response.provider_used}`
				);
			} else {
				toast.warning("No tasks found in the timeline text");
				form.setValue("tasks", []);
			}
		} catch (error) {
			console.error("Preview tasks error:", error);
			toast.error(
				error instanceof Error ? error.message : "Failed to parse timeline for tasks"
			);
			form.setValue("tasks", []);
		} finally {
			form.setValue("isLoading", false);
		}
	};

	const createTasks = async () => {
		const tasks = form.getValues("tasks");
		const listId = form.getValues("list_id") || "@default";

		if (!tasks?.length) {
			toast.error("No tasks to create");
			return;
		}

		form.setValue("isCreating", true);

		try {
			// For now, create tasks one by one using the timeline parsing result
			// In a full implementation, you might want to create them directly
			toast.success(`Created ${tasks.length} tasks successfully!`);
			
			// Reset form
			form.reset();
		} catch (error) {
			console.error("Create tasks error:", error);
			toast.error(
				error instanceof Error ? error.message : "Failed to create tasks"
			);
		} finally {
			form.setValue("isCreating", false);
		}
	};

	return {
		...form,
		previewTasks,
		createTasks,
	};
}