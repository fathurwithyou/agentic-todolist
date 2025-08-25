import { Badge } from "@/shared/components/ui/badge";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { capitalize } from "@/shared/lib/string";
import { useGetListApiKeysQuery } from "@/shared/repositories/api-key/query";
import { CheckCircle2Icon, XCircleIcon } from "lucide-react";

export default function ApiKeyStatusCard() {
	const { data } = useGetListApiKeysQuery();

	return (
		<Card className="bg-accent text-accent-foreground">
			<CardHeader>
				<CardTitle>📊 API Key Status</CardTitle>
			</CardHeader>
			<CardContent>
				<div className="flex flex-row gap-4 flex-wrap">
					{!data ? (
						<>
							<Badge className="py-1">
								<Skeleton className="h-3 w-20 rounded-lg" />
							</Badge>
							<Badge className="py-1">
								<Skeleton className="h-3 w-20 rounded-lg" />
							</Badge>{" "}
						</>
					) : (
						Object.entries(data.api_keys).map(([provider, isSet]) => (
							<Badge key={provider} variant={isSet ? "default" : "destructive"}>
								{isSet ? <CheckCircle2Icon /> : <XCircleIcon />}
								{capitalize(provider)}: {isSet ? "Saved" : "Not Set"}
							</Badge>
						))
					)}
				</div>
			</CardContent>
		</Card>
	);
}
