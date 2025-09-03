import { Button } from "@/shared/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { CheckSquare, Clock, AlertTriangle, Loader2, Calendar } from "lucide-react";
import { useFormContext } from "react-hook-form";
import type { GoogleTask, TaskPriority } from "@/shared/types/task";

const priorityIcons = {
	high: <AlertTriangle className="w-3 h-3" />,
	medium: <Clock className="w-3 h-3" />,
	low: <CheckSquare className="w-3 h-3" />,
};

const priorityColors = {
	high: "bg-red-100 text-red-800 border-red-200",
	medium: "bg-yellow-100 text-yellow-800 border-yellow-200", 
	low: "bg-green-100 text-green-800 border-green-200",
};

export default function PreviewTasksCard() {
	const form = useFormContext();
	const tasks: GoogleTask[] = form.watch("tasks") || [];
	const isCreating = form.watch("isCreating");

	if (tasks.length === 0) {
		return null;
	}

	const formatDueDate = (dueDate?: string, dueTime?: string) => {
		if (!dueDate) return "No due date";
		
		const date = new Date(dueDate);
		let formatted = date.toLocaleDateString("en-US", {
			weekday: "short",
			month: "short",
			day: "numeric",
		});
		
		if (dueTime) {
			formatted += ` at ${dueTime}`;
		}
		
		return formatted;
	};

	return (
		<Card className="border-dashed">
			<CardHeader>
				<CardTitle className="flex items-center gap-2">
					<CheckSquare className="w-4 h-4" />
					Preview Tasks ({tasks.length})
				</CardTitle>
				<CardDescription>
					Review the tasks that will be created in Google Tasks
				</CardDescription>
			</CardHeader>

			<CardContent>
				<div className="space-y-3 mb-6">
					{tasks.map((task, index) => (
						<div
							key={index}
							className="border rounded-lg p-4 space-y-2 bg-muted/20"
						>
							<div className="flex items-start justify-between gap-3">
								<div className="flex-1 space-y-1">
									<h4 className="font-medium text-sm leading-tight">
										{task.title}
									</h4>
									{task.notes && (
										<p className="text-xs text-muted-foreground">
											{task.notes}
										</p>
									)}
								</div>
								
								{task.priority && (
									<Badge 
										variant="outline" 
										className={`text-xs ${priorityColors[task.priority as TaskPriority]}`}
									>
										{priorityIcons[task.priority as TaskPriority]}
										{task.priority}
									</Badge>
								)}
							</div>

							<div className="flex items-center gap-4 text-xs text-muted-foreground">
								<div className="flex items-center gap-1">
									<Calendar className="w-3 h-3" />
									{formatDueDate(task.due)}
								</div>
								
								{task.completed && (
									<Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
										Completed
									</Badge>
								)}
							</div>
						</div>
					))}
				</div>

				<Button
					type="button"
					onClick={form.createTasks}
					disabled={isCreating || tasks.length === 0}
					className="w-full"
					size="lg"
				>
					{isCreating ? (
						<>
							<Loader2 className="w-4 h-4 mr-2 animate-spin" />
							Creating Tasks...
						</>
					) : (
						<>
							<CheckSquare className="w-4 h-4 mr-2" />
							Create {tasks.length} Tasks in Google Tasks
						</>
					)}
				</Button>
			</CardContent>
		</Card>
	);
}