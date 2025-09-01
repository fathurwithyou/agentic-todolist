// frontend/src/shared/components/ui/textarea.tsx
import * as React from "react"

import { cn } from "@/shared/lib/utils"

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "flex min-h-[140px] w-full rounded-xl border border-border/40 bg-background/60 backdrop-blur-sm px-4 py-3 text-sm transition-all duration-200 resize-none",
        "placeholder:text-muted-foreground/60",
        "hover:border-border/70 hover:bg-background/80",
        "focus:border-primary/50 focus:bg-background focus:outline-none focus:ring-4 focus:ring-primary/10",
        "disabled:cursor-not-allowed disabled:opacity-50",
        "shadow-sm focus:shadow-md",
        className
      )}
      {...props}
    />
  )
}

export { Textarea }