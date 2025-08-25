import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
	getListApiKeys,
	getListProviders,
	removeApiKey,
	saveApiKey,
	testApiKey,
} from "./action";

export const useGetListProvidersQuery = () => {
	return useQuery({
		queryKey: ["providers"],
		queryFn: getListProviders,
	});
};

export const useGetListApiKeysQuery = () => {
	return useQuery({
		queryKey: ["api-keys"],
		queryFn: getListApiKeys,
	});
};

export const useSaveApiKeyMutation = () => {
	const qc = useQueryClient();

	return useMutation({
		mutationFn: saveApiKey,
		onSuccess: () => {
			qc.invalidateQueries({ queryKey: ["api-keys"] });
		},
	});
};

export const useRemoveApiKeyMutation = () => {
	const qc = useQueryClient();

	return useMutation({
		mutationFn: removeApiKey,
		onSuccess: () => {
			qc.invalidateQueries({ queryKey: ["api-keys"] });
		},
	});
};

export const useTestApiKeyMutation = () => {
	const qc = useQueryClient();

	return useMutation({
		mutationFn: testApiKey,
		onSuccess: () => {
			qc.invalidateQueries({ queryKey: ["api-keys"] });
		},
	});
};
