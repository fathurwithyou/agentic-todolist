import { Slot } from "@radix-ui/react-slot";
import { type VariantProps, cva } from "class-variance-authority";
import type * as React from "react";

import { cn } from "@/shared/lib/utils";

const badgeVariants = cva(
	"inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
	{
		variants: {
			variant: {
				default:
					"bg-primary/10 text-primary hover:bg-primary/20",
				secondary:
					"bg-secondary text-secondary-foreground hover:bg-secondary/80",
				destructive:
					"bg-destructive/10 text-destructive hover:bg-destructive/20",
				outline:
					"border border-border text-foreground hover:bg-accent hover:text-accent-foreground",
				success:
					"bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400",
			},
		},
		defaultVariants: {
			variant: "default",
		},
	},
);

function Badge({
	className,
	variant,
	asChild = false,
	...props
}: React.ComponentProps<"span"> &
	VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
	const Comp = asChild ? Slot : "span";

	return (
		<Comp
			data-slot="badge"
			className={cn(badgeVariants({ variant }), className)}
			{...props}
		/>
	);
}

export { Badge, badgeVariants };