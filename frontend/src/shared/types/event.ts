export type CalendarEvent = {
	title: string;
	description: string;
	start_date: string; // YYYY-MM-DD
	end_date: string; // YYYY-MM-DD
	start_time: string | null; // HH:MM or null for all-day events
	end_time: string | null; // HH:MM or null for all-day events
	attendees: string[]; // array of email addresses
	location: string | null;
	all_day: boolean;
};
