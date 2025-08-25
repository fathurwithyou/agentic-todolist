import { Button } from "@/shared/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import {
	Form,
	FormControl,
	FormDescription,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
} from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/shared/components/ui/select";
import { capitalize } from "@/shared/lib/string";
import {
	type SaveApiKeyRequest,
	SaveApiKeySchema,
} from "@/shared/repositories/api-key/dto";
import {
	useGetListProvidersQuery,
	useSaveApiKeyMutation,
	useTestApiKeyMutation,
} from "@/shared/repositories/api-key/query";
import { zodResolver } from "@hookform/resolvers/zod";
import { LoaderCircle } from "lucide-react";
import { useForm, useWatch } from "react-hook-form";
import { toast } from "sonner";
import ApiKeyStatusCard from "./api-key-status-card";
import HowToGetApiKeysCard from "./how-to-get-api-keys-card";

export default function ApiKeyManagementCard() {
	const { data: listProvidersRes } = useGetListProvidersQuery();
	const { mutate: saveApiKey, isPending: isSaveApiKeyPending } =
		useSaveApiKeyMutation();
	const { mutate: testApiKey, isPending: isTestApiKeyPending } =
		useTestApiKeyMutation();

	const form = useForm<SaveApiKeyRequest>({
		resolver: zodResolver(SaveApiKeySchema),
		defaultValues: {
			provider: "",
			api_key: "",
		},
	});

	const [providers, apiKey] = useWatch({
		control: form.control,
		name: ["provider", "api_key"],
	});

	const onSubmitHandler = form.handleSubmit((data) => {
		saveApiKey(data, {
			onSuccess: () => {
				toast.success("API key saved successfully");
				form.reset();
			},
			onError: (err) => {
				toast.error(err.message || "Failed to save API key");
			},
		});
	});

	const onTestHandler = () => {
		const data = form.getValues();
		if (!data.provider) {
			form.setError("provider", { message: "Please select a provider" });
			return;
		}

		testApiKey(
			{ provider: data.provider },
			{
				onSuccess: (res) => {
					if (!res.success) {
						toast.error(res.message);
						return;
					}

					toast.success(res.message);
				},
				onError: (err) => {
					toast.error(err.message || "Failed to test API key");
				},
			},
		);
	};

	return (
		<Card>
			<CardHeader>
				<CardTitle>API Key Management</CardTitle>
				<CardDescription>
					Manage your AI provider API keys securely
				</CardDescription>
			</CardHeader>
			<CardContent className="space-y-4">
				<ApiKeyStatusCard />

				<Form {...form}>
					<form onSubmit={onSubmitHandler} className="space-y-4">
						<FormField
							control={form.control}
							name="provider"
							render={({ field }) => (
								<FormItem>
									<FormLabel htmlFor="provider">Available Providers</FormLabel>
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

						{providers && (
							<FormField
								control={form.control}
								name="api_key"
								render={({ field }) => (
									<FormItem>
										<FormLabel htmlFor="api-key">API Key</FormLabel>
										<FormControl>
											<Input
												id="api-key"
												type="password"
												placeholder="Enter your API key"
												{...field}
											/>
										</FormControl>
										<FormDescription>
											Your API Key is stored securely and only used for your
											requests.
										</FormDescription>
										<FormMessage />
									</FormItem>
								)}
							/>
						)}

						<div className="grid grid-cols-2 gap-2 md:flex">
							{providers && (
								<Button
									onClick={onTestHandler}
									type="button"
									className="flex-1"
									variant="secondary"
									disabled={isTestApiKeyPending}
								>
									{isTestApiKeyPending && (
										<LoaderCircle className="animate-spin" />
									)}
									Test
								</Button>
							)}
							{apiKey && (
								<Button
									type="submit"
									className="flex-1"
									disabled={isSaveApiKeyPending}
								>
									{isSaveApiKeyPending && (
										<LoaderCircle className="animate-spin" />
									)}
									Save
								</Button>
							)}
						</div>
					</form>
				</Form>

				<HowToGetApiKeysCard />
			</CardContent>
		</Card>
	);
}
