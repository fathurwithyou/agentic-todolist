import { Button } from "@/shared/components/ui/button";
import { Calendar, LogOut, Menu } from "lucide-react";
import { useAuth } from "../hooks/use-auth";
import { useIsMobile } from "../hooks/use-mobile";
import { getInitials } from "../lib/string";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "./ui/dropdown-menu";

export default function Header() {
	const { isAuthenticated, user, logout } = useAuth();
	const isMobile = useIsMobile();

	if (!isAuthenticated) {
		return null;
	}
	
	return (
		<header className="sticky top-0 z-50 w-full glass mb-8">
			<div className="container-width">
				<div className="flex h-16 items-center justify-between">
					<div className="flex items-center space-x-3">
						<div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-sm">
							<Calendar className="w-5 h-5 text-primary-foreground" />
						</div>
						<div>
							<h1 className="text-lg font-semibold">CalendarAI</h1>
							<p className="text-xs text-muted-foreground hidden sm:block">
								Smart calendar management
							</p>
						</div>
					</div>

					{isMobile ? (
						<DropdownMenu>
							<DropdownMenuTrigger asChild>
								<Button variant="ghost" size="icon" className="rounded-lg">
									<Menu className="h-5 w-5" />
								</Button>
							</DropdownMenuTrigger>
							<DropdownMenuContent align="end" className="w-56 rounded-xl">
								<DropdownMenuLabel className="flex items-center gap-3">
									<Avatar className="h-8 w-8">
										<AvatarImage
											src={user.picture}
											alt={user.name || "User Avatar"}
										/>
										<AvatarFallback className="text-xs">
											{getInitials(user.name)}
										</AvatarFallback>
									</Avatar>
									<div className="flex flex-col">
										<span className="text-sm font-medium">{user.name}</span>
										<span className="text-xs text-muted-foreground">{user.email}</span>
									</div>
								</DropdownMenuLabel>
								<DropdownMenuSeparator />
								<DropdownMenuItem onClick={logout} className="text-destructive">
									<LogOut className="mr-2 h-4 w-4" />
									Log out
								</DropdownMenuItem>
							</DropdownMenuContent>
						</DropdownMenu>
					) : (
						<div className="flex items-center gap-4">
							<div className="flex items-center gap-3">
								<div className="text-right hidden lg:block">
									<p className="text-sm font-medium leading-none">{user.name}</p>
									<p className="text-xs text-muted-foreground mt-1">{user.email}</p>
								</div>
								<DropdownMenu>
									<DropdownMenuTrigger asChild>
										<Button variant="ghost" className="relative h-10 w-10 rounded-xl p-0">
											<Avatar className="h-10 w-10">
												<AvatarImage
													src={user.picture}
													alt={user.name || "User Avatar"}
												/>
												<AvatarFallback>
													{getInitials(user.name)}
												</AvatarFallback>
											</Avatar>
										</Button>
									</DropdownMenuTrigger>
									<DropdownMenuContent align="end" className="w-56 rounded-xl">
										<DropdownMenuLabel className="font-normal">
											<div className="flex flex-col space-y-1">
												<p className="text-sm font-medium leading-none">{user.name}</p>
												<p className="text-xs leading-none text-muted-foreground">
													{user.email}
												</p>
											</div>
										</DropdownMenuLabel>
										<DropdownMenuSeparator />
										<DropdownMenuItem onClick={logout} className="text-destructive">
											<LogOut className="mr-2 h-4 w-4" />
											Log out
										</DropdownMenuItem>
									</DropdownMenuContent>
								</DropdownMenu>
							</div>
						</div>
					)}
				</div>
			</div>
		</header>
	);
}