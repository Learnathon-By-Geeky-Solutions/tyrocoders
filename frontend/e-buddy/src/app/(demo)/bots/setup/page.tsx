'use client';

import { useState } from 'react';

export default function BotSetupPage() {
  const [step, setStep] = useState(1);

  const nextStep = () => setStep((prev) => Math.min(prev + 1, 3));
  const prevStep = () => setStep((prev) => Math.max(prev - 1, 1));

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-3xl bg-white shadow-xl rounded-xl p-8">
        <h1 className="text-3xl font-extrabold text-center text-blue-700 mb-10">Bot Setup</h1>
        
        {/* Modern Step Indicator */}
        <div className="flex items-center justify-between mb-12">
          {/** Step Circle Component */}
          {[1, 2, 3].map((s, idx) => (
            <div key={s} className="flex flex-col items-center w-1/3">
              <div
                className={`w-12 h-12 flex items-center justify-center rounded-full border-2 transition-colors 
                ${step === s 
                  ? 'bg-blue-600 border-blue-600 text-white shadow-md' 
                  : step > s 
                  ? 'bg-green-500 border-green-500 text-white shadow-md' 
                  : 'bg-white border-gray-300 text-gray-600'}`}
              >
                {s}
              </div>
              <span className={`mt-2 text-sm ${step === s || step > s ? 'font-bold text-blue-600' : 'text-gray-600'}`}>
                {s === 1 ? 'Info' : s === 2 ? 'URL Setup' : 'Tuning'}
              </span>
              {idx < 2 && (
                <div className="flex-1 h-1 bg-gray-300 w-full mx-2 rounded-full" />
              )}
            </div>
          ))}
        </div>

        {/* Form Container */}
        <div className="space-y-8">
          {/* Step 1: Info */}
          {step === 1 && (
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Step 1: Information</h2>
              <form className="space-y-6">
                <div>
                  <label className="block text-gray-700 mb-2">Bot Name</label>
                  <input 
                    type="text" 
                    placeholder="Enter bot name" 
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Model</label>
                  <select 
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                  >
                    <option value="">Select model</option>
                    <option value="gemini">Gemini</option>
                    <option value="others">Others</option>
                  </select>
                </div>
              </form>
              <div className="mt-8 flex justify-end">
                <button 
                  onClick={nextStep} 
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          )}

          {/* Step 2: URL Setup */}
          {step === 2 && (
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Step 2: URL for Scrape</h2>
              <form className="space-y-6">
                <div>
                  <label className="block text-gray-700 mb-2">URL for Scrape</label>
                  <input 
                    type="url" 
                    placeholder="Enter URL to scrape" 
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                  />
                </div>
              </form>
              <div className="mt-8 flex justify-between">
                <button 
                  onClick={prevStep} 
                  className="bg-gray-300 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  Back
                </button>
                <button 
                  onClick={nextStep} 
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Tuning */}
          {step === 3 && (
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Step 3: Tuning</h2>
              <form className="space-y-6">
                <div>
                  <label className="block text-gray-700 mb-2">Initial Output Message</label>
                  <textarea 
                    placeholder="What should the bot say first?" 
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                    rows={2}
                  ></textarea>
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">FAQ / Company Info</label>
                  <textarea 
                    placeholder="Enter FAQ or company information" 
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                    rows={3}
                  ></textarea>
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Customer Care Contact Number</label>
                  <input 
                    type="text" 
                    placeholder="Enter contact number" 
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                  />
                </div>
              </form>
              <div className="mt-8 flex justify-between">
                <button 
                  onClick={prevStep} 
                  className="bg-gray-300 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  Back
                </button>
                <button 
                  onClick={() => alert('Setup complete!')} 
                  className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
                >
                  Finish Setup
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
