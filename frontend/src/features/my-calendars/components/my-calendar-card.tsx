import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";

export default function MyCalendarCard() {
	return (
		<Card>
			<CardHeader>
				<CardTitle>My Calendars</CardTitle>
				<CardDescription>
					Manage and view your connected calendars
				</CardDescription>
			</CardHeader>
			<CardContent className="space-y-4">
				{/* Future implementation: List and manage connected calendars */}
				<p>Feature coming soon!</p>
			</CardContent>
		</Card>
	);
}
