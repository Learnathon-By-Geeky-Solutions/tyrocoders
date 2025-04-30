from fastapi import APIRouter, Depends, HTTPException
from services.subscription_service import SubscriptionService
from middlewares import authenticate_token
from schemas.subscription import PaymentRequest, SaveCheckoutSessionRequest
from fastapi.responses import JSONResponse

subscription_router = APIRouter()
subscription_service = SubscriptionService()

@subscription_router.post("/create-checkout-session")
async def create_checkout_session(
    payment_data: PaymentRequest,
    user_id=Depends(authenticate_token),
):
    """
    Create a Stripe checkout session for the user to initiate a subscription payment.

    Args:
        payment_data (PaymentRequest): Payment request details including subscription type and amount.
        user_id: Authenticated user ID obtained from the token.

    Returns:
        JSONResponse: Stripe session details for frontend redirection.
    """
    return await subscription_service.create_checkout_session(
        user_id, payment_data
    )


@subscription_router.post("/save-checkout-session")
async def save_checkout_session(
    session_id: SaveCheckoutSessionRequest,
    user_id=Depends(authenticate_token),
):
    """
    Save the completed checkout session after payment confirmation.

    Args:
        session_id (SaveCheckoutSessionRequest): Stripe session ID to be saved after successful payment.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: Confirmation of successful subscription save operation.
    """
    return await subscription_service.save_checkout_session(
        user_id, session_id
    )
