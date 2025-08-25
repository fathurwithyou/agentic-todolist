import {
	type SaveApiKeyRequest,
	SaveApiKeySchema,
} from "@/shared/repositories/api-key/dto";
import {
	useSaveApiKeyMutation,
	useTestApiKeyMutation,
} from "@/shared/repositories/api-key/query";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, useWatch } from "react-hook-form";
import { toast } from "sonner";

export const useManageAPIKeyForm = () => {
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

	return {
		...form,
		providers,
		apiKey,
		isSaveApiKeyPending,
		isTestApiKeyPending,
		onSubmitHandler,
		onTestHandler,
	};
};
