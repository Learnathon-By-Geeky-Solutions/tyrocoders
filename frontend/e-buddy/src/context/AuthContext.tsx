"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { authAPI } from "@/services/api";
import { toast } from "sonner";

type AuthContextType = {
  isAuthenticated: boolean;
  user: any | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  requestPasswordReset: (email: string) => Promise<void>;
  resetPassword: (token: string, password: string) => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(
    !!localStorage.getItem("auth_token")
  );
  const [user, setUser] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    // Check token validity on app load
    const token = localStorage.getItem("auth_token");
    if (token) {
      setIsAuthenticated(true);
      // TODO: Fetch user profile if needed
    }
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await authAPI.signIn({ email, password });
      const { token, user } = response.data;

      localStorage.setItem("auth_token", token);
      console.log('auth token: ', token);
      setIsAuthenticated(true);
      setUser(user);
      toast.success("Successfully signed in!");
    } catch (error: any) {
      console.error("Login error:", error);
      toast.error(
        error.response?.data?.message || "Failed to sign in. Please try again."
      );
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (name: string, email: string, password: string) => {
    setLoading(true);
    try {
      const response = await authAPI.signUp({ name, email, password });
      const { token, user } = response.data;

      localStorage.setItem("auth_token", token);
      setIsAuthenticated(true);
      setUser(user);
      toast.success("Account created successfully!");
    } catch (error: any) {
      console.error("Signup error:", error);
      toast.error(
        error.response?.data?.message ||
          "Failed to create account. Please try again."
      );
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    setIsAuthenticated(false);
    setUser(null);
    toast.info("You have been logged out");
  };

  const requestPasswordReset = async (email: string) => {
    setLoading(true);
    try {
      await authAPI.generateResetToken({ email });
      toast.success("Password reset instructions sent to your email");
    } catch (error: any) {
      console.error("Password reset request error:", error);
      toast.error(
        error.response?.data?.message ||
          "Failed to request password reset. Please try again."
      );
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (token: string, password: string) => {
    setLoading(true);
    try {
      await authAPI.resetPassword({ token, password });
      toast.success("Password has been reset successfully");
    } catch (error: any) {
      console.error("Password reset error:", error);
      toast.error(
        error.response?.data?.message ||
          "Failed to reset password. Please try again."
      );
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        loading,
        login,
        signup,
        logout,
        requestPasswordReset,
        resetPassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
