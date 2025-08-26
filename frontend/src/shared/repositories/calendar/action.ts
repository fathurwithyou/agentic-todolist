import { jsonFetcher } from "../../lib/fetcher";
import type { GetListWritableCalendars } from "./dto";

export const getListWritableCalendars = async () => {
	const response = await jsonFetcher<GetListWritableCalendars>(
		"/api/v1/calendar/google/calendars/writable",
	);

	return response;
};
