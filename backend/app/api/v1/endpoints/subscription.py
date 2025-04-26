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
    return await subscription_service.create_checkout_session(
        user_id, payment_data
    )

@subscription_router.post("/save-checkout-session")
async def save_checkout_session(
    session_id: SaveCheckoutSessionRequest,
    user_id=Depends(authenticate_token),
):
    return await subscription_service.save_checkout_session(
        user_id, session_id
    )
