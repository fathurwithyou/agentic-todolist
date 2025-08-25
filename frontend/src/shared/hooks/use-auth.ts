import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import type { VerifyTokenResponse } from "../repositories/auth/dto";
import {
	useLoginWithGoogleMutation,
	useLogoutMutation,
	useVerifyTokenMutation,
} from "../repositories/auth/query";
import type { User } from "../types";

export const useAuth = () => {
	const [state, setState] = useState<
		{
			isLoading: boolean;
		} & (
			| {
					isAuthenticated: true;
					user: User;
					token: string;
			  }
			| {
					isAuthenticated: false;
					user: null;
					token: null;
			  }
		)
	>({
		isAuthenticated: false,
		user: null,
		isLoading: true,
		token: null,
	});

	const { mutate: loginWithGoogle, isPending: isLoadingLoginWithGoogle } =
		useLoginWithGoogleMutation();
	const { mutate: verifyToken, isPending: isLoadingVerifyToken } =
		useVerifyTokenMutation();
	const { mutate: removeSession } = useLogoutMutation();

	const handleGoogleLogin = () => {
		loginWithGoogle(undefined, {
			onError: (error) => {
				toast.error("Failed to login with Google", {
					description: String(error),
				});
			},
		});
	};

	const logout = () => {
		setState((prev) => ({
			...prev,
			isLoading: true,
		}));

		removeSession(undefined);

		localStorage.removeItem("token");
		setState({
			isAuthenticated: false,
			user: null,
			isLoading: false,
			token: null,
		});

		window.location.href = "/";
	};

	const onSuccessVerifyToken = useCallback(
		(token: string, data: VerifyTokenResponse, callbackFn?: () => void) => {
			localStorage.setItem("token", token);

			const user = data.user;
			setState({
				isAuthenticated: true,
				user,
				isLoading: false,
				token,
			});

			if (callbackFn) {
				callbackFn();
			}
		},
		[],
	);

	const onErrorVerifyToken = useCallback(
		(error: unknown, callbackFn?: () => void) => {
			console.error(error);

			toast.error("Session expired. Please login again.");

			localStorage.removeItem("token");

			setState({
				isAuthenticated: false,
				user: null,
				isLoading: false,
				token: null,
			});

			if (callbackFn) {
				callbackFn();
			}
		},
		[],
	);

	// biome-ignore lint/correctness/useExhaustiveDependencies: <explanation>
	useEffect(() => {
		const searchParams = new URLSearchParams(window.location.search);
		const token = searchParams.get("token");

		if (token) {
			setState((prev) => ({
				...prev,
				isLoading: true,
			}));
			verifyToken(
				{ token },
				{
					onError: (error) => {
						onErrorVerifyToken(error, () => {
							window.location.href = "/";
						});
					},
					onSuccess: (data) => {
						onSuccessVerifyToken(token, data, () => {
							window.location.href = "/";
						});
					},
				},
			);
			return;
		}

		const storedToken = localStorage.getItem("token");
		if (storedToken) {
			setState((prev) => ({
				...prev,
				isLoading: true,
			}));
			verifyToken(
				{ token: storedToken },
				{
					onError: (error) => {
						onErrorVerifyToken(error);
					},
					onSuccess: (data) => {
						onSuccessVerifyToken(storedToken, data);
					},
				},
			);
		}
	}, []);

	return {
		...state,
		isLoading:
			state.isLoading || isLoadingLoginWithGoogle || isLoadingVerifyToken,
		loginWithGoogle: handleGoogleLogin,
		logout,
	};
};
