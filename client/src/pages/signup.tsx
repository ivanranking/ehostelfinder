import { useState, useEffect } from "react";
import { Link } from "wouter";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { Eye, EyeOff, ArrowLeft, User, UserPlus, Shield } from "lucide-react";
import { FaGoogle } from "react-icons/fa";

export default function Signup() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { toast } = useToast();

  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      window.location.href = "/";
    }
  }, [isAuthenticated, authLoading]);

  const handleReplitSignup = () => {
    setIsLoading(true);
    window.location.href = "/api/login";
  };

  const handleGoogleSignup = () => {
    setIsLoading(true);
    window.location.href = "/api/auth/google";
  };

  const handleEmailSignup = (e: React.FormEvent) => {
    e.preventDefault();
    toast({
      title: "Coming Soon",
      description: "Email registration will be available soon. Please use Replit authentication for now.",
    });
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <Link href="/" className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-6">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to E-Hostel
          </Link>
          <h2 className="text-3xl font-bold text-slate-900">Create account</h2>
          <p className="mt-2 text-slate-600">Start your journey to find the perfect student accommodation</p>
        </div>

        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-center">Sign Up</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Authentication Options */}
            <div className="space-y-3">
              <Button
                onClick={handleGoogleSignup}
                disabled={isLoading}
                variant="outline"
                className="w-full h-12 text-lg border-red-200 hover:bg-red-50"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-red-500 border-t-transparent rounded-full animate-spin mr-2" />
                ) : (
                  <FaGoogle className="w-5 h-5 mr-2 text-red-500" />
                )}
                Sign up with Google
              </Button>

              <Button
                onClick={handleReplitSignup}
                disabled={isLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 h-12 text-lg"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                ) : (
                  <User className="w-5 h-5 mr-2" />
                )}
                Sign up with Replit
              </Button>
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <Separator className="w-full" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-slate-500">Or create account with email</span>
              </div>
            </div>

            {/* Email Signup Form */}
            <form onSubmit={handleEmailSignup} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="firstName">First name</Label>
                  <Input
                    id="firstName"
                    name="firstName"
                    type="text"
                    autoComplete="given-name"
                    required
                    placeholder="John"
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="lastName">Last name</Label>
                  <Input
                    id="lastName"
                    name="lastName"
                    type="text"
                    autoComplete="family-name"
                    required
                    placeholder="Doe"
                    className="mt-1"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="email">Email address</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  placeholder="john.doe@student.ac.ug"
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="university">University</Label>
                <select
                  id="university"
                  name="university"
                  required
                  className="mt-1 block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select your university</option>
                  <option value="Makerere University">Makerere University</option>
                  <option value="MUBS">Makerere University Business School (MUBS)</option>
                </select>
              </div>

              <div>
                <Label htmlFor="password">Password</Label>
                <div className="relative mt-1">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="new-password"
                    required
                    placeholder="Create a strong password"
                    className="pr-10"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-slate-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-slate-400" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <Label htmlFor="confirmPassword">Confirm password</Label>
                <div className="relative mt-1">
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    autoComplete="new-password"
                    required
                    placeholder="Confirm your password"
                    className="pr-10"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4 text-slate-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-slate-400" />
                    )}
                  </button>
                </div>
              </div>

              <div className="flex items-center">
                <input
                  id="terms"
                  name="terms"
                  type="checkbox"
                  required
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-300 rounded"
                />
                <label htmlFor="terms" className="ml-2 block text-sm text-slate-700">
                  I agree to the{" "}
                  <a href="#" className="text-blue-600 hover:text-blue-500">Terms of Service</a>
                  {" "}and{" "}
                  <a href="#" className="text-blue-600 hover:text-blue-500">Privacy Policy</a>
                </label>
              </div>

              <Button
                type="submit"
                variant="outline"
                className="w-full h-12"
                disabled
              >
                <UserPlus className="w-4 h-4 mr-2" />
                Create Account (Coming Soon)
              </Button>
            </form>

            <div className="text-center">
              <span className="text-slate-600">Already have an account? </span>
              <Link href="/login" className="font-medium text-blue-600 hover:text-blue-500">
                Sign in
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Benefits */}
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
            <Shield className="w-5 h-5 mr-2 text-blue-600" />
            Why create an E-Hostel account?
          </h3>
          <ul className="space-y-2 text-sm text-slate-600">
            <li className="flex items-center">
              <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-3"></div>
              Book hostels directly with verified providers
            </li>
            <li className="flex items-center">
              <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-3"></div>
              Save your favorite accommodations
            </li>
            <li className="flex items-center">
              <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-3"></div>
              Track your booking history and status
            </li>
            <li className="flex items-center">
              <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-3"></div>
              Get personalized recommendations
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}