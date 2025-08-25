import { z } from "zod";

export const SaveApiKeySchema = z.object({
	provider: z.string().min(2).max(100),
	api_key: z.string().min(10).max(100),
});

export type SaveApiKeyRequest = z.infer<typeof SaveApiKeySchema>;

export type GetListApiKeysResponse = {
	api_keys: Record<string, boolean>;
};

export type RemoveApiKeyParams = {
	provider: string;
};

export type GetListProvidersResponse = {
	available_providers: string[];
	provider_models: {
		[provider: string]: string[];
	};
};

export type TestApiKeyParams = {
	provider: string;
};

export type TestApiKeyResponse = {
  success: boolean
  message: string;
}
