import { Button } from "@/shared/components/ui/button";
import { Calendar, LogOut } from "lucide-react";
import { useAuth } from "../hooks/use-auth";
import { useIsMobile } from "../hooks/use-mobile";
import { getInitials } from "../lib/string";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuTrigger,
} from "./ui/dropdown-menu";

export default function Header() {
	const { isAuthenticated, user, logout } = useAuth();
	const isMobile = useIsMobile();

	if (!isAuthenticated) {
		return null;
	}
	return (
		<div className="flex items-center justify-between">
			<div className="flex items-center space-x-4">
				<div className="w-12 h-12 bg-accent rounded-full flex items-center justify-center">
					<Calendar className="w-6 h-6 text-accent-foreground" />
				</div>
				<div>
					<h1 className="text-2xl font-bold font-geist">CalendarAI</h1>
					<p className="text-sm text-muted-foreground font-manrope">
						Transform text to calendar events
					</p>
				</div>
			</div>

			{isMobile ? (
				<DropdownMenu>
					<DropdownMenuTrigger asChild>
						<Avatar className="cursor-pointer">
							<AvatarImage
								src={user.picture}
								alt={user.name || "User Avatar"}
							/>
							<AvatarFallback>{getInitials(user.name)}</AvatarFallback>
						</Avatar>
					</DropdownMenuTrigger>
					<DropdownMenuContent align="end">
						<DropdownMenuLabel>Hi, {user.name}!</DropdownMenuLabel>
						<DropdownMenuItem onClick={logout}>Log out</DropdownMenuItem>
					</DropdownMenuContent>
				</DropdownMenu>
			) : (
				<div className="flex items-center space-x-4">
					<div className="flex items-center space-x-2">
						<div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
							<Avatar>
								<AvatarImage
									src={user.picture}
									alt={user.name || "User Avatar"}
								/>
								<AvatarFallback>{getInitials(user.name)}</AvatarFallback>
							</Avatar>
						</div>
						<div className="text-right">
							<p className="text-sm font-medium font-manrope">
								Hi, {user.name}!
							</p>
						</div>
					</div>
					<Button
						variant="outline"
						size="sm"
						onClick={logout}
						className="font-manrope bg-transparent"
					>
						<LogOut className="w-4 h-4 mr-1" />
						Logout
					</Button>
				</div>
			)}
		</div>
	);
}
