import { jsonFetcher } from "../../lib/fetcher";
import type {
	CreateEventsFromTimelineRequest,
	GetTimelineProvidersResponse,
	PreviewTimelineRequest,
	PreviewTimelineResponse,
} from "./dto";

export const getTimelineProviders = async () => {
	const response = await jsonFetcher<GetTimelineProvidersResponse>(
		"/api/v1/timeline/providers",
		{
			method: "GET",
		},
	);

	return response;
};

export const previewTimeline = async (req: PreviewTimelineRequest) => {
	const response = await jsonFetcher<PreviewTimelineResponse>(
		"/api/v1/timeline/preview",
		{
			method: "POST",
			body: JSON.stringify(req),
			headers: {
				"Content-Type": "application/json",
			},
		},
	);

	return response;
};

export const createEventsFromTimeline = async (
	req: CreateEventsFromTimelineRequest,
) => {
	const response = await jsonFetcher("/api/v1/timeline/create-events", {
		method: "POST",
		body: JSON.stringify(req),
		headers: {
			"Content-Type": "application/json",
		},
	});

	return response;
};
