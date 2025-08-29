import { Badge } from "@/shared/components/ui/badge";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { capitalize } from "@/shared/lib/string";
import { useGetListApiKeysQuery } from "@/shared/repositories/api-key/query";
import { CheckCircle2Icon, XCircleIcon, Key } from "lucide-react";

export default function ApiKeyStatusCard() {
	const { data } = useGetListApiKeysQuery();

	return (
		<div className="rounded-xl bg-muted/30 p-4 space-y-3">
			<div className="flex items-center gap-2 text-sm font-medium">
				<Key className="w-4 h-4 text-muted-foreground" />
				<span>API Key Status</span>
			</div>
			<div className="flex flex-row gap-2 flex-wrap">
				{!data ? (
					<>
						<Skeleton className="h-6 w-24 rounded-full" />
						<Skeleton className="h-6 w-24 rounded-full" />
					</>
				) : (
					Object.entries(data.api_keys).map(([provider, isSet]) => (
						<Badge 
							key={provider} 
							variant={isSet ? "success" : "destructive"}
							className="gap-1.5"
						>
							{isSet ? (
								<CheckCircle2Icon className="w-3 h-3" />
							) : (
								<XCircleIcon className="w-3 h-3" />
							)}
							{capitalize(provider)}
						</Badge>
					))
				)}
			</div>
		</div>
	);
}