import { cn } from "@/shared/lib/utils";

function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
	return (
		<div
			data-slot="skeleton"
			className={cn(
				"animate-pulse rounded-lg bg-gradient-to-r from-muted/50 to-muted/30",
				className
			)}
			{...props}
		/>
	);
}

export { Skeleton };