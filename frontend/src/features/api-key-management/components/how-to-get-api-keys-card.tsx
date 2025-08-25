import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";

export default function HowToGetApiKeysCard() {
	return (
		<Card className="bg-accent text-accent-foreground">
			<CardHeader>
				<CardTitle>💡 How to get API Keys:</CardTitle>
			</CardHeader>
			<CardContent>
				<ul className="text-sm space-y-1 font-manrope">
					<li>
						<strong>Google Gemini:</strong>{" "}
						<a
							href="https://makersuite.google.com/app/apikey"
							target="_blank"
							rel="noopener noreferrer"
							className="text-blue-600 hover:underline"
						>
							Google AI Studio
						</a>
					</li>
					<li>
						<strong>OpenAI:</strong>{" "}
						<a
							href="https://platform.openai.com/api-keys"
							target="_blank"
							rel="noopener noreferrer"
							className="text-blue-600 hover:underline"
						>
							OpenAI Platform
						</a>
					</li>
				</ul>
			</CardContent>
		</Card>
	);
}
