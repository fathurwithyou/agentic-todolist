// frontend/src/shared/components/ui/input.tsx
import * as React from "react"

import { cn } from "@/shared/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "flex h-12 w-full rounded-xl border border-border/40 bg-background/60 backdrop-blur-sm px-4 py-3 text-sm transition-all duration-200",
        "placeholder:text-muted-foreground/60",
        "hover:border-border/70 hover:bg-background/80",
        "focus:border-primary/50 focus:bg-background focus:outline-none focus:ring-4 focus:ring-primary/10",
        "disabled:cursor-not-allowed disabled:opacity-50",
        "file:border-0 file:bg-transparent file:text-sm file:font-medium",
        "shadow-sm focus:shadow-md",
        className
      )}
      {...props}
    />
  )
}

export { Input }