import { Button } from "@/shared/components/ui/button";
import { Calendar } from "@/shared/components/ui/calendar";
import {
	Card,
	CardContent,
	CardDescription,
	CardFooter,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import { DateInput, TimeField } from "@/shared/components/ui/datefield-rac";
import { FormControl, FormField, FormItem } from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import {
	Popover,
	PopoverContent,
	PopoverTrigger,
} from "@/shared/components/ui/popover";
import { Textarea } from "@/shared/components/ui/textarea";
import type { CreateEventsFromTimelineRequest } from "@/shared/repositories/timeline/dto";
import { parseTime } from "@internationalized/date";
import { format, parse } from "date-fns";
import {
	Calendar as CalendarIcon,
	CheckIcon,
	Clock,
	Clock2Icon,
	MapPin,
	PencilIcon,
	PlusIcon,
	Users,
	XIcon,
} from "lucide-react";
import { useState } from "react";
import { useFormContext, useWatch } from "react-hook-form";

type Props = {
	idx: number;
};

export default function PreviewTimelineCard({ idx }: Props) {
	const [isEditing, setIsEditing] = useState(false);
	const formCtx = useFormContext<CreateEventsFromTimelineRequest>();

	const event = useWatch({
		control: formCtx.control,
		name: `events.${idx}`,
	});

	return (
		<Card className="border-border/40 shadow-none hover:shadow-soft transition-all duration-150">
			<CardHeader className="pb-3 px-5 pt-5">
				<div className="flex flex-row justify-between items-center gap-2">
					{isEditing ? (
						<CardTitle className="text-base flex items-center gap-2 font-medium w-full">
							<CalendarIcon className="w-4 h-4 text-primary/60 shrink-0" />
							<FormField
								control={formCtx.control}
								name={`events.${idx}.title`}
								render={({ field }) => (
									<FormItem className="w-full">
										<FormControl>
											<Input
												className="p-1 h-min text-lg font-medium"
												{...field}
											/>
										</FormControl>
									</FormItem>
								)}
							/>
						</CardTitle>
					) : (
						<CardTitle className="text-base flex items-center gap-2 font-medium break-all">
							<CalendarIcon className="w-4 h-4 text-primary/60" />
							{event.title}
						</CardTitle>
					)}
					<Button
						type="button"
						size="icon"
						variant="ghost"
						className="rounded-lg"
						onClick={() => setIsEditing((prev) => !prev)}
					>
						{isEditing ? (
							<CheckIcon className="w-5 h-5 shrink-0" />
						) : (
							<PencilIcon className="w-5 h-5 shrink-0" />
						)}
					</Button>
				</div>
				{isEditing ? (
					<CardDescription className="text-sm mt-1.5 text-muted-foreground">
						<FormField
							control={formCtx.control}
							name={`events.${idx}.description`}
							render={({ field }) => (
								<FormItem>
									<FormControl>
										<Textarea
											className="p-1 h-min text-sm resize-none min-h-[60px]"
											{...field}
										/>
									</FormControl>
								</FormItem>
							)}
						/>
					</CardDescription>
				) : (
					<CardDescription className="text-sm mt-1.5 text-muted-foreground break-all">
						{event.description ?? "-"}
					</CardDescription>
				)}
			</CardHeader>
			<CardContent className="space-y-2.5 text-sm px-5 pb-5">
				<div className="flex flex-row items-center justify-between gap-2">
					<div className="flex items-center gap-2.5 text-muted-foreground">
						<Clock className="w-3.5 h-3.5 shrink-0" />
						{event.start_date === event.end_date ? (
							<span>
								{new Date(event.start_date).toLocaleDateString("en-US", {
									weekday: "short",
									year: "numeric",
									month: "short",
									day: "numeric",
								})}
								{event.start_time && ` • ${event.start_time}`}
								{event.end_time && ` - ${event.end_time}`}
							</span>
						) : (
							<span>
								{new Date(event.start_date).toLocaleDateString("en-US", {
									month: "short",
									day: "numeric",
								})}
								{" - "}
								{new Date(event.end_date).toLocaleDateString("en-US", {
									month: "short",
									day: "numeric",
									year: "numeric",
								})}
								{event.start_time && ` • ${event.start_time}`}
								{event.end_time && ` - ${event.end_time}`}
							</span>
						)}
					</div>
					{isEditing && (
						<Popover>
							<PopoverTrigger asChild>
								<Button
									type="button"
									size="icon"
									variant="ghost"
									className="rounded-lg"
								>
									<PencilIcon className="w-3.5 h-3.5 shrink-0" />
								</Button>
							</PopoverTrigger>
							<PopoverContent className="w-auto p-0">
								<Card className="w-fit py-4">
									<CardContent className="px-4">
										<Calendar
											mode="range"
											selected={{
												from: parse(event.start_date, "yyyy-MM-dd", new Date()),
												to: parse(event.end_date, "yyyy-MM-dd", new Date()),
											}}
											onSelect={(date) => {
												if (!date || !date.from || !date.to) {
													return;
												}
												const from = format(date.from, "yyyy-MM-dd");
												const to = format(date.to, "yyyy-MM-dd");
												formCtx.setValue(`events.${idx}.start_date`, from);
												formCtx.setValue(`events.${idx}.end_date`, to);
											}}
											className="bg-transparent p-0"
										/>
									</CardContent>
									<CardFooter className="flex flex-col gap-6 border-t px-4 !pt-4">
										<div className="flex w-full flex-col gap-3">
											<Label htmlFor="time-from">Start Time</Label>
											<FormField
												control={formCtx.control}
												name={`events.${idx}.start_time`}
												render={({ field: { value, onChange, ...rest } }) => (
													<FormItem className="w-full">
														<FormControl>
															<TimeField
																className="*:not-first:mt-2"
																id="time-from"
																onChange={(e) => {
																	if (!e) {
																		return;
																	}

																	const time = e.toString();
																	const [hours, minutes] = time.split(":");
																	const formattedTime = `${hours}:${minutes}`;
																	onChange(formattedTime);
																}}
																value={value ? parseTime(value) : undefined}
																{...rest}
															>
																<div className="relative">
																	<div className="absolute inset-y-0 start-0 z-10 flex items-center justify-center ps-3">
																		<Clock2Icon className="text-muted-foreground pointer-events-none size-4" />
																	</div>
																	<DateInput className="ps-9" />
																</div>
															</TimeField>
														</FormControl>
													</FormItem>
												)}
											/>
										</div>
										<div className="flex w-full flex-col gap-3">
											<Label htmlFor="time-to">End Time</Label>
											<FormField
												control={formCtx.control}
												name={`events.${idx}.end_time`}
												render={({ field: { value, onChange, ...rest } }) => (
													<FormItem className="w-full">
														<FormControl>
															<TimeField
																className="*:not-first:mt-2"
																id="time-to"
																onChange={(e) => {
																	if (!e) {
																		return;
																	}

																	const time = e.toString();
																	const [hours, minutes] = time.split(":");
																	const formattedTime = `${hours}:${minutes}`;
																	onChange(formattedTime);
																}}
																value={value ? parseTime(value) : undefined}
																{...rest}
															>
																<div className="relative">
																	<div className="absolute inset-y-0 start-0 z-10 flex items-center justify-center ps-3">
																		<Clock2Icon className="text-muted-foreground pointer-events-none size-4" />
																	</div>
																	<DateInput className="ps-9" />
																</div>
															</TimeField>
														</FormControl>
													</FormItem>
												)}
											/>
										</div>
									</CardFooter>
								</Card>
							</PopoverContent>
						</Popover>
					)}
				</div>

				{isEditing ? (
					<div className="flex items-center gap-2.5 text-muted-foreground">
						<MapPin className="w-3.5 h-3.5 shrink-0" />
						<FormField
							control={formCtx.control}
							name={`events.${idx}.location`}
							render={({ field }) => (
								<FormItem className="w-full">
									<FormControl>
										<Input
											className="p-1 h-min text-sm"
											{...field}
											value={field.value ?? undefined}
										/>
									</FormControl>
								</FormItem>
							)}
						/>
					</div>
				) : (
					<div className="flex items-center gap-2.5 text-muted-foreground">
						<MapPin className="w-3.5 h-3.5 shrink-0" />
						<span className="break-all">{event.location || "-"}</span>
					</div>
				)}

				{isEditing ? (
					<div className="space-y-2">
						<div className="flex items-center justify-between gap-2.5 text-muted-foreground">
							<div className="flex items-center gap-2.5">
								<Users className="w-3.5 h-3.5 shrink-0" />
								<span className="ml-1.5">Attendees</span>
							</div>
							<Button
								type="button"
								size="icon"
								variant="ghost"
								className="rounded-lg"
								onClick={() => {
									formCtx.setValue(`events.${idx}.attendees`, [
										...(event.attendees || []),
										"",
									]);
								}}
							>
								<PlusIcon className="w-3.5 h-3.5 shrink-0" />
							</Button>
						</div>
						{event.attendees.map((_, attendeeIdx) => (
							<div
								// biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
								key={attendeeIdx}
								className="flex items-center gap-2.5 text-muted-foreground"
							>
								<FormField
									control={formCtx.control}
									name={`events.${idx}.attendees.${attendeeIdx}`}
									render={({ field }) => (
										<FormItem className="w-full">
											<FormControl>
												<Input
													className="p-1 h-min text-sm"
													{...field}
													value={field.value ?? undefined}
													placeholder="Attendee email"
													type="email"
												/>
											</FormControl>
										</FormItem>
									)}
								/>
								<Button
									type="button"
									size="icon"
									variant="ghost"
									className="rounded-lg"
									onClick={() => {
										const attendees = formCtx.getValues(
											`events.${idx}.attendees`,
										);
										attendees.splice(attendeeIdx, 1);
										formCtx.setValue(`events.${idx}.attendees`, attendees);
									}}
								>
									<XIcon className="w-3.5 h-3.5 shrink-0" />
								</Button>
							</div>
						))}
					</div>
				) : (
					<div className="flex items-center gap-2.5 text-muted-foreground">
						<Users className="w-3.5 h-3.5 shrink-0" />
						<span className="break-all">
							{event.attendees && event.attendees.length > 0
								? event.attendees.join(", ")
								: "-"}
						</span>
					</div>
				)}
			</CardContent>
		</Card>
	);
}
