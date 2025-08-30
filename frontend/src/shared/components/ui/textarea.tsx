import * as React from "react"

import { cn } from "@/shared/lib/utils"

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "flex min-h-[120px] w-full rounded-lg border border-border bg-background/50 px-3 py-2 text-sm transition-all resize-none",
        "placeholder:text-muted-foreground",
        "hover:border-border/80 hover:bg-background/80",
        "focus:border-primary focus:bg-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        "disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...props}
    />
  )
}

export { Textarea }