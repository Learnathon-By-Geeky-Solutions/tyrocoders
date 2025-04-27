// context/AuthContext.tsx
"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import api, { authAPI } from "@/services/api";
import { toast } from "sonner";

// Helper to decode JWT and check expiration
function isTokenValid(token: string | null): boolean {
  if (!token) return false;
  try {
    const [, payload] = token.split(".");
    const decoded = JSON.parse(atob(payload));
    // exp is in seconds
    return Date.now() < decoded.exp * 1000;
  } catch {
    return false;
  }
}

interface User {
  id: string;
  name: string;
  email: string;
  // any other user fields
}

type AuthContextType = {
  isAuthenticated: boolean;
  user: User | null;
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
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Clear auth state
  const logout = useCallback(() => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("refresh_token");
    setIsAuthenticated(false);
    setUser(null);
    delete api.defaults.headers.common["Authorization"];
    toast.info("Logged out");
  }, []);

  // Refresh access token using refresh token
  const refreshAuthToken = useCallback(async (): Promise<boolean> => {
    // start loading
    setLoading(true);
    const storedRefresh = localStorage.getItem("refresh_token");
    if (!storedRefresh) {
      // no refresh token: clear state and stop loading
      logout();
      setLoading(false);
      return false;
    }
    try {
      const response = await authAPI.renewToken({
        refresh_token: storedRefresh,
      });
      // tokens and user in response.data.data
      const { access_token, refresh_token, user: newUser } = response.data.data;
      localStorage.setItem("auth_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);
      api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      setUser(newUser);
      setIsAuthenticated(true);
      return true;
    } catch {
      logout();
      return false;
    } finally {
      // always stop loading
      setLoading(false);
    }
  }, [logout]);

  // On mount: check access token validity or refresh
  useEffect(() => {
    (async () => {
      const savedAccess = localStorage.getItem("auth_token");
      if (isTokenValid(savedAccess)) {
        api.defaults.headers.common["Authorization"] = `Bearer ${savedAccess}`;
        setIsAuthenticated(true);
        // optionally setUser by fetching profile
        setLoading(false);
      } else {
        await refreshAuthToken();
      }
    })();
  }, [refreshAuthToken]);

  // Axios response interceptor: on 401 try refresh then retry
  useEffect(() => {
    const interceptor = api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalReq = error.config;
        if (error.response?.status === 401 && !originalReq._retry) {
          originalReq._retry = true;
          const success = await refreshAuthToken();
          if (success) {
            const newToken = localStorage.getItem("auth_token");
            originalReq.headers = {
              ...originalReq.headers,
              Authorization: `Bearer ${newToken}`,
            };
            return api(originalReq);
          }
        }
        return Promise.reject(error);
      }
    );
    return () => api.interceptors.response.eject(interceptor);
  }, [refreshAuthToken]);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await authAPI.signIn({ email, password });
      const {
        access_token,
        refresh_token,
        user: loggedUser,
      } = response.data.data;
      localStorage.setItem("auth_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);
      api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      setUser(loggedUser);
      setIsAuthenticated(true);
      toast.success("Signed in successfully");
    } catch (err: any) {
      toast.error(err.response?.data?.message || "Sign in failed");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (name: string, email: string, password: string) => {
    setLoading(true);
    try {
      const response = await authAPI.signUp({ name, email, password });
      const { access_token, refresh_token, user: newUser } = response.data.data;
      localStorage.setItem("auth_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);
      api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      setUser(newUser);
      setIsAuthenticated(true);
      toast.success("Account created");
    } catch (err: any) {
      toast.error(err.response?.data?.message || "Signup failed");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const requestPasswordReset = async (email: string) => {
    setLoading(true);
    try {
      await authAPI.generateResetToken({ email });
      toast.success("Reset instructions sent");
    } catch (err: any) {
      toast.error(err.response?.data?.message || "Reset request failed");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (token: string, password: string) => {
    setLoading(true);
    try {
      await authAPI.resetPassword({ token, password });
      toast.success("Password reset");
    } catch (err: any) {
      toast.error(err.response?.data?.message || "Reset failed");
      throw err;
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

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};
