import { ExternalLink, Info } from "lucide-react";

export default function HowToGetApiKeysCard() {
	return (
		<div className="rounded-xl bg-primary/5 border border-primary/10 p-5 space-y-3 transition-all duration-200">
			<div className="flex items-center gap-2.5 text-sm font-medium text-foreground/90">
				<Info className="w-4 h-4 text-primary/70" />
				<span>How to get API Keys</span>
			</div>
			<div className="space-y-2.5 text-sm">
				<a
					href="https://makersuite.google.com/app/apikey"
					target="_blank"
					rel="noopener noreferrer"
					className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors duration-150 group"
				>
					<span className="font-medium">Google Gemini:</span>
					<span className="text-primary/80 group-hover:text-primary transition-colors duration-150">Google AI Studio</span>
					<ExternalLink className="w-3 h-3 opacity-50 group-hover:opacity-100 transition-opacity duration-150" />
				</a>
				<a
					href="https://platform.openai.com/api-keys"
					target="_blank"
					rel="noopener noreferrer"
					className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors duration-150 group"
				>
					<span className="font-medium">OpenAI:</span>
					<span className="text-primary/80 group-hover:text-primary transition-colors duration-150">OpenAI Platform</span>
					<ExternalLink className="w-3 h-3 opacity-50 group-hover:opacity-100 transition-opacity duration-150" />
				</a>
			</div>
		</div>
	);
}