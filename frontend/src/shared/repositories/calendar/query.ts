import { useQuery } from "@tanstack/react-query";
import { getListWritableCalendars } from "./action";

export const useGetListWritableCalendarsQuery = () => {
	return useQuery({
		queryKey: ["writable-calendars"],
		queryFn: getListWritableCalendars,
	});
};
