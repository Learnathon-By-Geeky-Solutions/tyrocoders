SUBSCRIPTION_PACKAGES = [
    {
        "name": "Free",
        "price_per_month": 0,
        "price_per_year": 0,
        "features": {
            "chatbot_limit": 1,
            "monthly_message_limit": 100,
            "character_training_limit": 10000,
            "models_available": ["gemini-2.0-flash"],
            "support": "Community Support",
        },
    },
    {
        "name": "Starter",
        "price_per_month": 19,
        "price_per_year": 199,
        "features": {
            "chatbot_limit": 3,
            "monthly_message_limit": 3000,
            "character_training_limit": 100000,
            "models_available": ["gemini-2.0-flash", "gpt-3.5-turbo"],
            "support": "Email Support",
        },
    },
    {
        "name": "Pro",
        "price_per_month": 49,
        "price_per_year": 499,
        "features": {
            "chatbot_limit": 10,
            "monthly_message_limit": 10000,
            "character_training_limit": 500000,
            "models_available": ["gemini-2.0-flash", "gemini-2.0-pro", "gpt-4", "claude-3-sonnet"],
            "support": "Priority Email & Chat Support",
        },
    },
    {
        "name": "Enterprise",
        "price_per_month": 129,
        "price_per_year": 1299,
        "features": {
            "chatbot_limit": "Unlimited",
            "monthly_message_limit": "Unlimited",
            "character_training_limit": "Unlimited",
            "models_available": ["gemini-2.0-flash", "gemini-2.0-pro", "gpt-4", "claude-3-opus", "deepseek-coder"],
            "support": "Dedicated Account Manager + SLA",
        },
    },
]


COMMON_ADDONS = {
    # Standardized pricing, tier-based quantities
    "extra_chatbot": {
        "description": "Additional Chatbots",
        "unit_price": 7.99,  # Fixed price
        "tier_quantities": {
            "Free": 1,
            "Starter": 1, 
            "Pro": 2,
        }
    },
    
    "extra_messages": {
        "description": "Message Pack",
        "unit_price": 4.99,  # Fixed price
        "tier_quantities": {
            "Free": 500,
            "Starter": 1000,
            "Pro": 2500,
        }
    }
}