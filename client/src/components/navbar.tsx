import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { User, Menu } from "lucide-react";
import { useState } from "react";

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

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
              <a href="#" className="text-slate-700 hover:text-blue-600 transition-colors">Universities</a>
              <a href="#" className="text-slate-700 hover:text-blue-600 transition-colors">How it Works</a>
              <a href="#" className="text-slate-700 hover:text-blue-600 transition-colors">Contact</a>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" className="hidden md:flex">
              <User className="w-4 h-4 mr-2" />
              Login
            </Button>
            <Button className="bg-blue-600 hover:bg-blue-700">
              Sign Up
            </Button>
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
              <a href="#" className="text-slate-700 hover:text-blue-600 transition-colors px-2 py-1">Universities</a>
              <a href="#" className="text-slate-700 hover:text-blue-600 transition-colors px-2 py-1">How it Works</a>
              <a href="#" className="text-slate-700 hover:text-blue-600 transition-colors px-2 py-1">Contact</a>
              <Button variant="ghost" size="sm" className="justify-start">
                <User className="w-4 h-4 mr-2" />
                Login
              </Button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
