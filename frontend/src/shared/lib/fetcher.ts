const API_BASE_URL = "http://localhost:8000";

export const apiFetcher = async (
	url: string,
	options?: RequestInit,
): Promise<Response> => {
	const token = localStorage.getItem("token");

	let optionsWithAuth = options;
	if (token) {
		optionsWithAuth = {
			...options,
			headers: {
				...options?.headers,
				Authorization: `Bearer ${token}`,
			},
		};
	}

	console.info(
		`[apiFetcher] Request: ${optionsWithAuth?.method || "GET"} ${url}`,
		optionsWithAuth?.body ? { body: optionsWithAuth.body } : {},
	);

	return fetch(`${API_BASE_URL}${url}`, optionsWithAuth);
};

export const jsonFetcher = async <T>(
	url: string,
	options?: RequestInit,
): Promise<T> => {
	const response = await apiFetcher(url, options);

	const body = await response.json();

	console.info(
		`[jsonFetcher] Response: ${options?.method || "GET"} ${url} ${response.status}`,
		body,
	);

	if (!response.ok) {
		throw new Error(`${body.message || "Unknown error"}`);
	}

	return body;
};
