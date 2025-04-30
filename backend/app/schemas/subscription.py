from pydantic import BaseModel, field_validator
from core.subscription_packages import SUBSCRIPTION_PACKAGES, COMMON_ADDONS

class PaymentRequest(BaseModel):
    """
    Model representing a payment request for a subscription or addon.

    This model is used to process payments for different subscription packages or addons. It includes 
    validation for the amount and quantity based on the package and addon details.

    Attributes:
        package_name (str): The name of the subscription package or addon (e.g., "Pro", "extra_chatbot", "extra_messages").
        interval (str): The billing interval for the package ("month", "year", or "addon").
        amount (float): The amount to be paid for the selected package or addon.
        quantity (int): The quantity of the addon, default is 1 (only used for addons).

    Example:
        {
            "package_name": "Pro",
            "interval": "year",
            "amount": 499.00,
        }
        {
            "package_name": "extra_chatbot",
            "interval": "addon",
            "amount": 7.99,
            "quantity": 2
        }

    Validators:
        - `validate_amount`: Ensures that the amount corresponds to the expected price for the given package or addon.
        - `validate_quantity`: Ensures that the quantity is greater than 1 only for addons.
    """
    package_name: str
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
        """
        Validates the payment amount to ensure it matches the expected value for the package or addon.

        - For addons, the amount must match the unit price of the addon multiplied by the quantity.
        - For subscriptions, the amount must match the subscription price per the selected billing interval.
        
        Args:
            value (float): The amount to be validated.
            values (dict): The other field values in the request.

        Raises:
            ValueError: If the amount does not match the expected value.
        
        Returns:
            float: The validated amount.
        """
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
        """
        Validates the quantity for an addon.

        - Quantity can only be greater than 1 for addons. 
        - For subscription packages, quantity must be 1.

        Args:
            v (int): The quantity value to be validated.
            values (dict): The other field values in the request.

        Raises:
            ValueError: If the quantity is greater than 1 for subscriptions.

        Returns:
            int: The validated quantity.
        """
        if values.data.get('interval') != "addon" and v != 1:
            raise ValueError("Quantity can only be >1 for addons")
        return v
    

class SaveCheckoutSessionRequest(BaseModel):
    """
    Model representing a request to save a checkout session.

    This model is used to store the session ID of a checkout session, which is generated after the user initiates the payment process.

    Attributes:
        session_id (str): The unique identifier for the checkout session.

    Example:
        {
            "session_id": "cs_test_a1KSmXns62YUwVISfGFCS6gaiRHvKBncb9KoyZnbcM7A4K5ydLd1rX4CTm"
        }
    """
    session_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "cs_test_a1KSmXns62YUwVISfGFCS6gaiRHvKBncb9KoyZnbcM7A4K5ydLd1rX4CTm"
            }
        }
