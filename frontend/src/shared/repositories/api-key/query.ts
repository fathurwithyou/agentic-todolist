import { useMutation, useQuery } from "@tanstack/react-query";
import { getListApiKeys, saveApiKey, testApiKey, getListProviders } from "./action";
import { type SaveApiKeyRequest } from "./dto";

export const useGetListApiKeysQuery = () => {
  return useQuery({
    queryKey: ["api-keys"],
    queryFn: getListApiKeys,
  });
};

export const useSaveApiKeyMutation = () =>
	useMutation({
		mutationFn: async (data: SaveApiKeyRequest) => {
			return await saveApiKey(data);
		},
	});

export const useTestApiKeyMutation = () =>
	useMutation({
		mutationFn: async (data: { provider: string }) => {
			return await testApiKey(data);
		},
	});

export const useGetListProvidersQuery = () => {
  return useQuery({
    queryKey: ["api-providers"],
    queryFn: getListProviders,
  });
};
