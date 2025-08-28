import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Button } from "../../../shared/components/ui/button";
import {
	Form,
	FormControl,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
} from "../../../shared/components/ui/form";
import { Textarea } from "../../../shared/components/ui/textarea";
import {
	useGetSystemPromptQuery,
	useSaveSystemPromptMutation,
} from "../../../shared/repositories/auth/query";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

const formSchema = z.object({
	system_prompt: z.string().min(1, "System prompt is required"),
});

type FormValues = z.infer<typeof formSchema>;

export function SystemPromptForm() {
	const queryClient = useQueryClient();
	const { data: systemPromptData, isLoading } = useGetSystemPromptQuery();
	const saveSystemPromptMutation = useSaveSystemPromptMutation();

	const form = useForm<FormValues>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			system_prompt: "",
		},
	});

	// Load existing system prompt when data is available
	useEffect(() => {
		if (systemPromptData?.system_prompt) {
			form.setValue("system_prompt", systemPromptData.system_prompt);
		}
	}, [systemPromptData, form]);

	async function onSubmit(values: FormValues) {
		try {
			await saveSystemPromptMutation.mutateAsync({
				system_prompt: values.system_prompt,
			});

			// Invalidate queries to refresh data
			queryClient.invalidateQueries({ queryKey: ["system-prompt"] });

			toast.success("System prompt saved successfully!");
		} catch (error) {
			toast.error("Failed to save system prompt. Please try again.");
			console.error("Save system prompt error:", error);
		}
	}

	const handleClear = () => {
		form.setValue("system_prompt", "");
	};

	if (isLoading) {
		return <div className="text-sm text-muted-foreground">Loading...</div>;
	}

	return (
		<Form {...form}>
			<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
				<FormField
					control={form.control}
					name="system_prompt"
					render={({ field }) => (
						<FormItem>
							<FormLabel>General Knowledge & Context</FormLabel>
							<FormControl>
								<Textarea
									placeholder="Example:&#10;Fathur: fathurwithyou@gmail.com&#10;Office: Jakarta, Menara BCA 15th floor&#10;Meeting Room A: 2nd floor&#10;Team Lead: John (john@company.com)&#10;Regular Meeting: Every Monday 10 AM"
									className="min-h-[150px]"
									{...field}
								/>
							</FormControl>
							<FormMessage />
						</FormItem>
					)}
				/>

				<div className="flex gap-2">
					<Button
						type="submit"
						disabled={saveSystemPromptMutation.isPending}
					>
						{saveSystemPromptMutation.isPending ? "Saving..." : "Save"}
					</Button>
					<Button
						type="button"
						variant="outline"
						onClick={handleClear}
					>
						Clear
					</Button>
				</div>
			</form>
		</Form>
	);
}