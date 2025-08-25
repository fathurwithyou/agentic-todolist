import "@/shared/styles/globals.css";
import AppPages from "./pages/app";
import RootLayout from "./shared/components/layouts/root-layout";

export default function AppWrapper() {
	return (
		<RootLayout>
			<AppPages />
		</RootLayout>
	);
}
