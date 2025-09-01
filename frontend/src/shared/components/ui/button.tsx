// frontend/src/shared/components/ui/button.tsx
import { Slot } from "@radix-ui/react-slot";
import { type VariantProps, cva } from "class-variance-authority";
import type * as React from "react";

import { cn } from "@/shared/lib/utils";

const buttonVariants = cva(
	"inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl font-medium transition-all duration-200 disabled:pointer-events-none disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 active:scale-[0.98] relative overflow-hidden",
	{
		variants: {
			variant: {
				default:
					"bg-gradient-to-b from-primary to-primary/90 text-primary-foreground shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 hover:from-primary/95 hover:to-primary/85 border border-primary/20",
				destructive:
					"bg-gradient-to-b from-destructive to-destructive/90 text-white shadow-lg shadow-destructive/25 hover:shadow-xl hover:shadow-destructive/30 hover:from-destructive/95 hover:to-destructive/85",
				outline:
					"border-2 border-border/60 bg-background/50 backdrop-blur-sm hover:bg-accent/80 hover:text-accent-foreground hover:border-border/80 shadow-sm hover:shadow-md",
				secondary:
					"bg-gradient-to-b from-secondary to-secondary/90 text-secondary-foreground shadow-md hover:shadow-lg hover:from-secondary/95 hover:to-secondary/85",
				ghost:
					"hover:bg-accent/80 hover:text-accent-foreground backdrop-blur-sm rounded-lg",
				link: "text-primary underline-offset-4 hover:underline",
			},
			size: {
				default: "h-11 px-6 py-3 text-sm",
				sm: "h-9 px-4 text-xs rounded-lg",
				lg: "h-13 px-8 text-base rounded-xl",
				icon: "h-11 w-11",
			},
		},
		defaultVariants: {
			variant: "default",
			size: "default",
		},
	},
);

function Button({
	className,
	variant,
	size,
	asChild = false,
	...props
}: React.ComponentProps<"button"> &
	VariantProps<typeof buttonVariants> & {
		asChild?: boolean;
	}) {
	const Comp = asChild ? Slot : "button";

	return (
		<Comp
			data-slot="button"
			className={cn(buttonVariants({ variant, size, className }))}
			{...props}
		/>
	);
}

export { Button, buttonVariants };