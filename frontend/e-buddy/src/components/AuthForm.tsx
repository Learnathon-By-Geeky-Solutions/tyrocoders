"use client"

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Checkbox } from "@/components/ui/checkbox";
import { useAuth } from "@/context/AuthContext";
import { Eye, EyeOff, Mail, Lock, User, LogIn, UserPlus } from "lucide-react";
import { toast } from "sonner";

const AuthForm = () => {
  const { login, signup, loading } = useAuth();
  const [activeTab, setActiveTab] = useState<string>("signin");
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState<boolean>(false);
  const [rememberMe, setRememberMe] = useState<boolean>(false);

  // Sign In form state
  const [signInData, setSignInData] = useState({
    email: "",
    password: "",
  });

  // Sign Up form state
  const [signUpData, setSignUpData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  // Form errors
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSignInChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setSignInData((prev) => ({ ...prev, [name]: value }));

    // Clear error when user types
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleSignUpChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setSignUpData((prev) => ({ ...prev, [name]: value }));

    // Clear error when user types
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }

    // Check password match
    if (
      name === "confirmPassword" ||
      (name === "password" && signUpData.confirmPassword)
    ) {
      if (name === "password" && value !== signUpData.confirmPassword) {
        setErrors((prev) => ({
          ...prev,
          confirmPassword: "Passwords do not match",
        }));
      } else if (name === "confirmPassword" && value !== signUpData.password) {
        setErrors((prev) => ({
          ...prev,
          confirmPassword: "Passwords do not match",
        }));
      } else {
        setErrors((prev) => ({ ...prev, confirmPassword: "" }));
      }
    }
  };

  // ... keep existing code (validation functions)

  const validateSignInForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!signInData.email) {
      newErrors.email = "Email is required";
    } else if (!validateEmail(signInData.email)) {
      newErrors.email = "Please enter a valid email";
    }

    if (!signInData.password) {
      newErrors.password = "Password is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateSignUpForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!signUpData.name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!signUpData.email) {
      newErrors.email = "Email is required";
    } else if (!validateEmail(signUpData.email)) {
      newErrors.email = "Please enter a valid email";
    }

    if (!signUpData.password) {
      newErrors.password = "Password is required";
    } else if (signUpData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    if (!signUpData.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (signUpData.password !== signUpData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateSignInForm()) {
      return;
    }

    try {
      await login(signInData.email, signInData.password);
      // Redirect or show success will be handled by the AuthContext
    } catch (error) {
      // Error handling is done in AuthContext
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateSignUpForm()) {
      return;
    }

    try {
      await signup(signUpData.name, signUpData.email, signUpData.password);
      // Redirect or show success will be handled by the AuthContext
    } catch (error) {
      // Error handling is done in AuthContext
    }
  };

  const handleForgotPassword = () => {
    // For now, just a placeholder
    toast.info("Password reset functionality would be implemented here.");
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  return (
    <Card className="w-full max-w-sm mx-auto shadow-lg border border-gray-200 bg-white overflow-hidden">
      <CardHeader className="space-y-1 bg-gray-50 pb-12">
        <CardTitle className="text-2xl text-center text-dark">
          {activeTab === "signin" ? "Welcome back" : "Create an account"}
        </CardTitle>
      </CardHeader>

      <Tabs
        defaultValue="signin"
        value={activeTab}
        onValueChange={setActiveTab}
        className="w-full"
      >
        <TabsList className="grid grid-cols-2 w-[80%] mx-auto -mt-6 relative z-10 bg-gray-50 shadow-md rounded-full">
          <TabsTrigger
            value="signin"
            className="rounded-full data-[state=active]:bg-accent data-[state=active]:text-white text-gray-600"
          >
            <LogIn className="w-4 h-4 mr-2 text-accent" /> Sign In
          </TabsTrigger>
          <TabsTrigger
            value="signup"
            className="rounded-full data-[state=active]:bg-accent data-[state=active]:text-white text-gray-600"
          >
            <UserPlus className="w-4 h-4 mr-2 text-accent" /> Sign Up
          </TabsTrigger>
        </TabsList>

        <TabsContent value="signin" className="space-y-4 pt-4">
          <form onSubmit={handleSignIn}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-accent">
                    <Mail className="h-5 w-5" />
                  </div>
                  <Input
                    type="email"
                    name="email"
                    placeholder="Email"
                    className={`pl-10 bg-gray-50 border ${
                      errors.email ? "border-red-500" : "border-gray-300"
                    } text-gray-900 focus:border-accent focus:ring-accent transition-all duration-200`}
                    value={signInData.email}
                    onChange={handleSignInChange}
                  />
                </div>
                {errors.email && (
                  <p className="text-red-600 text-xs">{errors.email}</p>
                )}
              </div>

              <div className="space-y-2">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-accent">
                    <Lock className="h-5 w-5" />
                  </div>
                  <Input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    placeholder="Password"
                    className={`pl-10 pr-10 bg-gray-50 border ${
                      errors.password ? "border-red-500" : "border-gray-300"
                    } text-gray-900 focus:border-accent focus:ring-accent transition-all duration-200`}
                    value={signInData.password}
                    onChange={handleSignInChange}
                  />
                  <div
                    className="absolute inset-y-0 right-0 flex items-center pr-3 cursor-pointer"
                    onClick={togglePasswordVisibility}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-500 hover:text-accent transition-colors" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-500 hover:text-accent transition-colors" />
                    )}
                  </div>
                </div>
                {errors.password && (
                  <p className="text-red-600 text-xs">{errors.password}</p>
                )}
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="remember"
                    checked={rememberMe}
                    onCheckedChange={(checked) =>
                      setRememberMe(checked as boolean)
                    }
                    className="data-[state=checked]:bg-accent data-[state=checked]:border-accent border-gray-300"
                  />
                  <label
                    htmlFor="remember"
                    className="text-sm font-medium text-gray-700"
                  >
                    Remember me
                  </label>
                </div>
                <Button
                  variant="link"
                  className="px-0 font-normal text-sm text-accent hover:opacity-90"
                  type="button"
                  onClick={handleForgotPassword}
                >
                  Forgot password?
                </Button>
              </div>
            </CardContent>
            <CardFooter>
              <Button
                type="submit"
                className="w-full bg-accent hover:opacity-90 hover:bg-accent text-white font-medium transition-colors"
                disabled={loading}
              >
                {loading ? "Signing in..." : "Sign In"}
              </Button>
            </CardFooter>
          </form>
        </TabsContent>

        <TabsContent value="signup" className="space-y-4 pt-4">
          <form onSubmit={handleSignUp}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-accent">
                    <User className="h-5 w-5" />
                  </div>
                  <Input
                    type="text"
                    name="name"
                    placeholder="Full Name"
                    className={`pl-10 bg-gray-50 border ${
                      errors.name ? "border-red-500" : "border-gray-300"
                    } text-gray-900 focus:border-accent focus:ring-accent transition-all duration-200`}
                    value={signUpData.name}
                    onChange={handleSignUpChange}
                  />
                </div>
                {errors.name && (
                  <p className="text-red-600 text-xs">{errors.name}</p>
                )}
              </div>

              <div className="space-y-2">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-accent">
                    <Mail className="h-5 w-5" />
                  </div>
                  <Input
                    type="email"
                    name="email"
                    placeholder="Email"
                    className={`pl-10 bg-gray-50 border ${
                      errors.email ? "border-red-500" : "border-gray-300"
                    } text-gray-900 focus:border-accent focus:ring-accent transition-all duration-200`}
                    value={signUpData.email}
                    onChange={handleSignUpChange}
                  />
                </div>
                {errors.email && (
                  <p className="text-red-600 text-xs">{errors.email}</p>
                )}
              </div>

              <div className="space-y-2">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-accent">
                    <Lock className="h-5 w-5" />
                  </div>
                  <Input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    placeholder="Password"
                    className={`pl-10 pr-10 bg-gray-50 border ${
                      errors.password ? "border-red-500" : "border-gray-300"
                    } text-gray-900 focus:border-accent focus:ring-accent transition-all duration-200`}
                    value={signUpData.password}
                    onChange={handleSignUpChange}
                  />
                  <div
                    className="absolute inset-y-0 right-0 flex items-center pr-3 cursor-pointer"
                    onClick={togglePasswordVisibility}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-500 hover:text-accent transition-colors" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-500 hover:text-accent transition-colors" />
                    )}
                  </div>
                </div>
                {errors.password && (
                  <p className="text-red-600 text-xs">{errors.password}</p>
                )}
              </div>

              <div className="space-y-2">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-accent">
                    <Lock className="h-5 w-5" />
                  </div>
                  <Input
                    type={showConfirmPassword ? "text" : "password"}
                    name="confirmPassword"
                    placeholder="Confirm Password"
                    className={`pl-10 pr-10 bg-gray-50 border ${
                      errors.confirmPassword
                        ? "border-red-500"
                        : "border-gray-300"
                    } text-gray-900 focus:border-accent focus:ring-accent transition-all duration-200`}
                    value={signUpData.confirmPassword}
                    onChange={handleSignUpChange}
                  />
                  <div
                    className="absolute inset-y-0 right-0 flex items-center pr-3 cursor-pointer"
                    onClick={toggleConfirmPasswordVisibility}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-500 hover:text-accent transition-colors" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-500 hover:text-accent transition-colors" />
                    )}
                  </div>
                </div>
                {errors.confirmPassword && (
                  <p className="text-red-600 text-xs">
                    {errors.confirmPassword}
                  </p>
                )}
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="terms"
                  className="data-[state=checked]:bg-accent data-[state=checked]:border-accent border-gray-300"
                />
                <label
                  htmlFor="terms"
                  className="text-sm font-medium text-gray-700"
                >
                  I agree to the{" "}
                  <span className="text-accent hover:opacity-90 cursor-pointer">
                    Terms of Service
                  </span>
                </label>
              </div>
            </CardContent>

            <CardFooter>
              <Button
                type="submit"
                className="w-full bg-accent hover:opacity-90 hover:bg-accent text-white font-medium transition-colors"
                disabled={loading}
              >
                {loading ? "Creating account..." : "Create Account"}
              </Button>
            </CardFooter>
          </form>
        </TabsContent>
      </Tabs>
    </Card>
  );
};

export default AuthForm;
