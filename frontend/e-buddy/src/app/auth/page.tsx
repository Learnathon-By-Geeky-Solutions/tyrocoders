"use client";

import React from "react";
import AuthForm from "@/components/AuthForm";
import { useAuth } from "@/context/AuthContext";
import { Navigate } from "react-router-dom";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

const AuthPage = () => {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0F151C] p-4">
      <div className="w-full max-w-sm">
        

        <AuthForm />

        <p className="text-center text-sm text-gray-500 mt-6">
          By using this service, you agree to our Terms of Service and Privacy
          Policy.
        </p>
      </div>
    </div>
  );
};

export default AuthPage;