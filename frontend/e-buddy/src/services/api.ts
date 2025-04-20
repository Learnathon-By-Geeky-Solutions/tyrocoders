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

// Bot APIs
export const botAPI = {
  // Create a new bot
  createBot: (data: {
    name: string;
    ai_model_name: string;
    description: string;
    is_active: boolean;
    website_url: string;
    initial_message?: string;
    faq_info?: string;
    contact_info?: string;
  }) => api.post("/chatbot/create", data),
  
  // Get all bots for the current user
  getAllBots: () => api.get("/chatbot/get-all-chatbots"),
  
  // Get a specific bot by ID
  getBot: (botId: string) => api.get(`/chatbot/${botId}`),
  
  // Update an existing bot
  updateBot: (
    botId: string,
    data: {
      name?: string;
      ai_model_name?: string;
      description?: string;
      is_active?: boolean;
      website_url?: string;
      initial_message?: string;
      faq_info?: string;
      contact_info?: string;
    }
  ) => api.put(`/bots/${botId}`, data),
  
  // File upload
  fileUpload : (botId: string) => api.post(`/chatbot/${botId}/files`),

  // Delete a bot
  deleteBot: (botId: string) => api.delete(`/chatbot/${botId}`),
  
  // Toggle bot active status
  toggleBotStatus: (botId: string, isActive: boolean) => 
    api.patch(`/chatbot/${botId}/status`, { is_active: isActive }),
  
  // Get bot analytics
  getBotAnalytics: (botId: string, period?: string) => 
    api.get(`/chatbot/${botId}/analytics`, { params: { period } }),
};


export const chatAPI = {
  /**
   * Start a new conversation with the bot.
   * POST /api/v1/chatbot-conversation/chat/{chatbot_id}
   */
  startConversation: (chatbotId: string) =>
    api.post(`/chatbot-conversation/chat/${chatbotId}`),

  continueConversation: (conversationId: string, userMessage: string) =>
    api.post(`/chatbot-conversation/continue-conversation/${conversationId}`, {
      user_message: userMessage,
    }),
};

export default api;