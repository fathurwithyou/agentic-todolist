import { useMutation, useQuery } from "@tanstack/react-query";
import {
	createEventsFromTimeline,
	getTimelineProviders,
	previewTimeline,
} from "./action";
import type {
	CreateEventsFromTimelineRequest,
	PreviewTimelineRequest,
} from "./dto";

export const useGetTimelineProvidersQuery = () => {
	return useQuery({
		queryKey: ["timelineProviders"],
		queryFn: getTimelineProviders,
	});
};

export const usePreviewTimelineMutation = () => {
	return useMutation({
		mutationFn: (req: PreviewTimelineRequest) => previewTimeline(req),
	});
};

export const useCreateEventsFromTimelineMutation = () => {
	return useMutation({
		mutationFn: (req: CreateEventsFromTimelineRequest) =>
			createEventsFromTimeline(req),
	});
};
