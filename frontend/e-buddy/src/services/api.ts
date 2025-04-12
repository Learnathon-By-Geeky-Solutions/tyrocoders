import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/v1";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth APIs
export const authAPI = {
  signUp: (data: { name: string; email: string; password: string }) =>
    api.post("/user/signup", data),

  signIn: (data: { email: string; password: string }) =>
    api.post("/user/login", data),

  renewToken: () => api.post("/user/renew-access-token"),

  generateResetToken: (data: { email: string }) =>
    api.post("/user/generate-pass-reset", data),

  resetPassword: (data: { token: string; password: string }) =>
    api.post("/user/reset-password", data),
};

export default api;
