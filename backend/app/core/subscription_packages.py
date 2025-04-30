"""
Subscription and Add-on Configuration

This module defines all available subscription packages and common add-ons
for users of the chatbot platform. Each package offers a different level of
resources, access to models, and support tiers. Add-ons allow users to extend
specific capabilities like chatbots and message quotas beyond their base plans.
"""

# Default LLM model used across subscription tiers
GEMINI_MODEL = "gemini-2.0-flash"

# Subscription packages available for users
SUBSCRIPTION_PACKAGES = [
    {
        "name": "Free",  # Free tier with basic access
        "price_per_month": 0,
        "price_per_year": 0,
        "features": {
            "chatbot_limit": 1,
            "monthly_message_limit": 100,
            "character_training_limit": 10000,
            "models_available": [GEMINI_MODEL],
            "support": "Community Support",  # No guaranteed support
        },
    },
    {
        "name": "Starter",  # Low-cost entry-level plan
        "price_per_month": 19,
        "price_per_year": 199,
        "features": {
            "chatbot_limit": 3,
            "monthly_message_limit": 3000,
            "character_training_limit": 100000,
            "models_available": [GEMINI_MODEL, "gpt-3.5-turbo"],
            "support": "Email Support",  # Basic email help
        },
    },
    {
        "name": "Pro",  # Mid-tier package for serious users
        "price_per_month": 49,
        "price_per_year": 499,
        "features": {
            "chatbot_limit": 10,
            "monthly_message_limit": 10000,
            "character_training_limit": 500000,
            "models_available": [
                GEMINI_MODEL,
                "gemini-2.0-pro",
                "gpt-4",
                "claude-3-sonnet",
            ],
            "support": "Priority Email & Chat Support",  # Faster response times
        },
    },
    {
        "name": "Enterprise",  # High-end package for organizations
        "price_per_month": 129,
        "price_per_year": 1299,
        "features": {
            "chatbot_limit": "Unlimited",
            "monthly_message_limit": "Unlimited",
            "character_training_limit": "Unlimited",
            "models_available": [
                GEMINI_MODEL,
                "gemini-2.0-pro",
                "gpt-4",
                "claude-3-opus",
                "deepseek-coder",
            ],
            "support": "Dedicated Account Manager + SLA",  # Highest level of support
        },
    },
]

# Add-ons available to supplement base plans
COMMON_ADDONS = {
    "extra_chatbot": {
        "description": "Additional Chatbots",  # Extend chatbot count beyond plan
        "unit_price": 7.99,  # Flat price per chatbot
        "tier_quantities": {
            "Free": 1,
            "Starter": 1,
            "Pro": 2,
        },
    },

    "extra_messages": {
        "description": "Message Pack",  # Extend monthly message limits
        "unit_price": 4.99,  # Flat price per pack
        "tier_quantities": {
            "Free": 500,     # Adds 500 messages for Free users
            "Starter": 1000, # Adds 1000 for Starter users
            "Pro": 2500,     # Adds 2500 for Pro users
        },
    }
}
