import { apiFetcher, jsonFetcher } from "../../lib/fetcher";
import type { VerifyTokenParams, VerifyTokenResponse } from "./dto";
import type { GetProfileResponse } from "./dto";

export const verifyToken = async (params: VerifyTokenParams) => {
	const response = await jsonFetcher<VerifyTokenResponse>(
		`/api/v1/auth/verify?token=${params.token}`,
		{
			method: "GET",
		},
	);

	return response;
};

export const getProfile = async () => {
	const response = await jsonFetcher<GetProfileResponse>(
		"/api/v1/auth/profile",
		{
			method: "GET",
		},
	);

	return response;
};

export const logout = async () => {
	const response = await apiFetcher("/api/v1/auth/logout", {
		method: "POST",
	});

	return response;
};
