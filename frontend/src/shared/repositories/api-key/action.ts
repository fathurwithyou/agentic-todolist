import { jsonFetcher } from "../../lib/fetcher";
import type {
	GetListApiKeysResponse,
	GetListProvidersResponse,
	RemoveApiKeyParams,
	SaveApiKeyRequest,
	TestApiKeyParams,
	TestApiKeyResponse,
} from "./dto";

export const getListProviders = async () => {
	const response = await jsonFetcher<GetListProvidersResponse>(
		"/api/v1/api-keys/providers",
	);
	return response;
};

export const getListApiKeys = async () => {
	const response = await jsonFetcher<GetListApiKeysResponse>(
		"/api/v1/api-keys/list",
	);
	return response;
};

export const saveApiKey = async (req: SaveApiKeyRequest) => {
	const response = await jsonFetcher("/api/v1/api-keys/save", {
		method: "POST",

		data: req,
	});
	return response;
};

export const removeApiKey = async (params: RemoveApiKeyParams) => {
	const response = await jsonFetcher(
		`/api/v1/api-keys/remove/${params.provider}`,
		{
			method: "DELETE",
		},
	);
	return response;
};

export const testApiKey = async (params: TestApiKeyParams) => {
	const response = await jsonFetcher<TestApiKeyResponse>(
		`/api/v1/api-keys/test/${params.provider}`,
		{
			method: "GET",

		},
	);
	return response;
};
