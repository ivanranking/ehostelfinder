import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { User, Menu, LogOut } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { user, isAuthenticated, isLoading } = useAuth();

  return (
    <nav className="bg-white shadow-sm border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <div className="flex-shrink-0">
              <Link href="/">
                <h1 className="text-2xl font-bold text-blue-600 cursor-pointer">E-Hostel</h1>
              </Link>
            </div>
            <div className="hidden md:flex space-x-8">
              <Link href="/" className="text-slate-700 hover:text-blue-600 transition-colors">
                Browse Hostels
              </Link>
              <Link href="/universities" className="text-slate-700 hover:text-blue-600 transition-colors">
                Universities
              </Link>
              <Link href="/how-it-works" className="text-slate-700 hover:text-blue-600 transition-colors">
                How it Works
              </Link>
              <Link href="/contact" className="text-slate-700 hover:text-blue-600 transition-colors">
                Contact
              </Link>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {isLoading ? (
              <div className="w-8 h-8 bg-slate-200 rounded-full animate-pulse"></div>
            ) : isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={user?.profileImageUrl || ""} alt={user?.firstName || "User"} />
                      <AvatarFallback>
                        {user?.firstName?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || "U"}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end">
                  <div className="flex items-center justify-start gap-2 p-2">
                    <div className="flex flex-col space-y-1 leading-none">
                      {user?.firstName && (
                        <p className="font-medium">{user.firstName} {user.lastName}</p>
                      )}
                      {user?.email && (
                        <p className="w-[200px] truncate text-sm text-slate-600">{user.email}</p>
                      )}
                    </div>
                  </div>
                  <DropdownMenuItem asChild>
                    <a href="/api/logout" className="flex items-center">
                      <LogOut className="mr-2 h-4 w-4" />
                      <span>Log out</span>
                    </a>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <>
                <Button variant="ghost" size="sm" className="hidden md:flex" asChild>
                  <a href="/api/login">
                    <User className="w-4 h-4 mr-2" />
                    Login
                  </a>
                </Button>
                <Button className="bg-blue-600 hover:bg-blue-700" asChild>
                  <a href="/api/login">Sign Up</a>
                </Button>
              </>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              <Menu className="w-5 h-5" />
            </Button>
          </div>
        </div>
        
        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-slate-200 py-4">
            <div className="flex flex-col space-y-2">
              <Link href="/" className="text-slate-700 hover:text-blue-600 transition-colors px-2 py-1">
                Browse Hostels
              </Link>
              <Link href="/universities" className="text-slate-700 hover:text-blue-600 transition-colors px-2 py-1">
                Universities
              </Link>
              <Link href="/how-it-works" className="text-slate-700 hover:text-blue-600 transition-colors px-2 py-1">
                How it Works
              </Link>
              <Link href="/contact" className="text-slate-700 hover:text-blue-600 transition-colors px-2 py-1">
                Contact
              </Link>
              {!isAuthenticated && (
                <Button variant="ghost" size="sm" className="justify-start" asChild>
                  <a href="/api/login">
                    <User className="w-4 h-4 mr-2" />
                    Login
                  </a>
                </Button>
              )}
              {isAuthenticated && (
                <Button variant="ghost" size="sm" className="justify-start" asChild>
                  <a href="/api/logout">
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </a>
                </Button>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
