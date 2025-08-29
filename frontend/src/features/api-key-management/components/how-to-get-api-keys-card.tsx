import { ExternalLink, Info } from "lucide-react";

export default function HowToGetApiKeysCard() {
	return (
		<div className="rounded-xl bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900/50 p-4 space-y-3">
			<div className="flex items-center gap-2 text-sm font-medium text-blue-900 dark:text-blue-400">
				<Info className="w-4 h-4" />
				<span>How to get API Keys</span>
			</div>
			<div className="space-y-2 text-sm text-blue-800 dark:text-blue-300">
				<a
					href="https://makersuite.google.com/app/apikey"
					target="_blank"
					rel="noopener noreferrer"
					className="flex items-center gap-2 hover:underline"
				>
					<span className="font-medium">Google Gemini:</span>
					<span className="text-blue-600 dark:text-blue-400">Google AI Studio</span>
					<ExternalLink className="w-3 h-3" />
				</a>
				<a
					href="https://platform.openai.com/api-keys"
					target="_blank"
					rel="noopener noreferrer"
					className="flex items-center gap-2 hover:underline"
				>
					<span className="font-medium">OpenAI:</span>
					<span className="text-blue-600 dark:text-blue-400">OpenAI Platform</span>
					<ExternalLink className="w-3 h-3" />
				</a>
			</div>
		</div>
	);
}