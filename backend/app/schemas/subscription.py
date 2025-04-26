from pydantic import BaseModel, field_validator
from core.subscription_packages import SUBSCRIPTION_PACKAGES, COMMON_ADDONS

class PaymentRequest(BaseModel):
    package_name: str  # "Pro" or "extra_chatbot" or "extra_messages"
    interval: str
    amount: float
    quantity: int = 1  # Default for addons

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "package_name": "Pro",
                    "interval": "year",
                    "amount": 499.00,
                },
                {
                    "package_name": "extra_chatbot",
                    "interval": "addon",
                    "amount": 7.99,
                    "quantity": 2
                }
            ]
        }

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, value, values):
        package_name = values.data.get('package_name')
        interval = values.data.get('interval')
        quantity = values.data.get('quantity', 1)

        if interval == "addon":
            addon = COMMON_ADDONS.get(package_name)
            if not addon:
                raise ValueError(f"Invalid addon type: {package_name}")
            
            expected_amount = addon["unit_price"] * quantity
            if abs(value - expected_amount) > 0.01:
                raise ValueError(
                    f"Invalid amount for {package_name} addon. "
                    f"Expected: {expected_amount}, Received: {value}"
                )
        else:  # Subscription
            package = next(
                (p for p in SUBSCRIPTION_PACKAGES 
                 if p["name"].lower() == package_name.lower()),
                None
            )
            if not package:
                raise ValueError(f"Invalid package name: {package_name}")
            
            expected_amount = package.get(f"price_per_{interval}")
            if expected_amount is None:
                raise ValueError(f"Package {package_name} doesn't support {interval}ly billing")
            
            if abs(value - expected_amount) > 0.01:
                raise ValueError(
                    f"Invalid amount for {package_name} {interval}ly subscription. "
                    f"Expected: {expected_amount}, Received: {value}"
                )
        
        return value

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v, values):
        if values.data.get('interval') != "addon" and v != 1:
            raise ValueError("Quantity can only be >1 for addons")
        return v
    

class SaveCheckoutSessionRequest(BaseModel):
    session_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "cs_test_a1KSmXns62YUwVISfGFCS6gaiRHvKBncb9KoyZnbcM7A4K5ydLd1rX4CTm"
            }
        }
    
