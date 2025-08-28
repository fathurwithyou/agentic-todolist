import { useMutation, useQuery } from "@tanstack/react-query";
import { getProfile, logout, verifyToken, saveSystemPrompt } from "./action";
import { jsonFetcher } from "../../lib/fetcher";
import type { VerifyTokenParams, SaveSystemPromptParams, GetSystemPromptResponse } from "./dto";

export const useLoginWithGoogleMutation = () => {
	return useMutation({
		mutationFn: async () => {
			return window.location.assign("/api/v1/auth/google");
		},
	});
};

export const useVerifyTokenMutation = () => {
	return useMutation({
		mutationFn: (params: VerifyTokenParams) => verifyToken(params),
	});
};

export const useGetProfileQuery = () => {
	return useQuery({
		queryKey: ["profile"],
		queryFn: getProfile,
	});
};

export const useLogoutMutation = () => {
	return useMutation({
		mutationFn: logout,
	});
};

export const useSaveSystemPromptMutation = () => {
	return useMutation({
		mutationFn: (params: SaveSystemPromptParams) => saveSystemPrompt(params),
	});
};

export const useGetSystemPromptQuery = () => {
	return useQuery({
		queryKey: ["system-prompt"],
		queryFn: () => jsonFetcher<GetSystemPromptResponse>("/api/v1/auth/system-prompt", {
			method: "GET",
		}),
	});
};
