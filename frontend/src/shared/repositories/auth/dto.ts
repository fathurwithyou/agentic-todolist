import type { User } from "../../types";

export type VerifyTokenParams = {
	token: string;
};

export type VerifyTokenResponse = {
	valid: boolean;
	user: User;
};

export type GetProfileResponse = User;
