import { Badge } from "@/shared/components/ui/badge";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { capitalize } from "@/shared/lib/string";
import { useGetListApiKeysQuery } from "@/shared/repositories/api-key/query";
import { CheckCircle2Icon, XCircleIcon, Key } from "lucide-react";

export default function ApiKeyStatusCard() {
	const { data } = useGetListApiKeysQuery();

	return (
		<div className="rounded-xl bg-muted/10 border border-border/30 p-5 space-y-3 transition-all duration-200 hover:border-border/50">
			<div className="flex items-center gap-2.5 text-sm font-medium text-foreground/90">
				<Key className="w-4 h-4 text-muted-foreground" />
				<span>API Key Status</span>
			</div>
			<div className="flex flex-row gap-2.5 flex-wrap">
				{!data ? (
					<>
						<Skeleton className="h-7 w-28 rounded-lg" />
						<Skeleton className="h-7 w-28 rounded-lg" />
					</>
				) : (
					Object.entries(data.api_keys).map(([provider, isSet]) => (
						<Badge 
							key={provider} 
							variant={isSet ? "success" : "destructive"}
							className="gap-1.5 px-3 py-1 rounded-lg font-normal transition-all duration-150"
						>
							{isSet ? (
								<CheckCircle2Icon className="w-3.5 h-3.5" />
							) : (
								<XCircleIcon className="w-3.5 h-3.5" />
							)}
							{capitalize(provider)}
						</Badge>
					))
				)}
			</div>
		</div>
	);
}