import { Button } from "@/shared/components/ui/button";
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
import { useGetListProvidersQuery } from "@/shared/repositories/api-key/query";
import { LoaderCircle } from "lucide-react";
import { useManageAPIKeyForm } from "../hooks/use-manage-api-key-form";

export default function ManageApiKeyForm() {
	const { data: listProvidersRes } = useGetListProvidersQuery();
	const {
		onSubmitHandler,
		onTestHandler,
		isSaveApiKeyPending,
		isTestApiKeyPending,
		apiKey,
		providers,
		...form
	} = useManageAPIKeyForm();

	return (
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
					<Button
						onClick={onTestHandler}
						type="button"
						className="flex-1"
						variant="secondary"
						disabled={isTestApiKeyPending || !providers}
					>
						{isTestApiKeyPending && <LoaderCircle className="animate-spin" />}
						Test
					</Button>
					<Button
						type="submit"
						className="flex-1"
						disabled={isSaveApiKeyPending || !apiKey}
					>
						{isSaveApiKeyPending && <LoaderCircle className="animate-spin" />}
						Save
					</Button>
				</div>
			</form>
		</Form>
	);
}
