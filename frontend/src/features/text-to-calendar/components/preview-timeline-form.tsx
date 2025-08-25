import { Button } from "@/shared/components/ui/button";
import { Checkbox } from "@/shared/components/ui/checkbox";
import {
	Form,
	FormControl,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
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
import { useGetTimelineProvidersQuery } from "@/shared/repositories/timeline/query";
import type { CalendarEvent } from "@/shared/types";
import { LoaderCircle } from "lucide-react";
import { usePreviewTimelineForm } from "../hooks/use-preview-timeline-form";

type Props = {
	onSuccess: (events: CalendarEvent[]) => void;
};

export default function PreviewTimelineForm({ onSuccess }: Props) {
	const { data: listProvidersRes } = useGetTimelineProvidersQuery();
	const { onSubmitHandler, isPreviewTimelinePending, llmProvider, ...form } =
		usePreviewTimelineForm({ onSuccess });

	return (
		<Form {...form}>
			<form className="space-y-4" onSubmit={onSubmitHandler}>
				<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
					<FormField
						control={form.control}
						name="llm_provider"
						render={({ field }) => (
							<FormItem>
								<FormLabel htmlFor="llm_provider">AI Provider</FormLabel>
								<Select
									onValueChange={field.onChange}
									value={field.value}
									defaultValue={field.value}
								>
									<FormControl>
										<SelectTrigger className="w-full">
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
									<FormLabel htmlFor="llm_model">Model</FormLabel>
									<Select
										onValueChange={field.onChange}
										value={field.value}
										defaultValue={field.value}
									>
										<FormControl>
											<SelectTrigger className="w-full">
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
					name="timeline_text"
					render={({ field }) => (
						<FormItem>
							<FormLabel htmlFor="timeline_text">Timeline Text</FormLabel>
							<FormControl>
								<Textarea
									id="timeline_text"
									placeholder="Enter your timeline text here...
Example:
Timeline Gemastik

1 Juli-10 Agustus: Masa Submisi Proposal
11 Agustus-2 September: Penjurian
8 September pukul 10:00: Pengumuman Finalis
27 Oktober 09:00-17:00: Babak Final Hari 1
28 Oktober 13:30-15:30: Presentasi Final

Meeting jadwal:
15 Juli jam 14:00: Rapat Koordinasi
20 Juli 10:30-12:00: Review Progress

Invite: Fathur, Bimo, Guntara"
									className="resize-none h-32"
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
						<FormItem className="flex items-center space-x-3 space-y-0">
							<FormControl>
								<Checkbox
									checked={field.value}
									onCheckedChange={field.onChange}
								/>
							</FormControl>
							<FormLabel className="font-normal">
								Use flexible parsing (handles various text formats)
							</FormLabel>
						</FormItem>
					)}
				/>
				<Button
					type="submit"
					className="w-full"
					disabled={isPreviewTimelinePending}
				>
					{isPreviewTimelinePending && (
						<LoaderCircle className="animate-spin" />
					)}
					Preview Timeline
				</Button>
			</form>
		</Form>
	);
}
