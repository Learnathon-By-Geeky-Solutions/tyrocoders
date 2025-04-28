"use client";

import { useState } from "react";
import { Check, ArrowRight, ArrowLeft, Loader2 } from "lucide-react";
import axios from "axios";
import { botAPI } from "@/services/api";

const MyBotsPage = () => {
  // State for tracking the current step in the wizard
  const [step, setStep] = useState(1);
  
  // State for storing all form data across steps
  const [formData, setFormData] = useState({
    botName: "",
    model: "",
    url: "",
    initialMessage: "",
    faqInfo: "",
    contactNumber: "",
    isActive: true,  // Default value
    description: "",
  });
  
  // Loading and error states for API interactions
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Handler for form input changes
  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Navigation functions for the wizard
  const nextStep = () => setStep((prev) => Math.min(prev + 1, 3));
  const prevStep = () => setStep((prev) => Math.max(prev - 1, 1));

  // Form submission handler with API call
  // Form submission handler with API call
  const handleSubmit = async () => {
    try {
      // Transform form data to match the API structure
      const apiData = {
        name: formData.botName,
        ai_model_name: formData.model === "gpt" ? "GPT-4o" : formData.model,
        description: formData.description || "A chatbot for my online store",
        is_active: true,
        website_url: formData.url,
        initial_message: formData.initialMessage,
        faq_info: formData.faqInfo,
        contact_info: formData.contactNumber
      };
      
      // Log the data that will be sent to the API
      console.log("Data to be sent to API:", apiData);
      
      // Set loading state
      setIsLoading(true);
      setError(null);
      
      // Use the imported botAPI service instead of axios directly
      const response = await botAPI.createBot(apiData);
      
      // Handle success
      setIsLoading(false);
      setSuccess(true);
      console.log('Bot created successfully:', response.data);
      
      // Show success message
      setTimeout(() => {
        alert("Bot setup completed! Ready to deploy.");
      }, 500);
      
    } catch (err) {
      setIsLoading(false);
      // Type assertion
      const error = err as any; // or as Error or as AxiosError
      setError(error.response?.data?.message || "Failed to create bot. Please try again.");
      console.error('Error creating bot:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-bot-background to-white flex items-center justify-center p-4">
      <div className="w-full max-w-3xl bot-card">
        <div className="mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-bot-primary to-bot-secondary bg-clip-text text-transparent">
            Bot Builder Wizard
          </h1>
          <p className="text-gray-500 mt-2">
            Complete the steps below to set up your custom bot
          </p>
        </div>

        {/* Modern Step Indicator */}
        <div className="relative flex justify-between mb-16 px-6">
          {[1, 2, 3].map((s, idx) => (
            <div key={s} className="flex flex-col items-center relative z-10">
              <div
                className={`step-bubble ${
                  step === s
                    ? "step-bubble-active animate-pulse-subtle"
                    : step > s
                    ? "step-bubble-completed"
                    : "step-bubble-inactive"
                }`}
              >
                {step > s ? <Check className="w-5 h-5" /> : s}
              </div>
              <span
                className={`mt-3 text-sm font-medium ${
                  step === s
                    ? "text-bot-primary"
                    : step > s
                    ? "text-bot-success"
                    : "text-gray-500"
                }`}
              >
                {s === 1
                  ? "Basic Info"
                  : s === 2
                  ? "Data Source"
                  : "Configuration"}
              </span>

              {/* Connector lines between steps */}
              {idx < 2 && (
                <div
                  className={`step-connector ${
                    step > s ? "step-connector-active" : ""
                  }`}
                ></div>
              )}
            </div>
          ))}
        </div>

        {/* Form Container */}
        <div className="transition-all duration-300">
          {/* Step 1: Basic Information */}
          {step === 1 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6">
                Basic Information
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-700 font-medium mb-2">
                    Bot Name
                  </label>
                  <input
                    type="text"
                    name="botName"
                    value={formData.botName}
                    onChange={handleChange}
                    placeholder="Give your bot a name"
                    className="w-full border border-gray-200 rounded-lg px-4 py-3 shadow-sm form-input-focus"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 font-medium mb-2">
                    Description
                  </label>
                  <input
                    type="text"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    placeholder="A short description of your bot"
                    className="w-full border border-gray-200 rounded-lg px-4 py-3 shadow-sm form-input-focus"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 font-medium mb-2">
                    AI Model
                  </label>
                  <select
                    name="model"
                    value={formData.model}
                    onChange={handleChange}
                    className="w-full border border-gray-200 rounded-lg px-4 py-3 shadow-sm form-input-focus"
                  >
                    <option value="">Select a model</option>
                    <option value="gemini">Gemini-Flash</option>
                    <option value="gpt">GPT-4o</option>
                    <option value="claude">Claude</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>
              </div>
              <div className="mt-10 flex justify-end">
                <button
                  onClick={nextStep}
                  className="btn-primary flex items-center gap-2"
                >
                  Next <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Data Source */}
          {step === 2 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6">
                Data Source
              </h2>
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Website URL to Scrape
                </label>
                <div className="relative">
                  <input
                    type="url"
                    name="url"
                    value={formData.url}
                    onChange={handleChange}
                    placeholder="https://example.com"
                    className="w-full border border-gray-200 rounded-lg px-4 py-3 shadow-sm form-input-focus"
                  />
                  <div className="absolute right-3 top-3 text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                    Public URL
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  We'll extract data from this website to train your bot
                </p>
              </div>
              <div className="mt-10 flex justify-between">
                <button
                  onClick={prevStep}
                  className="btn-secondary flex items-center gap-2"
                >
                  <ArrowLeft className="w-4 h-4" /> Back
                </button>
                <button
                  onClick={nextStep}
                  className="btn-primary flex items-center gap-2"
                >
                  Next <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Bot Configuration */}
          {step === 3 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6">
                Bot Configuration
              </h2>
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Initial Message
                </label>
                <textarea
                  name="initialMessage"
                  value={formData.initialMessage}
                  onChange={handleChange}
                  placeholder="Hi there! How can I help you today?"
                  className="w-full border border-gray-200 rounded-lg px-4 py-3 shadow-sm form-input-focus resize-none"
                  rows={2}
                ></textarea>
                <p className="text-xs text-gray-500 mt-1">
                  First message users will see when they interact with your bot
                </p>
              </div>
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Company Information / FAQ
                </label>
                <textarea
                  name="faqInfo"
                  value={formData.faqInfo}
                  onChange={handleChange}
                  placeholder="Add company details, FAQs, or any information your bot should know"
                  className="w-full border border-gray-200 rounded-lg px-4 py-3 shadow-sm form-input-focus resize-none"
                  rows={3}
                ></textarea>
              </div>
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Customer Support Contact
                </label>
                <input
                  type="text"
                  name="contactNumber"
                  value={formData.contactNumber}
                  onChange={handleChange}
                  placeholder="+1 (555) 123-4567"
                  className="w-full border border-gray-200 rounded-lg px-4 py-3 shadow-sm form-input-focus"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Your bot will share this when users need human assistance
                </p>
              </div>
              <div className="mt-10 flex justify-between">
                <button
                  onClick={prevStep}
                  className="btn-secondary flex items-center gap-2"
                  disabled={isLoading}
                >
                  <ArrowLeft className="w-4 h-4" /> Back
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={isLoading}
                  className={`${isLoading 
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-bot-success to-emerald-500'
                    } text-white font-medium py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] shadow-md hover:shadow-lg flex items-center gap-2`}
                >

                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Creating...
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4" /> Complete Setup
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
          
          {/* Error message display */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg border border-red-200">
              {error}
            </div>
          )}
          
          {/* Success message */}
          {success && !isLoading && (
            <div className="mt-4 p-3 bg-green-50 text-green-700 rounded-lg border border-green-200">
              Bot successfully created!
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MyBotsPage;