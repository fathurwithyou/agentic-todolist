import { useMutation, useQuery } from "@tanstack/react-query";
import { getProfile, logout, verifyToken } from "./action";
import type { VerifyTokenParams } from "./dto";

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
