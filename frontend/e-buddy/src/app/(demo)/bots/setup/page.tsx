"use client";

import { useState } from "react";
import { Check, ArrowRight, ArrowLeft, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { botAPI } from "@/services/api";

const MyBotsPage = () => {
  const totalSteps = 3;
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    botName: "",
    model: "",
    url: "",
    sitemapUrl: "",
    initialMessage: "",
    faqInfo: "",
    contactNumber: "",
    description: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const nextStep = () => {
    if (step < totalSteps) setStep(step + 1);
  };
  const prevStep = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = async () => {
    setError(null);
    setIsLoading(true);
    try {
      const apiData: any = {
        name: formData.botName,
        ai_model_name: formData.model === "gpt" ? "GPT-4o" : formData.model,
        description: formData.description || "A chatbot for my online store",
        is_active: true,
        website_url: formData.url,
        initial_message: formData.initialMessage,
        faq_info: formData.faqInfo,
        contact_info: formData.contactNumber,
      };
      if (formData.sitemapUrl) {
        apiData.sitemap_url = formData.sitemapUrl;
      }

      const response = await botAPI.createBot(apiData);
      setSuccess(true);
      setTimeout(() => alert("Bot setup completed! Ready to deploy."), 500);
    } catch (err: any) {
      setError(
        err.response?.data?.message || "Failed to create bot. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-bot-background to-white flex items-center justify-center p-6">
      <Card className="w-full max-w-3xl shadow-lg">
        <CardHeader>
          <CardTitle className="text-3xl font-bold">
            <span className="bg-gradient-to-r from-bot-primary to-bot-secondary bg-clip-text text-transparent">
              Bot Builder Wizard
            </span>
          </CardTitle>
          <p className="text-gray-500 mt-1">
            Fill in the details to create your custom chatbot
          </p>
        </CardHeader>
        <CardContent>
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 h-2 rounded-full mb-6">
            <div
              className="h-2 rounded-full bg-bot-primary transition-width"
              style={{ width: `${(step / totalSteps) * 100}%` }}
            />
          </div>

          {/* Steps Indicator */}
          <div className="flex justify-between mb-8">
            {["Basic Info", "Data Source", "Configuration"].map(
              (label, idx) => {
                const s = idx + 1;
                const isActive = s === step;
                const isCompleted = s < step;
                return (
                  <div key={s} className="flex-1 text-center relative">
                    <div
                      className={`mx-auto w-8 h-8 flex items-center justify-center rounded-full mb-2 
                      ${
                        isCompleted
                          ? "bg-bot-success"
                          : isActive
                          ? "bg-bot-primary animate-pulse-subtle"
                          : "bg-gray-200"
                      }`}
                    >
                      {isCompleted ? (
                        <Check className="w-4 h-4 text-white" />
                      ) : (
                        s
                      )}
                    </div>
                    <span
                      className={`${
                        isActive
                          ? "text-bot-primary"
                          : isCompleted
                          ? "text-bot-success"
                          : "text-gray-400"
                      } text-sm font-medium`}
                    >
                      {label}
                    </span>
                  </div>
                );
              }
            )}
          </div>

          {/* Form Steps */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <Label htmlFor="botName" className="text-gray-700 font-medium">
                  Bot Name
                </Label>
                <Input
                  id="botName"
                  name="botName"
                  value={formData.botName}
                  onChange={handleChange}
                  placeholder="Your bot's name"
                />
              </div>
              <div>
                <Label
                  htmlFor="description"
                  className="text-gray-700 font-medium"
                >
                  Description (optional)
                </Label>
                <Input
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="Short description"
                />
              </div>
              <div>
                <Label htmlFor="model" className="text-gray-700 font-medium">
                  AI Model
                </Label>
                <Select
                  name="model"
                  onValueChange={(val) =>
                    setFormData((prev) => ({ ...prev, model: val }))
                  }
                >
                  <SelectTrigger id="model" className="w-full">
                    <SelectValue placeholder="Select a model" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gemini">Gemini-Flash</SelectItem>
                    <SelectItem value="gpt">GPT-4o</SelectItem>
                    <SelectItem value="claude">Claude</SelectItem>
                    <SelectItem value="custom">Custom</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex justify-end">
                <Button
                  onClick={nextStep}
                  disabled={!formData.botName || !formData.model}
                >
                  Next <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div>
                <Label htmlFor="url" className="text-gray-700 font-medium">
                  Website URL to Scrape
                </Label>
                <Input
                  id="url"
                  type="url"
                  name="url"
                  value={formData.url}
                  onChange={handleChange}
                  placeholder="https://example.com"
                />
                <p className="text-xs text-gray-500 mt-1">
                  We’ll extract data from this site to train your bot.
                </p>
              </div>
              <div>
                <Label
                  htmlFor="sitemapUrl"
                  className="text-gray-700 font-medium"
                >
                  Sitemap URL (optional)
                </Label>
                <Input
                  id="sitemapUrl"
                  type="url"
                  name="sitemapUrl"
                  value={formData.sitemapUrl}
                  onChange={handleChange}
                  placeholder="https://example.com/sitemap.xml"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Add a sitemap for broader content coverage (optional).
                </p>
              </div>
              <div className="flex justify-between">
                <Button variant="secondary" onClick={prevStep}>
                  <ArrowLeft className="w-4 h-4 mr-1" /> Back
                </Button>
                <Button onClick={nextStep} disabled={!formData.url}>
                  Next <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <div>
                <Label
                  htmlFor="initialMessage"
                  className="text-gray-700 font-medium"
                >
                  Initial Message
                </Label>
                <Textarea
                  id="initialMessage"
                  name="initialMessage"
                  value={formData.initialMessage}
                  onChange={handleChange}
                  placeholder="Hi there! How can I help you today?"
                  rows={2}
                />
                <p className="text-xs text-gray-500 mt-1">
                  First message users will see when they start.
                </p>
              </div>
              <div>
                <Label htmlFor="faqInfo" className="text-gray-700 font-medium">
                  Company Info / FAQ
                </Label>
                <Textarea
                  id="faqInfo"
                  name="faqInfo"
                  value={formData.faqInfo}
                  onChange={handleChange}
                  placeholder="Add FAQs or any info your bot should know"
                  rows={3}
                />
              </div>
              <div>
                <Label
                  htmlFor="contactNumber"
                  className="text-gray-700 font-medium"
                >
                  Customer Support Contact
                </Label>
                <Input
                  id="contactNumber"
                  name="contactNumber"
                  value={formData.contactNumber}
                  onChange={handleChange}
                  placeholder="+1 (555) 123-4567"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Your bot will share this for human assistance.
                </p>
              </div>
              <div className="flex justify-between">
                <Button
                  variant="secondary"
                  onClick={prevStep}
                  disabled={isLoading}
                >
                  <ArrowLeft className="w-4 h-4 mr-1" /> Back
                </Button>
                <Button onClick={handleSubmit} disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />{" "}
                      Creating...
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4 mr-2" /> Complete Setup
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}

          {error && <p className="mt-4 text-red-600">{error}</p>}
          {success && !isLoading && (
            <p className="mt-4 text-green-600">Bot successfully created!</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default MyBotsPage;
