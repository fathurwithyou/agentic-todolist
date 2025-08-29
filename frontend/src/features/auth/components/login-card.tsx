import { Button } from "@/shared/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/shared/components/ui/card";
import { useAuth } from "@/shared/hooks/use-auth";
import { Calendar, Sparkles, Shield, Clock, ArrowLeft } from "lucide-react";

export default function LoginCard() {
	const { loginWithGoogle, isLoading } = useAuth();

	return (
		<div className="min-h-screen flex items-center justify-center p-4 bg-background">
			<div className="w-full max-w-md">
				<Button 
					variant="ghost" 
					className="mb-8 text-muted-foreground hover:text-foreground transition-colors duration-150 border-1"
					onClick={() => window.location.href = '/'}
				>
					<ArrowLeft className="w-4 h-4 mr-2" />
					Back to home
				</Button>

				<Card className="border-0 shadow-soft">
					<CardHeader className="text-center space-y-2 px-8 pt-10 pb-8">
						<CardTitle className="text-2xl font-medium tracking-tight">
							Welcome back
						</CardTitle>
						<CardDescription className="text-muted-foreground">
							Sign in to CalendarAI to continue managing your events
						</CardDescription>
					</CardHeader>
					
					<CardContent className="px-8 pb-10">
						<div className="space-y-6">
							<Button
								onClick={loginWithGoogle}
								className="w-full h-12 text-base font-medium transition-all duration-150"
								size="lg"
								disabled={isLoading}
							>
								{isLoading ? (
									<div className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
								) : (
									<>
										<svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
											<title>Google</title>
											<path
												fill="currentColor"
												d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
											/>
											<path
												fill="currentColor"
												d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
											/>
											<path
												fill="currentColor"
												d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
											/>
											<path
												fill="currentColor"
												d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
											/>
										</svg>
										Continue with Google
									</>
								)}
							</Button>
							
							<div className="relative">
								<div className="absolute inset-0 flex items-center">
									<span className="w-full border-t border-border/40" />
								</div>
								<div className="relative flex justify-center text-xs">
									<span className="bg-card px-3 text-muted-foreground">
										Secure authentication
									</span>
								</div>
							</div>
							
							<div className="space-y-3">
								<div className="flex items-start gap-3 text-sm text-muted-foreground">
									<div className="w-8 h-8 rounded-lg bg-muted/30 flex items-center justify-center flex-shrink-0 mt-0.5">
										<Sparkles className="w-4 h-4 text-primary/60" />
									</div>
									<div>
										<p className="font-medium text-foreground/90 mb-0.5">AI-powered parsing</p>
										<p className="text-xs">Convert any text format to calendar events instantly</p>
									</div>
								</div>
								
								<div className="flex items-start gap-3 text-sm text-muted-foreground">
									<div className="w-8 h-8 rounded-lg bg-muted/30 flex items-center justify-center flex-shrink-0 mt-0.5">
										<Clock className="w-4 h-4 text-primary/60" />
									</div>
									<div>
										<p className="font-medium text-foreground/90 mb-0.5">Save hours weekly</p>
										<p className="text-xs">Automate event creation from emails, docs, and messages</p>
									</div>
								</div>
								
								<div className="flex items-start gap-3 text-sm text-muted-foreground">
									<div className="w-8 h-8 rounded-lg bg-muted/30 flex items-center justify-center flex-shrink-0 mt-0.5">
										<Shield className="w-4 h-4 text-primary/60" />
									</div>
									<div>
										<p className="font-medium text-foreground/90 mb-0.5">Enterprise security</p>
										<p className="text-xs">Your data is encrypted and never stored permanently</p>
									</div>
								</div>
							</div>
							
							<div className="pt-4 text-center">
								<p className="text-xs text-muted-foreground">
									By continuing, you agree to our{" "}
									<a href="#" className="text-primary/80 hover:text-primary transition-colors duration-150">
										Terms of Service
									</a>{" "}
									and{" "}
									<a href="#" className="text-primary/80 hover:text-primary transition-colors duration-150">
										Privacy Policy
									</a>
								</p>
							</div>
						</div>
					</CardContent>
				</Card>
				
				<div className="mt-8 text-center">
					<p className="text-sm text-muted-foreground">
						Don't have an account?{" "}
						<button 
							onClick={loginWithGoogle}
							className="text-primary/80 hover:text-primary transition-colors duration-150 font-medium"
						>
							Sign up for free
						</button>
					</p>
				</div>
			</div>
		</div>
	);
}