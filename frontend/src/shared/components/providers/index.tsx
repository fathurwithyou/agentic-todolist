import { Toaster } from "@/shared/components/ui/sonner";
import ReactQueryProvider from "./react-query-provider";

export default function Providers({ children }: { children: React.ReactNode }) {
	return (
		<ReactQueryProvider>
			{children}
			<Toaster richColors />
		</ReactQueryProvider>
	);
}
