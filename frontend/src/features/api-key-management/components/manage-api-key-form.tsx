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
import { Loader2, TestTube, Save, Key } from "lucide-react";
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
			<form onSubmit={onSubmitHandler} className="space-y-6">
				<FormField
					control={form.control}
					name="provider"
					render={({ field }) => (
						<FormItem>
							<FormLabel className="flex items-center gap-2">
								<Key className="w-4 h-4" />
								Provider
							</FormLabel>
							<Select
								onValueChange={field.onChange}
								value={field.value}
								defaultValue={field.value}
							>
								<FormControl>
									<SelectTrigger>
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
								<FormLabel>API Key</FormLabel>
								<FormControl>
									<Input
										type="password"
										placeholder="sk-..."
										className="font-mono text-sm"
										{...field}
									/>
								</FormControl>
								<FormDescription>
									Your API key is encrypted and stored securely
								</FormDescription>
								<FormMessage />
							</FormItem>
						)}
					/>
				)}

				<div className="flex gap-3">
					<Button
						onClick={onTestHandler}
						type="button"
						variant="outline"
						disabled={isTestApiKeyPending || !providers}
						className="gap-2"
					>
						{isTestApiKeyPending ? (
							<Loader2 className="h-4 w-4 animate-spin" />
						) : (
							<TestTube className="h-4 w-4" />
						)}
						Test Connection
					</Button>
					<Button
						type="submit"
						disabled={isSaveApiKeyPending || !apiKey}
						className="gap-2"
					>
						{isSaveApiKeyPending ? (
							<Loader2 className="h-4 w-4 animate-spin" />
						) : (
							<Save className="h-4 w-4" />
						)}
						Save API Key
					</Button>
				</div>
			</form>
		</Form>
	);
}