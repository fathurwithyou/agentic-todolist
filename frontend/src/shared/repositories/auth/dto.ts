import type { User } from "../../types";

export type VerifyTokenParams = {
	token: string;
};

export type VerifyTokenResponse = {
	valid: boolean;
	user: User;
};

export type GetProfileResponse = User;

export type SaveSystemPromptParams = {
	system_prompt: string;
};

export type SaveSystemPromptResponse = {
	success: boolean;
	message: string;
};

export type GetSystemPromptResponse = {
	system_prompt: string | null;
};
