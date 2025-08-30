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
	FormDescription,
} from "../../../shared/components/ui/form";
import { Textarea } from "../../../shared/components/ui/textarea";
import {
	useGetSystemPromptQuery,
	useSaveSystemPromptMutation,
} from "../../../shared/repositories/auth/query";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { Loader2, Save, RotateCcw } from "lucide-react";

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
		return (
			<div className="flex items-center justify-center py-12">
				<Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
			</div>
		);
	}

	return (
		<Form {...form}>
			<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
				<FormField
					control={form.control}
					name="system_prompt"
					render={({ field }) => (
						<FormItem>
							<FormLabel className="text-sm font-medium text-foreground/90">Knowledge Base</FormLabel>
							<FormDescription className="text-xs text-muted-foreground mb-3">
								Add information that will help AI understand your context better
							</FormDescription>
							<FormControl>
								<Textarea
									placeholder="Example:&#10;&#10;Contacts:&#10;• Fathur: fathurwithyou@gmail.com&#10;• John (Team Lead): john@company.com&#10;• Sarah (PM): sarah@company.com&#10;&#10;Locations:&#10;• Main Office: Jakarta, Menara BCA 15th floor&#10;• Meeting Room A: 2nd floor&#10;• Conference Room: 3rd floor&#10;&#10;Regular Events:&#10;• Team Standup: Every Monday 10 AM&#10;• Sprint Review: Every 2 weeks Friday 2 PM"
									className="min-h-[220px] font-mono text-xs bg-background/50 transition-all duration-150 focus:bg-background"
									{...field}
								/>
							</FormControl>
							<FormMessage />
						</FormItem>
					)}
				/>

				<div className="flex gap-3 pt-2">
					<Button
						type="submit"
						disabled={saveSystemPromptMutation.isPending}
						className="gap-2 transition-all duration-150"
					>
						{saveSystemPromptMutation.isPending ? (
							<Loader2 className="h-4 w-4 animate-spin" />
						) : (
							<Save className="h-4 w-4" />
						)}
						Save Changes
					</Button>
					<Button
						type="button"
						variant="outline"
						onClick={handleClear}
						className="gap-2 transition-all duration-150 hover:bg-muted/50"
					>
						<RotateCcw className="h-4 w-4" />
						Clear
					</Button>
				</div>
			</form>
		</Form>
	);
}