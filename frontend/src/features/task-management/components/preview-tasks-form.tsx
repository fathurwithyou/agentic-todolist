import { Button } from "@/shared/components/ui/button";
import {
	FormControl,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
} from "@/shared/components/ui/form";
import { Textarea } from "@/shared/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Loader2 } from "lucide-react";
import { useFormContext } from "react-hook-form";
import { useQuery } from "@tanstack/react-query";
import { getListProviders } from "@/shared/repositories/api-key/action";
import { useGetModelsQuery } from "@/shared/repositories/llm/query";
import { useGetListApiKeysQuery } from "@/shared/repositories/api-key/query";
import { capitalize } from "@/shared/lib/string";

export default function PreviewTasksForm() {
	const form = useFormContext();

	const { data: providersData } = useQuery({
		queryKey: ["api-providers"],
		queryFn: () => getListProviders(),
	});

	const providers = providersData?.available_providers || [];
	const selectedProvider = form.watch("provider");
	
	const { data: apiKeys } = useGetListApiKeysQuery();
	const hasApiKey = selectedProvider ? apiKeys?.api_keys[selectedProvider] : false;

	// Use dynamic model fetching for better accuracy
	const { data: models, isLoading: isLoadingModels } = useGetModelsQuery(
		selectedProvider,
		hasApiKey ?? false,
	);
	const selectedProviderModels = models || [];

	return (
		<div className="space-y-4">
			<FormField
				control={form.control}
				name="timeline"
				render={({ field }) => (
					<FormItem>
						<FormLabel>Timeline Text</FormLabel>
						<FormControl>
							<Textarea
								placeholder="Enter your timeline text here... (e.g., 'Todo: finish project proposal by Friday', 'Call client urgent priority', etc.)"
								className="min-h-32 resize-none"
								{...field}
							/>
						</FormControl>
						<FormMessage />
					</FormItem>
				)}
			/>

			<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
				<FormField
					control={form.control}
					name="list_id"
					render={({ field }) => (
						<FormItem>
							<FormLabel>Task List</FormLabel>
							<FormControl>
								<Select onValueChange={field.onChange} value={field.value}>
									<SelectTrigger>
										<SelectValue placeholder="Default list" />
									</SelectTrigger>
									<SelectContent>
										<SelectItem value="@default">My Tasks</SelectItem>
									</SelectContent>
								</Select>
							</FormControl>
							<FormMessage />
						</FormItem>
					)}
				/>

				<FormField
					control={form.control}
					name="provider"
					render={({ field }) => (
						<FormItem>
							<FormLabel>AI Provider</FormLabel>
							<FormControl>
								<Select onValueChange={field.onChange} value={field.value}>
									<SelectTrigger>
										<SelectValue placeholder="Select provider" />
									</SelectTrigger>
									<SelectContent>
										{providers.map((provider) => (
											<SelectItem key={provider} value={provider}>
												{capitalize(provider)}
											</SelectItem>
										))}
									</SelectContent>
								</Select>
							</FormControl>
							<FormMessage />
						</FormItem>
					)}
				/>

				{selectedProvider && (
					<FormField
						control={form.control}
						name="model"
						render={({ field }) => (
							<FormItem>
								<FormLabel>Model</FormLabel>
								<FormControl>
									<Select 
										onValueChange={field.onChange} 
										value={field.value}
										disabled={!hasApiKey || isLoadingModels}
									>
										<SelectTrigger>
											<SelectValue placeholder={!hasApiKey ? "API key required" : "Select model"} />
										</SelectTrigger>
										<SelectContent side="bottom" align="start" className="max-h-60 overflow-y-auto">
											{isLoadingModels && <SelectItem value="loading" disabled>Loading...</SelectItem>}
											{selectedProviderModels.map((model) => (
												<SelectItem key={model} value={model}>
													{model}
												</SelectItem>
											))}
										</SelectContent>
									</Select>
								</FormControl>
								<FormMessage />
							</FormItem>
						)}
					/>
				)}
			</div>

			<Button
				type="button"
				onClick={form.previewTasks}
				disabled={form.watch("isLoading") || !form.watch("timeline")?.trim()}
				className="w-full"
				size="lg"
			>
				{form.watch("isLoading") ? (
					<>
						<Loader2 className="w-4 h-4 mr-2 animate-spin" />
						Parsing Tasks...
					</>
				) : (
					"Parse Timeline for Tasks"
				)}
			</Button>
		</div>
	);
}