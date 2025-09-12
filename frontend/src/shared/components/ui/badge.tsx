// frontend/src/shared/components/ui/badge.tsx
import { Slot } from "@radix-ui/react-slot";
import { type VariantProps, cva } from "class-variance-authority";
import type * as React from "react";

import { cn } from "@/shared/lib/utils";

const badgeVariants = cva(
	"inline-flex items-center rounded-xl px-3 py-1.5 text-xs font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 shadow-sm backdrop-blur-sm",
	{
		variants: {
			variant: {
				default:
					"bg-primary/10 text-primary hover:bg-primary/20 border border-primary/20",
				secondary:
					"bg-secondary/80 text-secondary-foreground hover:bg-secondary border border-secondary/40",
				destructive:
					"bg-destructive/10 text-destructive hover:bg-destructive/20 border border-destructive/20",
				outline:
					"border border-border/60 text-foreground hover:bg-accent hover:text-accent-foreground",
				success:
					"bg-green-100/80 text-green-800 dark:bg-green-900/30 dark:text-green-400 border border-green-200/50 dark:border-green-800/50",
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